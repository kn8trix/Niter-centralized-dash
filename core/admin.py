from django.contrib import admin

from .models import (
    AcademicEvent,
    BusSchedule,
    ClassRoutine,
    Club,
    ClubEvent,
    ClubRegistration,
    ContentBlock,
    Course,
    CourseMaterial,
    Department,
    Driver,
    EditablePage,
    FacultyMember,
    GoogleUserToken,
    MedicalAppointment,
    MedicalChatMessage,
    MedicalChatThread,
    MealSubscription,
    MealTicket,
    NoteAnalysis,
    Notice,
    Notification,
    PageTemplate,
    PaymentTransaction,
    ResearchMessage,
    ResearchThread,
    Routine,
    TransportBooking,
    TransportRoute,
    UserNote,
    UserNotificationPreference,
)


@admin.register(NoteAnalysis)
class NoteAnalysisAdmin(admin.ModelAdmin):
    """Inspect queued/failed note analyses (Huey background tasks)."""

    list_display = ('analysis_id', 'user', 'status', 'sentence_count', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('analysis_id', 'user__username')
    list_select_related = ('user',)
    readonly_fields = ('analysis_id', 'content', 'summary', 'keywords', 'created_at', 'completed_at')


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
    list_display = ('title', 'slug', 'page_type', 'template', 'is_published', 'show_in_nav', 'updated_at')
    list_filter = ('page_type', 'is_published', 'show_in_nav')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ContentBlockInline]


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ('element_id', 'page', 'block_type', 'updated_at')
    list_filter = ('block_type',)
    list_select_related = ('page',)
    search_fields = ('element_id', 'page__title')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """Publish/manage official institutional announcements."""

    list_display = ('title', 'category', 'author', 'is_published', 'created_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    list_select_related = ('author',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Course catalog entries grouping uploaded materials."""

    list_display = ('code', 'title', 'department', 'semester')
    list_filter = ('department', 'semester')
    search_fields = ('code', 'title')


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    """Uploaded documents served on the Academic Notes drive."""

    list_display = ('title', 'course', 'display_type', 'file', 'uploaded_at')
    list_filter = ('uploaded_at', 'course__department')
    search_fields = ('title', 'course__code', 'course__title')
    list_select_related = ('course',)
    date_hierarchy = 'uploaded_at'
    readonly_fields = ('uploaded_at',)


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

    list_display = ('ticket_token', 'user', 'meal_type', 'payment_status', 'is_redeemed', 'claimed_at')
    list_filter = ('meal_type', 'payment_status', 'is_redeemed', 'claimed_at')
    search_fields = ('ticket_token', 'user__username')
    list_select_related = ('user',)


@admin.register(TransportBooking)
class TransportBookingAdmin(admin.ModelAdmin):
    """Inspect seat bookings; QR tokens are scanned at boarding."""

    list_display = ('qr_token', 'user', 'route_name', 'departure_time', 'seat_number', 'payment_status', 'booked_at')
    list_filter = ('payment_status', 'departure_time', 'booked_at')
    search_fields = ('qr_token', 'route_name', 'user__username')
    list_select_related = ('user',)


class BusScheduleInline(admin.TabularInline):
    """Manage a route's departure times directly under the route form."""

    model = BusSchedule
    extra = 1


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """Campus transport drivers assigned to routes."""

    list_display = ('name', 'phone', 'license_number', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'phone', 'license_number')


@admin.register(TransportRoute)
class TransportRouteAdmin(admin.ModelAdmin):
    """DB-backed bus routes with per-route capacity, driver, and schedules."""

    list_display = ('name', 'origin', 'destination', 'capacity', 'fare', 'driver', 'is_active')
    list_filter = ('is_active', 'driver')
    search_fields = ('name', 'origin', 'destination')
    list_select_related = ('driver',)
    inlines = [BusScheduleInline]


@admin.register(MedicalAppointment)
class MedicalAppointmentAdmin(admin.ModelAdmin):
    """Manage doctor appointment slots and statuses."""

    list_display = ('doctor_name', 'user', 'appointment_date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'doctor_name', 'appointment_date')
    search_fields = ('doctor_name', 'user__username', 'reason')
    list_select_related = ('user',)


@admin.register(MedicalChatThread)
class MedicalChatThreadAdmin(admin.ModelAdmin):
    """Patient ↔ doctor consultation threads (one per appointment)."""

    list_display = ('id', 'patient', 'doctor_name', 'status', 'updated_at')
    list_filter = ('status', 'updated_at')
    search_fields = ('patient__username', 'patient__email', 'doctor_name')
    list_select_related = ('patient', 'appointment')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MedicalChatMessage)
class MedicalChatMessageAdmin(admin.ModelAdmin):
    """Messages inside consultation threads."""

    list_display = ('thread', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__username', 'thread__doctor_name')
    list_select_related = ('thread', 'sender')
    readonly_fields = ('created_at',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Academic departments powering the directory + detail hubs."""

    list_display = ('name', 'code', 'slug', 'head_of_dept', 'office_location')
    list_filter = ('code',)
    search_fields = ('name', 'code', 'head_of_dept')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(FacultyMember)
class FacultyMemberAdmin(admin.ModelAdmin):
    """Faculty listings on each department hub."""

    list_display = ('name', 'department', 'designation', 'email')
    list_filter = ('department',)
    search_fields = ('name', 'designation', 'email', 'department__name')
    list_select_related = ('department',)


@admin.register(ClassRoutine)
class ClassRoutineAdmin(admin.ModelAdmin):
    """Weekly class/lab periods per department and semester."""

    list_display = ('department', 'semester', 'day_of_week', 'subject', 'time_slot', 'room')
    list_filter = ('department', 'semester', 'day_of_week')
    search_fields = ('subject', 'room', 'department__name')
    list_select_related = ('department',)


@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    """Academic calendar entries — exams, holidays, assignment deadlines."""

    list_display = ('title', 'category', 'event_date')
    list_filter = ('category', 'event_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'event_date'


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    """Per-user weekly schedules (AI-extracted or pasted as JSON)."""

    list_display = ('user', 'source_name', 'updated_at')
    search_fields = ('user__username', 'source_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Student clubs — lead staff member and banner image."""

    list_display = ('name', 'slug', 'lead_user')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_select_related = ('lead_user',)


@admin.register(ClubEvent)
class ClubEventAdmin(admin.ModelAdmin):
    """Upcoming club events shown on the /clubs/ page."""

    list_display = ('title', 'club', 'event_date', 'location', 'capacity')
    list_filter = ('event_date', 'club')
    search_fields = ('title', 'club__name', 'location')
    list_select_related = ('club',)
    date_hierarchy = 'event_date'


@admin.register(ClubRegistration)
class ClubRegistrationAdmin(admin.ModelAdmin):
    """Approve club membership requests from the admin."""

    list_display = ('student', 'club', 'status', 'joined_at')
    list_filter = ('status', 'club', 'joined_at')
    search_fields = ('student__username', 'student__email', 'club__name')
    list_select_related = ('student', 'club')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """Recorded checkout payments — mark pending wallet payments completed."""

    list_display = ('transaction_id', 'user', 'amount', 'payment_method', 'purpose', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'purpose', 'created_at')
    search_fields = ('transaction_id', 'wallet_trx', 'user__username', 'description')
    list_select_related = ('user',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    @admin.display(description='Mark completed')
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, '%d payment(s) marked completed.' % updated)

    actions = ['mark_completed']


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    """Per-user alert + theme preferences."""

    list_display = ('user', 'email_alerts', 'sms_alerts', 'push_notifications', 'dark_mode', 'theme', 'compact_layout')
    list_filter = ('email_alerts', 'sms_alerts', 'push_notifications', 'dark_mode', 'theme', 'compact_layout')
    search_fields = ('user__username', 'user__email')
    list_select_related = ('user',)


@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    """Student notes backing the Notes Engine workspace."""

    list_display = ('title', 'user', 'updated_at')
    search_fields = ('title', 'content', 'user__username')
    list_filter = ('updated_at',)
    list_select_related = ('user',)


class ResearchMessageInline(admin.TabularInline):
    """Messages inside a Research AI thread."""

    model = ResearchMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')


@admin.register(ResearchThread)
class ResearchThreadAdmin(admin.ModelAdmin):
    """Research AI conversations (OpenRouter-backed chat threads)."""

    list_display = ('title', 'user', 'citation_style', 'updated_at')
    list_filter = ('citation_style', 'updated_at')
    search_fields = ('title', 'user__username', 'user__email')
    list_select_related = ('user',)
    inlines = [ResearchMessageInline]


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

