import html
import html.parser
import json
import re
import secrets
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from google.auth.exceptions import RefreshError

from .consumers import notify_user
from .decorators import superuser_required
from .google_service import (
    GoogleAccountNotConnected,
    GoogleReauthRequired,
    GoogleServiceError,
    append_club_sheet_row,
    get_club_sheet_data,
    upload_note_to_user_drive,
    verify_club_transaction,
)
from .models import (
    ContentBlock,
    EditablePage,
    MedicalAppointment,
    MealSubscription,
    MealTicket,
    Notification,
    PageTemplate,
    StudentProfile,
    TransportBooking,
)


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


def research_ai_page(request):
    """Academic Research & Thesis Assistant — frontend-only page driven by
    mock JS data (canned assistant responses, no backend/AI calls).
    """
    return render(request, 'research_ai.html')


def departments_directory(request):
    """Department Directory — frontend-only page driven by mock JS data
    (search filter, quick-jump pills, showcase cards with HOD/stats).
    """
    return render(request, 'departments.html')


def department_detail(request, dept_slug):
    """Single Department Hub — frontend-only page driven by mock JS data
    keyed by ``dept_slug`` (tabs: overview, faculty, schedule, notes drive).
    """
    return render(request, 'department_detail.html', {'dept_slug': dept_slug})


# ============================================================================
# Campus services — production action handlers (atomic)
# ============================================================================

# Daily claim caps per meal type (mirrors the cafeteria admin capacities).
DAILY_MEAL_CAPACITY = {
    'breakfast': 80,
    'lunch': 200,
    'dinner': 160,
}

# Transport route catalog — the transport page posts a ``route_id``.
TRANSPORT_ROUTES = {
    '1': {'route_name': 'Route 1: Main Campus Loop', 'departure_time': '08:00 AM'},
    '2': {'route_name': 'Route 2: Sports Complex Shuttle', 'departure_time': '09:30 AM'},
    '3': {'route_name': 'Route 3: City Center Express', 'departure_time': '10:00 AM'},
}

# Medical doctor catalog — the booking page posts a ``doctor`` id.
DOCTORS = {
    '1': 'Dr. Ahmed Khan',
    '2': 'Dr. Sarah Smith',
    '3': 'Dr. Michael Chen',
    '4': 'Dr. Emily Johnson',
}


def _generate_meal_token():
    """Return an unused ``#MEAL-XXXX`` token (4 random digits)."""
    for _ in range(50):
        token = '#MEAL-%04d' % secrets.randbelow(10000)
        if not MealTicket.objects.filter(ticket_token=token).exists():
            return token
    raise RuntimeError('Could not allocate a unique meal token')


def _generate_qr_token():
    """Return a random boarding-pass QR token, e.g. ``TR-4F2A1C``."""
    return 'TR-' + secrets.token_hex(3).upper()


def _broadcast_notification(notification):
    """Push a freshly-created Notification over the user's WebSocket group.

    Called only after the enclosing ``transaction.atomic`` block commits, so a
    rolled-back booking never produces a real-time alert.
    """
    notify_user(notification.user_id, {
        'id': notification.pk,
        'title': notification.title,
        'message': notification.message,
        'category': notification.category,
        'is_read': notification.is_read,
        'created_at': notification.created_at.isoformat(),
    })


@login_required
def claim_meal(request):
    """Claim a daily meal ticket against an active subscription.

    Validates the subscription, enforces the per-meal daily capacity and a
    one-per-user-per-day rule, then atomically saves a ``MealTicket`` and a
    real-time ``Notification``.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    meal_type = request.POST.get('meal_type', '').strip()
    if meal_type not in DAILY_MEAL_CAPACITY:
        return JsonResponse({'status': 'error', 'message': 'Invalid meal type.'}, status=400)

    subscription = getattr(request.user, 'meal_subscription', None)
    if subscription is None or not subscription.is_active or subscription.is_expired:
        return JsonResponse(
            {'status': 'error', 'message': 'No active meal subscription.'},
            status=403,
        )

    # USE_TZ=False → timezone.now() is already naive local time.
    today = timezone.now().date()

    # One ticket per meal type per user per day.
    if MealTicket.objects.filter(
        user=request.user, meal_type=meal_type, claimed_at__date=today
    ).exists():
        return JsonResponse(
            {'status': 'error', 'message': 'You already claimed %s today.' % meal_type},
            status=409,
        )

    # Remaining daily capacity across all users. This is a check-then-act guard:
    # the DB cannot express "capacity" as a constraint, so a rare concurrent
    # oversubscription is bounded by the ticket_token unique constraint and is
    # reconciled at redemption time by the cafeteria staff.
    claimed_today = MealTicket.objects.filter(meal_type=meal_type, claimed_at__date=today).count()
    if claimed_today >= DAILY_MEAL_CAPACITY[meal_type]:
        return JsonResponse(
            {'status': 'error', 'message': 'Daily capacity reached for %s.' % meal_type},
            status=429,
        )

    try:
        with transaction.atomic():
            ticket = MealTicket.objects.create(
                user=request.user,
                meal_type=meal_type,
                ticket_token=_generate_meal_token(),
            )
            notification = Notification.objects.create(
                user=request.user,
                title='Meal ticket claimed',
                message='Your %s ticket %s is ready.' % (meal_type, ticket.ticket_token),
                category='meal',
            )
    except IntegrityError:
        # Token collision or a concurrent claim of the same slot.
        return JsonResponse(
            {'status': 'error', 'message': 'Could not claim meal ticket. Please try again.'},
            status=409,
        )

    _broadcast_notification(notification)
    return JsonResponse({
        'status': 'success',
        'ticket_token': ticket.ticket_token,
        'meal_type': ticket.meal_type,
        'message': 'Meal ticket claimed successfully.',
    })


@login_required
def book_transport(request):
    """Atomically book a seat on a route/departure, QR-verified on boarding.

    The DB's ``unique_together`` on (route, time, seat) is the seat-availability
    arbiter: a concurrent request for an already-taken seat hits an
    ``IntegrityError`` inside ``transaction.atomic`` and is answered 409.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    route_id = request.POST.get('route_id', '').strip()
    route_name = request.POST.get('route_name', '').strip()
    departure_time = request.POST.get('departure_time', '').strip()
    seat_raw = request.POST.get('seat_number', '').strip()

    # The legacy transport form posts only route_id — fill the rest from catalog.
    # Explicit route_name/departure_time (if both sent) take precedence.
    if route_id and route_id in TRANSPORT_ROUTES:
        route_name = route_name or TRANSPORT_ROUTES[route_id]['route_name']
        departure_time = departure_time or TRANSPORT_ROUTES[route_id]['departure_time']

    if not route_name or not departure_time:
        return JsonResponse(
            {'status': 'error', 'message': 'route_name and departure_time are required.'},
            status=400,
        )

    try:
        seat_number = int(seat_raw)
    except (TypeError, ValueError):
        return JsonResponse(
            {'status': 'error', 'message': 'seat_number must be an integer.'},
            status=400,
        )
    if not 1 <= seat_number <= 40:
        return JsonResponse(
            {'status': 'error', 'message': 'Seat number must be between 1 and 40.'},
            status=400,
        )

    try:
        with transaction.atomic():
            booking = TransportBooking.objects.create(
                user=request.user,
                route_name=route_name,
                departure_time=departure_time,
                seat_number=seat_number,
                qr_token=_generate_qr_token(),
            )
            notification = Notification.objects.create(
                user=request.user,
                title='Transport seat booked',
                message='Seat %s on %s (%s) is booked.' % (seat_number, route_name, departure_time),
                category='transport',
            )
    except IntegrityError:
        return JsonResponse(
            {'status': 'error', 'message': 'That seat is already taken on this route.'},
            status=409,
        )

    _broadcast_notification(notification)
    return JsonResponse({
        'status': 'success',
        'booking_id': booking.pk,
        'route_name': booking.route_name,
        'departure_time': booking.departure_time,
        'seat_number': booking.seat_number,
        'qr_token': booking.qr_token,
        'message': 'Transport seat booked successfully.',
    })


