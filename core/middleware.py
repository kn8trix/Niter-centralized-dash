"""Request middleware for per-user display preferences.

The portal lets every signed-in user pick a theme (light / dark / system), a
display timezone and a layout density from /settings/?tab=display. This
middleware loads those preferences once per authenticated request into
``request.display_prefs`` (so the ``core.context_processors.display_prefs``
processor never issues its own query) and activates the user's timezone via
``django.utils.timezone.activate`` — the canonical Django mechanism that makes
aware datetime handling (``{% load tz %}`` / ``|localtime``, API responses)
render in the user's zone.

Also hosts the campus-network helpers used by the QR Attendance module:
``is_campus_wifi`` is a placeholder gate that stays open until
``ENFORCE_CAMPUS_WIFI`` is flipped on (with ``CAMPUS_NETWORK_CIDRS`` set).
"""

import ipaddress

from django.conf import settings
from django.utils import timezone
from django.shortcuts import redirect

from .models import UserNotificationPreference
from .roles import get_user_role, role_home_path


# --- Campus Wi-Fi gate (QR Attendance) --------------------------------------
# Placeholder IP/network check: attendance scans can be restricted to the
# campus network by flipping ``ENFORCE_CAMPUS_WIFI = True`` in settings and
# listing the campus CIDRs in ``CAMPUS_NETWORK_CIDRS``. Until then every
# request passes, so the feature works on any network during development.


def _client_ip(request):
    """Best-effort client IP (first X-Forwarded-For hop, else REMOTE_ADDR).

    NOTE: ``X-Forwarded-For`` is client-spoofable, so this is only
    trustworthy when the app sits behind a reverse proxy that overwrites the
    header (Render/gunicorn + nginx do). When ``ENFORCE_CAMPUS_WIFI`` is
    enabled in front of a plain dev server, a crafted header could bypass
    the gate — acceptable for the placeholder utility, but harden this
    (e.g. drop to ``REMOTE_ADDR`` unless a trusted proxy is configured)
    before enforcing the restriction in production.
    """
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip() or None
    return request.META.get('REMOTE_ADDR') or None


def is_campus_wifi(request):
    """Return True when the request originates from the campus network.

    When ``ENFORCE_CAMPUS_WIFI`` is False (default) the gate is open and
    every request passes — the restriction can be enabled later without any
    caller changes. When enabled, the client IP must fall inside one of the
    ``CAMPUS_NETWORK_CIDRS`` entries (e.g. ``['10.0.0.0/8', '192.168.10.0/24']``).
    """
    if not getattr(settings, 'ENFORCE_CAMPUS_WIFI', False):
        return True
    ip = _client_ip(request)
    if not ip:
        return False
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    for cidr in getattr(settings, 'CAMPUS_NETWORK_CIDRS', []):
        try:
            if addr in ipaddress.ip_network(cidr, strict=False):
                return True
        except ValueError:
            continue
    return False

DEFAULT_DISPLAY_PREFS = {
    'theme': 'system',
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
