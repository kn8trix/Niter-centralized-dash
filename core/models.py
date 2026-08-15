import secrets as _secrets
import uuid
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class StudentProfile(models.Model):
    """Extra student identity fields (student ID + department) tied to a User.

    The Django ``User`` model only carries username/name/email; the portal also
    needs the institutional student ID and department, so they live here on a
    one-to-one profile record.
    """

    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science & Engineering'),
        ('TEX', 'Textile Engineering'),
        ('IPE', 'Industrial & Production Engineering'),
        ('FDAE', 'Fashion Design & Technology'),
        ('EEE', 'Electrical & Electronic Engineering'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES)

    def get_department_display_name(self):
        return dict(self.DEPARTMENT_CHOICES).get(self.department, self.department)

    def __str__(self):
        return self.student_id


class PageTemplate(models.Model):
    """A reusable layout blueprint for the Website Builder.

    The ``layout_json`` field defines the default section order and the
    block placeholders a page built from this template will expose, e.g.:

    .. code-block:: json

        {
            "sections": [
                {"name": "hero", "label": "Hero Banner"},
                {"name": "body", "label": "Main Content"}
            ],
            "blocks": [
                {"element_id": "hero-title", "section": "hero", "type": "text"}
            ]
        }
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    layout_json = models.JSONField(
        default=dict,
        help_text="Defines default section order and block placeholders",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EditablePage(models.Model):
    """A URL-addressable page whose content can be edited via the Website Builder."""

    PAGE_TYPES = [
        ('global', 'Global Page'),
        ('department', 'Department Hub'),
        ('club', 'Club Page'),
        ('notice', 'Notice Page'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True,
        help_text="URL endpoint, e.g., 'dashboard', 'research-ai'",
    )
    system_key = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Registered core system page key (home / study-corner / pharmacy / news / clubs) — set by the register_system_pages command",
    )
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, default='global')
    template = models.ForeignKey(
        PageTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pages',
    )
    custom_css = models.TextField(
        blank=True,
        help_text="Theme style overrides",
    )
    is_published = models.BooleanField(default=True)
    seo_description = models.TextField(
        blank=True,
        help_text="Meta description used for search-engine snippets",
    )
    show_in_nav = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Show a link to this page in the top navigation Pages menu",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ContentBlock(models.Model):
    """A single editable region on a page, keyed by its ``element_id``.

    ``block_type`` selects the rendering strategy:

      * ``html`` — the original mode: ``content_html`` is rendered as-is
        (sanitized on save through the builder API).
      * ``faq`` / ``stats`` / ``testimonials`` / ``cta`` — structured blocks
        whose data lives in ``content_json`` (see ``BLOCK_SCHEMAS``) and is
        rendered through the matching partial in ``templates/builder/blocks/``
        by ``render_block`` / ``editable_page_view``.

    ``style_json`` keeps the per-block visual overrides in both modes; it is
    flattened into an inline style attribute on the block's container.
    """

    # Structured block type → template partial basename. The ``render_block``
    # tag and the editable-page renderer share this map, so a new type only
    # needs a partial in templates/builder/blocks/ and a row here.
    BLOCK_TYPE_CHOICES = [
        ('html', 'Text Block'),
        ('hero', 'Hero Header'),
        ('features', 'Feature Cards Grid'),
        ('split', 'Text & Image Split'),
        ('links', 'Link Hub'),
        ('staff', 'Staff Grid'),
        ('faq', 'FAQ Accordion'),
        ('stats', 'Stats Counter Grid'),
        ('testimonials', 'Testimonial Slider'),
        ('cta', 'CTA Section'),
        # System-page feature blocks (extracted from the core routes so admins
        # can edit them from the Block Manager and render them live).
        ('announcements', 'Quick Announcements'),
        ('notes', 'Notes Listing'),
        ('youtube', 'YouTube Search & Video Section'),
        ('chat', 'Study Assistant Chat Container'),
        ('category_nav', 'Category Navigation Strip'),
        ('promo', 'Hero Promo Banner'),
        ('brands', 'Top Brands Showcase'),
        ('products', 'Product Grid'),
        ('news_search', 'News Search Bar'),
        ('card_grid', 'Image Card Grid'),
        ('video_feed', 'YouTube Video Feed'),
    ]

    # Documented JSON shape of ``content_json`` per structured block type.
    # These are the canonical schemas the block partials consume.
    BLOCK_SCHEMAS = {
        'faq': {
            'title': 'Optional heading',
            'subtitle': 'Optional intro line',
            'items': [
                {'question': 'What are the admission requirements?', 'answer': '…'},
            ],
        },
        'stats': {
            'title': 'Optional heading',
            'subtitle': 'Optional intro line',
            'items': [
                {'value': '4,500+', 'label': 'Active Students', 'icon': 'fa-user-graduate', 'highlight': True},
            ],
        },
        'hero': {
            'headline': 'Welcome to NITER',
            'subheadline': 'A supporting line under the headline',
            'image_url': 'https://…',
            'primary_label': 'Explore',
            'primary_url': '/departments/',
        },
        'features': {
            'title': 'Why NITER',
            'subtitle': 'Optional intro line',
            'items': [
                {'icon': 'fa-laptop-code', 'title': 'Feature', 'text': '…'},
            ],
        },
        'split': {
            'heading': 'Our mission',
            'text': 'Rich text content…',
            'image_url': 'https://…',
            'image_alt': 'Description',
        },
        'links': {
            'title': 'Explore',
            'subtitle': 'Optional intro line',
            'items': [
                {'label': 'Admissions', 'url': '/admissions/'},
            ],
        },
        'staff': {
            'title': 'Our team',
            'subtitle': 'Optional intro line',
            'items': [
                {'name': 'Jane Doe', 'role': 'Dean', 'photo_url': 'https://…'},
            ],
        },
        'testimonials': {
            'title': 'Optional heading',
            'items': [
                {'quote': '…', 'author': 'Jane Doe', 'title': 'CSE Alumna', 'avatar': 'https://…'},
            ],
        },
        'cta': {
            'headline': 'Ready to join NITER?',
            'subtext': 'Optional supporting line',
            'primary_label': 'Apply Now',
            'primary_url': '/signup/',
            'secondary_label': 'Learn More',
            'secondary_url': '/departments/',
        },
        # --- System-page feature blocks (Website Builder CMS overhaul) ---
        'announcements': {
            'title': 'Quick Announcements',
            'subtitle': 'Optional intro line',
            'items': [
                {'title': 'Notice title', 'text': 'Short description…'},
            ],
        },
        'notes': {
            'title': 'Academic Notes',
            'subtitle': 'Optional intro line',
            'items': [
                {'title': 'Lecture 1', 'course': 'CSE-1101', 'url': '/study-corner/'},
            ],
        },
        'youtube': {
            'title': 'Video Tutorials & Lectures',
            'subtitle': 'Optional intro line',
            'placeholder': 'e.g. Circuit Analysis',
            'embed_url': 'https://www.youtube.com/embed/…',
        },
        'chat': {
            'title': 'Study Assistant',
            'subtitle': 'Ask questions about your courses',
            'placeholder': 'Type a question…',
        },
        'category_nav': {
            'title': 'Shop by Category',
            'items': [
                {'label': 'Tablets', 'icon': 'fa-tablets', 'url': '/pharmacy/'},
            ],
        },
        'promo': {
            'headline': 'Special offer headline',
            'subtext': 'Supporting line',
            'image_url': 'https://…',
            'primary_label': 'Shop Now',
            'primary_url': '/pharmacy/',
        },
        'brands': {
            'title': 'Top Brands',
            'subtitle': 'Optional intro line',
            'items': [
                {'name': 'Brand', 'tagline': 'Tagline', 'logo_url': 'https://…'},
            ],
        },
        'products': {
            'title': 'Featured Medicines',
            'subtitle': 'Optional intro line',
            'items': [
                {'name': 'Napa 500mg', 'price': '৳10', 'url': '/pharmacy/'},
            ],
        },
        'news_search': {
            'title': 'Search the News',
            'placeholder': 'e.g. bangladesh',
        },
        'card_grid': {
            'title': 'Latest Stories',
            'subtitle': 'Optional intro line',
            'items': [
                {'image_url': 'https://…', 'title': 'Headline', 'source': 'Source', 'url': 'https://…'},
            ],
        },
        'video_feed': {
            'title': 'Video News',
            'items': [
                {'video_id': '…', 'title': 'Video title', 'channel': 'Channel name'},
            ],
        },
    }

    page = models.ForeignKey(
        EditablePage,
        on_delete=models.CASCADE,
        related_name='content_blocks',
    )
    element_id = models.CharField(max_length=100)
    block_type = models.CharField(
        max_length=20,
        choices=BLOCK_TYPE_CHOICES,
        default='html',
        db_index=True,
        help_text="Rendering strategy: raw HTML or a structured component",
    )
    content_html = models.TextField(blank=True)
    content_json = models.JSONField(
        default=dict,
        blank=True,
        help_text='Structured data for faq / stats / testimonials / cta blocks — see BLOCK_SCHEMAS',
    )
    style_json = models.JSONField(default=dict, blank=True)
    visible = models.BooleanField(
        default=True,
        help_text='Show / hide this block on the live page (system-page sections like video feeds or chat boxes)',
    )
    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text='Display order within the page (lowest first)',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('page', 'element_id')
        # Stable display order: explicit ``order`` first, then creation order
        # so rows created before the field existed keep their relative order.
        ordering = ['order', 'id']

    def __str__(self):
        return self.element_id


class GoogleUserToken(models.Model):
    """Long-lived Google OAuth credentials for a user (Drive + Sheets backends).

    Persists the tokens returned by the allauth Google OAuth2 ``offline``
    flow so later phases can call the Drive and Sheets APIs on the user's
    behalf. Fields mirror ``google.oauth2.credentials.Credentials`` for easy
    round-tripping.

    .. warning:: These are sensitive credentials (plaintext bearer tokens).
       Keep this table restricted to super admins and rotate tokens when a
       user disconnects their Google account.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='google_token',
    )
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_uri = models.CharField(
        max_length=255,
        default='https://oauth2.googleapis.com/token',
    )
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    scopes = models.JSONField(default=list)
    expiry = models.DateTimeField()

    @property
    def is_expired(self):
        """True once the access token's expiry has passed.

        Aligns aware/naive datetimes before comparing so it never raises
        ``TypeError`` (the project currently runs ``USE_TZ=False``).
        """
        if self.expiry is None:
            return False
        now = timezone.now()
        expiry = self.expiry
        if timezone.is_aware(now) != timezone.is_aware(expiry):
            if timezone.is_aware(expiry):
                now = timezone.make_aware(now, timezone.get_current_timezone())
            else:
                now = timezone.make_naive(now, timezone.get_current_timezone())
        return now >= expiry

    def __str__(self):
        return 'Google OAuth Token - %s' % self.user.username