@login_required
def book_appointment(request):
    """Atomically book a medical appointment slot (pending confirmation).

    The DB's ``unique_together`` on (doctor, date, slot) prevents two patients
    double-booking the same doctor time slot; a conflicting request is 409.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    doctor_id = request.POST.get('doctor', '').strip()
    doctor_name = request.POST.get('doctor_name', '').strip()
    if not doctor_name and doctor_id in DOCTORS:
        doctor_name = DOCTORS[doctor_id]

    date_raw = request.POST.get('appointment_date', '').strip()
    time_slot = request.POST.get('time_slot', '').strip()
    reason = request.POST.get('reason', '').strip()

    if not doctor_name or not date_raw or not time_slot:
        return JsonResponse(
            {'status': 'error', 'message': 'doctor, appointment_date and time_slot are required.'},
            status=400,
        )

    try:
        appointment_date = datetime.strptime(date_raw, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'appointment_date must be YYYY-MM-DD.'},
            status=400,
        )

    try:
        with transaction.atomic():
            appointment = MedicalAppointment.objects.create(
                user=request.user,
                doctor_name=doctor_name,
                appointment_date=appointment_date,
                time_slot=time_slot,
                reason=reason,
            )
            notification = Notification.objects.create(
                user=request.user,
                title='Appointment booked',
                message='%s on %s at %s is pending confirmation.' % (
                    doctor_name, appointment_date, time_slot,
                ),
                category='medical',
            )
    except IntegrityError:
        return JsonResponse(
            {'status': 'error', 'message': 'That time slot is already booked for this doctor.'},
            status=409,
        )

    _broadcast_notification(notification)
    return JsonResponse({
        'status': 'success',
        'appointment_id': appointment.pk,
        'doctor_name': appointment.doctor_name,
        'appointment_date': appointment.appointment_date.isoformat(),
        'time_slot': appointment.time_slot,
        'appointment_status': appointment.status,
        'message': 'Appointment booked successfully.',
    })


# ============================================================================
# Account & profile pages
# ============================================================================

def signup_view(request):
    """Self-registration — creates a User + StudentProfile and signs the
    student in. Departments come from the StudentProfile choices so the
    dropdown and the stored value can never drift apart.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    errors = []
    if request.method == 'POST':
        student_id = request.POST.get('student_id', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        department = request.POST.get('department', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not student_id:
            errors.append('Student ID is required.')
        elif User.objects.filter(username=student_id).exists() or StudentProfile.objects.filter(student_id=student_id).exists():
            errors.append('An account with this Student ID already exists.')

        if not full_name:
            errors.append('Full name is required.')

        if department not in dict(StudentProfile.DEPARTMENT_CHOICES):
            errors.append('Please choose a valid department.')

        if not email:
            errors.append('Email is required.')

        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        if not errors:
            name_parts = full_name.split(' ', 1)
            user = User.objects.create_user(
                username=student_id,
                email=email,
                password=password,
                first_name=name_parts[0],
                last_name=name_parts[1] if len(name_parts) > 1 else '',
            )
            StudentProfile.objects.create(user=user, student_id=student_id, department=department)
            auth_login(request, user)
            return redirect('dashboard')

    return render(request, 'signup.html', {
        'errors': errors,
        'departments': StudentProfile.DEPARTMENT_CHOICES,
        'form_data': request.POST if request.method == 'POST' else None,
    })


@login_required
def settings_view(request):
    """Account settings — password change (Django PasswordChangeForm) plus
    client-side notification & theme preference toggles.
    """
    password_updated = False
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            password_updated = True
            password_form = PasswordChangeForm(request.user)
    else:
        password_form = PasswordChangeForm(request.user)

    return render(request, 'settings.html', {
        'password_form': password_form,
        'password_updated': password_updated,
    })


@login_required
def profile_view(request):
    """Virtual student ID card + booking & activity history.

    Activity data is mock-only for now (the portal's booking flows are
    frontend-only); swap in real models once tickets/appointments land.
    """
    profile = getattr(request.user, 'student_profile', None)

    appointments = [
        {'doctor': 'Dr. Ahmed Khan', 'date': '2026-08-12', 'time': '10:00 AM', 'status': 'Confirmed'},
        {'doctor': 'Dr. Sarah Smith', 'date': '2026-08-19', 'time': '11:30 AM', 'status': 'Pending'},
    ]
    transport_tickets = [
        {'route': 'Route 1 · Campus → Town Center', 'seat': '12A', 'time': '8:00 AM', 'status': 'Booked'},
        {'route': 'Route 3 · Campus → Mirpur', 'seat': '5C', 'time': '5:30 PM', 'status': 'Boarded'},
    ]
    meal_coupons = [
        {'meal': 'Lunch', 'date': '2026-08-09', 'token': '#MEAL-8921', 'status': 'Active'},
        {'meal': 'Dinner', 'date': '2026-08-10', 'token': '#MEAL-8927', 'status': 'Unused'},
    ]

    return render(request, 'profile.html', {
        'profile': profile,
        'appointments': appointments,
        'transport_tickets': transport_tickets,
        'meal_coupons': meal_coupons,
    })


# ============================================================================
# Notifications — JSON API + real-time alert engine
# ============================================================================

@login_required
def fetch_notifications(request):
    """JSON API: unread count + the 10 most recent notifications for the user.

    Returned items are serialized for the topbar bell: id, title, message,
    category, read state, and creation timestamp (ISO 8601). The project runs
    ``USE_TZ=False``, so ``created_at`` is a naive local timestamp — clients
    should treat it as server-local time rather than UTC.
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'GET required'}, status=405)

    notifications = request.user.notifications.all()[:10]
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({
        'status': 'success',
        'unread_count': unread_count,
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'category': n.category,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
            }
            for n in notifications
        ],
    })


@login_required
def mark_notification_read(request, notification_id):
    """JSON API: mark one of the user's own notifications as read.

    Other users' notifications 404 so a notification id can never be
    acknowledged on someone else's behalf.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    notification = get_object_or_404(request.user.notifications, pk=notification_id)
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    return JsonResponse({'status': 'success'})


# ============================================================================
# Staff / admin dashboards
# ============================================================================

@staff_member_required(login_url=settings.LOGIN_URL)
def system_admin_view(request):
    """System Admin Dashboard — live users, transport bookings, and activity
    audit feed alongside the mock notices/AI/security consoles.

    Students/staff come straight from ``User`` + ``StudentProfile``, the
    transport tab from live ``TransportBooking`` rows, and the security log
    from recent meal/transport/medical activity.
    """
    profiles = StudentProfile.objects.select_related('user').order_by('student_id')
    students = [
        {
            'name': p.user.get_full_name() or p.user.username,
            'student_id': p.student_id,
            'department': p.get_department_display_name(),
            'status': 'Active' if p.user.is_active else 'Inactive',
        }
        for p in profiles
    ]

    staff_users = User.objects.filter(is_staff=True).order_by('username')
    staff = [
        {
            'user_id': u.pk,
            'name': u.get_full_name() or u.username,
            'role': 'System Admin' if u.is_superuser else 'Staff',
            'department': getattr(getattr(u, 'student_profile', None), 'department', 'Administration'),
            'status': 'Active' if u.is_active else 'Inactive',
        }
        for u in staff_users
    ]

    # Live database counts (shown as stat cards on the Users & Roles tab).
    stats = {
        'students': StudentProfile.objects.count(),
        'staff': staff_users.count(),
        'superusers': User.objects.filter(is_superuser=True).count(),
        'subscriptions': MealSubscription.objects.filter(
            is_active=True, expires_at__gt=timezone.now()
        ).count(),
    }

    # Role × permission matrix (render: roles are columns, permissions are rows)
    roles = ['Student', 'Staff', 'Host Admin', 'System Admin']
    permissions = [
        {'name': 'View notices', 'roles': [True, True, True, True]},
        {'name': 'Book transport', 'roles': [True, True, True, True]},
        {'name': 'Claim meal tickets', 'roles': [True, True, True, True]},
        {'name': 'Book appointments', 'roles': [True, True, True, True]},
        {'name': 'Approve club members', 'roles': [False, True, True, True]},
        {'name': 'Edit medical content', 'roles': [False, False, True, True]},
        {'name': 'Manage users & roles', 'roles': [False, False, False, True]},
        {'name': 'View security logs', 'roles': [False, False, False, True]},
    ]

    notices = [
        {'title': 'Midterm Exam Schedule Update', 'category': 'Academic', 'status': 'Published', 'date': '2026-08-08'},
        {'title': 'Library Extended Hours', 'category': 'General', 'status': 'Published', 'date': '2026-08-07'},
        {'title': 'Tech Fest 2026 — Call for Volunteers', 'category': 'Event', 'status': 'Draft', 'date': '2026-08-09'},
        {'title': 'Holiday Notice: National Mourning Day', 'category': 'General', 'status': 'Scheduled', 'date': '2026-08-15'},
    ]
    materials = [
        {'course': 'CS101', 'title': 'Introduction to AI — Lecture Slides', 'type': 'PDF', 'size': '4.2 MB', 'date': '2026-08-05'},
        {'course': 'MATH201', 'title': 'Linear Algebra Problem Set 4', 'type': 'PDF', 'size': '1.1 MB', 'date': '2026-08-06'},
        {'course': 'PHY101', 'title': 'Physics Lab Manual (Updated)', 'type': 'DOCX', 'size': '2.8 MB', 'date': '2026-08-07'},
        {'course': 'CS201', 'title': 'Data Structures — Trees & Graphs Notes', 'type': 'PDF', 'size': '3.4 MB', 'date': '2026-08-08'},
    ]

    # --- Transport Management (consolidated from /transport/ — live data) ---
    bookings = TransportBooking.objects.select_related('user').order_by('-booked_at')
    route_counts = {}
    for booking in bookings:
        route_counts[booking.route_name] = route_counts.get(booking.route_name, 0) + 1
    buses = [
        {
            'route': route_name,
            'driver': '—',
            'status': 'Active' if count > 0 else 'Scheduled',
            'next_stop': '—',
            'eta': '—',
        }
        for route_name, count in sorted(route_counts.items())
    ] or [
        {'route': 'No live bookings yet', 'driver': '—', 'status': 'Scheduled', 'next_stop': '—', 'eta': '—'},
    ]
    boarding_scans = [
        {
            'token': booking.qr_token,
            'route': booking.route_name,
            'time': booking.booked_at.strftime('%I:%M %p'),
            'status': 'Valid',
        }
        for booking in bookings[:10]
    ]

    driver_updates = [
        {'route': 'Route 1', 'driver': 'Abdul Karim', 'update': 'Departed campus on time', 'time': '7:45 AM'},
        {'route': 'Route 2', 'driver': 'Rafiq Uddin', 'update': 'Heavy traffic near Savar bypass', 'time': '7:58 AM'},
        {'route': 'Route 3', 'driver': 'Jamal Hossain', 'update': 'Boarding complete, closing doors', 'time': '5:20 PM'},
    ]

    # --- Local AI Vector DB & Security ---
    vector_stats = {
        'documents': 1240,
        'chunks': 18260,
        'storage': '2.4 GB',
        'last_index': '2026-08-09 06:30 AM',
    }
    vector_queries = [
        {'query': 'AI syllabus CS101', 'hits': 12, 'time': '8:02 AM'},
        {'query': 'midterm schedule', 'hits': 5, 'time': '7:55 AM'},
        {'query': 'cafeteria menu this week', 'hits': 8, 'time': '7:41 AM'},
    ]
    # Real-time activity audit feed — recent meal/transport/medical events.
    security_logs = []
    for ticket in MealTicket.objects.select_related('user').order_by('-claimed_at')[:3]:
        security_logs.append({
            'time': ticket.claimed_at.strftime('%I:%M %p'),
            'user': ticket.user.username,
            'action': 'Meal ticket claimed — %s (%s)' % (ticket.ticket_token, ticket.get_meal_type_display()),
            'ip': '—',
            'status': 'Success',
        })
    for booking in bookings[:3]:
        security_logs.append({
            'time': booking.booked_at.strftime('%I:%M %p'),
            'user': booking.user.username,
            'action': 'Boarding pass issued — %s seat %s' % (booking.route_name, booking.seat_number),
            'ip': '—',
            'status': 'Success',
        })
    for appointment in MedicalAppointment.objects.select_related('user').order_by('-created_at')[:3]:
        security_logs.append({
            'time': appointment.created_at.strftime('%I:%M %p'),
            'user': appointment.user.username,
            'action': 'Appointment booked — %s (%s)' % (appointment.doctor_name, appointment.get_status_display()),
            'ip': '—',
            'status': 'Success',
        })
    if not security_logs:
        security_logs = [
            {'time': '—', 'user': 'system', 'action': 'No recent activity recorded yet', 'ip': '—', 'status': 'Success'},
        ]

    return render(request, 'sys_admin.html', {
        'students': students,
        'staff': staff,
        'stats': stats,
        'roles': roles,
        'permissions': permissions,
        'notices': notices,
        'materials': materials,
        'buses': buses,
        'driver_updates': driver_updates,
        'boarding_scans': boarding_scans,
        'vector_stats': vector_stats,
        'vector_queries': vector_queries,
        'security_logs': security_logs,
    })


@staff_member_required(login_url=settings.LOGIN_URL)
def cafeteria_admin_view(request):
    """Cafeteria admin — live meal slot capacity, subscription counts, and QR
    meal coupon redemption backed by the MealSubscription / MealTicket models.

    Kitchen inventory stays as curated mock data (no inventory model exists).
    """
    today = timezone.now().date()

    # Live claim counts per meal type against the daily capacity caps.
    slots = [
        {
            'meal': meal.capitalize(),
            'capacity': DAILY_MEAL_CAPACITY[meal],
            'claimed': MealTicket.objects.filter(
                meal_type=meal, claimed_at__date=today
            ).count(),
        }
        for meal in ('breakfast', 'lunch', 'dinner')
    ]

    # Live subscription counts.
    subscriptions = {
        'active': MealSubscription.objects.filter(
            is_active=True, expires_at__gt=timezone.now()
        ).count(),
        'total': MealSubscription.objects.count(),
    }

    inventory = [
        {'item': 'Basmati Rice', 'category': 'Grains', 'stock': 320, 'unit': 'kg', 'status': 'In Stock'},
        {'item': 'Lentils (Daal)', 'category': 'Grains', 'stock': 85, 'unit': 'kg', 'status': 'In Stock'},
        {'item': 'Chicken (dressed)', 'category': 'Protein', 'stock': 24, 'unit': 'kg', 'status': 'Low'},
        {'item': 'Cooking Oil', 'category': 'Staples', 'stock': 18, 'unit': 'L', 'status': 'Low'},
        {'item': 'Potatoes', 'category': 'Vegetables', 'stock': 210, 'unit': 'kg', 'status': 'In Stock'},
        {'item': 'Milk Powder', 'category': 'Dairy', 'stock': 6, 'unit': 'kg', 'status': 'Out'},
        {'item': 'Eggs', 'category': 'Protein', 'stock': 480, 'unit': 'pcs', 'status': 'In Stock'},
    ]

    # Real tickets — most recent first with redemption state.
    redemptions = [
        {
            'token': ticket.ticket_token,
            'student': ticket.user.get_full_name() or ticket.user.username,
            'meal': ticket.get_meal_type_display(),
            'time': (ticket.redeemed_at or ticket.claimed_at).strftime('%I:%M %p'),
            'status': 'Redeemed' if ticket.is_redeemed else 'Unused',
        }
        for ticket in MealTicket.objects.select_related('user').order_by('-claimed_at')[:10]
    ]

    return render(request, 'cafeteria_admin.html', {
        'slots': slots,
        'subscriptions': subscriptions,
        'inventory': inventory,
        'redemptions': redemptions,
    })


@staff_member_required(login_url=settings.LOGIN_URL)
def redeem_meal_ticket(request):
    """Redeem a ``#MEAL-XXXX`` coupon at the cafeteria counter.

    Validates the token format, looks up the real ``MealTicket``, marks it
    redeemed (with a timestamp) and returns the ticket details so the admin
    UI can update the redemption log and supply counters.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    token = request.POST.get('token', '').strip().upper()
    if not re.fullmatch(r'#MEAL-\d{4}', token):
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid token — expected format #MEAL-XXXX.'},
            status=400,
        )

    try:
        ticket = MealTicket.objects.select_related('user').get(ticket_token=token)
    except MealTicket.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'No ticket found for %s.' % token},
            status=404,
        )

    if ticket.is_redeemed:
        return JsonResponse(
            {'status': 'error', 'message': 'Ticket %s has already been redeemed.' % token},
            status=409,
        )

    ticket.is_redeemed = True
    ticket.redeemed_at = timezone.now()
    ticket.save(update_fields=['is_redeemed', 'redeemed_at'])

    return JsonResponse({
        'status': 'success',
        'token': ticket.ticket_token,
        'student': ticket.user.get_full_name() or ticket.user.username,
        'meal': ticket.get_meal_type_display(),
        'redeemed_at': ticket.redeemed_at.isoformat(),
        'message': 'Coupon %s redeemed successfully.' % token,
    })


@staff_member_required(login_url=settings.LOGIN_URL)
def update_appointment_status(request, appointment_id):
    """Persist a medical appointment status change and notify the student.

    Accepts ``status`` ∈ {pending, confirmed, completed, cancelled}, saves it
    on the real ``MedicalAppointment`` row, and pushes a real-time
    ``Notification`` to the student's WebSocket group. Answers JSON for AJAX
    callers and redirects (with a Django message) for plain form submits from
    the medical admin / host dashboards.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        appointment = MedicalAppointment.objects.get(pk=appointment_id)
    except MedicalAppointment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Appointment not found.'}, status=404)
    new_status = request.POST.get('status', '').strip()
    valid_statuses = {code for code, _label in MedicalAppointment.STATUS_CHOICES}
    if new_status not in valid_statuses:
        return JsonResponse({'status': 'error', 'message': 'Invalid status.'}, status=400)

    old_label = appointment.get_status_display()
    appointment.status = new_status
    appointment.save(update_fields=['status'])

    label = appointment.get_status_display()
    notification = Notification.objects.create(
        user=appointment.user,
        title='Appointment updated',
        message='Your appointment with %s on %s at %s is now %s.' % (
            appointment.doctor_name,
            appointment.appointment_date,
            appointment.time_slot,
            label,
        ),
        category='medical',
    )
    _broadcast_notification(notification)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'appointment_id': appointment.pk,
            'status': appointment.status,
            'message': 'Appointment %s → %s.' % (old_label, label),
        })

    messages.success(request, 'Appointment %s.' % label)
    next_url = request.POST.get('next', '')
    if not next_url or not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=False
    ):
        next_url = reverse('medical_admin_dashboard')
    return redirect(next_url)


