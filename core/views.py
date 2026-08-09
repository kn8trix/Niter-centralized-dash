from django.shortcuts import render


def public_home(request):
    """Public homepage (landing page) served at the root URL."""
    return render(request, 'index.html')


def dashboard(request):
    return render(request, 'dashboard/home.html')

def tickets(request):
    return render(request, 'ticketing/tickets.html')

def medical(request):
    return render(request, 'medical/booking.html')

def notes(request):
    return render(request, 'notes/notes_engine.html')

def academic_notes(request):
    return render(request, 'academic/notes.html')

def notices(request):
    return render(request, 'notices/notices.html')


def clubs_dashboard(request):
    """Club & Event dashboard — frontend-only page driven by mock JS data."""
    return render(request, 'clubs.html')


def transport_dashboard(request):
    """Transport online ticket system — frontend-only page driven by mock JS data."""
    return render(request, 'transport.html')


def meal_dashboard(request):
    """Online meal ticket system — frontend-only page driven by mock JS data."""
    return render(request, 'meals.html')


def checkout_page(request):
    """Payment Gateway & Checkout — frontend-only page driven by mock JS data.

    Handles payments for club event registrations, transport ticket bookings,
    and meal tokens via local mobile wallets (bKash / Nagad / Rocket / Card).
    """
    return render(request, 'checkout.html')

def placeholder(request, page='settings'):
    """Minimal warm-beige placeholder pages (settings / signup) so the shared
    profile popover links resolve. Swap in real pages later."""
    pages = {
        'settings': {
            'title': 'Account Settings',
            'subtitle': 'Manage your profile, notifications, and preferences.',
            'icon': 'fa-gear',
            'message': 'Profile, notification, and privacy preferences are being prepared and will live here soon.',
        },
        'signup': {
            'title': 'Create an Account',
            'subtitle': 'Join the Niter campus portal.',
            'icon': 'fa-user-plus',
            'message': 'Self-registration is not available yet — contact the administration office to get your student account created.',
        },
    }
    data = pages.get(page, pages['settings'])
    return render(request, 'placeholder.html', data)


def claim_meal_ticket(request):
    return render(request, 'ticketing/tickets.html')

def book_transport_ticket(request):
    return render(request, 'ticketing/tickets.html')

def book_appointment(request):
    return render(request, 'medical/booking.html')
