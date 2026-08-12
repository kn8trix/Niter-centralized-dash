"""Explicit portal roles — the single source of truth for RBAC.

The app previously only had implicit Django flags (``is_staff`` /
``is_superuser``) with no named roles, so every authenticated user landed on
the student dashboard. This module defines the three explicit roles used for
routing, middleware guards and page-level decorators:

- ``admin``  — staff or superuser (access to the ``/dashboard/admin/*`` area)
- ``club``   — an active ``ClubAccount`` (club executive/manager workspace)
- ``student`` — everyone else (the ``/dashboard/student/*`` area)
"""

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

ROLE_ADMIN = 'admin'
ROLE_CLUB = 'club'
ROLE_STUDENT = 'student'

ROLE_CHOICES = [
    (ROLE_ADMIN, 'Admin'),
    (ROLE_CLUB, 'Club'),
    (ROLE_STUDENT, 'Student'),
]


def get_user_role(user):
    """Resolve a user to one of the explicit portal roles (or ``None``).

    Precedence: superuser/staff → admin, active club account → club,
    everything else authenticated → student.
    """
    if user is None or not user.is_authenticated:
        return None
    if user.is_superuser or user.is_staff:
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
    if role == ROLE_CLUB:
        return reverse('club_admin')
    return reverse('student_dashboard')
