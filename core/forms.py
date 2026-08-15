"""Form definitions for the campus portal.

``SignUpForm`` validates self-registration input — Student ID, full name,
department, email, password + confirmation — and persists the ``User`` and
``StudentProfile`` rows using Django's standard auth hashing.

``ClubEventForm`` creates club events from the Club Management dashboard
(``/dashboard/club/events/``) — banner image upload with a remote-URL
fallback, published/draft flag, and the standard event fields.
"""

from django import forms
from django.contrib.auth.models import User

from .models import ClubEvent, StudentProfile


class SignUpForm(forms.Form):
    """Self-registration form.

    Enforces:
      * duplicate Student ID / email checks,
      * password length (>= 8) and confirmation match,
      * department must be one of the seeded ``StudentProfile`` choices.
    """

    student_id = forms.CharField(
        label='Student ID',
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. S1024'}),
    )
    full_name = forms.CharField(
        label='Full Name',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your full name'}),
    )
    department = forms.ChoiceField(
        label='Department',
        choices=StudentProfile.DEPARTMENT_CHOICES,
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )
    password = forms.CharField(
        label='Password',
        min_length=8,
        widget=forms.PasswordInput(attrs={'placeholder': 'At least 8 characters'}),
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat password'}),
    )

    def clean_student_id(self):
        # Student IDs are stored uppercase (S1001-style) so `s7777` and
        # `S7777` can never become two separate accounts.
        student_id = self.cleaned_data['student_id'].strip().upper()
        if (User.objects.filter(username=student_id).exists()
                or StudentProfile.objects.filter(student_id=student_id).exists()):
            raise forms.ValidationError('An account with this Student ID already exists.')
        return student_id

    def clean_email(self):
        # Normalize to lowercase so stored emails match the case-insensitive
        # uniqueness rule (a case variant can never sneak past the check).
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm_password = cleaned.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned

    def save(self):
        """Create the ``User`` (password hashed by ``create_user``) + profile."""
        data = self.cleaned_data
        full_name = data['full_name'].strip()
        name_parts = full_name.split(' ', 1)
        user = User.objects.create_user(
            username=data['student_id'],
            email=data['email'],
            password=data['password'],
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else '',
        )
        StudentProfile.objects.create(
            user=user,
            student_id=data['student_id'],
            department=data['department'],
        )
        return user


class ClubEventForm(forms.ModelForm):
    """Create / edit a ``ClubEvent`` from the club dashboard.

    Supports both a banner image upload (``banner``, served from MEDIA_ROOT)
    and a remote ``banner_url`` fallback, plus the published/draft toggle so
    club managers can prepare an event before it shows on the student
    dashboard and the public /clubs/ page.
    """

    class Meta:
        model = ClubEvent
        fields = [
            'club', 'title', 'description', 'event_date', 'location',
            'capacity', 'banner', 'banner_url', 'is_published',
        ]
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe the event…'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Auditorium'}),
            'capacity': forms.NumberInput(attrs={'min': 1, 'placeholder': 'e.g. 100'}),
            'banner_url': forms.URLInput(attrs={'placeholder': 'https://…/poster.jpg (optional)'}),
        }
