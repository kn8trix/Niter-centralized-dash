"""Centralized endpoint registry (decoupled endpoint mappings).

Templates reference logical endpoint keys (``{{ ENDPOINTS.tickets }}``)
instead of hardcoding ``{% url %}`` lookups in markup. This keeps the
endpoint map in one place so the Visual Builder can remap/override routes
without touching template HTML.
"""

from django.urls import reverse

from core.models import EditablePage


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


def endpoints(request):
    """Expose a single ENDPOINTS dict to every template.

    Logical name -> resolved URL. Add new routes here when pages are added.
    """
    return {
        'ENDPOINTS': {
            # Public homepage + student app pages
            'home': reverse('home'),
            'dashboard': reverse('dashboard'),
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

            # Host portal pages
            'medical_admin_dashboard': reverse('medical_admin_dashboard'),
            'host_index': reverse('host:index'),
            'host_medical_dashboard': reverse('host:medical_host_dashboard'),
        }
    }
