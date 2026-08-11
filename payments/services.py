"""Payment domain logic shared by the webhook views and the dev tooling.

Kept free of request/response handling so the bKash / Nagad webhook views
(``payments.views``) and the ``simulate_payment_callback`` management command
exercise exactly the same code path.

Import graph is deliberately shallow (``core.models`` + ``core.consumers``
only) so ``core.views`` can import ``create_payment_order`` without creating
a circular import.
"""

import hashlib
import logging
import secrets
from decimal import Decimal, InvalidOperation

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from django.utils import timezone

from core.consumers import notify_user
from core.models import (
    MealTicket,
    Notification,
    TransportBooking,
    generate_meal_token,
    generate_qr_token,
)

from .models import PaymentOrder

logger = logging.getLogger('payments')

# --- Callback status classification ------------------------------------------
# bKash callback GET status: 'success' / 'failure' / 'cancel'; bKash status
# API / webhook: 'Completed' / 'Failed' / 'Cancelled' / 'Initiated' /
# 'Processing'. Nagad callback: 'Success' / 'Failure' / 'Cancel'.
SUCCESS_STATUSES = frozenset({'success', 'completed'})
FAILURE_STATUSES = frozenset({'failure', 'failed', 'cancel', 'cancelled'})


def classify_callback_status(raw_status):
    """Map a gateway status string to an order state.

    Returns ``'paid'``, ``'failed'``, or ``'pending'`` (not yet final —
    e.g. bKash ``Initiated``/``Processing`` means keep waiting).
    """
    status = (raw_status or '').strip().lower()
    if status in SUCCESS_STATUSES:
        return 'paid'
    if status in FAILURE_STATUSES:
        return 'failed'
    return 'pending'


def nagad_signature(payment_ref_id, order_id, status):
    """Recompute the Nagad callback signature for verification.

    Nagad signs its callback as ``sha256(payment_ref_id . order_id . status)``
    (lowercase hex). The merchant recomputes the same value and compares it to
    the ``signature`` query parameter the gateway returned.
    """
    raw = '%s%s%s' % (payment_ref_id or '', order_id or '', status or '')
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


# --- Order creation -----------------------------------------------------------

def _generate_invoice_id():
    """Return an unused merchant invoice reference, e.g. ``PINV-4F2A1C``."""
    for _ in range(50):
        invoice_id = 'PINV-' + secrets.token_hex(3).upper()
        if not PaymentOrder.objects.filter(merchant_invoice_id=invoice_id).exists():
            return invoice_id
    raise RuntimeError('Could not allocate a unique payment invoice id')


def create_payment_order(user, item, provider, amount, currency='BDT'):
    """Create (or return the existing) PaymentOrder for a paid-flow item.

    Idempotent per item: an item has at most one order (unique constraint on
    content_type + object_id), so a retry after a partial save returns the
    same order instead of duplicating it.
    """
    if provider not in dict(PaymentOrder.PROVIDER_CHOICES):
        raise ValueError(
            'provider must be one of %s' % ', '.join(dict(PaymentOrder.PROVIDER_CHOICES))
        )
    try:
        amount = Decimal(amount)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError('amount must be a valid decimal number.') from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError('amount must be a positive number.')

    item_type = ContentType.objects.get_for_model(item)
    existing = PaymentOrder.objects.filter(content_type=item_type, object_id=item.pk).first()
    if existing is not None:
        return existing

    try:
        return PaymentOrder.objects.create(
            user=user,
            provider=provider,
            amount=amount,
            currency=currency,
            merchant_invoice_id=_generate_invoice_id(),
            content_type=item_type,
            object_id=item.pk,
        )
    except IntegrityError:
        # Concurrent creation for the same item — return the winner's order
        # instead of surfacing a misleading conflict to the caller.
        return PaymentOrder.objects.get(content_type=item_type, object_id=item.pk)


# --- SUCCESS connector: item -> PAID + active QR/token ------------------------

def _push_notification(notification):
    """Broadcast a fresh Notification over the user's WebSocket group.

    Mirrors ``core.views._broadcast_notification`` (kept here to avoid a
    views->services import cycle). Must only fire after the enclosing
    transaction commits — call via ``transaction.on_commit``.
    """
    notify_user(notification.user_id, {
        'id': notification.pk,
        'title': notification.title,
        'message': notification.message,
        'category': notification.category,
        'is_read': notification.is_read,
        'created_at': notification.created_at.isoformat(),
    })


def _unique_qr_token(attempts=5):
    """Return a QR token that is not already taken (retry on collision)."""
    for _ in range(attempts):
        token = generate_qr_token()
        if not TransportBooking.objects.filter(qr_token=token).exists():
            return token
    # Exhausted — take the last generated token; the unique constraint will
    # surface a genuine collision to the caller.
    return generate_qr_token()


@transaction.atomic
def fulfill_payment_order(order, provider_transaction_id='', raw_callback=None):
    """Confirm a SUCCESS callback: order -> paid, item -> PAID + QR/token.

    Idempotent: repeated callbacks (gateways often resend) return the already
    paid order and never regenerate or clobber an existing code. The real-time
    notification push is deferred with ``on_commit`` so a rollback can never
    leave a phantom alert.
    """
    if order.status == 'paid':
        return order

    item = order.item
    if item is None:
        order.status = 'failed'
        order.error_message = 'Linked item no longer exists.'
        order.save(update_fields=['status', 'error_message', 'updated_at'])
        return order

    order.status = 'paid'
    if provider_transaction_id:
        order.provider_transaction_id = provider_transaction_id
    if raw_callback:
        order.raw_callback = raw_callback
    order.paid_at = timezone.now()
    order.save(update_fields=['status', 'provider_transaction_id', 'raw_callback', 'paid_at', 'updated_at'])

    if isinstance(item, TransportBooking):
        if not item.qr_token:
            item.qr_token = _unique_qr_token()
        item.payment_status = 'paid'
        item.paid_at = timezone.now()
        item.save(update_fields=['qr_token', 'payment_status', 'paid_at'])
        title = 'Transport payment confirmed'
        message = 'Seat %s on %s (%s) is PAID — boarding code %s is ready.' % (
            item.seat_number, item.route_name, item.departure_time, item.qr_token)
        category = 'transport'
    elif isinstance(item, MealTicket):
        if not item.ticket_token:
            item.ticket_token = generate_meal_token()
        item.payment_status = 'paid'
        item.paid_at = timezone.now()
        item.save(update_fields=['ticket_token', 'payment_status', 'paid_at'])
        title = 'Meal payment confirmed'
        message = 'Your %s token %s is PAID and ready to redeem.' % (item.meal_type, item.ticket_token)
        category = 'meal'
    else:
        logger.warning(
            'fulfill_payment_order: unsupported item type %s for order %s',
            type(item).__name__, order.merchant_invoice_id,
        )
        return order

    notification = Notification.objects.create(
        user=item.user,
        title=title,
        message=message,
        category=category,
    )
    transaction.on_commit(lambda: _push_notification(notification))
    return order


def reject_payment_order(order, reason, status='failed'):
    """Mark an order failed/cancelled (the linked item stays pending)."""
    order.status = status
    order.error_message = reason
    order.save(update_fields=['status', 'error_message', 'updated_at'])
    return order
