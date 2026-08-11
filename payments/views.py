"""bKash / Nagad webhook + callback endpoints.

These are server-to-server endpoints (no CSRF token, no login): the payment
gateway calls them with the outcome of a checkout. Each callback is matched
to a ``PaymentOrder`` and, on SUCCESS, fulfilled through
``payments.services.fulfill_payment_order`` which marks the linked ticket /
booking PAID and generates its active QR / token code.

Use ``python manage.py simulate_payment_callback`` to exercise these
endpoints end-to-end without merchant credentials.
"""

import json
import logging
import secrets
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import services
from .models import PaymentOrder

logger = logging.getLogger('payments')


def _match_order(payment_id='', merchant_invoice='', payment_ref_id=''):
    """Locate the PaymentOrder a callback refers to.

    Gateways identify the order either by the merchant's invoice reference
    (bKash ``merchantInvoiceNumber`` / Nagad ``order_id``) or by the
    provider-side transaction id (bKash ``paymentID`` / Nagad
    ``payment_ref_id``).
    """
    if merchant_invoice:
        order = PaymentOrder.objects.filter(merchant_invoice_id=merchant_invoice).first()
        if order is not None:
            return order
    provider_ids = [pid for pid in (payment_id, payment_ref_id) if pid]
    if provider_ids:
        return PaymentOrder.objects.filter(provider_transaction_id__in=provider_ids).first()
    return None


