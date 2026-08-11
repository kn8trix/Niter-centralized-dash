from django.contrib import admin

from .models import PaymentOrder


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    """Audit payment orders and their gateway callbacks."""

    list_display = (
        'merchant_invoice_id', 'user', 'provider', 'amount', 'currency',
        'status', 'paid_at', 'created_at',
    )
    list_filter = ('provider', 'status', 'created_at')
    search_fields = ('merchant_invoice_id', 'provider_transaction_id', 'user__username')
    list_select_related = ('user',)
    readonly_fields = ('merchant_invoice_id', 'created_at', 'updated_at', 'paid_at')
