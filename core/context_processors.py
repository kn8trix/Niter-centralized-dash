"""Centralized endpoint registry (decoupled endpoint mappings).

Templates reference logical endpoint keys (``{{ ENDPOINTS.tickets }}``)
instead of hardcoding ``{% url %}`` lookups in markup. This keeps the
endpoint map in one place so the Visual Builder can remap/override routes
without touching template HTML.
"""

import json

from django.urls import reverse

from core.models import EditablePage, UserNotificationPreference
from core.roles import get_user_role


def display_prefs(request):
    """Expose the signed-in user's display preferences to every template.

    The per-request values are cached on ``request.display_prefs`` by
    ``core.middleware.UserDisplayPreferencesMiddleware`` (one DB query per
    authenticated request); this processor re-wraps them in a JSON-safe dict
    plus the settings save endpoint so ``partials/display_prefs.html`` can
    apply the saved theme / density before first paint (no flash) and the
    global ``display-preferences.js`` driver can persist changes back.

    Anonymous visitors get an empty payload — the driver then falls back to
    their device's ``localStorage`` choices.
    """
    data = dict(getattr(request, 'display_prefs', None) or {})
    if request.user.is_authenticated:
        if not data:
            # Middleware-less render path (tests / shortcuts): fetch directly.
            try:
                row = UserNotificationPreference.objects.get(user=request.user)
                data = {
                    'theme': row.theme,
                    'timezone': row.timezone or None,
                    'density': 'compact' if row.compact_layout else 'comfortable',
                }
            except UserNotificationPreference.DoesNotExist:
                data = {}
        data['authenticated'] = True
        data['saveUrl'] = reverse('settings')
    # Serialised by the template via ``{{ DISPLAY_PREFS|json_script }}``.
    return {'DISPLAY_PREFS': data}


def custom_pages_nav(request):
    """Expose published builder pages flagged for the top navigation.

    Only ``EditablePage`` rows that are both published and marked
    ``show_in_nav`` appear in ``NAV_CUSTOM_PAGES`` (ordered by title), so the
    shared topbar's Pages dropdown / mobile menu is always a live view of the
    database and never references unpublished work.
    """
    return {
        'NAV_CUSTOM_PAGES': EditablePage.objects.filter(
            is_published=True,
            show_in_nav=True,
        ).order_by('title'),
    }


def user_role(request):
    """Expose the signed-in user's explicit portal role to every template.

    ``USER_ROLE`` is one of ``admin`` / ``club`` / ``student`` (``None`` for
    anonymous visitors) — the same value the middleware and view decorators
    use, so templates can render role-appropriate navigation without
    duplicating the is_staff / club_account logic.
    """
    return {'USER_ROLE': get_user_role(request.user)}


def endpoints(request):
    """Expose a single ENDPOINTS dict to every template.

    Logical name -> resolved URL. Add new routes here when pages are added.
    """
    return {
        'ENDPOINTS': {
            # Public homepage + student app pages
            'home': reverse('home'),
            'dashboard': reverse('dashboard'),
            'student_dashboard': reverse('student_dashboard'),
            'admin_dashboard': reverse('admin_dashboard'),
            'admin_users': reverse('admin_users'),
            'admin_club_accounts': reverse('admin_club_accounts'),
            'admin_database': reverse('admin_database'),
            'admin_content': reverse('admin_content'),
            'admin_settings': reverse('admin_settings'),
            'academic_notes': reverse('academic_notes'),
            'notices': reverse('notices'),
            'tickets': reverse('tickets'),
            'medical': reverse('medical'),
            'notes': reverse('notes'),
            'clubs_dashboard': reverse('clubs_dashboard'),
            'transport_dashboard': reverse('transport_dashboard'),
            'meal_dashboard': reverse('meal_dashboard'),
            'checkout': reverse('checkout'),
            'research_ai': reverse('research_ai'),
            'departments': reverse('departments'),
            # Representative department hub URL (any slug resolves; mock data is client-side)
            'department_detail': reverse('department_detail', args=['fde']),

            # Form submission endpoints (placeholders)
            'claim_meal_ticket': reverse('claim_meal_ticket'),
            'book_transport_ticket': reverse('book_transport_ticket'),
            'book_appointment': reverse('book_appointment'),

            # Staff / admin persistent action endpoints
            'api_cafeteria_redeem': reverse('api_cafeteria_redeem'),
            'api_club_verify_transaction': reverse('api_club_verify_transaction'),
            'api_admin_update_role': reverse('api_admin_update_role'),
            'api_club_accounts': reverse('api_club_accounts'),

            # Authentication
            'login': reverse('login'),
            'logout': reverse('logout'),
            'settings': reverse('settings'),
            'signup': reverse('signup'),
            'profile': reverse('profile'),

            # Staff / admin dashboards
            'sys_admin': reverse('sys_admin'),
            'cafeteria_admin': reverse('cafeteria_admin'),
            'club_admin': reverse('club_admin'),

            # Reports & Feedback
            'reports_student': reverse('reports_student'),
            'reports_admin': reverse('reports_admin'),
            'api_reports': reverse('api_reports'),
            'api_admin_reports': reverse('api_admin_reports'),

            # Host portal pages
            'medical_admin_dashboard': reverse('medical_admin_dashboard'),
            'host_index': reverse('host:index'),
            'host_medical_dashboard': reverse('host:medical_host_dashboard'),

            # Website Builder console
            'builder_dashboard': reverse('builder_dashboard'),
        }
    }