def _process_callback(order, status, provider_transaction_id, amount_raw, raw_payload):
    """Classify a callback and drive the order + linked item state."""
    classification = services.classify_callback_status(status)

    if classification == 'paid':
        # When the gateway echoes an amount, it must match the order exactly —
        # a mismatched "SUCCESS" is a forgery or a stale callback, not a win.
        if amount_raw is not None and str(amount_raw).strip():
            try:
                callback_amount = Decimal(str(amount_raw).strip())
            except (InvalidOperation, TypeError, ValueError):
                callback_amount = None
            if callback_amount is None:
                # Provided but unparseable — treat as suspicious, never skip.
                services.reject_payment_order(
                    order, 'Amount not parseable: %s' % amount_raw,
                )
                logger.warning(
                    'Rejected SUCCESS callback for %s: unparseable amount %r',
                    order.merchant_invoice_id, amount_raw,
                )
                return JsonResponse({'status': 'error', 'message': 'Invalid amount'}, status=400)
            if callback_amount != order.amount:
                services.reject_payment_order(
                    order,
                    'Amount mismatch: callback %s vs order %s' % (amount_raw, order.amount),
                )
                logger.warning(
                    'Rejected SUCCESS callback for %s: amount mismatch', order.merchant_invoice_id,
                )
                return JsonResponse({'status': 'error', 'message': 'Amount mismatch'}, status=400)

        services.fulfill_payment_order(order, provider_transaction_id, raw_payload)
        return JsonResponse({'status': 'success', 'order': order.merchant_invoice_id})

    if classification == 'failed':
        if order.status == 'paid':
            # A stale/out-of-order failure callback after SUCCESS must never
            # undo a confirmed payment — acknowledge and leave state as is.
            return JsonResponse({'status': 'success', 'order': order.merchant_invoice_id})
        services.reject_payment_order(order, 'Gateway reported status: %s' % status)
        return JsonResponse({'status': 'failed', 'order': order.merchant_invoice_id})

    # Initiated / Processing — not final yet. Acknowledge and keep waiting.
    return JsonResponse({'status': 'pending', 'order': order.merchant_invoice_id})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def bkash_callback(request):
    """bKash payment callback / webhook.

    Tokenized-checkout callback (GET):
        ``?paymentID=..&status=success|failure|cancel&apiVersion=1.2.0-beta``
    Sandbox webhook (JSON POST):
        ``{paymentID, transactionStatus, trxID, merchantInvoiceNumber, amount}``
    Matching is by ``merchantInvoiceNumber`` (== our
    ``PaymentOrder.merchant_invoice_id``) first, then ``paymentID``.
    ``status``/``transactionStatus`` values of ``success`` / ``Completed``
    count as SUCCESS.

    .. warning:: bKash callbacks carry no signature, so this endpoint trusts
       the gateway's word (hardened by the amount check). Production should
       confirm via the bKash status API once merchant credentials are wired
       up (reserved BKASH_* vars in .env.example).
    """
    payload = {}
    if request.method == 'POST' and request.body:
        try:
            payload = json.loads(request.body or '{}')
        except (json.JSONDecodeError, TypeError):
            payload = {}
    # Fall back to form-encoded POST fields when the body wasn't JSON.
    if not payload and request.POST:
        payload = {k: v for k, v in request.POST.items()}

    payment_id = payload.get('paymentID') or request.GET.get('paymentID', '')
    status = (
        payload.get('status')
        or payload.get('transactionStatus')
        or request.GET.get('status', '')
    )
    trx_id = (
        payload.get('trxID')
        or payload.get('trxId')
        or request.GET.get('trxID', '')
    )
    merchant_invoice = payload.get('merchantInvoiceNumber') or ''
    amount = payload.get('amount')

    order = _match_order(payment_id=payment_id, merchant_invoice=merchant_invoice)
    if order is None:
        logger.warning('bKash callback for unknown order: paymentID=%r invoice=%r', payment_id, merchant_invoice)
        return JsonResponse({'status': 'error', 'message': 'Unknown order'}, status=404)
    if order.provider != 'bkash':
        logger.warning('bKash callback for non-bKash order %s', order.merchant_invoice_id)
        return JsonResponse({'status': 'error', 'message': 'Order is not a bKash order'}, status=400)

    return _process_callback(order, status, trx_id or payment_id, amount, payload)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def nagad_callback(request):
    """Nagad payment callback.

    Nagad redirects the customer back with ``order_id``, ``payment_ref_id``,
    ``status`` ('Success'/'Failure') and a ``signature`` = ``sha256(
    payment_ref_id . order_id . status)``. The signature is recomputed and
    compared before the callback is trusted; a mismatch is rejected with 400
    and the order stays pending.

    .. warning:: The recomputed signature is tamper-evidence, not
       authentication — all three inputs are public data, so it does NOT
       prove the callback came from Nagad. Production must confirm payments
       through Nagad's verify API (``POST /verify/payment/{payment_ref_id}``)
       once merchant credentials are wired up; the signature check here only
       catches accidental corruption.
    """
    # GET/POST merged without the QueryDict multi-value pitfall ({**qs} yields
    # lists); first source that has the param wins.
    order_id = request.GET.get('order_id') or request.POST.get('order_id') or ''
    payment_ref = (
        request.GET.get('payment_ref_id') or request.POST.get('payment_ref_id')
        or request.GET.get('paymentReferenceId') or request.POST.get('paymentReferenceId')
        or ''
    )
    status = request.GET.get('status') or request.POST.get('status') or ''
    signature = request.GET.get('signature') or request.POST.get('signature') or ''

    if not order_id and not payment_ref:
        return JsonResponse(
            {'status': 'error', 'message': 'order_id or payment_ref_id required'},
            status=400,
        )

    if settings.PAYMENTS_VERIFY_SIGNATURES:
        expected = services.nagad_signature(payment_ref, order_id, status)
        provided = signature.lower()
        if not provided or not secrets.compare_digest(expected, provided):
            logger.warning('Nagad callback signature mismatch for order_id=%s', order_id)
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)

    order = _match_order(merchant_invoice=order_id, payment_ref_id=payment_ref)
    if order is None:
        logger.warning('Nagad callback for unknown order: order_id=%r ref=%r', order_id, payment_ref)
        return JsonResponse({'status': 'error', 'message': 'Unknown order'}, status=404)
    if order.provider != 'nagad':
        logger.warning('Nagad callback for non-Nagad order %s', order.merchant_invoice_id)
        return JsonResponse({'status': 'error', 'message': 'Order is not a Nagad order'}, status=400)

    raw = {
        'order_id': order_id,
        'payment_ref_id': payment_ref,
        'status': status,
        'signature': signature,
    }
    return _process_callback(order, status, payment_ref, None, raw)
