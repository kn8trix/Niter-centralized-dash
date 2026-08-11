"""Tests for the payments app: order creation, bKash / Nagad webhook
handling, and the SUCCESS connector that marks tickets/bookings PAID and
generates their active QR / token code."""

import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import MealTicket, Notification, TransportBooking

from . import services
from .models import PaymentOrder


def _user(username='pay_tester'):
    return User.objects.create_user(username=username, password='x12345678')


def _booking(user, **kwargs):
    defaults = {
        'user': user,
        'route_name': 'Route 1: Main Campus Loop',
        'departure_time': '08:00 AM',
        'seat_number': 1,
        'payment_status': 'pending',
    }
    defaults.update(kwargs)
    return TransportBooking.objects.create(**defaults)


def _ticket(user, **kwargs):
    defaults = {
        'user': user,
        'meal_type': 'lunch',
        'payment_status': 'pending',
    }
    defaults.update(kwargs)
    return MealTicket.objects.create(**defaults)


class CreatePaymentOrderTests(TestCase):
    def setUp(self):
        self.user = _user()
        self.booking = _booking(self.user)

    def test_creates_pending_order_with_invoice_id(self):
        order = services.create_payment_order(self.user, self.booking, 'bkash', '30.00')
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.amount, 30)
        self.assertEqual(order.provider, 'bkash')
        self.assertTrue(order.merchant_invoice_id.startswith('PINV-'))
        self.assertEqual(order.item, self.booking)

    def test_idempotent_for_same_item(self):
        first = services.create_payment_order(self.user, self.booking, 'nagad', 45)
        second = services.create_payment_order(self.user, self.booking, 'nagad', 45)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(PaymentOrder.objects.count(), 1)

    def test_rejects_bad_provider(self):
        with self.assertRaises(ValueError):
            services.create_payment_order(self.user, self.booking, 'paypal', 10)

    def test_rejects_non_positive_amount(self):
        with self.assertRaises(ValueError):
            services.create_payment_order(self.user, self.booking, 'bkash', '0')
        with self.assertRaises(ValueError):
            services.create_payment_order(self.user, self.booking, 'bkash', '-5')


class BkashWebhookTests(TestCase):
    def setUp(self):
        self.user = _user()
        self.booking = _booking(self.user)
        self.order = services.create_payment_order(self.user, self.booking, 'bkash', '30.00')
        self.url = reverse('payments_bkash_webhook')

    def _post(self, **overrides):
        payload = {
            'paymentID': 'BKA1234567890ABCD',
            'status': 'success',
            'transactionStatus': 'Completed',
            'trxID': '9J32X8KL',
            'merchantInvoiceNumber': self.order.merchant_invoice_id,
            'amount': '30.00',
            'currency': 'BDT',
        }
        payload.update(overrides)
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_success_marks_booking_paid_and_generates_qr(self):
        response = self._post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        self.order.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')
        self.assertEqual(self.order.provider_transaction_id, '9J32X8KL')
        self.assertIsNotNone(self.order.paid_at)
        self.assertEqual(self.booking.payment_status, 'paid')
        self.assertIsNotNone(self.booking.paid_at)
        self.assertTrue(self.booking.qr_token.startswith('TR-'))
        # Real-time notification pushed for the owner.
        self.assertTrue(
            Notification.objects.filter(user=self.user, category='transport').exists()
        )

    def test_repeated_callback_is_idempotent(self):
        self._post()
        self.booking.refresh_from_db()
        first_token = self.booking.qr_token
        self._post()
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.qr_token, first_token)

    def test_get_callback_with_payment_id(self):
        # Callback GET carries only paymentID — match by provider_transaction_id.
        self.order.provider_transaction_id = 'BKA1234567890ABCD'
        self.order.save(update_fields=['provider_transaction_id'])
        response = self.client.get(self.url, {
            'paymentID': 'BKA1234567890ABCD',
            'status': 'success',
        })
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, 'paid')

    def test_unknown_order_returns_404(self):
        response = self._post(merchantInvoiceNumber='PINV-NOPE')
        self.assertEqual(response.status_code, 404)

    def test_amount_mismatch_rejected(self):
        response = self._post(amount='999.00')
        self.assertEqual(response.status_code, 400)
        self.order.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(self.order.status, 'failed')
        self.assertEqual(self.booking.payment_status, 'pending')
        self.assertIsNone(self.booking.qr_token)

    def test_unparseable_amount_rejected(self):
        response = self._post(amount='not-a-number')
        self.assertEqual(response.status_code, 400)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'failed')

    def test_failure_after_success_keeps_paid(self):
        self._post()
        response = self._post(status='failure', transactionStatus='Failed')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')
        self.assertEqual(self.booking.payment_status, 'paid')
        self.assertIsNotNone(self.booking.qr_token)

    def test_cross_provider_callback_rejected(self):
        # A Nagad order must never be fulfilled through the bKash endpoint.
        ticket = _ticket(self.user, meal_type='dinner')
        nagad_order = services.create_payment_order(self.user, ticket, 'nagad', '90.00')
        response = self._post(merchantInvoiceNumber=nagad_order.merchant_invoice_id)
        self.assertEqual(response.status_code, 400)
        ticket.refresh_from_db()
        self.assertEqual(ticket.payment_status, 'pending')

    def test_failure_marks_order_failed_keeps_item_pending(self):
        response = self._post(status='failure', transactionStatus='Failed')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'failed')
        self.order.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(self.order.status, 'failed')
        self.assertEqual(self.booking.payment_status, 'pending')
        self.assertIsNone(self.booking.qr_token)

    def test_non_final_status_keeps_waiting(self):
        response = self._post(status='Initiated', transactionStatus='Initiated')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'pending')
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'pending')