def _sheet_cell(row, *keys):
    """Return the first non-empty string value for ``row`` under any of ``keys``."""
    for key in keys:
        value = row.get(key)
        if value not in (None, ''):
            return str(value).strip()
    return ''


def _club_rows_from_sheet(records):
    """Parse a club Google Sheet into pending members, rosters, and transactions.

    Rows are matched by header names (tolerant of 'Student ID' vs 'student_id'
    etc.). Pending/registered rows become member approvals, paid/active rows
    become the roster, and any row carrying a TrxID becomes a transaction.
    """
    pending, members, transactions = [], [], []
    for row in records:
        name = _sheet_cell(row, 'Name', 'name', 'Student Name', 'Full Name')
        student_id = _sheet_cell(row, 'Student ID', 'student_id', 'Student Id', 'ID')
        status = _sheet_cell(row, 'Status', 'status', 'Payment Status').lower()
        club = _sheet_cell(row, 'Club', 'club') or '—'
        applied = _sheet_cell(row, 'Applied', 'Registered', 'Date') or '—'
        trx = _sheet_cell(row, 'TrxID', 'trx', 'Transaction ID', 'Trx Id')

        if trx:
            transactions.append({
                'student': name or student_id or '—',
                'method': _sheet_cell(row, 'Method', 'Payment Method') or 'bKash',
                'trx_id': trx,
                'amount': _sheet_cell(row, 'Amount', 'Fee') or '—',
                'status': _sheet_cell(row, 'Status', 'status', 'Payment Status') or 'Pending Review',
            })

        if status in ('pending', 'registered', 'applied', 'unverified'):
            pending.append({
                'name': name or '—',
                'student_id': student_id or '—',
                'club': club,
                'applied': applied,
            })
        elif status in ('paid', 'active', 'verified', 'approved', 'member'):
            members.append({
                'name': name or '—',
                'student_id': student_id or '—',
                'club': club,
                'role': 'Member',
            })
    return {'pending': pending, 'members': members, 'transactions': transactions}


