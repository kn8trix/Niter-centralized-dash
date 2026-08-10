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
        ('html', 'Rich Text / HTML'),
        ('faq', 'FAQ Accordion'),
        ('stats', 'Stats Counter Grid'),
        ('testimonials', 'Testimonial Slider'),
        ('cta', 'CTA Section'),
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
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('page', 'element_id')

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
    course, served to students on the Academic Notes drive."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials',
        db_index=True,
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_materials/')
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
    """A user's active meal plan entitlement.

    While ``is_active`` and not yet ``expires_at``, the student may claim
    daily ``MealTicket`` rows through ``core.views.claim_meal``.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='meal_subscription',
    )
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        """True once the subscription's expiry has passed."""
        if self.expires_at is None:
            return False
        return timezone.now() >= self.expires_at

    def __str__(self):
        return 'Meal subscription - %s' % self.user.username


class MealTicket(models.Model):
    """A single redeemable meal token claimed against a MealSubscription."""

    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meal_tickets',
        db_index=True,
    )
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    ticket_token = models.CharField(
        max_length=20,
        unique=True,
        help_text='Format e.g. #MEAL-XXXX',
    )
    is_redeemed = models.BooleanField(default=False, db_index=True)
    claimed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    redeemed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the cafeteria counter redeemed this ticket',
    )

    class Meta:
        ordering = ['-claimed_at']

    def __str__(self):
        return self.ticket_token


class TransportBooking(models.Model):
    """A booked seat on a campus transport route (QR-checked on boarding).

    ``unique_together`` makes the DB itself the seat-availability arbiter:
    two requests racing for the same (route, time, seat) can only win once.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transport_bookings',
        db_index=True,
    )
    route_name = models.CharField(max_length=100, db_index=True)
    departure_time = models.CharField(max_length=50)
    seat_number = models.IntegerField(help_text='Seats 1 to 40')
    qr_token = models.CharField(max_length=50, unique=True)
    booked_at = models.DateTimeField(auto_now_add=True, db_index=True)

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
    ]

    METHOD_CHOICES = [
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('card', 'Card'),
        ('rocket', 'Rocket'),
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
