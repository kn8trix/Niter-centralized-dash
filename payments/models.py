"""Payment orders awaiting confirmation from the bKash / Nagad callbacks.

The purchased item (a ``TransportBooking`` or ``MealTicket``) is created in a
*pending* state with no active QR / token code; when the gateway callback
reports SUCCESS, ``payments.services.fulfill_payment_order`` flips the order
to ``paid`` and activates the item (status PAID + freshly generated code).
"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class PaymentOrder(models.Model):
    """A server-side payment order identified by ``merchant_invoice_id``.

    Generic-linked to the purchased item, so one table covers both the
    transport ticketing and the cafeteria meal token paid flows without
    touching their schemas beyond a status field.
    """

    PROVIDER_CHOICES = [
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_orders',
        db_index=True,
    )
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    merchant_invoice_id = models.CharField(
        max_length=32,
        unique=True,
        help_text='Merchant reference sent to the gateway, e.g. PINV-4F2A1C',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    provider_transaction_id = models.CharField(
        max_length=64,
        blank=True,
        default='',
        db_index=True,
        help_text='Gateway-side id: bKash paymentID/trxID or Nagad payment_ref_id',
    )
    raw_callback = models.JSONField(
        default=dict,
        blank=True,
        help_text='Raw callback payload for audit/debugging',
    )
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Generic link to the purchased item (TransportBooking / MealTicket).
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='+',
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']
        # Fast lookup of an item's order from the webhook matcher.
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        # At most one order per item — retries never duplicate an order.
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id'],
                name='uniq_payment_order_item',
            ),
        ]

    def __str__(self):
        return '%s · %s' % (self.merchant_invoice_id, self.get_provider_display())