@staff_member_required(login_url=settings.LOGIN_URL)
def verify_club_transaction_view(request):
    """Verify a bKash/Nagad/Rocket TrxID against the club's linked Google Sheet.

    Marks the matching row ``Verified`` in the sheet and pushes a real-time
    ``Notification`` to the student the row belongs to (matched by Student ID).
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    sheet_url = request.POST.get('sheet_url', '').strip()
    trx_id = request.POST.get('trx', '').strip()
    if not sheet_url or not trx_id:
        return JsonResponse(
            {'status': 'error', 'message': 'sheet_url and trx are required.'},
            status=400,
        )

    try:
        row = verify_club_transaction(sheet_url, trx_id, request.user)
    except (GoogleAccountNotConnected, GoogleReauthRequired, RefreshError):
        return _auth_required_response()
    except GoogleServiceError as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=400)

    student_id = _sheet_cell(row, 'Student ID', 'student_id', 'Student Id', 'ID')
    student = None
    notified = False
    if student_id:
        user = User.objects.filter(
            Q(student_profile__student_id__iexact=student_id)
            | Q(username__iexact=student_id)
        ).first()
        if user is not None:
            student = user.get_full_name() or user.username
            notification = Notification.objects.create(
                user=user,
                title='Payment verified',
                message='Your payment (TrxID %s) has been verified.' % trx_id,
                category='club',
            )
            _broadcast_notification(notification)
            notified = True

    return JsonResponse({
        'status': 'success',
        'message': 'Payment verified successfully.',
        'student': student,
        'notified': notified,
    })


@superuser_required
def update_user_role(request):
    """Toggle a user's ``is_staff`` / ``is_superuser`` flags safely.

    Superadmins only. Guards: you cannot change your own role, and the last
    remaining superuser can never be demoted.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        user_id = int(request.POST.get('user_id', '') or 0)
    except (TypeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'user_id is required.'}, status=400)

    role = request.POST.get('role', '').strip()
    if role not in ('student', 'staff', 'superuser'):
        return JsonResponse({'status': 'error', 'message': 'Invalid role.'}, status=400)

    try:
        target = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    if target == request.user:
        return JsonResponse(
            {'status': 'error', 'message': 'You cannot change your own role.'},
            status=400,
        )
    if (
        target.is_superuser
        and role != 'superuser'
        and User.objects.filter(is_superuser=True).count() <= 1
    ):  # never strand the platform without a superuser
        return JsonResponse(
            {'status': 'error', 'message': 'Cannot demote the last superuser.'},
            status=400,
        )

    target.is_staff = role in ('staff', 'superuser')
    target.is_superuser = role == 'superuser'
    target.save(update_fields=['is_staff', 'is_superuser'])

    return JsonResponse({
        'status': 'success',
        'message': 'Role updated for %s.' % target.username,
        'user_id': target.pk,
        'role': role,
        'is_staff': target.is_staff,
        'is_superuser': target.is_superuser,
    })