class ClubSheetsConfig(models.Model):
    """Per-user Google Sheets connection for the Clubs module (Settings tab).

    Stores the club spreadsheet reference — a bare Sheet ID (``1AbC…``) or a
    full ``docs.google.com/spreadsheets/d/…`` URL — entered from Settings →
    Club Google Sheets. The OAuth tokens themselves live in
    ``GoogleUserToken`` (mirrored from allauth) and are shared by every
    Sheets call via ``core/club_sheets.py``.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='club_sheets_config',
    )
    sheet_ref = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text='Club Google Sheet ID or full spreadsheet URL',
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Club sheets - %s' % self.user.username


class Notification(models.Model):
    """A user-facing system alert delivered via the topbar bell + WebSockets.

    Rows are created by any subsystem that needs to surface something to a
    student (urgent notices, new academic materials, meal/transport/medical
    updates). The API layer exposes an unread count + the 10 most recent
    notifications, and ``core.consumers.NotificationConsumer`` pushes new
    rows to the user's ``user_<id>`` channel group in real time.
    """

    CATEGORY_CHOICES = [
        ('urgent', 'Urgent'),
        ('academic', 'Academic'),
        ('meal', 'Meal System'),
        ('transport', 'Transport'),
        ('medical', 'Medical'),
        ('club', 'Club & Events'),
        ('report', 'Reports & Feedback'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at', '-id']
        # Fast path for the topbar bell: a user's unread notifications, newest first.
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return self.title


class EmergencyAlert(models.Model):
    """A campus-wide emergency broadcast (siren banner + mobile push).

    At most one alert is ``is_active`` at a time — triggering a new alert
    deactivates the previous one so the student dashboards always show a
    single live emergency state. The active payload is served by
    ``/api/emergency/active/`` and pushed in real time over the global
    ``emergency_alerts`` WebSocket group; ``play_alarm_sound`` asks clients
    to loop the siren audio until the alert is resolved.
    """

    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('WARNING', 'Warning'),
        ('INFO', 'Info'),
    ]

    title = models.CharField(
        max_length=200,
        help_text='Short headline, e.g. "Severe Weather Warning"',
    )
    message = models.TextField(
        help_text='Detailed instructions shown to students',
    )
    severity_level = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='WARNING',
        db_index=True,
    )
    play_alarm_sound = models.BooleanField(
        default=False,
        help_text='Triggers the siren audio loop on student dashboards',
    )
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Only one alert is live at a time — the active emergency state',
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_alerts_created',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When an admin cleared/resolved this alert',
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_alerts_resolved',
    )

    class Meta:
        ordering = ['-created_at']
        # Fast path for the live-state lookups used by every dashboard poll.
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
        ]

    def __str__(self):
        return '%s · %s' % (self.title, self.get_severity_level_display())

    @property
    def severity_lower(self):
        """Lowercase severity key for client-side styling (critical/warning/info)."""
        return (self.severity_level or 'WARNING').lower()


class Notice(models.Model):
    """An official institutional announcement published on the /notices/ feed.

    ``is_published`` gates visibility: drafts are stored for admins but never
    shown to students, and only published rows trigger student notifications.
    """

    CATEGORY_CHOICES = [
        ('urgent', 'Urgent'),
        ('academic', 'Academic'),
        ('event', 'Event'),
        ('general', 'General'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_published = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Drafts are stored but never shown to students',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notices',
        help_text='Staff member who authored this notice',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
        # The /notices/ feed always filters published rows, newest first.
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
        ]

    def __str__(self):
        return self.title


class Course(models.Model):
    """A course catalog entry grouping uploaded course materials."""

    code = models.CharField(
        max_length=20,
        unique=True,
        help_text='Course code, e.g. CS101',
    )
    title = models.CharField(max_length=200)
    department = models.CharField(
        max_length=10,
        choices=StudentProfile.DEPARTMENT_CHOICES,
    )
    semester = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        ordering = ['code']

    def __str__(self):
        return '%s — %s' % (self.code, self.title)


class CourseMaterial(models.Model):
    """A single uploaded document (lecture slides, manual, problem set) for a
    course, served to students on the Study Corner drive."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials',
        db_index=True,
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_materials/', blank=True, default='')
    drive_view_link = models.URLField(
        blank=True,
        default='',
        help_text='Google Drive webViewLink for this lecture material',
    )
    drive_content_link = models.URLField(
        blank=True,
        default='',
        help_text='Google Drive webContentLink (direct download) for this material',
    )
    file_type = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text='Optional override; falls back to the file extension',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-uploaded_at', '-id']

    @property
    def display_type(self):
        """Return the file type label, derived from the extension when blank."""
        if self.file_type:
            return self.file_type
        name = self.file.name or ''
        if '.' in name:
            return name.rsplit('.', 1)[1].upper()
        return 'FILE'

    @property
    def size_display(self):
        """Human-readable file size (e.g. '1.2 MB'), or '—' if unavailable."""
        try:
            size = self.file.size
        except (OSError, ValueError, AttributeError):
            return '—'
        if size is None:
            return '—'
        units = ('B', 'KB', 'MB', 'GB')
        value = float(size)
        for unit in units:
            if value < 1024 or unit == units[-1]:
                if unit == 'B':
                    return '%d B' % size
                return '%.1f %s' % (value, unit)
            value /= 1024.0

    def __str__(self):
        return self.title


