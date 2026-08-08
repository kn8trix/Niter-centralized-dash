"""Centralized endpoint registry (decoupled endpoint mappings).

Templates reference logical endpoint keys (``{{ ENDPOINTS.tickets }}``)
instead of hardcoding ``{% url %}`` lookups in markup. This keeps the
endpoint map in one place so the Visual Builder can remap/override routes
without touching template HTML.
"""

from django.urls import reverse


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

            # Form submission endpoints (placeholders)
            'claim_meal_ticket': reverse('claim_meal_ticket'),
            'book_transport_ticket': reverse('book_transport_ticket'),
            'book_appointment': reverse('book_appointment'),

            # Authentication
            'login': reverse('login'),
            'logout': reverse('logout'),

            # Host portal pages
            'medical_admin_dashboard': reverse('medical_admin_dashboard'),
            'host_index': reverse('host:index'),
            'host_medical_dashboard': reverse('host:medical_host_dashboard'),
        }
    }