class NagadWebhookTests(TestCase):
    def setUp(self):
        self.user = _user()
        self.ticket = _ticket(self.user)
        self.order = services.create_payment_order(self.user, self.ticket, 'nagad', '90.00')
        self.url = reverse('payments_nagad_webhook')

    def _callback_params(self, status='Success', signature=None, ref='NGX987654'):
        if signature is None:
            signature = services.nagad_signature(ref, self.order.merchant_invoice_id, status)
        return {
            'order_id': self.order.merchant_invoice_id,
            'payment_ref_id': ref,
            'status': status,
            'signature': signature,
        }

    def test_success_marks_ticket_paid_and_generates_token(self):
        response = self.client.get(self.url, self._callback_params())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        self.order.refresh_from_db()
        self.ticket.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')
        self.assertEqual(self.order.provider_transaction_id, 'NGX987654')
        self.assertEqual(self.ticket.payment_status, 'paid')
        self.assertTrue(self.ticket.ticket_token.startswith('#MEAL-'))
        self.assertTrue(
            Notification.objects.filter(user=self.user, category='meal').exists()
        )

    def test_bad_signature_rejected(self):
        response = self.client.get(self.url, self._callback_params(signature='deadbeef' * 8))
        self.assertEqual(response.status_code, 400)
        self.ticket.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.ticket.payment_status, 'pending')
        self.assertEqual(self.order.status, 'pending')

    def test_missing_signature_rejected(self):
        params = self._callback_params()
        params.pop('signature')
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 400)

    def test_failure_status_keeps_ticket_pending(self):
        response = self.client.get(self.url, self._callback_params(status='Failure'))
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.ticket.refresh_from_db()
        self.assertEqual(self.order.status, 'failed')
        self.assertEqual(self.ticket.payment_status, 'pending')
        self.assertIsNone(self.ticket.ticket_token)

    def test_unknown_order_returns_404(self):
        params = self._callback_params()
        params['order_id'] = 'PINV-NOPE'
        # Re-sign for the bogus order id so we reach the order lookup (a valid
        # signature with an unknown order must 404, not fail the signature check).
        params['signature'] = services.nagad_signature(
            params['payment_ref_id'], params['order_id'], params['status'],
        )
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 404)

    def test_signature_verification_can_be_disabled(self):
        with self.settings(PAYMENTS_VERIFY_SIGNATURES=False):
            params = self._callback_params(signature='totally-wrong')
            response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.payment_status, 'paid')

    def test_cross_provider_callback_rejected(self):
        booking = _booking(self.user, seat_number=3)
        bkash_order = services.create_payment_order(self.user, booking, 'bkash', '30.00')
        params = self._callback_params()
        params['order_id'] = bkash_order.merchant_invoice_id
        params['signature'] = services.nagad_signature(
            params['payment_ref_id'], params['order_id'], params['status'],
        )
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 400)
        booking.refresh_from_db()
        self.assertEqual(booking.payment_status, 'pending')