@staff_member_required(login_url=settings.LOGIN_URL)
def club_admin_view(request):
    """Club admin — member approvals, role assignments, event posts, and
    bKash/Nagad/Rocket transaction verification.

    When a ``sheet_url`` query parameter is present the pending registrations,
    member roster, and transactions are synced live from the club's linked
    Google Sheet through the ``gspread`` service layer (using the signed-in
    staff member's stored ``GoogleUserToken``). Without a sheet, curated mock
    data is shown so the page still renders.
    """
    pending_members = [
        {'name': 'Fahim Chowdhury', 'student_id': 'S1012', 'club': 'Computer Club', 'applied': '2026-08-08'},
        {'name': 'Nusrat Jahan', 'student_id': 'S1017', 'club': 'Cultural Society', 'applied': '2026-08-08'},
        {'name': 'Imran Hossain', 'student_id': 'S1021', 'club': 'Electronics Club', 'applied': '2026-08-09'},
    ]
    members = [
        {'name': 'Alice Johnson', 'student_id': 'S1001', 'club': 'Computer Club', 'role': 'Executive'},
        {'name': 'David Tennant', 'student_id': 'S1004', 'club': 'Sports Club', 'role': 'Member'},
        {'name': 'Eve Parker', 'student_id': 'S1005', 'club': 'Cultural Society', 'role': 'Member'},
    ]
    events = [
        {'title': 'Hackathon 2026', 'club': 'Computer Club', 'date': '2026-08-22', 'fee': 'Free'},
        {'title': 'Cultural Night', 'club': 'Cultural Society', 'date': '2026-08-28', 'fee': '৳200 BDT'},
        {'title': 'Robotics Workshop', 'club': 'Electronics Club', 'date': '2026-09-05', 'fee': '৳300 BDT'},
    ]
    transactions = [
        {'student': 'Nusrat Jahan', 'method': 'bKash', 'trx_id': '9J32X8KL', 'amount': '৳200', 'status': 'Verified'},
        {'student': 'Imran Hossain', 'method': 'Nagad', 'trx_id': 'NA7K2P1M', 'amount': '৳300', 'status': 'Pending Review'},
        {'student': 'Fahim Chowdhury', 'method': 'Rocket', 'trx_id': 'RC5Q9W3T', 'amount': '৳0', 'status': 'Pending Review'},
    ]

    sheet_url = request.GET.get('sheet_url', '').strip()
    sheet_error = None
    if sheet_url:
        try:
            records = get_club_sheet_data(sheet_url, request.user)
            parsed = _club_rows_from_sheet(records)
            if parsed['pending'] or parsed['members'] or parsed['transactions']:
                pending_members = parsed['pending']
                members = parsed['members']
                transactions = parsed['transactions']
            else:
                sheet_error = 'Sheet loaded, but no recognizable registrations were found.'
        except (GoogleAccountNotConnected, GoogleReauthRequired, RefreshError):
            sheet_error = 'Google access required — connect your Google account to sync the sheet.'
        except GoogleServiceError as exc:
            sheet_error = str(exc)

    return render(request, 'club_admin.html', {
        'pending_members': pending_members,
        'members': members,
        'events': events,
        'transactions': transactions,
        'sheet_url': sheet_url,
        'sheet_error': sheet_error,
    })