class MealSubscription(models.Model):
    """A user's active monthly meal plan entitlement.

    While ``is_active`` and not yet ``expires_at``, the student may claim
    daily ``MealTicket`` rows through ``core.views.claim_meal``. ``month_start``
    marks the paid billing month and ``slots_remaining`` is the pre-allocated
    meal balance for that month (one Lunch + one Dinner slot per remaining
    calendar day, credited on payment). A successful cancellation refunds a
    slot back into the balance.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='meal_subscription',
    )
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    month_start = models.DateField(
        null=True,
        blank=True,
        help_text='First day of the paid billing month',
    )
    slots_remaining = models.PositiveIntegerField(
        default=0,
        help_text='Unused meal slots in the current billing month — claimed tickets decrement, cancellations refund',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        """True once the subscription's expiry has passed."""
        if self.expires_at is None:
            return False
        return timezone.now() >= self.expires_at

    def __str__(self):
        return 'Meal subscription - %s' % self.user.username


# --- Payment-gated entitlement helpers ----------------------------------------
# Shared by the instant (free) flow in core.views and the paid flow in
# payments.services — one source of truth for the token formats.

def generate_meal_token():
    """Return an unused ``#MEAL-XXXX`` token (4 random digits)."""
    for _ in range(50):
        token = '#MEAL-%04d' % _secrets.randbelow(10000)
        if not MealTicket.objects.filter(ticket_token=token).exists():
            return token
    raise RuntimeError('Could not allocate a unique meal token')


