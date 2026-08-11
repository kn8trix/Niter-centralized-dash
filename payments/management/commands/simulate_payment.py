"""Alias for ``simulate_payment_callback``.

``python manage.py simulate_payment`` is a convenience alias so dev tooling
can use the shorter, gateway-native name. Options are identical:

    python manage.py simulate_payment --order PINV-XXXXXX \
        --provider bkash --status success
"""

from payments.management.commands.simulate_payment_callback import Command as BaseCommand


class Command(BaseCommand):
    help = 'Simulate a bKash/Nagad payment callback (alias for simulate_payment_callback).'
