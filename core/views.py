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

def claim_meal_ticket(request):
    return render(request, 'ticketing/tickets.html')

def book_transport_ticket(request):
    return render(request, 'ticketing/tickets.html')

def book_appointment(request):
    return render(request, 'medical/booking.html')