# ============================================================================
# Website Builder — dynamic page renderer (Phase 2)
# ============================================================================

def _style_attr(style_json):
    """Flatten a builder style dict into a CSS inline-style attribute string.

    CamelCase keys (e.g. ``fontSize`` / ``paddingTop``) are converted to
    kebab-case CSS properties (``font-size`` / ``padding-top``) so styles
    authored in the builder apply directly in the browser.
    """
    parts = []
    for key, value in (style_json or {}).items():
        kebab = re.sub(r'(?<!^)(?=[A-Z])', '-', key).lower()
        parts.append('%s: %s' % (kebab, value))
    return '; '.join(parts)


def editable_page_view(request, slug):
    """Public renderer for a builder-authored page and its ContentBlocks.

    Serves the page at ``/page/<slug>/``. Unknown or unpublished pages 404
    so drafts are never exposed to visitors. Blocks are ordered by their
    creation order (stable pk order).
    """
    page = get_object_or_404(EditablePage, slug=slug, is_published=True)
    blocks = [
        {
            'element_id': block.element_id,
            'content_html': block.content_html,
            'style_attr': _style_attr(block.style_json),
        }
        for block in page.content_blocks.all()
    ]
    return render(request, 'editable_page.html', {
        'page': page,
        'blocks': blocks,
    })


