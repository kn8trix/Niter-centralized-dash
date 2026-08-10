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
    """A single editable region on a page, keyed by its ``element_id``."""

    page = models.ForeignKey(
        EditablePage,
        on_delete=models.CASCADE,
        related_name='content_blocks',
    )
    element_id = models.CharField(max_length=100)
    content_html = models.TextField(blank=True)
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
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']

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
    )
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    ticket_token = models.CharField(
        max_length=20,
        unique=True,
        help_text='Format e.g. #MEAL-XXXX',
    )
    is_redeemed = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(auto_now_add=True)
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
    )
    route_name = models.CharField(max_length=100)
    departure_time = models.CharField(max_length=50)
    seat_number = models.IntegerField(help_text='Seats 1 to 40')
    qr_token = models.CharField(max_length=50, unique=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One seat per route + departure time — prevents duplicate assignments.
        unique_together = ('route_name', 'departure_time', 'seat_number')
        ordering = ['-booked_at']

    def __str__(self):
        return '%s · seat %s' % (self.route_name, self.seat_number)


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
    )
    doctor_name = models.CharField(max_length=100)
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=50)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One patient per doctor slot — prevents double-booking.
        unique_together = ('doctor_name', 'appointment_date', 'time_slot')
        ordering = ['-created_at']

    def __str__(self):
        return '%s · %s %s' % (self.doctor_name, self.appointment_date, self.time_slot)
