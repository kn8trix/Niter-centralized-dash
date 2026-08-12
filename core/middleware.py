"""Request middleware for per-user display preferences.

The portal lets every signed-in user pick a theme (light / dark / system), a
display timezone and a layout density from /settings/?tab=display. This
middleware loads those preferences once per authenticated request into
``request.display_prefs`` (so the ``core.context_processors.display_prefs``
processor never issues its own query) and activates the user's timezone via
``django.utils.timezone.activate`` — the canonical Django mechanism that makes
aware datetime handling (``{% load tz %}`` / ``|localtime``, API responses)
render in the user's zone.
"""

from django.utils import timezone
from django.shortcuts import redirect

from .models import UserNotificationPreference
from .roles import get_user_role, role_home_path

DEFAULT_DISPLAY_PREFS = {
    'theme': 'light',
    'timezone': None,
    'density': 'comfortable',
}


class RoleAccessMiddleware:
    """Enforce the portal's role-based area separation at the request layer.

    Every authenticated request is resolved to an explicit role
    (admin / club / student — see ``core.roles``). Requests that land on the
    wrong role's area are redirected to that role's home URL so a student can
    never browse ``/dashboard/admin/*`` and a club manager can never open the
    admin area by typing a URL.

    The role dispatcher for the bare ``/dashboard/`` URL lives in the view
    (``core.views.dashboard``) so anonymous guests keep the pre-RBAC public
    behaviour of viewing the student dashboard.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self._guard(request)
        if response is not None:
            return response
        return self.get_response(request)

    def _guard(self, request):
        user = request.user
        if not user.is_authenticated:
            return None

        role = get_user_role(user)
        path = request.path

        # Admin area (/dashboard/admin/*) — admins only.
        if path.startswith('/dashboard/admin/'):
            if role != 'admin':
                return redirect(role_home_path(role))
        # Club area (/dashboard/club/*) — club accounts (staff may preview as
        # club leads); students are bounced to their own dashboard.
        elif path.startswith('/dashboard/club/'):
            if role not in ('club', 'admin'):
                return redirect(role_home_path(role))
        # Student area (/dashboard/student/*) — students (admins may preview).
        elif path.startswith('/dashboard/student/'):
            if role == 'club':
                return redirect(role_home_path(role))
        return None


class UserDisplayPreferencesMiddleware:
    """Attach display prefs to the request + activate the user's timezone."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        prefs = dict(DEFAULT_DISPLAY_PREFS)
        if request.user.is_authenticated:
            try:
                row = UserNotificationPreference.objects.get(user=request.user)
                prefs = {
                    'theme': row.theme,
                    'timezone': row.timezone or None,
                    'density': 'compact' if row.compact_layout else 'comfortable',
                }
            except UserNotificationPreference.DoesNotExist:
                # Rowless users (e.g. created outside the signal path) simply
                # get the defaults — never 500 a page over missing prefs.
                prefs = dict(DEFAULT_DISPLAY_PREFS)

        request.display_prefs = prefs

        tz = prefs.get('timezone')
        if tz:
            timezone.activate(tz)
        try:
            return self.get_response(request)
        finally:
            if tz:
                timezone.deactivate()