# ============================================================================
# Website Builder — Super Admin console (Phase 2)
# ============================================================================

# ----------------------------------------------------------------------------
# Block HTML sanitizer (defense-in-depth)
# ----------------------------------------------------------------------------
# The builder API is superuser-only, so this is belt-and-braces on top of the
# existing trust model: a strict allow-list keeps pasted content free of
# script tags, event handlers, and inline-style / javascript: URL injection.

ALLOWED_TAGS = frozenset({
    'p', 'br', 'hr', 'div', 'span',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'b', 'em', 'i', 'u', 's', 'mark',
    'a', 'img', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
})

VOID_TAGS = frozenset({'br', 'hr', 'img'})

# Per-tag attribute allow-list (``style``, ``on*`` and anything else is dropped).
ALLOWED_ATTRS = {
    'a': {'href', 'title', 'target'},
    'img': {'src', 'alt', 'title', 'width', 'height'},
    'code': {'class'},
    'pre': {'class'},
    'div': {'class'},
    'span': {'class'},
    'th': {'colspan', 'rowspan'},
    'td': {'colspan', 'rowspan'},
}

SAFE_URL_SCHEMES = frozenset({'http', 'https', 'mailto', 'tel', 'ftp'})


def _is_safe_url(value):
    """Allow relative/absolute links but reject dangerous URL schemes."""
    stripped = (value or '').strip().lower()
    if not stripped or stripped.startswith('#') or stripped.startswith('//'):
        return True
    scheme = re.match(r'^([a-z][a-z0-9+.-]*):', stripped)
    if not scheme:
        return True  # relative path such as /dashboard/ or images/x.png
    return scheme.group(1) in SAFE_URL_SCHEMES


