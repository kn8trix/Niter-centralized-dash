from django.contrib import admin

from .models import (
    ContentBlock,
    EditablePage,
    GoogleUserToken,
    MedicalAppointment,
    MealSubscription,
    MealTicket,
    Notification,
    PageTemplate,
    TransportBooking,
)


class ContentBlockInline(admin.StackedInline):
    """Manage a page's editable regions directly under the page form."""

    model = ContentBlock
    extra = 1


@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')


@admin.register(EditablePage)
class EditablePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'page_type', 'template', 'is_published', 'updated_at')
    list_filter = ('page_type', 'is_published')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ContentBlockInline]


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ('element_id', 'page', 'updated_at')
    list_select_related = ('page',)
    search_fields = ('element_id', 'page__title')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Browse/manage system alerts per user."""

    list_display = ('title', 'user', 'category', 'is_read', 'created_at')
    list_filter = ('category', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    list_select_related = ('user',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


@admin.register(MealSubscription)
class MealSubscriptionAdmin(admin.ModelAdmin):
    """Manage student meal plan entitlements."""

    list_display = ('user', 'is_active', 'expires_at', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'user__email')
    list_select_related = ('user',)


@admin.register(MealTicket)
class MealTicketAdmin(admin.ModelAdmin):
    """Browse and redeem issued meal tickets."""

    list_display = ('ticket_token', 'user', 'meal_type', 'is_redeemed', 'claimed_at')
    list_filter = ('meal_type', 'is_redeemed', 'claimed_at')
    search_fields = ('ticket_token', 'user__username')
    list_select_related = ('user',)


@admin.register(TransportBooking)
class TransportBookingAdmin(admin.ModelAdmin):
    """Inspect seat bookings; QR tokens are scanned at boarding."""

    list_display = ('qr_token', 'user', 'route_name', 'departure_time', 'seat_number', 'booked_at')
    list_filter = ('departure_time', 'booked_at')
    search_fields = ('qr_token', 'route_name', 'user__username')
    list_select_related = ('user',)


@admin.register(MedicalAppointment)
class MedicalAppointmentAdmin(admin.ModelAdmin):
    """Manage doctor appointment slots and statuses."""

    list_display = ('doctor_name', 'user', 'appointment_date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'doctor_name', 'appointment_date')
    search_fields = ('doctor_name', 'user__username', 'reason')
    list_select_related = ('user',)


@admin.register(GoogleUserToken)
class GoogleUserTokenAdmin(admin.ModelAdmin):
    """Inspect per-user Google OAuth token statuses and expiry dates."""

    list_display = ('user', 'expiry', 'token_status', 'token_uri', 'scopes_count')
    list_filter = ('expiry',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = (
        'user', 'access_token', 'refresh_token', 'client_id', 'client_secret',
        'token_uri', 'scopes', 'expiry',
    )
    list_select_related = ('user',)

    @admin.display(description='Status')
    def token_status(self, obj):
        return 'Expired' if obj.is_expired else 'Active'

    @admin.display(description='Scopes')
    def scopes_count(self, obj):
        return len(obj.scopes or [])