def generate_qr_token():
    """Return a random boarding-pass QR token, e.g. ``TR-4F2A1C``."""
    return 'TR-' + _secrets.token_hex(3).upper()


class MealTicket(models.Model):
    """A single redeemable meal token claimed against a MealSubscription.

    In the paid flow the ticket starts ``pending`` with no ``ticket_token``;
    the bKash / Nagad SUCCESS callback (``payments.services.fulfill_payment_order``)
    flips it to ``paid`` and generates the token. The instant (free) claim
    flow records the ticket as ``paid`` (entitled) immediately.
    """

    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending payment'),
        ('paid', 'Paid / entitled'),
        ('failed', 'Payment failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meal_tickets',
        db_index=True,
    )
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    # NOTE: 'breakfast' stays in MEAL_TYPE_CHOICES only for legacy rows — the
    # claim API and every booking UI accept just Lunch / Dinner.
    meal_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text='The calendar date this meal is for — defaults to the claim date for legacy rows',
    )
    ticket_token = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        help_text='Format e.g. #MEAL-XXXX — generated when the ticket is activated (instant claim or payment confirmed)',
    )
    is_redeemed = models.BooleanField(default=False, db_index=True)
    claimed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    redeemed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the cafeteria counter redeemed this ticket',
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='Paid-flow gating: pending until the gateway SUCCESS callback; instant claims record paid.',
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this ticket was activated (instant claim or payment confirmed)',
    )
    payment_order = models.OneToOneField(
        'payments.PaymentOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meal_ticket',
        help_text='The payment order that activated this ticket (paid flow)',
    )

    class Meta:
        ordering = ['-claimed_at']

    def __str__(self):
        return self.ticket_token


class MealMenu(models.Model):
    """A cafeteria daily-menu line (breakfast / lunch / evening snacks).

    Seeded by ``seed_demo_data``; consumed by the cafeteria UI to show what
    is being served on a given day.
    """

    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Morning Breakfast'),
        ('lunch', 'Lunch'),
        ('snacks', 'Evening Snacks'),
    ]

    day = models.CharField(
        max_length=20,
        default='Daily',
        help_text='Day label, e.g. Daily or a weekday (Sun, Mon, …)',
    )
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    items = models.TextField(
        help_text='Comma-separated menu items served for this meal',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']
        unique_together = ('day', 'meal_type')

    def __str__(self):
        return '%s — %s' % (self.day, self.get_meal_type_display())


class TransportBooking(models.Model):
    """A booked seat on a campus transport route (QR-checked on boarding).

    ``unique_together`` makes the DB itself the seat-availability arbiter:
    two requests racing for the same (route, time, seat) can only win once.

    In the paid flow the booking starts ``pending`` with no ``qr_token``;
    the bKash / Nagad SUCCESS callback activates it (PAID + QR code).
    """

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending payment'),
        ('paid', 'Paid / entitled'),
        ('failed', 'Payment failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transport_bookings',
        db_index=True,
    )
    route_name = models.CharField(max_length=100, db_index=True)
    departure_time = models.CharField(max_length=50)
    seat_number = models.IntegerField(help_text='Seats 1 to 40')
    qr_token = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text='Boarding QR code — generated when the booking is activated (instant book or payment confirmed)',
    )
    booked_at = models.DateTimeField(auto_now_add=True, db_index=True)
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='Paid-flow gating: pending until the gateway SUCCESS callback; instant bookings record paid.',
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this booking was activated (instant book or payment confirmed)',
    )
    payment_order = models.OneToOneField(
        'payments.PaymentOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transport_booking',
        help_text='The payment order that activated this booking (paid flow)',
    )

    class Meta:
        # One seat per route + departure time — prevents duplicate assignments.
        unique_together = ('route_name', 'departure_time', 'seat_number')
        ordering = ['-booked_at']

    def __str__(self):
        return '%s · seat %s' % (self.route_name, self.seat_number)