class _BlockHtmlSanitizer(html.parser.HTMLParser):
    """Rebuild input HTML keeping only allow-listed tags and attributes.

    Content inside a disallowed element (e.g. ``<script>``) is dropped
    entirely rather than being leaked as text. Fail-safe: an unclosed
    disallowed tag swallows the rest of the document, which can only
    ever lose content (never allow it through).
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._out = []
        self._skip_depth = 0

    def _safe_attrs(self, tag, attrs):
        allowed = ALLOWED_ATTRS.get(tag, frozenset())
        for key, value in attrs:
            if key not in allowed or key.lower().startswith('on'):
                continue
            if key in ('href', 'src') and not _is_safe_url(value):
                continue
            yield key, html.escape(value, quote=True)

    def _emit_start(self, tag, attrs, self_closing):
        parts = ['<%s' % tag]
        for key, value in self._safe_attrs(tag, attrs):
            parts.append(' %s="%s"' % (key, value))
        parts.append(' />' if self_closing else '>')
        self._out.append(''.join(parts))

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            self._skip_depth += 1
            return
        if not self._skip_depth:
            self._emit_start(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag, attrs):
        # XHTML-style self-closing tags such as <img /> / <br />
        if tag in ALLOWED_TAGS and not self._skip_depth:
            self._emit_start(tag, attrs, self_closing=True)

    def handle_endtag(self, tag):
        if tag not in ALLOWED_TAGS:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if not self._skip_depth and tag not in VOID_TAGS:
            self._out.append('</%s>' % tag)

    def handle_data(self, data):
        if not self._skip_depth:
            self._out.append(html.escape(data))

    def handle_comment(self, data):
        pass  # drop comments

    def handle_decl(self, decl):
        pass  # drop <!DOCTYPE ...>

    def handle_pi(self, data):
        pass  # drop <?...?>


def sanitize_html(raw_html):
    """Return ``raw_html`` with all non-allow-listed tags/attributes removed."""
    if not raw_html:
        return ''
    parser = _BlockHtmlSanitizer()
    parser.feed(raw_html)
    parser.close()
    return ''.join(parser._out)


# custom_css is injected with ``|safe`` inside a <style> tag on the live page,
# so strip anything that could break out of it (closing tags / HTML comments).
_UNSAFE_CSS_PATTERNS = (
    re.compile(r'</\s*style', re.IGNORECASE),
    re.compile(r'</\s*script', re.IGNORECASE),
    re.compile(r'<!--'),
)


def _sanitize_css(raw_css):
    """Light guard for custom_css: remove <style>/<script> break-out tokens."""
    if not raw_css:
        return ''
    css = raw_css
    for pattern in _UNSAFE_CSS_PATTERNS:
        css = pattern.sub('', css)
    return css


def _parse_json_body(request):
    """Parse a JSON request body, returning ``(data, error_response)``."""
    if request.method != 'POST':
        return None, JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    try:
        return json.loads(request.body or b'{}'), None
    except (json.JSONDecodeError, ValueError):
        return None, JsonResponse({'status': 'error', 'message': 'Invalid JSON body'}, status=400)


# ----------------------------------------------------------------------------
# Views
# ----------------------------------------------------------------------------

@superuser_required
def builder_dashboard(request):
    """Super admin console listing every EditablePage and PageTemplate."""
    pages = (
        EditablePage.objects
        .select_related('template')
        .annotate(block_count=Count('content_blocks'))
        .order_by('title')
    )
    templates = PageTemplate.objects.order_by('name')
    return render(request, 'builder/dashboard.html', {
        'pages': pages,
        'templates': templates,
    })


@superuser_required
def visual_editor(request, page_slug):
    """Split-screen visual editor for a single page and its ContentBlocks."""
    page = get_object_or_404(EditablePage, slug=page_slug)
    blocks = [
        {
            'element_id': block.element_id,
            'content_html': block.content_html,
            'style': block.style_json or {},
        }
        for block in page.content_blocks.all()
    ]
    return render(request, 'builder/editor.html', {
        'page': page,
        'blocks': blocks,
    })


@superuser_required
def create_page(request):
    """JSON API: register a new EditablePage from the builder dashboard modal.

    Expects ``{title, slug, template_id?}``; returns the edit URL so the
    dashboard can jump straight into the visual editor.
    """
    data, error = _parse_json_body(request)
    if error is not None:
        return error

    title = (data.get('title') or '').strip()
    slug = (data.get('slug') or '').strip()
    if not title or not slug:
        return JsonResponse(
            {'status': 'error', 'message': 'title and slug are required'},
            status=400,
        )
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        return JsonResponse(
            {'status': 'error', 'message': 'Slug must be lowercase letters, numbers and dashes (e.g. about-us).'},
            status=400,
        )
    if EditablePage.objects.filter(slug=slug).exists():
        return JsonResponse(
            {'status': 'error', 'message': 'A page with this slug already exists.'},
            status=400,
        )

    template = None
    template_id = data.get('template_id')
    if template_id:
        try:
            template = PageTemplate.objects.get(pk=template_id)
        except (PageTemplate.DoesNotExist, ValueError, TypeError):
            return JsonResponse(
                {'status': 'error', 'message': 'Template not found.'},
                status=400,
            )

    page = EditablePage.objects.create(title=title, slug=slug, template=template)
    return JsonResponse({
        'status': 'success',
        'page_slug': page.slug,
        'edit_url': reverse('visual_editor', args=[page.slug]),
    })


@superuser_required
def save_content_block(request):
    """JSON API: create/update a ContentBlock from the visual editor.

    Expects ``{page_slug, element_id, content_html, style_json}``. HTML is
    sanitized before it is stored; the response is ``{'status': 'success'}``.
    """
    data, error = _parse_json_body(request)
    if error is not None:
        return error

    page_slug = data.get('page_slug')
    element_id = data.get('element_id')
    if not page_slug or not element_id:
        return JsonResponse(
            {'status': 'error', 'message': 'page_slug and element_id are required'},
            status=400,
        )

    try:
        page = EditablePage.objects.get(slug=page_slug)
    except EditablePage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Page not found'}, status=404)

    style_json = data.get('style_json') or {}
    if not isinstance(style_json, dict):
        style_json = {}

    ContentBlock.objects.update_or_create(
        page=page,
        element_id=element_id,
        defaults={
            'content_html': sanitize_html(data.get('content_html', '')),
            'style_json': style_json,
        },
    )
    return JsonResponse({'status': 'success'})


@superuser_required
def save_page_css(request):
    """JSON API: update an EditablePage's ``custom_css`` theme overrides.

    CSS is given a light guard (``</style>``/``</script>`` break-out tokens
    removed) before saving since it is rendered with ``|safe`` on the live
    page inside a ``<style>`` tag.
    """
    data, error = _parse_json_body(request)
    if error is not None:
        return error

    page_slug = data.get('page_slug')
    if not page_slug:
        return JsonResponse({'status': 'error', 'message': 'page_slug is required'}, status=400)

    try:
        page = EditablePage.objects.get(slug=page_slug)
    except EditablePage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Page not found'}, status=404)

    page.custom_css = _sanitize_css(data.get('custom_css', ''))
    page.save(update_fields=['custom_css', 'updated_at'])
    return JsonResponse({'status': 'success'})


# ============================================================================
# Google integration — API endpoints (Phase 4)
# ============================================================================

def _auth_required_response():
    """401 JSON telling the client the user must (re)connect their Google account.

    Used for missing tokens, expired sessions, and failed token refreshes. The
    ``redirect_url`` points at allauth's Google re-consent flow so the frontend
    can open it in a new window and continue after re-authenticating.
    """
    return JsonResponse({
        'status': 'auth_required',
        'redirect_url': reverse('google_login'),
    }, status=401)


def _google_error_response(exc):
    """Map a non-auth Google service failure to a 500 JSON error response.

    Auth problems (missing token, expired session, failed refresh) never reach
    this helper — the views catch ``(GoogleAccountNotConnected,
    GoogleReauthRequired, RefreshError)`` first and answer 401 instead.
    """
    return JsonResponse({'status': 'error', 'message': str(exc)}, status=500)


@login_required
def upload_note_view(request):
    """Upload a note file to the user's Google Drive (CampusDash Notes folder)."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    file_obj = request.FILES.get('file')
    if file_obj is None:
        return JsonResponse(
            {'status': 'error', 'message': 'No file provided (multipart field "file").'},
            status=400,
        )
    if file_obj.size == 0:
        return JsonResponse({'status': 'error', 'message': 'The uploaded file is empty.'}, status=400)

    try:
        result = upload_note_to_user_drive(request.user, file_obj)
    except (GoogleAccountNotConnected, GoogleReauthRequired, RefreshError):
        return _auth_required_response()
    except GoogleServiceError as exc:
        return _google_error_response(exc)

    return JsonResponse({
        'status': 'success',
        'file_id': result.get('file_id'),
        'web_link': result.get('web_link'),
    })


@login_required
def fetch_club_sheet_view(request):
    """Return every row of the club Google Sheet as JSON records."""
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'GET required'}, status=405)

    sheet_url = (request.GET.get('sheet_url') or '').strip()
    if not sheet_url:
        return JsonResponse(
            {'status': 'error', 'message': 'sheet_url query parameter is required.'},
            status=400,
        )

    try:
        records = get_club_sheet_data(sheet_url, request.user)
    except (GoogleAccountNotConnected, GoogleReauthRequired, RefreshError):
        return _auth_required_response()
    except GoogleServiceError as exc:
        return _google_error_response(exc)

    return JsonResponse({'status': 'success', 'records': records})


@login_required
def append_club_sheet_view(request):
    """Append a row of values to the club Google Sheet."""
    data, error = _parse_json_body(request)
    if error is not None:
        return error

    sheet_url = (data.get('sheet_url') or '').strip()
    row_data = data.get('row_data')
    if not sheet_url:
        return JsonResponse({'status': 'error', 'message': 'sheet_url is required.'}, status=400)
    if not isinstance(row_data, list):
        return JsonResponse(
            {'status': 'error', 'message': 'row_data must be a list of values.'},
            status=400,
        )

    try:
        append_club_sheet_row(sheet_url, row_data, request.user)
    except (GoogleAccountNotConnected, GoogleReauthRequired, RefreshError):
        return _auth_required_response()
    except GoogleServiceError as exc:
        return _google_error_response(exc)

    return JsonResponse({'status': 'success', 'message': 'Row added'})
