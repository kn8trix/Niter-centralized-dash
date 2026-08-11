"""Dev/testing tool: fire a realistic bKash / Nagad callback at a PaymentOrder.

Runs without any merchant credentials by posting to the real webhook
endpoints through Django's test client, so routing, CSRF exemption and the
Nagad signature check are all exercised exactly as a live gateway would.

Usage:
    python manage.py simulate_payment_callback --order PINV-XXXXXX \
        --provider bkash --status success
    python manage.py simulate_payment_callback --order PINV-XXXXXX \
        --provider nagad --status failure --trx NGX123456
"""

import json
import secrets

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.urls import reverse

from payments import services
from payments.models import PaymentOrder


class Command(BaseCommand):
    help = 'Simulate a bKash/Nagad callback for a PaymentOrder (no merchant credentials needed).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--order',
            required=True,
            help='merchant_invoice_id of the PaymentOrder to update',
        )
        parser.add_argument(
            '--provider',
            choices=['bkash', 'nagad'],
            default='bkash',
            help='which gateway callback to simulate',
        )
        parser.add_argument(
            '--status',
            choices=['success', 'failure'],
            default='success',
        )
        parser.add_argument(
            '--trx',
            default='',
            help='provider transaction id to attach (default: random)',
        )

    def handle(self, *args, **options):
        order = PaymentOrder.objects.filter(merchant_invoice_id=options['order']).first()
        if order is None:
            raise CommandError('No PaymentOrder with merchant_invoice_id %s' % options['order'])

        trx = options['trx'] or 'SIM' + secrets.token_hex(4).upper()
        success = options['status'] == 'success'
        client = Client()

        # The test client always sends ``Host: testserver``, which a hardened
        # ALLOWED_HOSTS rejects outside the test runner. Allow it for the
        # duration of this dev-only command.
        original_allowed_hosts = settings.ALLOWED_HOSTS
        if 'testserver' not in original_allowed_hosts:
            settings.ALLOWED_HOSTS = [*original_allowed_hosts, 'testserver']
        try:
            if options['provider'] == 'bkash':
                payload = {
                    'paymentID': 'BKA' + secrets.token_hex(6).upper(),
                    'status': 'success' if success else 'failure',
                    'transactionStatus': 'Completed' if success else 'Failed',
                    'trxID': trx,
                    'merchantInvoiceNumber': order.merchant_invoice_id,
                    'amount': str(order.amount),
                    'currency': 'BDT',
                }
                response = client.post(
                    reverse('payments_bkash_webhook'),
                    data=json.dumps(payload),
                    content_type='application/json',
                )
            else:
                status_str = 'Success' if success else 'Failure'
                payment_ref = trx
                data = {
                    'order_id': order.merchant_invoice_id,
                    'payment_ref_id': payment_ref,
                    'status': status_str,
                    'signature': services.nagad_signature(payment_ref, order.merchant_invoice_id, status_str),
                }
                response = client.post(reverse('payments_nagad_webhook'), data=data)
        finally:
            settings.ALLOWED_HOSTS = original_allowed_hosts

        order.refresh_from_db()
        self.stdout.write(self.style.SUCCESS(
            'Callback fired -> HTTP %s | order %s | status %s'
            % (response.status_code, order.merchant_invoice_id, order.status)
        ))