class Driver(models.Model):
    """A campus transport driver, assigned to a ``TransportRoute``."""

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True, default='')
    license_number = models.CharField(max_length=50, blank=True, default='')
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TransportRoute(models.Model):
    """A DB-backed campus bus route (replaces the hardcoded ``TRANSPORT_ROUTES``).

    Seat availability is derived from live ``TransportBooking`` rows against
    ``capacity``; departure times live on the linked ``BusSchedule`` rows so a
    route can run multiple trips a day.
    """

    name = models.CharField(max_length=150, unique=True)
    origin = models.CharField(max_length=120, blank=True, default='')
    destination = models.CharField(max_length=120, blank=True, default='')
    capacity = models.PositiveIntegerField(
        default=40,
        help_text='Seats per bus — bounds the seat numbers book_transport accepts',
    )
    fare = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='routes',
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BusSchedule(models.Model):
    """One departure time for a ``TransportRoute`` (multiple trips per day)."""

    route = models.ForeignKey(
        TransportRoute,
        on_delete=models.CASCADE,
        related_name='schedules',
    )
    departure_time = models.CharField(
        max_length=50,
        help_text='Display departure time, e.g. 08:00 AM',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        # No duplicate departures for the same route. NO string ordering here:
        # alphabetical sorting would put '01:00 PM' before '08:00 AM'. The
        # catalog iterates schedules by id (insertion order) instead, so the
        # first departure stays the seeded morning departure.
        unique_together = ('route', 'departure_time')

    def __str__(self):
        return '%s @ %s' % (self.route.name, self.departure_time)


class Department(models.Model):
    """An academic department whose directory card + detail hub are rendered
    live from the database (no mock data).

    The ``code`` mirrors ``StudentProfile.department`` so student counts and
    the department's course materials can be aggregated across the portal.
    """

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    slug = models.SlugField(unique=True)
    head_of_dept = models.CharField(max_length=120, blank=True, default='')
    description = models.TextField(blank=True, default='')
    office_location = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FacultyMember(models.Model):
    """A faculty member listed on a department hub's Faculty Directory tab."""

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='faculty',
    )
    name = models.CharField(max_length=120)
    designation = models.CharField(max_length=120, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    office_hours = models.CharField(max_length=120, blank=True, default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Teacher(models.Model):
    """A course teacher managed from the Admin dashboard's Teachers tab.

    Teachers are the email recipients for the Attendance module's QR-dispatch
    and session-report emails: the course a teacher is assigned to (via the
    ``courses`` M2M) decides which class sessions' QR codes / reports are
    emailed to them. ``is_active`` lets admins retire a teacher without
    losing their historical email / course assignments.
    """

    name = models.CharField(max_length=120)
    email = models.EmailField(
        unique=True,
        help_text='Email address the class QR code and attendance reports are sent to',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers',
        help_text='The department this teacher belongs to',
    )
    designation = models.CharField(max_length=120, blank=True, default='')
    phone_number = models.CharField(
        max_length=30,
        blank=True,
        default='',
        help_text='Optional contact number',
    )
    courses = models.ManyToManyField(
        Course,
        blank=True,
        related_name='teachers',
        help_text='Courses this teacher takes attendance for',
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Inactive teachers are hidden from dispatch selection',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def course_codes(self):
        """Sorted list of assigned course codes (for admin tables/selects)."""
        return sorted(self.courses.values_list('code', flat=True))

    @classmethod
    def for_course(cls, course_code):
        """First active teacher assigned to a course code, or None."""
        return (
            cls.objects.filter(courses__code__iexact=course_code, is_active=True)
            .distinct()
            .first()
        )


class ClassRoutine(models.Model):
    """One weekly class/lab period on a department hub's schedule tab.

    ``day_of_week`` stores the weekday abbreviation ('Sun', 'Mon', …) so the
    hub can order periods by the campus week (Sunday → Thursday).
    """

    DAY_CHOICES = [
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
    ]

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='class_routines',
    )
    semester = models.CharField(max_length=50, default='Semester 1')
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    subject = models.CharField(max_length=120)
    time_slot = models.CharField(max_length=50)
    room = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['semester', 'day_of_week', 'time_slot']

    def __str__(self):
        return '%s · %s %s' % (self.subject, self.get_day_of_week_display(), self.time_slot)


class Routine(models.Model):
    """A student's weekly class schedule, one row per user.

    ``schedule`` stores the canonical JSON shape produced by the AI routine
    extractor (or pasted manually) and consumed by the student dashboard's
    BST clock / next-class highlighter:

    .. code-block:: json

        {
            "days": [
                {
                    "day": "Sun",
                    "slots": [
                        {"start": "08:30", "end": "10:00",
                         "course": "CSE-1101", "room": "201"}
                    ]
                }
            ]
        }

    Times are normalised to 24-hour ``HH:MM`` so the client-side comparator
    can compare them against the live Asia/Dhaka clock without parsing.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='routine',
        db_index=True,
    )
    schedule = models.JSONField(
        default=dict,
        blank=True,
        help_text='Weekly schedule in the canonical {"days": [...]} shape',
    )
    source_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Uploaded file name or "manual" when pasted as JSON',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Routine - %s' % self.user.username


class AcademicEvent(models.Model):
    """An academic calendar entry — exam, holiday, assignment deadline or event.

    Feeds the student dashboard's interactive monthly calendar. Rows are
    managed by staff (a default set is seeded by data migration); students
    only read them.
    """

    CATEGORY_CHOICES = [
        ('exam', 'Exam'),
        ('holiday', 'Holiday'),
        ('assignment', 'Assignment'),
        ('event', 'Event'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='event',
        db_index=True,
    )
    event_date = models.DateField(db_index=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date', 'id']
        indexes = [
            models.Index(fields=['event_date', 'category']),
        ]

    def __str__(self):
        return '%s · %s' % (self.title, self.event_date)


class Club(models.Model):
    """A student club shown on the /clubs/ page.

    ``lead_user`` is the staff member who owns the club (receives membership
    request notifications); it may be unset while a club is being set up.
    """

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default='')
    lead_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_clubs',
    )
    banner_image = models.FileField(
        upload_to='club_banners/',
        blank=True,
        help_text='Optional banner image (served from MEDIA_ROOT)',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ClubEvent(models.Model):
    """An upcoming club event listed on the /clubs/ page (registration routes
    through the existing payment-gateway checkout flow)."""

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='events',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    event_date = models.DateField(db_index=True)
    location = models.CharField(max_length=200, blank=True, default='')
    capacity = models.PositiveIntegerField(
        default=100,
        help_text='Maximum number of participants',
    )

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return self.title


class ClubRegistration(models.Model):
    """A student's club membership request.

    ``unique_together`` on (student, club) means a student can hold only one
    registration per club — the DB is the duplicate-join arbiter.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='club_registrations',
        db_index=True,
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='registrations',
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )

    class Meta:
        unique_together = ('student', 'club')
        ordering = ['-joined_at']

    def __str__(self):
        return '%s → %s' % (self.student.username, self.club.name)


class ClubAccount(models.Model):
    """A dedicated club-manager account linked to a club.

    Admins create/assign these accounts so club executives and managers get
    their own login for the club workspace (``/clubs/manage/``). Each account
    carries its own role, granular permission flags and an active switch — a
    user can be a student and a club manager at the same time.
    """

    ROLE_CHOICES = [
        ('manager', 'Club Manager'),
        ('executive', 'Club Executive'),
        ('president', 'Club President'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='club_account',
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='accounts',
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='manager',
    )
    can_post_events = models.BooleanField(
        default=True,
        help_text='May publish events and announcements for the club',
    )
    can_manage_members = models.BooleanField(
        default=True,
        help_text='May approve/reject membership requests',
    )
    can_manage_finances = models.BooleanField(
        default=False,
        help_text='May verify payments and manage club funds',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Inactive club accounts are locked out of the club workspace',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['club__name', 'user__username']

    def __str__(self):
        return '%s · %s' % (self.club.name, self.user.username)


class MedicalAppointment(models.Model):
    """A booked appointment slot with a campus doctor.

    ``unique_together`` on (doctor, date, slot) prevents double-booking a
    doctor's time slot from concurrent requests.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medical_appointments',
        db_index=True,
    )
    doctor_name = models.CharField(max_length=100)
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=50)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        # One patient per doctor slot — prevents double-booking.
        unique_together = ('doctor_name', 'appointment_date', 'time_slot')
        ordering = ['-created_at']

    def __str__(self):
        return '%s · %s %s' % (self.doctor_name, self.appointment_date, self.time_slot)


class Doctor(models.Model):
    """A campus doctor whose availability/schedule is managed from the Medical
    Admin dashboard (persisted, seeded with defaults by a data migration)."""

    name = models.CharField(max_length=100, unique=True)
    specialty = models.CharField(max_length=100, blank=True, default='')
    working_days = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='e.g. Sunday - Thursday',
    )
    start_time = models.CharField(max_length=20, blank=True, default='10:00 AM')
    end_time = models.CharField(max_length=20, blank=True, default='2:00 PM')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class DoctorSchedule(models.Model):
    """Daily availability + slot capacity for one doctor (one row per day).

    ``is_available`` powers the daily availability toggle on the Medical Admin
    dashboard; ``max_appointments`` is the slot-management cap enforced by the
    booking flow. Rows are upserted lazily when staff toggle availability or a
    student books, so the dashboard works immediately even before any row
    exists (defaults: available, 20 appointments).
    """

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='schedules',
    )
    date = models.DateField(db_index=True)
    is_available = models.BooleanField(default=True)
    max_appointments = models.PositiveIntegerField(default=20)

    class Meta:
        unique_together = ('doctor', 'date')
        ordering = ['date']

    def __str__(self):
        return '%s · %s' % (self.doctor.name, self.date)


class MedicalChatThread(models.Model):
    """A persistent patient ↔ doctor consultation thread tied to an appointment.

    One thread per appointment (``OneToOne``), so a consultation always has a
    single message history. Messages are pushed over WebSockets
    (``ws/medical-chat/<id>/``) via ``core.consumers.MedicalChatConsumer`` and
    persisted as ``MedicalChatMessage`` rows.
    """

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    appointment = models.OneToOneField(
        MedicalAppointment,
        on_delete=models.CASCADE,
        related_name='chat_thread',
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medical_chat_threads',
    )
    doctor_name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return 'Thread #%s · %s × %s' % (self.pk, self.patient.username, self.doctor_name)


class MedicalChatMessage(models.Model):
    """One message inside a ``MedicalChatThread``."""

    thread = models.ForeignKey(
        MedicalChatThread,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medical_chat_messages',
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['created_at', 'id']
        # Unread-count fast path: per-thread unseen messages, oldest first.
        indexes = [
            models.Index(fields=['thread', 'is_read']),
        ]

    def __str__(self):
        return '%s: %s…' % (self.sender.username, self.content[:40])


# --- Pharmacy (Online Pharmacy module) ----------------------------------------
# Medicine catalog + prescriptions + orders for the campus pharmacy. The store
# is browsable by anyone; checkout / prescriptions / tracking are
# login-required, and the operational admin dashboard lives at
# /dashboard/medical/pharmacy/ (staff-only).


class MedicineItem(models.Model):
    """A medicine stocked by the campus pharmacy.

    ``is_prescription`` (Rx-required) items can only be purchased with an
    approved :class:`Prescription` attached to the order. Batch / expiry /
    reorder fields drive the admin inventory alerts (``stock_status``): red
    for out-of-stock or expiring within 30 days, yellow for low stock, and
    the admin dashboard offers bulk restock + expiry update actions.
    """

    CATEGORY_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('ointment', 'Ointment'),
        ('injection', 'Injection'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=120, db_index=True, help_text='Brand name, e.g. Napa')
    generic_name = models.CharField(
        max_length=120,
        blank=True,
        default='',
        db_index=True,
        help_text='Generic name, e.g. Paracetamol — drives substitute suggestions',
    )
    strength = models.CharField(max_length=60, blank=True, default='', help_text='e.g. 500mg')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='tablet')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_prescription = models.BooleanField(
        default=False,
        help_text='Rx Required — needs an approved prescription to purchase',
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    batch_number = models.CharField(max_length=50, blank=True, default='')
    expiry_date = models.DateField(null=True, blank=True)
    reorder_level = models.PositiveIntegerField(
        default=10,
        help_text='Restock warning threshold — stock at or below this is low',
    )
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    @property
    def stock_status(self):
        """Inventory alert key for the admin dashboard: out | expiring | low | ok.

        Red takes precedence: an item that is both out of stock and expiring
        reports ``out``. Expiring means the expiry date is within 30 days.
        """
        if self.stock_quantity <= 0:
            return 'out'
        if self.expiry_date is not None and self.expiry_date <= date.today() + timedelta(days=30):
            return 'expiring'
        if self.stock_quantity <= self.reorder_level:
            return 'low'
        return 'ok'

    def __str__(self):
        label = self.name
        if self.strength:
            label += ' %s' % self.strength
        return label


class Prescription(models.Model):
    """A student-uploaded prescription (PDF / JPG / PNG) awaiting staff review.

    Uploads start ``pending``; a medical staff member approves or rejects them
    from the pharmacy admin dashboard. Only ``approved`` prescriptions can be
    attached to orders containing Rx-required medicines.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        db_index=True,
    )
    file = models.FileField(upload_to='prescriptions/', help_text='PDF, JPG or PNG of the prescription')
    notes = models.CharField(max_length=300, blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    reason = models.CharField(max_length=300, blank=True, default='', help_text='Rejection reason')
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_prescriptions',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return 'Rx #%s — %s' % (self.pk, self.user.username)


class PharmacyOrder(models.Model):
    """A pharmacy purchase with shipping, payment and fulfilment state.

    ``status`` follows the customer tracker: placed → rx_verified → packaging
    → out_for_delivery → delivered (or cancelled). Orders carrying Rx-required
    items must attach an approved :class:`Prescription`. Paid (non-COD) orders
    carry the wallet TrxID and are also recorded as a ``PaymentTransaction``
    with the ``pharmacy`` purpose.
    """

    STATUS_CHOICES = [
        ('placed', 'Order Placed'),
        ('rx_verified', 'Rx Verified'),
        ('packaging', 'Packaging'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('sslcommerz', 'SSLCommerz'),
        ('cod', 'Cash on Delivery / Pay at Medical Center'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('cod', 'Pay on Delivery'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pharmacy_orders',
        db_index=True,
    )
    reference = models.CharField(max_length=32, unique=True, help_text='Customer-facing order id, e.g. PO-A1B2C3')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='placed',
        db_index=True,
    )
    prescription = models.ForeignKey(
        Prescription,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders',
    )

    # Shipping / delivery details.
    hall_name = models.CharField(max_length=100, blank=True, default='')
    room_no = models.CharField(max_length=40, blank=True, default='')
    department = models.CharField(max_length=10, blank=True, default='')
    delivery_instructions = models.CharField(max_length=300, blank=True, default='')
    emergency_phone = models.CharField(max_length=20, blank=True, default='')

    # Payment.
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
    )
    wallet_trx = models.CharField(max_length=64, blank=True, default='')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def step_index(self):
        """Tracker position 0-4 (placed=0 … delivered=4); cancelled → -1."""
        if self.status == 'cancelled':
            return -1
        steps = [code for code, _label in self.STATUS_CHOICES if code != 'cancelled']
        return steps.index(self.status)

    def __str__(self):
        return '%s — %s' % (self.reference, self.user.username)


class PharmacyOrderItem(models.Model):
    """One medicine line on a pharmacy order (quantity + snapshot unit price)."""

    order = models.ForeignKey(
        PharmacyOrder,
        on_delete=models.CASCADE,
        related_name='items',
    )
    medicine = models.ForeignKey(
        MedicineItem,
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return '%s x%d' % (self.medicine.name, self.quantity)


class PaymentTransaction(models.Model):
    """A server-recorded payment for a checkout order (bKash / Nagad / Card).

    ``transaction_id`` is the platform-generated reference returned to the
    student (e.g. ``NTR-4F2A1C``); ``wallet_trx`` stores the TrxID the user
    entered from their wallet app. Status starts ``pending`` until a staff
    member verifies the wallet payment, at which point the linked item is
    fulfilled (e.g. a paid ``MealSubscription`` entitlement).
    """

    PURPOSE_CHOICES = [
        ('meal', 'Meal Ticket'),
        ('tuition', 'Tuition'),
        ('event', 'Event'),
        ('transport', 'Transport'),
        ('pharmacy', 'Pharmacy'),
    ]

    METHOD_CHOICES = [
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('card', 'Card'),
        ('rocket', 'Rocket'),
        ('sslcommerz', 'SSLCommerz'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        db_index=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=32, unique=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Label of the paid item, e.g. "Monthly Meal Subscription"',
    )
    wallet_trx = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text='TrxID the student entered from their wallet app',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        # Profile/payment history always filters by user, then status.
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return '%s · %s' % (self.transaction_id, self.get_purpose_display())


# --- Attendance helpers ------------------------------------------------------
# One source of truth for the class-session token format.

def generate_attendance_token():
    """Return an unused attendance session token, e.g. ``ATD-9F4A2C``."""
    for _ in range(50):
        token = 'ATD-' + _secrets.token_hex(3).upper()
        if not AttendanceSession.objects.filter(session_token=token).exists():
            return token
    raise RuntimeError('Could not allocate a unique attendance token')


class AttendanceSession(models.Model):
    """A single live class session students scan into for attendance.

    ``session_token`` is the short code encoded in the classroom QR; records
    are captured against it until ``expires_at`` (or an admin closes it
    early). One course can run many sessions, so attendance percentages are
    computed per ``course_code`` across sessions.
    """

    course_code = models.CharField(max_length=20, db_index=True)
    session_token = models.CharField(
        max_length=20,
        unique=True,
        help_text='Short code embedded in the classroom QR, e.g. ATD-9F4A2C',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course_code', '-created_at']),
        ]

    @property
    def is_expired(self):
        """True once the session's expiry has passed (regardless of the flag)."""
        if self.expires_at is None:
            return False
        return timezone.now() >= self.expires_at

    @property
    def is_live(self):
        """A session students can still scan into: active AND unexpired."""
        return self.is_active and not self.is_expired

    def __str__(self):
        return '%s · %s' % (self.course_code, self.session_token)


class AttendanceRecord(models.Model):
    """One student's 'Present' entry for a class session.

    ``unique_together`` (student, session) makes the DB the duplicate guard: a
    second scan for the same session cannot create a second row.
    """

    STATUS_CHOICES = [
        ('present', 'Present'),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        db_index=True,
    )
    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records',
        db_index=True,
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='present',
        help_text='Attendance status (Present today — future statuses can extend this)',
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='Client IP captured at scan time (campus Wi-Fi gate uses it)',
    )

    class Meta:
        ordering = ['-timestamp']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'session'],
                name='uniq_attendance_student_session',
            ),
        ]

    def __str__(self):
        return '%s → %s' % (self.student.username, self.session.session_token)


class UserNotificationPreference(models.Model):
    """Per-user alert + appearance preferences persisted in the database.

    A row is auto-created for every new ``User`` via the ``post_save`` signal
    at the bottom of this module, so ``/settings/`` always has a row to load.
    """

    TIMEZONE_CHOICES = [
        ('Asia/Dhaka', 'Bangladesh (BST, UTC+6)'),
        ('Asia/Kolkata', 'India (IST, UTC+5:30)'),
        ('UTC', 'Coordinated Universal Time'),
        ('America/New_York', 'Eastern Time (US & Canada)'),
        ('Europe/London', 'London (GMT/BST)'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_prefs',
    )
    email_alerts = models.BooleanField(default=True)
    sms_alerts = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    dark_mode = models.BooleanField(
        default=False,
        help_text='Apply the dark portal theme across pages',
    )

    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
        ('system', 'System Default'),
    ]
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='system',
        help_text='Portal theme: light, dark, or follow the system preference',
    )
    compact_layout = models.BooleanField(
        default=False,
        help_text='Use a more compact, denser layout',
    )
    # Per-category notification toggles (default all on — checked in addition
    # to the channel-level toggles above).
    notify_meals = models.BooleanField(
        default=True,
        help_text='Receive meal ticket notifications',
    )
    notify_transport = models.BooleanField(
        default=True,
        help_text='Receive transport booking notifications',
    )
    notify_medical = models.BooleanField(
        default=True,
        help_text='Receive medical appointment notifications',
    )
    notify_notices = models.BooleanField(
        default=True,
        help_text='Receive official notice alerts',
    )
    timezone = models.CharField(
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default='Asia/Dhaka',
        help_text='Display timezone for timestamps',
    )

    def __str__(self):
        return 'Preferences - %s' % self.user.username


class UserNote(models.Model):
    """A student's personal note (title + Markdown-ish content).

    Backs the Notes Engine workspace so the AI summary / keyword extraction /
    exporter actions operate on real saved note objects.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes',
        db_index=True,
    )
    title = models.CharField(max_length=200, default='Untitled Note')
    content = models.TextField(blank=True, default='')
    drive_view_link = models.URLField(
        blank=True,
        default='',
        help_text='Google Drive webViewLink for the exported copy of this note',
    )
    drive_content_link = models.URLField(
        blank=True,
        default='',
        help_text='Google Drive webContentLink (direct download) for this note',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['-updated_at']
        # Notes sidebar is always scoped to one user, most recently edited first.
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]

    def __str__(self):
        return self.title


class NoteAnalysis(models.Model):
    """A queued/extracted analysis of note content (Huey background task).

    ``note_summary`` / ``note_keywords`` create a row, enqueue
    ``core.tasks.analyze_note_content`` and answer immediately (either inline
    in Huey's immediate mode, or a ``queued`` response the frontend polls via
    ``/api/notes/analysis/<id>/``). The worker fills in ``summary``,
    ``keywords`` and ``sentence_count`` off the HTTP request path.
    """

    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    analysis_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='note_analyses',
        db_index=True,
    )
    content = models.TextField(blank=True, default='')
    summary = models.TextField(blank=True, default='')
    keywords = models.JSONField(default=list, blank=True)
    sentence_count = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default='queued',
        db_index=True,
    )
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '%s · %s' % (self.analysis_id, self.status)


class ResearchThread(models.Model):
    """A persisted conversation in the Academic Research & Thesis Assistant.

    Backs the ``/research-ai/`` chat console so "Recent Research Threads" is a
    real, per-user list: a thread owns the citation style used and its message
    history, and carries an auto-generated title from the first user message.
    """

    CITATION_STYLE_CHOICES = [
        ('IEEE', 'IEEE'),
        ('APA 7', 'APA 7'),
        ('Harvard', 'Harvard'),
        ('Chicago', 'Chicago'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='research_threads',
        db_index=True,
    )
    title = models.CharField(max_length=200, default='New Research Thread')
    citation_style = models.CharField(
        max_length=20,
        choices=CITATION_STYLE_CHOICES,
        default='IEEE',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return '%s (%s)' % (self.title, self.user.username)


class ResearchMessage(models.Model):
    """One user/assistant turn inside a ``ResearchThread``."""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    thread = models.ForeignKey(
        ResearchThread,
        on_delete=models.CASCADE,
        related_name='messages',
        db_index=True,
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, db_index=True)
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return '%s · %s' % (self.get_role_display(), (self.content or '')[:60])


class Report(models.Model):
    """A student-submitted report/feedback item reviewed by staff.

    Students submit a title, category (academic/facility/medical/technical/
    general), an optional severity level and an optional screenshot/attachment;
    staff triage the item through the status workflow (pending → in_progress →
    resolved / rejected) and attach ``admin_notes`` as the visible response.
    Status changes push a real-time ``Notification`` (category ``report``) to
    the submitting student so they see the outcome without refreshing.
    """

    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('facility', 'Facility'),
        ('medical', 'Medical'),
        ('technical', 'Technical'),
        ('general', 'General'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        db_index=True,
        help_text='Student who submitted this report',
    )
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        db_index=True,
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        db_index=True,
        help_text='Low / Medium / High / Critical impact of the issue',
    )
    description = models.TextField()
    attachment = models.FileField(
        upload_to='reports/%Y/%m/',
        blank=True,
        null=True,
        help_text='Optional screenshot or supporting file (max 10 MB)',
    )
    attachment_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Original file name of the attachment for display',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    admin_notes = models.TextField(
        blank=True,
        default='',
        help_text='Staff response / resolution notes shown to the student',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
        # Student history always filters by user; the admin inbox filters by status.
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return self.title


# ----------------------------------------------------------------------------
# Signal: auto-create default notification preferences for every new user
# ----------------------------------------------------------------------------
from django.db.models.signals import post_save  # noqa: E402
from django.dispatch import receiver  # noqa: E402


@receiver(post_save, sender=User)
def create_default_notification_prefs(sender, instance, created, **kwargs):
    """Give every new user a default UserNotificationPreference row."""
    if created:
        UserNotificationPreference.objects.get_or_create(user=instance)