class PaidFlowViewTests(TestCase):
    """The parallel paid flow through the existing booking / claim views."""

    def setUp(self):
        self.user = _user()
        self.client.force_login(self.user)

    def test_book_transport_paid_flow_creates_pending_booking_and_order(self):
        response = self.client.post('/book-transport/', {
            'route_name': 'Route 1: Main Campus Loop',
            'departure_time': '08:00 AM',
            'seat_number': 5,
            'payment_method': 'bkash',
            'amount': '30.00',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['payment_status'], 'pending')
        self.assertIsNone(data['qr_token'])
        self.assertTrue(data['payment_order'].startswith('PINV-'))

        booking = TransportBooking.objects.get(pk=data['booking_id'])
        self.assertEqual(booking.payment_status, 'pending')
        self.assertIsNone(booking.qr_token)
        self.assertIsNotNone(booking.payment_order)

    def test_book_transport_free_flow_unchanged(self):
        response = self.client.post('/book-transport/', {
            'route_name': 'Route 1: Main Campus Loop',
            'departure_time': '08:00 AM',
            'seat_number': 6,
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['payment_status'], 'paid')
        self.assertTrue(data['qr_token'].startswith('TR-'))

    def test_book_transport_rejects_unknown_provider(self):
        response = self.client.post('/book-transport/', {
            'route_name': 'Route 1: Main Campus Loop',
            'departure_time': '08:00 AM',
            'seat_number': 7,
            'payment_method': 'paypal',
            'amount': '30.00',
        })
        self.assertEqual(response.status_code, 400)

    def test_claim_meal_paid_flow_creates_pending_ticket_and_order(self):
        from core.models import MealSubscription
        from django.utils import timezone
        from datetime import timedelta
        MealSubscription.objects.create(
            user=self.user, is_active=True,
            expires_at=timezone.now() + timedelta(days=30),
        )
        response = self.client.post('/claim-meal/', {
            'meal_type': 'lunch',
            'payment_method': 'nagad',
            'amount': '90.00',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['payment_status'], 'pending')
        self.assertIsNone(data['ticket_token'])
        self.assertTrue(data['payment_order'].startswith('PINV-'))

        ticket = MealTicket.objects.get(user=self.user)
        self.assertEqual(ticket.payment_status, 'pending')
        self.assertIsNone(ticket.ticket_token)

    def test_claim_meal_rejects_invalid_amount(self):
        from core.models import MealSubscription
        from django.utils import timezone
        from datetime import timedelta
        MealSubscription.objects.create(
            user=self.user, is_active=True,
            expires_at=timezone.now() + timedelta(days=30),
        )
        response = self.client.post('/claim-meal/', {
            'meal_type': 'lunch',
            'payment_method': 'nagad',
            'amount': 'not-a-number',
        })
        self.assertEqual(response.status_code, 400)

    def test_claim_meal_free_flow_unchanged(self):
        from core.models import MealSubscription
        from django.utils import timezone
        from datetime import timedelta
        MealSubscription.objects.create(
            user=self.user, is_active=True,
            expires_at=timezone.now() + timedelta(days=30),
        )
        response = self.client.post('/claim-meal/', {'meal_type': 'lunch'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['payment_status'], 'paid')
        self.assertTrue(data['ticket_token'].startswith('#MEAL-'))


class FulfillConnectorTests(TestCase):
    """Direct connector tests (idempotency + token uniqueness)."""

    def setUp(self):
        self.user = _user()

    def test_transport_connector_generates_unique_qr(self):
        booking = _booking(self.user)
        order = services.create_payment_order(self.user, booking, 'bkash', '30.00')
        services.fulfill_payment_order(order, 'TRX-1', {'status': 'success'})
        booking.refresh_from_db()
        self.assertTrue(booking.qr_token.startswith('TR-'))

        other = _booking(self.user, seat_number=2)
        other_order = services.create_payment_order(self.user, other, 'bkash', '30.00')
        services.fulfill_payment_order(other_order, 'TRX-2', {'status': 'success'})
        other.refresh_from_db()
        self.assertNotEqual(booking.qr_token, other.qr_token)

    def test_already_paid_order_is_left_untouched(self):
        booking = _booking(self.user)
        order = services.create_payment_order(self.user, booking, 'bkash', '30.00')
        services.fulfill_payment_order(order, 'TRX-1', {})
        booking.refresh_from_db()
        token = booking.qr_token
        services.fulfill_payment_order(order, 'TRX-2', {'other': 'payload'})
        booking.refresh_from_db()
        self.assertEqual(booking.qr_token, token)
        self.assertEqual(order.provider_transaction_id, 'TRX-1')

    def test_fulfill_with_deleted_item_marks_order_failed(self):
        booking = _booking(self.user)
        order = services.create_payment_order(self.user, booking, 'bkash', '30.00')
        booking.delete()
        services.fulfill_payment_order(order, 'TRX-1', {})
        order.refresh_from_db()
        self.assertEqual(order.status, 'failed')
        self.assertIn('no longer exists', order.error_message)


class GatewayCallbackApiTests(TestCase):
    """Versioned generic callback — /api/v1/payments/callback/<gateway>/.

    Thin dispatcher over the per-gateway handlers; behaviour must match the
    legacy /payments/webhook/<gateway>/ endpoints exactly."""

    def setUp(self):
        self.user = _user()
        self.booking = _booking(self.user)

    def test_bkash_success_through_generic_route(self):
        order = services.create_payment_order(self.user, self.booking, 'bkash', '30.00')
        url = reverse('payments_gateway_callback', args=['bkash'])
        response = self.client.post(url, data=json.dumps({
            'paymentID': 'BKAABC123',
            'status': 'success',
            'transactionStatus': 'Completed',
            'trxID': 'TRX-1',
            'merchantInvoiceNumber': order.merchant_invoice_id,
            'amount': '30.00',
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(order.status, 'paid')
        self.assertEqual(self.booking.payment_status, 'paid')
        self.assertTrue(self.booking.qr_token.startswith('TR-'))

    def test_nagad_success_through_generic_route(self):
        order = services.create_payment_order(self.user, self.booking, 'nagad', '45.00')
        url = reverse('payments_gateway_callback', args=['nagad'])
        payment_ref = 'NGX123456'
        status_str = 'Success'
        data = {
            'order_id': order.merchant_invoice_id,
            'payment_ref_id': payment_ref,
            'status': status_str,
            'signature': services.nagad_signature(payment_ref, order.merchant_invoice_id, status_str),
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'paid')
        self.assertEqual(order.provider_transaction_id, payment_ref)

    def test_unknown_gateway_returns_404(self):
        url = reverse('payments_gateway_callback', args=['unknown'])
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['status'], 'error')

    def test_generic_route_rejects_cross_provider_callback(self):
        # A bKash callback arriving for a Nagad order must be refused even
        # through the generic dispatcher.
        order = services.create_payment_order(self.user, self.booking, 'nagad', '45.00')
        url = reverse('payments_gateway_callback', args=['bkash'])
        response = self.client.post(url, data=json.dumps({
            'paymentID': 'BKAABC123',
            'status': 'success',
            'merchantInvoiceNumber': order.merchant_invoice_id,
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        order.refresh_from_db()
        self.assertEqual(order.status, 'pending')
