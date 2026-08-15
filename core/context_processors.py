"""Centralized endpoint registry (decoupled endpoint mappings).

Templates reference logical endpoint keys (``{{ ENDPOINTS.tickets }}``)
instead of hardcoding ``{% url %}`` lookups in markup. This keeps the
endpoint map in one place so the Visual Builder can remap/override routes
without touching template HTML.
"""

import json
import logging

from django.urls import reverse

from core.models import ContentBlock, EditablePage, UserNotificationPreference
from core.roles import get_user_role
from core.system_pages import SYSTEM_ROUTE_KEYS
from core.templatetags.builder_tags import render_block_html

logger = logging.getLogger(__name__)


def _block_has_content(block):
    """A block renders only when it actually carries editable content."""
    if block.content_html and block.content_html.strip():
        return True
    data = block.content_json or {}
    return bool(data) and any(
        data.get(key) for key in ('headline', 'title', 'items', 'subtext', 'placeholder', 'embed_url')
    )


def cms_system_blocks(request):
    """Expose customized CMS blocks for the current core system route.

    Core routes (home / study-corner / pharmacy / news / clubs) render their
    default templates until an admin edits one of the registered feature
    blocks in the Block Manager and reveals it. When visible, customized
    blocks are rendered into ``cms_blocks`` and injected by the shared
    ``cms/system_zone.html`` partial — hidden or empty blocks are skipped, so
    the fallback defaults stay untouched. Any failure degrades to an empty
    list (never a 500).
    """
    url_name = getattr(request.resolver_match, 'url_name', None)
    system_key = SYSTEM_ROUTE_KEYS.get(url_name)
    if not system_key:
        return {}
    try:
        page = EditablePage.objects.filter(system_key=system_key).first()
        if page is None:
            return {}
        blocks = [
            {
                'element_id': block.element_id,
                'block_type': block.block_type,
                'rendered_html': render_block_html(block),
            }
            for block in page.content_blocks.filter(visible=True).order_by('order', 'id')
            if _block_has_content(block)
        ]
        return {'cms_blocks': blocks}
    except Exception:
        logger.exception('cms_system_blocks failed for %s', url_name)
        return {}


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
            'club_dashboard': reverse('club_dashboard'),
            'admin_dashboard': reverse('admin_dashboard'),
            'admin_users': reverse('admin_users'),
            'admin_club_accounts': reverse('admin_club_accounts'),
            'admin_database': reverse('admin_database'),
            'admin_content': reverse('admin_content'),
            'admin_settings': reverse('admin_settings'),
            'admin_calendar': reverse('admin_calendar'),
            'admin_attendance': reverse('admin_attendance'),
            'admin_teachers': reverse('admin_teachers'),
            'api_admin_teachers': reverse('api_admin_teachers'),
            # Emergency broadcast system
            'api_emergency_active': reverse('api_emergency_active'),
            'api_admin_emergency_trigger': reverse('api_admin_emergency_trigger'),
            'api_admin_emergency_resolve': reverse('api_admin_emergency_resolve'),
            # Attendance QR/report email dispatch take a <session_token> path
            # arg — resolved with {% url %} in the admin template.
            'attendance': reverse('attendance'),
            'study_corner': reverse('study_corner'),
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
            'api_admin_academic_calendar': reverse('api_admin_academic_calendar'),
            'api_attendance_scan': reverse('api_attendance_scan'),
            'api_attendance_my_stats': reverse('api_attendance_my_stats'),
            'api_admin_attendance_session_create': reverse('api_admin_attendance_session_create'),
            'api_admin_attendance_records': reverse('api_admin_attendance_records'),
            # Live/close take a <session_token> path arg — resolved with {% url %} in the admin template.

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
