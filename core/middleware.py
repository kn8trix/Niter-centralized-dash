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

from .models import UserNotificationPreference

DEFAULT_DISPLAY_PREFS = {
    'theme': 'light',
    'timezone': None,
    'density': 'comfortable',
}


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
