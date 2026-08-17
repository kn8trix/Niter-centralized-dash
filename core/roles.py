"""Explicit portal roles — the single source of truth for RBAC.

The app previously only had implicit Django flags (``is_staff`` /
``is_superuser``) with no named roles, so every authenticated user landed on
the student dashboard. This module defines the four explicit roles used for
routing, middleware guards and page-level decorators:

- ``admin``  — staff or superuser (access to the ``/dashboard/admin/*`` area)
- ``medical`` — a staff member in the ``Medical Staff`` group (the dedicated
  ``/medical/admin/`` + ``/host/medical/`` area — kept separate from the
  main admin dashboard per the role-separation requirement)
- ``club``   — an active ``ClubAccount`` (club executive/manager workspace)
- ``student`` — everyone else (the ``/dashboard/student/*`` area)
"""

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

ROLE_ADMIN = 'admin'
ROLE_MEDICAL = 'medical'
ROLE_CLUB = 'club'
ROLE_STUDENT = 'student'

# Django group name that marks a staff member as medical staff. Members get
# the ``medical`` role: they land on and may browse the medical area
# (``/medical/admin/``, ``/host/medical/``, ``/dashboard/medical/``) but are
# kept out of the main admin area (``/dashboard/admin/*``).
MEDICAL_STAFF_GROUP = 'Medical Staff'

ROLE_CHOICES = [
    (ROLE_ADMIN, 'Admin'),
    (ROLE_MEDICAL, 'Medical'),
    (ROLE_CLUB, 'Club'),
    (ROLE_STUDENT, 'Student'),
]


def is_medical_staff(user):
    """True when the user holds the ``Medical Staff`` group."""
    return bool(user.is_authenticated and user.groups.filter(name=MEDICAL_STAFF_GROUP).exists())


def get_user_role(user):
    """Resolve a user to one of the explicit portal roles (or ``None``).

    Precedence: superuser/staff in the ``Medical Staff`` group → medical,
    superuser/staff → admin, active club account → club, everything else
    authenticated → student. Superusers always stay ``admin`` so the main
    admin keeps the whole platform (the medical role is for the dedicated
    medical staff account).
    """
    if user is None or not user.is_authenticated:
        return None
    if user.is_superuser:
        return ROLE_ADMIN
    if user.is_staff and is_medical_staff(user):
        return ROLE_MEDICAL
    if user.is_staff:
        return ROLE_ADMIN
    try:
        account = user.club_account
    except ObjectDoesNotExist:
        account = None
    if account is not None and account.is_active:
        return ROLE_CLUB
    return ROLE_STUDENT


def role_home_path(role):
    """The landing URL for a role (used by the /dashboard/ dispatcher and the
    RoleAccessMiddleware). Unknown/anonymous → the student dashboard (guest
    view), matching the pre-RBAC public behaviour."""
    if role == ROLE_ADMIN:
        return reverse('admin_dashboard')
    if role == ROLE_MEDICAL:
        return reverse('medical_admin_dashboard')
    if role == ROLE_CLUB:
        return reverse('club_dashboard')
    return reverse('student_dashboard')
