import colorsys
import html
import html.parser
import json
import re
import secrets
from collections import Counter
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Count, F, Max, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from google.auth.exceptions import RefreshError

from .consumers import notify_user, send_chat_push
from .decorators import change_editablepage_required, superuser_required
from .forms import SignUpForm
from .templatetags.builder_tags import render_block_html
from .google_service import (
    GoogleAccountNotConnected,
    GoogleReauthRequired,
    GoogleServiceError,
    append_club_sheet_row,
    get_club_sheet_data,
    upload_note_to_user_drive,
    user_has_drive_access,
    verify_club_transaction,
)
from .models import (
    ClassRoutine,
    Club,
    ClubEvent,
    ClubRegistration,
    ContentBlock,
    Course,
    CourseMaterial,
    Department,
    EditablePage,
    GoogleUserToken,
    MedicalAppointment,
    MedicalChatMessage,
    MedicalChatThread,
    MealSubscription,
    MealTicket,
    Notice,
    Notification,
    PageTemplate,
    PaymentTransaction,
    StudentProfile,
    TransportBooking,
    TransportRoute,
    UserNote,
    UserNotificationPreference,
)


def public_home(request):
    """Public homepage (landing page) served at the root URL."""
    return render(request, 'index.html')


def dashboard(request):
    """Student dashboard — live widgets + feeds computed from the database.

    The three summary cards are real-time aggregates (not hardcoded):
      * Meal ratio — tickets claimed today vs the daily capacity caps.
      * Transport — seats still available on the active catalog routes.
      * Medical — on-duty doctors and appointment slots open today.
    The feeds show the latest published notices and the courses with the most
    uploaded materials.
    """
    today = timezone.now().date()

    # --- Meal Ratio Counter (tickets claimed today / daily capacity) ---
    total_capacity = sum(DAILY_MEAL_CAPACITY.values())
    claimed_today = MealTicket.objects.filter(claimed_at__date=today).count()
    meal_widget = {
        'used': claimed_today,
        'remaining': max(total_capacity - claimed_today, 0),
        'total': total_capacity,
        # Cap at 100 so an over-capacity day cannot overflow the progress bar.
        'percent': min(100, round(claimed_today / total_capacity * 100)) if total_capacity else 0,
    }

    # --- Transport Service (available seats per active route) ---
    # One grouped query for every DB catalog route instead of a COUNT per route.
    transport_catalog = _transport_catalog()
    route_booked = {
        (row['route_name'], row['departure_time']): row['booked']
        for row in TransportBooking.objects.values('route_name', 'departure_time')
        .annotate(booked=Count('id'))
    }
    routes = []
    for route_id, info in transport_catalog.items():
        booked = route_booked.get((info['route_name'], info['departure_time']), 0)
        routes.append({
            'id': route_id,
            'name': info['route_name'],
            'time': info['departure_time'],
            'available': max(info['capacity'] - booked, 0),
            'booked': booked,
        })
    routes.sort(key=lambda r: r['available'], reverse=True)
    transport_widget = routes[0] if routes else None

    # --- Medical Center (on-duty doctors + slots open today) ---
    # One query for today's non-cancelled appointments: the row list doubles as
    # both the booked-slot count and the on-duty doctor set.
    today_rows = list(
        MedicalAppointment.objects.filter(appointment_date=today)
        .exclude(status='cancelled')
        .values_list('doctor_name', flat=True)
    )
    booked_slots = len(today_rows)
    in_session_today = set(today_rows)
    total_slots = len(DOCTORS) * MEDICAL_SLOTS_PER_DAY
    medical_widget = {
        'doctors': [
            {
                'name': doctor_name,
                'specialty': DOCTOR_SPECIALTIES.get(doctor_name, 'Campus Doctor'),
                'in_session': doctor_name in in_session_today,
            }
            for doctor_name in DOCTORS.values()
        ],
        'booked': booked_slots,
        'available': max(total_slots - booked_slots, 0),
        'total': total_slots,
    }

    # --- Feeds (latest published notices + top courses by material count) ---
    recent_notices = Notice.objects.filter(is_published=True).select_related('author')[:3]
    course_links = (
        Course.objects.annotate(material_count=Count('materials'))
        .order_by('-material_count', 'code')[:4]
    )

    return render(request, 'dashboard/home.html', {
        'meal_widget': meal_widget,
        'transport_widget': transport_widget,
        'medical_widget': medical_widget,
        'recent_notices': recent_notices,
        'course_links': course_links,
    })

def tickets(request):
    return render(request, 'ticketing/tickets.html')

def medical(request):
    """Medical booking page — form plus the signed-in student's live
    appointments and consultation threads (patient-side chat UI)."""
    context = {}
    if request.user.is_authenticated:
        context['my_appointments'] = request.user.medical_appointments.all()
        context['my_threads'] = MedicalChatThread.objects.filter(
            patient=request.user,
        ).select_related('patient').prefetch_related('messages')
    return render(request, 'medical/booking.html', context)

def notes(request):
    """Notes Engine workspace — the editor plus the live academic catalog.

    The sidebar is wired to the same database rows as the /academic-notes/
    drive: folder categories are built from the real ``Department`` rows that
    own at least one ``Course`` (falling back to ``StudentProfile`` choices
    for codes without a hub row), the Recent PDFs list shows the newest
    ``CourseMaterial`` rows, and My Notes lists the signed-in user's saved
    ``UserNote`` rows. The save / summarize / keywords / export actions are
    server-backed; clicking a saved note loads it over ``GET /api/notes/<id>/``
    (owner-scoped).
    """
    materials = CourseMaterial.objects.select_related('course').order_by('-uploaded_at')

    # Folder categories: one per department that has at least one course,
    # named from the real Department model, annotated with the course count
    # (two grouped queries total, no N+1).
    course_counts = {
        row['department']: row['count']
        for row in Course.objects.values('department').annotate(count=Count('id'))
    }
    department_names = dict(Department.objects.values_list('code', 'name'))
    fallback_names = dict(StudentProfile.DEPARTMENT_CHOICES)
    folders = [
        {
            'code': code,
            'name': department_names.get(code) or fallback_names.get(code, code),
            'count': count,
            'icon': _DEPARTMENT_ICONS.get(code, 'fa-folder'),
        }
        for code, count in course_counts.items()
    ]
    folders.sort(key=lambda folder: folder['name'])

    user_notes = (
        request.user.notes.all()
        if request.user.is_authenticated
        else UserNote.objects.none()
    )
    return render(request, 'notes/notes_engine.html', {
        'folders': folders,
        'materials': materials,
        'user_notes': user_notes,
    })

# Icon per department on the notes drive folder cards.
_DEPARTMENT_ICONS = {
    'CSE': 'fa-laptop-code',
    'TEX': 'fa-industry',
    'IPE': 'fa-robot',
    'FDAE': 'fa-palette',
    'EEE': 'fa-bolt',
}


def academic_notes(request):
    """Academic Notes Drive — live Course folders + CourseMaterial documents."""
    courses = Course.objects.prefetch_related('materials').order_by('code')
    materials = CourseMaterial.objects.select_related('course').order_by('-uploaded_at')

    # Folder cards: one per department that has at least one course, showing
    # the number of uploaded materials in that department (2 queries total).
    course_departments = set(Course.objects.values_list('department', flat=True))
    material_counts = {
        row['course__department']: row['count']
        for row in CourseMaterial.objects.values('course__department').annotate(
            count=Count('id')
        )
    }
    folders = []
    for code, name in StudentProfile.DEPARTMENT_CHOICES:
        if code not in course_departments:
            continue
        folders.append({
            'code': code,
            'name': name,
            'count': material_counts.get(code, 0),
            'icon': _DEPARTMENT_ICONS.get(code, 'fa-folder'),
        })

    return render(request, 'academic/notes.html', {
        'courses': courses,
        'materials': materials,
        'folders': folders,
    })

def notices(request):
    """Official Notices — published ``Notice`` rows, filtered by category.

    Accepts an optional ``?category=`` query parameter (urgent / academic /
    event / general); anything else (or nothing) shows every published notice.
    """
    category = (request.GET.get('category') or '').strip().lower()
    queryset = Notice.objects.filter(is_published=True).select_related('author')
    if category in dict(Notice.CATEGORY_CHOICES):
        queryset = queryset.filter(category=category)
    else:
        category = 'all'
    return render(request, 'notices/notices.html', {
        'notices': queryset,
        'active_category': category,
        'categories': Notice.CATEGORY_CHOICES,
    })


# Fallback icon per club (keyed by slug) for the /clubs/ cards when no
# banner image is uploaded — mirrors the _DEPARTMENT_ICONS convention.
_CLUB_ICONS = {
    'computer-club': 'fa-laptop-code',
    'electronics-club': 'fa-microchip',
    'cultural-society': 'fa-masks-theater',
    'sports-club': 'fa-trophy',
}


def clubs_dashboard(request):
    """Club & Event page — live ``Club`` / ``ClubEvent`` rows from the database.

    The student view lists every club (with a live active-member count) and
    every upcoming event; membership requests are handled by ``join_club``
    (``POST /api/clubs/join/``) and event seats route to the checkout gateway.
    """
    clubs = Club.objects.annotate(
        member_count=Count('registrations', filter=Q(registrations__status='active'))
    ).order_by('name')
    club_rows = [
        {
            'club': club,
            'icon': _CLUB_ICONS.get(club.slug, 'fa-flag'),
        }
        for club in clubs
    ]
    events = ClubEvent.objects.filter(
        event_date__gte=timezone.now().date()
    ).select_related('club').order_by('event_date')

    return render(request, 'clubs.html', {
        'clubs': club_rows,
        'events': events,
        'checkout_url': reverse('checkout'),
    })


@login_required
def join_club(request):
    """Register the signed-in student for club membership (pending approval).

    One registration per student+club — enforced by the model's
    ``unique_together`` — so a repeat request is answered 409. When the club
    has a lead staff member, they receive a real-time ``Notification``.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    club_id = request.POST.get('club_id', '').strip()
    try:
        club = Club.objects.select_related('lead_user').get(pk=int(club_id))
    except (Club.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Club not found.'}, status=404)

    existing = ClubRegistration.objects.filter(student=request.user, club=club).first()
    if existing is not None:
        return JsonResponse({
            'status': 'error',
            'message': 'You already requested to join %s (%s).' % (
                club.name, existing.get_status_display().lower(),
            ),
        }, status=409)

    try:
        with transaction.atomic():
            registration = ClubRegistration.objects.create(
                student=request.user, club=club, status='pending',
            )
    except IntegrityError:
        # Duplicate join raced in from a concurrent request.
        return JsonResponse(
            {'status': 'error', 'message': 'Could not join %s. Please try again.' % club.name},
            status=409,
        )

    if club.lead_user is not None and club.lead_user.is_active:
        notification = Notification.objects.create(
            user=club.lead_user,
            title='New club membership request',
            message='%s requested to join %s.' % (
                request.user.get_full_name() or request.user.username, club.name,
            ),
            category='club',
        )
        _broadcast_notification(notification)

    return JsonResponse({
        'status': 'success',
        'registration_id': registration.pk,
        'club': club.name,
        'registration_status': registration.status,
        'message': 'Membership request sent to %s.' % club.name,
    })


def transport_dashboard(request):
    """Transport online ticket system — live DB routes, schedules and drivers.

    The active catalog (routes, departures, driver details, and live booked-
    seat counts) is rendered as JSON for the page's frontend JS; seat booking
    goes through ``book_transport`` against the same DB rows.
    """
    catalog = _transport_catalog()
    route_booked = {
        (row['route_name'], row['departure_time']): row['booked']
        for row in TransportBooking.objects.values('route_name', 'departure_time')
        .annotate(booked=Count('id'))
    }
    routes = []
    for route_id, info in catalog.items():
        booked = route_booked.get((info['route_name'], info['departure_time']), 0)
        left = max(info['capacity'] - booked, 0)
        if left == 0:
            status, dot = 'Full', 'dot-red'
        elif left <= 5:
            status, dot = 'Few seats left', 'dot-amber'
        else:
            status, dot = 'On Time', 'dot-green'
        routes.append({
            'id': route_id,
            'name': info['route_name'],
            'dest': ' → '.join(x for x in (info['origin'], info['destination']) if x),
            'driver': info['driver_name'] or '—',
            'phone': info['driver_phone'] or '—',
            'departures': info['departures'],
            'total': info['capacity'],
            'booked': booked,
            'status': status,
            'dot': dot,
        })
    return render(request, 'transport.html', {'routes': routes})


def meal_dashboard(request):
    """Online meal ticket system — frontend-only page driven by mock JS data."""
    return render(request, 'meals.html')


# Wallet number + TrxID validation rules for the checkout form.
_WALLET_RE = re.compile(r'^01\d{9}$')
_TRX_RE = re.compile(r'^[A-Za-z0-9-]{6,}$')

# Checkout ``type`` query values → PaymentTransaction.purpose codes.
_CHECKOUT_PURPOSES = {
    'meal': 'meal',
    'tuition': 'tuition',
    'event': 'event',
    'transport': 'transport',
}


def _generate_transaction_id():
    """Return an unused platform transaction reference, e.g. ``NTR-4F2A1C``."""
    for _ in range(50):
        txn_id = 'NTR-' + secrets.token_hex(3).upper()
        if not PaymentTransaction.objects.filter(transaction_id=txn_id).exists():
            return txn_id
    raise RuntimeError('Could not allocate a unique transaction id')


def checkout_page(request):
    """Secure Checkout — renders the payment page (GET) or records a payment
    (POST).

    GET stays public so the order summary can be previewed before signing in;
    POST requires authentication and persists a ``PaymentTransaction`` with a
    freshly generated unique ``transaction_id``. Paid items are linked: a
    meal purpose activates the user's ``MealSubscription`` entitlement.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL + '?next=' + reverse('checkout'))
        return _process_checkout(request)

    return render(request, 'checkout.html')


def _process_checkout(request):
    """Validate wallet payment details, persist a PaymentTransaction, and link
    the paid item (meal → active MealSubscription)."""
    checkout_type = request.POST.get('type', '').strip().lower()
    purpose = _CHECKOUT_PURPOSES.get(checkout_type, 'event')
    description = request.POST.get('item', '').strip()

    fee_raw = request.POST.get('fee', '').strip()
    try:
        amount = Decimal(fee_raw)
    except (InvalidOperation, TypeError, ValueError):
        return JsonResponse(
            {'status': 'error', 'message': 'A valid amount is required.'},
            status=400,
        )
    if not amount.is_finite() or amount < 0:
        # Guards NaN / Infinity amounts that would otherwise corrupt the row
        # (or raise on stricter backends) and negative fees.
        return JsonResponse(
            {'status': 'error', 'message': 'A valid positive amount is required.'},
            status=400,
        )
    if amount > 99999999:
        return JsonResponse(
            {'status': 'error', 'message': 'Amount is too large.'},
            status=400,
        )

    method_raw = request.POST.get('method', '').strip().lower()
    valid_methods = {code for code, _label in PaymentTransaction.METHOD_CHOICES}
    if method_raw not in valid_methods:
        return JsonResponse(
            {'status': 'error', 'message': 'Please choose a valid payment method.'},
            status=400,
        )

    wallet_no = request.POST.get('wallet_no', '').strip()
    if not _WALLET_RE.fullmatch(wallet_no):
        return JsonResponse(
            {'status': 'error', 'message': 'Please enter a valid 11-digit wallet number (e.g. 017XXXXXXXX).'},
            status=400,
        )

    wallet_trx = request.POST.get('trx_id', '').strip()
    if not _TRX_RE.fullmatch(wallet_trx):
        return JsonResponse(
            {'status': 'error', 'message': 'Please enter the TrxID shown in your payment confirmation.'},
            status=400,
        )

    transaction_id = _generate_transaction_id()
    payment = PaymentTransaction.objects.create(
        user=request.user,
        amount=amount,
        payment_method=method_raw,
        transaction_id=transaction_id,
        purpose=purpose,
        description=description or 'Checkout order',
        wallet_trx=wallet_trx,
    )

    linked = None
    if purpose == 'meal':
        # The paid item is the monthly meal entitlement — activate it now.
        subscription, _ = MealSubscription.objects.update_or_create(
            user=request.user,
            defaults={'is_active': True, 'expires_at': timezone.now() + timedelta(days=30)},
        )
        linked = 'meal_subscription' if subscription.is_active else None

    bell_category = {'meal': 'meal', 'event': 'club', 'transport': 'transport', 'tuition': 'academic'}[purpose]
    notification = Notification.objects.create(
        user=request.user,
        title='Payment recorded',
        message='%s (%s) for %s is pending verification.' % (
            transaction_id, payment.get_payment_method_display(), payment.get_purpose_display(),
        ),
        category=bell_category,
    )
    _broadcast_notification(notification)

    return JsonResponse({
        'status': 'success',
        'transaction_id': payment.transaction_id,
        'amount': str(payment.amount),
        'payment_method': payment.get_payment_method_display(),
        'purpose': payment.get_purpose_display(),
        'payment_status': payment.status,
        'linked': linked,
        'message': 'Payment recorded — reference %s.' % payment.transaction_id,
    })


def research_ai_page(request):
    """Academic Research & Thesis Assistant — frontend-only page driven by
    mock JS data (canned assistant responses, no backend/AI calls).
    """
    return render(request, 'research_ai.html')


# Campus week order used to lay out the Class & Lab schedule tab (Sun → Thu
# are the working days, Friday is the weekly holiday).
_WEEKDAY_ORDER = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Sat', 'Fri']


def departments_directory(request):
    """Department Directory — every ``Department`` row from the database.

    Showcase cards carry live student counts (``StudentProfile`` by
    department code) and material counts (``CourseMaterial`` per course
    department), aggregated in two grouped queries so there is no N+1.
    """
    departments = Department.objects.order_by('name')

    student_counts = dict(
        StudentProfile.objects.values_list('department')
        .annotate(count=Count('id'))
    )
    material_counts = dict(
        CourseMaterial.objects.values('course__department')
        .annotate(count=Count('id'))
        .values_list('course__department', 'count')
    )
    rows = []
    for dept in departments:
        rows.append({
            'dept': dept,
            'students': student_counts.get(dept.code, 0),
            'notes': material_counts.get(dept.code, 0),
            'icon': _DEPARTMENT_ICONS.get(dept.code, 'fa-landmark'),
        })

    return render(request, 'departments.html', {
        'departments': rows,
    })


def department_detail(request, dept_slug):
    """Single Department Hub — live faculty, class routine, materials drive,
    and published academic notices, all keyed to a real ``Department`` row.

    Unknown slugs 404 (there is no client-side fallback any more).
    """
    dept = get_object_or_404(Department, slug=dept_slug)

    student_count = StudentProfile.objects.filter(department=dept.code).count()
    material_count = CourseMaterial.objects.filter(course__department=dept.code).count()
    faculty = dept.faculty.all()

    # Routines grouped by weekday in campus order.
    by_day = {}
    for routine in dept.class_routines.all():
        by_day.setdefault(routine.day_of_week, []).append(routine)
    routine_days = [
        {
            'day_code': day,
            'day_label': dict(ClassRoutine.DAY_CHOICES).get(day, day),
            'periods': by_day[day],
        }
        for day in _WEEKDAY_ORDER
        if day in by_day
    ]

    # Notes drive grouped by course semester (first-seen order).
    materials = CourseMaterial.objects.filter(
        course__department=dept.code,
    ).select_related('course').order_by('course__code', '-uploaded_at')
    semesters = []
    semester_index = {}
    for material in materials:
        sem = material.course.semester or 'General'
        if sem not in semester_index:
            semester_index[sem] = len(semesters)
            semesters.append({'name': sem, 'materials': []})
        semesters[semester_index[sem]]['materials'].append(material)

    # Department announcements: published academic notices (a department-scoped
    # notices feed would need a Notice.department FK — filtered by category for
    # now so hubs surface real, published content).
    announcements = Notice.objects.filter(
        is_published=True, category='academic',
    ).select_related('author')[:6]

    return render(request, 'department_detail.html', {
        'dept': dept,
        'icon': _DEPARTMENT_ICONS.get(dept.code, 'fa-landmark'),
        'students': student_count,
        'notes_count': material_count,
        'faculty': faculty,
        'routine_days': routine_days,
        'semesters': semesters,
        'announcements': announcements,
    })


# ============================================================================
# Campus services — production action handlers (atomic)
# ============================================================================

# Daily claim caps per meal type (mirrors the cafeteria admin capacities).
DAILY_MEAL_CAPACITY = {
    'breakfast': 80,
    'lunch': 200,
    'dinner': 160,
}

# Transport route catalog — fallback when no DB routes exist yet. The DB is
# the source of truth (TransportRoute + BusSchedule + Driver, seeded in
# migration 0013 with these exact names/times); the constant keeps legacy
# route ids and fresh-DB-less environments working.
TRANSPORT_ROUTES = {
    '1': {'route_name': 'Route 1: Main Campus Loop', 'departure_time': '08:00 AM'},
    '2': {'route_name': 'Route 2: Sports Complex Shuttle', 'departure_time': '09:30 AM'},
    '3': {'route_name': 'Route 3: City Center Express', 'departure_time': '10:00 AM'},
}

# Seat capacity per bus — used only by the legacy fallback catalog.
TRANSPORT_SEATS_PER_BUS = 40


def _transport_catalog():
    """Active DB routes merged with driver + schedule data, keyed by route id.

    Falls back to the legacy ``TRANSPORT_ROUTES`` constants when no DB routes
    exist (e.g. a checkout that hasn't run the 0013 seed migration) so
    historical route ids/names and older forms keep resolving.
    """
    catalog = {}
    for route in (
        TransportRoute.objects.filter(is_active=True)
        .select_related('driver')
        .prefetch_related('schedules')
    ):
        departures = [
            s.departure_time
            for s in route.schedules.filter(is_active=True).order_by('id')
        ]
        if not departures:
            continue
        catalog[route.pk] = {
            'route_name': route.name,
            'departures': departures,
            'departure_time': departures[0],
            'capacity': route.capacity,
            'origin': route.origin,
            'destination': route.destination,
            'driver_name': route.driver.name if route.driver else '',
            'driver_phone': route.driver.phone if route.driver else '',
        }
    if catalog:
        return catalog
    return {
        int(route_id): {
            'route_name': info['route_name'],
            'departures': [info['departure_time']],
            'departure_time': info['departure_time'],
            'capacity': TRANSPORT_SEATS_PER_BUS,
            'origin': '',
            'destination': '',
            'driver_name': '',
            'driver_phone': '',
        }
        for route_id, info in TRANSPORT_ROUTES.items()
    }

# Medical doctor catalog — the booking page posts a ``doctor`` id.
DOCTORS = {
    '1': 'Dr. Ahmed Khan',
    '2': 'Dr. Sarah Smith',
    '3': 'Dr. Michael Chen',
    '4': 'Dr. Emily Johnson',
}

# Presentation-only metadata for the dashboard's medical widget.
DOCTOR_SPECIALTIES = {
    'Dr. Ahmed Khan': 'General Physician',
    'Dr. Sarah Smith': 'General Physician',
    'Dr. Michael Chen': 'Specialist',
    'Dr. Emily Johnson': 'Specialist',
}

# Bookable appointment slots per doctor per day (dashboard availability math).
MEDICAL_SLOTS_PER_DAY = 4


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

    # Resolve route_id through the DB-backed catalog (legacy ids also resolve
    # via the constant fallback). Explicit route_name/departure_time (if both
    # sent) take precedence over the catalog values.
    route_info = None
    if route_id:
        try:
            route_info = _transport_catalog().get(int(route_id))
        except (TypeError, ValueError):
            route_info = None
    if route_info is not None:
        route_name = route_name or route_info['route_name']
        departure_time = departure_time or route_info['departure_time']
        capacity = route_info['capacity']
    else:
        # route_name-only submissions still honour the DB route's capacity.
        capacity = (
            TransportRoute.objects.filter(name=route_name, is_active=True)
            .values_list('capacity', flat=True)
            .first()
        ) or TRANSPORT_SEATS_PER_BUS

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
    if not 1 <= seat_number <= capacity:
        return JsonResponse(
            {'status': 'error', 'message': 'Seat number must be between 1 and %s.' % capacity},
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
    """Self-registration — ``SignUpForm`` validates the fields (duplicate
    Student ID / email, password confirmation), creates the User + StudentProfile
    with a securely hashed password, and signs the student in. Departments come
    from the StudentProfile choices so the dropdown and stored value can never
    drift apart.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()

    # Flatten form errors into the simple list the signup template renders.
    errors = []
    for field_errors in form.errors.values():
        errors.extend(field_errors)

    return render(request, 'signup.html', {
        'errors': errors,
        'departments': StudentProfile.DEPARTMENT_CHOICES,
        'form_data': request.POST if request.method == 'POST' else None,
    })


@login_required
def settings_view(request):
    """Account settings — tabbed dashboard: notification preferences, account
    (profile + password + Google OAuth integration), and display (theme +
    timezone + layout).

    POST requests are disambiguated by payload: a hidden ``form=profile``
    marker means the profile form, ``old_password`` means the password form,
    and anything else means preference toggles (form-encoded or JSON).
    """
    prefs, _ = UserNotificationPreference.objects.get_or_create(user=request.user)
    profile = getattr(request.user, 'student_profile', None)

    # Google OAuth connection status (allauth SocialAccount + GoogleUserToken).
    google_social = _get_google_social_account(request.user)
    has_google_token = hasattr(request.user, 'google_token') and bool(
        request.user.google_token.access_token
    )
    # Google Drive access status for the Account & Google tab (no network call).
    has_drive_access = user_has_drive_access(request.user)

    password_updated = False
    profile_updated = False
    profile_errors = []
    active_tab = 'notifications'
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if request.POST.get('form') == 'profile':
            # Account & Google tab → Profile Details form (full name + email).
            active_tab = 'account'
            profile_updated, profile_errors = _save_profile_settings(request)
        elif 'old_password' in request.POST:
            active_tab = 'account'
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                password_updated = True
                password_form = PasswordChangeForm(request.user)
        else:
            # Preference toggles (form-encoded or JSON) — answered directly.
            return _save_settings_prefs(request, prefs)
    else:
        active_tab = request.GET.get('tab', 'notifications')

    return render(request, 'settings.html', {
        'password_form': password_form,
        'password_updated': password_updated,
        'profile': profile,
        'profile_updated': profile_updated,
        'profile_errors': profile_errors,
        'prefs': prefs,
        'google_social': google_social,
        'has_google_token': has_google_token,
        'has_drive_access': has_drive_access,
        'active_tab': active_tab,
    })


def _save_profile_settings(request):
    """Update the signed-in user's full name and email (Profile Details).

    The Student ID is an institutional identity and is deliberately read-only
    here. Returns ``(saved, errors)`` where ``errors`` is a list of
    human-readable validation messages (empty when the save succeeded).
    """
    errors = []
    full_name = (request.POST.get('full_name') or '').strip()
    email = (request.POST.get('email') or '').strip()

    if not full_name:
        errors.append('Full name is required.')
    if not email:
        errors.append('An email address is required.')
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors.append('Please enter a valid email address.')
        else:
            duplicate = (
                User.objects.filter(email__iexact=email)
                .exclude(pk=request.user.pk)
                .exists()
            )
            if duplicate:
                errors.append('That email address is already used by another account.')

    if errors:
        return False, errors

    parts = full_name.split(None, 1)
    request.user.first_name = parts[0] if parts else ''
    request.user.last_name = parts[1] if len(parts) > 1 else ''
    request.user.email = email
    request.user.save(update_fields=['first_name', 'last_name', 'email'])
    return True, []


def _get_google_social_account(user):
    """Return the user's ``SocialAccount`` for Google, or None."""
    try:
        from allauth.socialaccount.models import SocialAccount
        return SocialAccount.objects.filter(user=user, provider='google').first()
    except Exception:
        return None


def _save_settings_prefs(request, prefs):
    """Persist preference toggles (form-encoded or JSON) and answer accordingly.

    Only fields explicitly present in the payload are updated — missing booleans
    keep their existing value so a partial toggle update never resets other
    prefs to their defaults.
    """
    data = request.POST
    if request.content_type == 'application/json':
        parsed, error = _parse_json_body(request)
        if error is not None:
            return error
        data = parsed

    # Checkbox semantics: present + truthy → True, everything else → False.
    # Returns None when the key is missing (caller decides to skip).
    def enabled(*keys):
        for key in keys:
            if key in data:
                value = data[key]
                if value in (True, 'true', 'on', '1', 1):
                    return True
                return False
        return None

    # Map request keys → preference attribute names.
    _BOOL_MAP = [
        ('email_alerts', 'email_alerts'), ('email', 'email_alerts'),
        ('sms_alerts', 'sms_alerts'), ('sms', 'sms_alerts'),
        ('push_notifications', 'push_notifications'), ('push', 'push_notifications'),
        ('dark_mode', 'dark_mode'),
        ('compact_layout', 'compact_layout'),
        ('notify_meals', 'notify_meals'),
        ('notify_transport', 'notify_transport'),
        ('notify_medical', 'notify_medical'),
        ('notify_notices', 'notify_notices'),
    ]
    for key, attr in _BOOL_MAP:
        val = enabled(key)
        if val is not None:
            setattr(prefs, attr, val)

    # Theme (tri-state light/dark/system) — takes precedence over the legacy
    # ``dark_mode`` key and keeps ``dark_mode`` in sync so older callers that
    # read the boolean stay correct.
    if 'theme' in data:
        theme = str(data['theme']).strip()
        valid_themes = {code for code, _label in UserNotificationPreference.THEME_CHOICES}
        if theme in valid_themes:
            prefs.theme = theme
            prefs.dark_mode = theme == 'dark'
    elif 'dark_mode' in data:
        dark = enabled('dark_mode')
        if dark is not None:
            prefs.dark_mode = dark
            prefs.theme = 'dark' if dark else 'light'

    # Timezone — only accept values from the model choices.
    if 'timezone' in data:
        tz = data['timezone'].strip()
        valid_tzs = {code for code, _label in UserNotificationPreference.TIMEZONE_CHOICES}
        if tz in valid_tzs:
            prefs.timezone = tz

    prefs.save()

    if request.content_type == 'application/json' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'email_alerts': prefs.email_alerts,
            'sms_alerts': prefs.sms_alerts,
            'push_notifications': prefs.push_notifications,
            'dark_mode': prefs.dark_mode,
            'theme': prefs.theme,
            'compact_layout': prefs.compact_layout,
            'notify_meals': prefs.notify_meals,
            'notify_transport': prefs.notify_transport,
            'notify_medical': prefs.notify_medical,
            'notify_notices': prefs.notify_notices,
            'timezone': prefs.timezone,
        })
    messages.success(request, 'Preferences saved.')
    return redirect('settings')


@login_required
def profile_view(request):
    """Virtual student ID card + live booking & activity history.

    Appointments, transport bookings, and meal coupons all come from the real
    per-user rows in ``MedicalAppointment`` / ``TransportBooking`` /
    ``MealTicket`` — no mock data.
    """
    profile = getattr(request.user, 'student_profile', None)

    return render(request, 'profile.html', {
        'profile': profile,
        'appointments': request.user.medical_appointments.all(),
        'transport_tickets': request.user.transport_bookings.all(),
        'meal_coupons': request.user.meal_tickets.all(),
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

    # Live notices & materials (created via the publisher form or /admin).
    notices = [
        {
            'title': notice.title,
            'category': notice.get_category_display(),
            'status': 'Published' if notice.is_published else 'Draft',
            'date': notice.created_at.strftime('%Y-%m-%d'),
        }
        for notice in Notice.objects.select_related('author').order_by('-created_at')
    ]
    materials = [
        {
            'course': material.course.code,
            'title': material.title,
            'type': material.display_type,
            'size': material.size_display,
            'date': material.uploaded_at.strftime('%Y-%m-%d'),
        }
        for material in CourseMaterial.objects.select_related('course').order_by('-uploaded_at')
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

    # Notify every active staff member so the host/admin queue widgets refresh
    # in real time (their WebSocket bell pushes the update without a reload).
    for staff_user in User.objects.filter(is_staff=True, is_active=True).exclude(pk=request.user.pk):
        staff_notice = Notification.objects.create(
            user=staff_user,
            title='Medical queue updated',
            message='%s · %s with %s is now %s.' % (
                appointment.user.get_full_name() or appointment.user.username,
                appointment.appointment_date,
                appointment.doctor_name,
                label,
            ),
            category='medical',
        )
        _broadcast_notification(staff_notice)

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


# ============================================================================
# Medical consultation chat + live queue (patient ↔ doctor, real-time)
# ============================================================================

def _chat_thread_serialize(thread, viewer):
    """Shape a MedicalChatThread for the chat lists/APIs.

    The unread count is viewer-scoped: messages the viewer sent are never
    counted against them. Uses the prefetched ``messages`` cache in one pass —
    ``order_by().first()`` / ``count()`` would each issue a new query per
    thread (N+1) instead of reading the prefetch cache.
    """
    messages = list(thread.messages.all())
    last = messages[-1] if messages else None
    unread = sum(1 for m in messages if not m.is_read and m.sender_id != viewer.pk)
    profile = getattr(thread.patient, 'student_profile', None)
    return {
        'id': thread.pk,
        'appointment_id': thread.appointment_id,
        'patient_name': thread.patient.get_full_name() or thread.patient.username,
        'patient_id': getattr(profile, 'student_id', thread.patient.username),
        'doctor_name': thread.doctor_name,
        'status': thread.status,
        'status_label': thread.get_status_display(),
        'unread': unread,
        'last_message': last.content if last else '',
        'last_time': last.created_at.strftime('%I:%M %p') if last else '',
        'updated_at': thread.updated_at.strftime('%Y-%m-%d %H:%M'),
    }


@login_required
def medical_chat_threads(request):
    """JSON API: consultation threads visible to the caller.

    Staff see every thread (newest activity first); students see only their
    own. Each row carries a viewer-scoped unread count and the last message.
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'GET required'}, status=405)
    threads = MedicalChatThread.objects.select_related('patient', 'appointment')
    if not request.user.is_staff:
        threads = threads.filter(patient=request.user)
    threads = threads.prefetch_related('messages').order_by('-updated_at', '-id')
    return JsonResponse({
        'status': 'success',
        'threads': [_chat_thread_serialize(t, request.user) for t in threads],
    })


@login_required
def medical_chat_start(request):
    """JSON API: open a consultation thread for an appointment (get-or-create).

    The patient may open their own thread; staff may open any thread. Calling
    again simply returns the existing thread (idempotent).
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        appointment = MedicalAppointment.objects.select_related('user').get(
            pk=request.POST.get('appointment_id', ''),
        )
    except (MedicalAppointment.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Appointment not found.'}, status=404)
    if not (request.user.is_staff or appointment.user_id == request.user.pk):
        return JsonResponse({'status': 'error', 'message': 'Not your appointment.'}, status=403)

    thread, created = MedicalChatThread.objects.get_or_create(
        appointment=appointment,
        defaults={'patient': appointment.user, 'doctor_name': appointment.doctor_name},
    )
    return JsonResponse({
        'status': 'success',
        'created': created,
        'thread': _chat_thread_serialize(thread, request.user),
    })


def _thread_for_user(thread_id, user):
    """Fetch a thread the user may view (patient owner or staff), else None."""
    try:
        thread = MedicalChatThread.objects.select_related('patient').get(pk=thread_id)
    except (MedicalChatThread.DoesNotExist, ValueError, TypeError):
        return None
    if not (user.is_staff or thread.patient_id == user.pk):
        return None
    return thread


def _chat_message_payload(message):
    """Serialize one message row for the chat APIs / WS pushes.

    ``is_mine`` is intentionally omitted — clients compare ``sender_id`` with
    their own viewer id so the same payload serves every recipient.
    """
    return {
        'id': message.pk,
        'sender_id': message.sender_id,
        'sender_name': message.sender.get_full_name() or message.sender.username,
        'content': message.content,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
    }


@login_required
def medical_chat_messages(request, thread_id):
    """JSON API: message history (GET) or append a message (POST) to a thread.

    GET marks the other party's messages as read. POST is the non-WebSocket
    fallback for sending — the UI normally sends over ``ws/medical-chat/``,
    but the payload is broadcast to the thread's channel group either way.
    """
    thread = _thread_for_user(thread_id, request.user)
    if thread is None:
        return JsonResponse({'status': 'error', 'message': 'Thread not found.'}, status=404)

    if request.method == 'GET':
        thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        messages = list(
            thread.messages.select_related('sender').order_by('created_at', 'id')
        )
        return JsonResponse({
            'status': 'success',
            'thread_id': thread.pk,
            'messages': [_chat_message_payload(m) for m in messages],
        })

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse(
                {'status': 'error', 'message': 'Message content is required.'},
                status=400,
            )
        message = MedicalChatMessage.objects.create(
            thread=thread, sender=request.user, content=content,
        )
        MedicalChatThread.objects.filter(pk=thread.pk).update(updated_at=timezone.now())
        payload = _chat_message_payload(message)
        send_chat_push(thread.pk, payload)
        return JsonResponse({'status': 'success', 'message': payload})

    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)


@staff_member_required(login_url=settings.LOGIN_URL)
def medical_queue_api(request):
    """JSON API: today's appointment queue (pending → confirmed, FIFO).

    Powers the live queue widget on the host dashboard. Every status change
    also pushes a real-time Notification to staff (see
    ``update_appointment_status``), so the queue refreshes without a reload.
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'GET required'}, status=405)

    today = timezone.now().date()
    queue = list(
        MedicalAppointment.objects.filter(
            appointment_date=today, status__in=['pending', 'confirmed'],
        ).select_related('user').order_by('created_at', 'id')
    )
    items = []
    for position, appointment in enumerate(queue, start=1):
        profile = getattr(appointment.user, 'student_profile', None)
        items.append({
            'position': position,
            'id': appointment.pk,
            'student_name': appointment.user.get_full_name() or appointment.user.username,
            'student_id': getattr(profile, 'student_id', appointment.user.username),
            'doctor': appointment.doctor_name,
            'time': appointment.time_slot,
            'status': appointment.status,
            'status_label': appointment.get_status_display(),
            'booking_time': appointment.created_at.strftime('%I:%M %p'),
        })
    return JsonResponse({
        'status': 'success',
        'today': today.isoformat(),
        'queue': items,
        'counts': {
            'waiting': sum(1 for i in items if i['status'] == 'pending'),
            'in_consultation': sum(1 for i in items if i['status'] == 'confirmed'),
            'total': len(items),
        },
    })


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
def create_notice(request):
    """Persist a new official ``Notice`` and notify every student in real time.

    Accepts ``title``, ``content``, ``category`` (urgent / academic / event /
    general) and ``status`` (published / draft). Draft notices are stored but
    never broadcast; publishing creates a ``Notification`` for every active
    user and pushes it over their WebSocket group via ``notify_user``.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    category = request.POST.get('category', '').strip().lower()
    status = request.POST.get('status', '').strip().lower()

    if not title:
        return JsonResponse({'status': 'error', 'message': 'Notice title is required.'}, status=400)
    if not content:
        return JsonResponse({'status': 'error', 'message': 'Notice content is required.'}, status=400)
    valid_categories = {code for code, _label in Notice.CATEGORY_CHOICES}
    if category not in valid_categories:
        return JsonResponse({'status': 'error', 'message': 'Invalid notice category.'}, status=400)
    if status not in ('published', 'draft'):
        return JsonResponse({'status': 'error', 'message': 'Invalid notice status.'}, status=400)

    is_published = status == 'published'
    notice = Notice.objects.create(
        title=title,
        content=content,
        category=category,
        is_published=is_published,
        author=request.user,
    )

    notified = 0
    if is_published:
        # Map Notice categories onto the Notification bell categories.
        bell_category = {
            'urgent': 'urgent',
            'academic': 'academic',
            'event': 'club',
            'general': 'academic',
        }[notice.category]
        for student in User.objects.filter(is_active=True):
            notification = Notification.objects.create(
                user=student,
                title='New notice: %s' % notice.title,
                message='%s — %s' % (notice.get_category_display(), notice.title),
                category=bell_category,
            )
            _broadcast_notification(notification)
            notified += 1

    return JsonResponse({
        'status': 'success',
        'notice_id': notice.pk,
        'title': notice.title,
        'category': notice.get_category_display(),
        'is_published': notice.is_published,
        'notified': notified,
        'created_at': notice.created_at.strftime('%Y-%m-%d'),
        'message': 'Notice %s.' % ('published' if is_published else 'saved as draft'),
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
# Notes Engine — server-side actions (save / summarize / keywords / export)
# ============================================================================

# Lightweight English stopword list for the keyword + summary extractors.
_STOPWORDS = frozenset(
    ("the a an and or but if then else for with without of on in at by from to "
     "is are was were be been being have has had do does did will would can could "
     "should may might must this that these those it its i you he she we they them "
     "my your our their his her not no nor so as about into over under again further "
     "once here there when where why how all any both each few more most other some "
     "such only own same too very just also than up down out off because while "
     "during before after above below between through during against per via "
     "us am etc e g ie vs").split()
)


def _note_tokens(text):
    """Lowercased alphanumeric tokens minus stopwords (min length 3)."""
    words = re.findall(r'[a-z0-9]+', (text or '').lower())
    return [w for w in words if w not in _STOPWORDS and len(w) >= 3]


def _extract_keywords(content, limit=8):
    """Top ``limit`` keywords by term frequency (deterministic server-side)."""
    tokens = _note_tokens(content)
    ranked = Counter(tokens).most_common()
    return [word for word, _count in ranked[:limit]]


def _extract_summary(content, max_sentences=3):
    """Extractive summarization — score sentences by term frequency, keep the
    highest-scoring sentences in their original order."""
    text = (content or '').strip()
    if not text:
        return ''
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text) if s.strip()]
    if len(sentences) <= max_sentences:
        return text

    freq = Counter(_note_tokens(text))

    def score(sentence):
        tokens = _note_tokens(sentence)
        if not tokens:
            return 0.0
        # Sum of term frequencies, dampened by length to favour dense sentences.
        return sum(freq.get(t, 0) for t in tokens) / (len(tokens) ** 0.6)

    scored = sorted(range(len(sentences)), key=lambda i: score(sentences[i]), reverse=True)
    picked = sorted(scored[:max_sentences])
    return ' '.join(sentences[i] for i in picked)


def _pdf_escape(text):
    """Escape a PDF literal string and drop characters outside latin-1."""
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def _note_pdf_bytes(title, content):
    """Build a dependency-free multi-page PDF (Helvetica) for a note.

    Long lines are wrapped at ~95 chars and lines are chunked into 42-line
    pages so arbitrarily long notes export cleanly. Non-ASCII glyphs outside
    latin-1 are replaced with ``?`` (the text export preserves them fully).
    """
    raw_lines = (title or 'Untitled Note').split('\n') + ['', ''] + (content or '').replace('\r\n', '\n').split('\n')
    wrapped = []
    for line in raw_lines:
        while len(line) > 95:
            wrapped.append(line[:95])
            line = line[95:]
        wrapped.append(line)
    pages = [wrapped[i:i + 42] for i in range(0, len(wrapped), 42)] or [['']]

    def content_stream(lines):
        out = ['BT /F1 11 Tf 50 750 Td 14 TL']
        for line in lines:
            out.append('(%s) Tj T*' % _pdf_escape(line))
        out.append('ET')
        stream = '\n'.join(out).encode('latin-1', 'replace')
        return b'<< /Length %d >>\nstream\n' % len(stream) + stream + b'\nendstream'

    font_index = 3 + 2 * len(pages)
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        ('<< /Type /Pages /Kids [%s] /Count %d >>' % (
            ' '.join('%d 0 R' % (3 + 2 * i) for i in range(len(pages))),
            len(pages),
        )).encode('latin-1'),
    ]
    for page_index, page_lines in enumerate(pages):
        page_num = 3 + 2 * page_index
        objects.append((
            '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
            '/Resources << /Font << /F1 %d 0 R >> >> /Contents %d 0 R >>'
            % (font_index, page_num + 1)
        ).encode('latin-1'))
        objects.append(content_stream(page_lines))
    objects.append(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')

    body = bytearray()
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body += b'%d 0 obj\n' % number + obj + b'\nendobj\n'

    xref_pos = len(body)
    body += b'xref\n0 %d\n' % (len(objects) + 1)
    body += b'0000000000 65535 f \n'
    for offset in offsets:
        body += b'%010d 00000 n \n' % offset
    body += b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (
        len(objects) + 1, xref_pos,
    )
    return b'%PDF-1.4\n' + bytes(body)


def google_unlink(request):
    """Disconnect the signed-in user's Google account (Drive/sheets backends).

    Deletes both the allauth ``SocialAccount`` row (so the Google OAuth
    connection is gone) and the stored ``GoogleUserToken`` credentials. Used by
    the Settings → Account tab's "Unlink Google Account" action. Always
    answers JSON — this endpoint is consumed via fetch from the settings page.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)

    try:
        from allauth.socialaccount.models import SocialAccount
        SocialAccount.objects.filter(user=request.user, provider='google').delete()
    except Exception:
        pass
    GoogleUserToken.objects.filter(user=request.user).delete()

    return JsonResponse({'status': 'success'})


# Timestamp format shared by the notes fetch/save API responses.
_NOTE_TIME_FORMAT = '%Y-%m-%d %H:%M'


@login_required
def get_note(request, note_id):
    """Fetch one saved UserNote for the editor sidebar (owner-scoped).

    The My Notes list only carries the note id/title in the markup; the full
    content is fetched here so large notes never bloat the page HTML.
    """
    note = get_object_or_404(request.user.notes, pk=note_id)
    return JsonResponse({
        'status': 'success',
        'note_id': note.pk,
        'title': note.title,
        'content': note.content,
        'updated_at': note.updated_at.strftime(_NOTE_TIME_FORMAT),
    })


@login_required
def save_note(request):
    """Persist the Notes Engine editor contents as a UserNote.

    Accepts ``title`` and ``content`` (and optional ``note_id`` to update an
    existing note); answers the saved note's id + updated timestamp.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    title = request.POST.get('title', '').strip() or 'Untitled Note'
    content = request.POST.get('content', '')
    if len(title) > 200:
        title = title[:200]

    note_id = request.POST.get('note_id', '').strip()
    if note_id:
        note = get_object_or_404(request.user.notes, pk=note_id)
        note.title = title
        note.content = content
        note.save(update_fields=['title', 'content', 'updated_at'])
    else:
        note = UserNote.objects.create(user=request.user, title=title, content=content)

    return JsonResponse({
        'status': 'success',
        'note_id': note.pk,
        'title': note.title,
        'updated_at': note.updated_at.strftime(_NOTE_TIME_FORMAT),
    })


@login_required
def note_summary(request):
    """Auto-summarize note content server-side (extractive)."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    content = request.POST.get('content', '')
    summary = _extract_summary(content)
    return JsonResponse({
        'status': 'success',
        'summary': summary,
        'sentence_count': len([s for s in re.split(r'(?<=[.!?])\s+|\n+', content.strip()) if s.strip()]),
    })


@login_required
def note_keywords(request):
    """Extract the top keywords from note content server-side (TF ranking)."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    content = request.POST.get('content', '')
    keywords = _extract_keywords(content)
    return JsonResponse({'status': 'success', 'keywords': keywords})


@login_required
def export_note(request):
    """Download a note as text or PDF (``?format=text|pdf``).

    Accepts a saved ``note_id`` or inline ``title``/``content`` so the export
    action works straight from the editor before the note is saved.
    """
    note = None
    note_id = (request.GET.get('note_id') or request.POST.get('note_id') or '').strip()
    if note_id:
        note = get_object_or_404(request.user.notes, pk=note_id)
        title = note.title
        content = note.content
    else:
        title = request.GET.get('title', '') or request.POST.get('title', '') or 'Untitled Note'
        content = request.GET.get('content', '') or request.POST.get('content', '') or ''

    export_format = (request.GET.get('format') or request.POST.get('format') or 'text').strip().lower()
    safe_name = re.sub(r'[^A-Za-z0-9._-]+', '_', title)[:60] or 'note'

    if export_format == 'pdf':
        payload = _note_pdf_bytes(title, content)
        return HttpResponse(
            payload,
            content_type='application/pdf',
            headers={'Content-Disposition': 'attachment; filename="%s.pdf"' % safe_name},
        )

    return HttpResponse(
        '%s\n\n%s' % (title, content),
        content_type='text/plain; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename="%s.txt"' % safe_name},
    )


# ============================================================================
# Research AI — server-side structured query endpoint
# ============================================================================

# Canned-but-server-side assistant knowledge base, routed by prompt keywords.
_RESEARCH_RESPONSES = {
    'literature': (
        '## Literature Review Draft — IoT in Textile Manufacturing\n\n'
        '### 1. Industry context\n\n'
        'The textile sector is adopting **Industrial IoT (IIoT)** to digitize loom '
        'monitoring, quality inspection, and predictive maintenance. Recent surveys '
        'report that smart factories cut unplanned downtime by up to **30–40%** '
        'through real-time sensor telemetry.\n\n'
        '### 2. Key research themes\n\n'
        '- **Loom condition monitoring** — vibration and temperature sensors feed edge gateways.\n'
        '- **Predictive maintenance** — machine-learning classifiers on spindle sensor data.\n'
        '- **Quality inspection** — computer-vision pipelines grade fabric defects at line speed.\n\n'
        '### 3. Gap your thesis can address\n\n'
        'Most published work assumes centralized cloud processing; fewer studies evaluate '
        '**on-device inference latency** for low-power textile microcontrollers. '
        'Positioning your work against this gap strengthens the contribution statement.'
    ),
    'methodology': (
        '## Methodology Breakdown\n\n'
        'Your paper’s methodology can be restructured into four reproducible steps:\n\n'
        '### Step 1 — Data acquisition\n'
        '- Describe the sensor set, sampling frequency, and placement on the test rig.\n'
        '- State how many trials were recorded and any exclusion criteria.\n\n'
        '### Step 2 — Preprocessing\n'
        '- Apply a **moving-average filter** to remove electrical noise.\n'
        '- Normalize each channel to zero mean and unit variance.\n\n'
        '### Step 3 — Model development\n'
        '- Split data 70/20/10 into train, validation, and test sets.\n'
        '- Train a baseline (logistic regression) and your proposed model for comparison.\n\n'
        '### Step 4 — Evaluation\n'
        '- Report precision, recall, F1, and confusion matrices.\n'
        '- Include a runtime benchmark table for deployment feasibility.'
    ),
    'citation': (
        '## Citation Formatting Check\n\n'
        'I checked the excerpt against the selected citation style. Key fixes:\n\n'
        '- Author initials come **before** the surname (e.g. `M. H. Rahman`).\n'
        '- Journal names are **italicized**; article titles stay in sentence case.\n'
        '- Page ranges use an en dash (`44210–44222`), not a hyphen.\n\n'
        '### In-text checklist\n\n'
        '- Place the bracketed number before the period: `... textile industry [1].`\n'
        '- For three or more authors, use `et al.`\n'
        '- Number references in the order they first appear.'
    ),
    'summary': (
        '## Abstract Summary\n\n'
        '### Core contribution\n'
        'The work proposes a **low-cost IoT monitoring layer** for textile looms that '
        'streams vibration and current data to an on-premise edge server.\n\n'
        '### Main results\n\n'
        '- Detection of yarn-break events within **2.1 s** on average.\n'
        '- **94% F1** on the fault-classification task.\n'
        '- Deployment cost estimated at under **৳18,000 per loom bank**.\n\n'
        'Paste the full abstract if you want a one-paragraph version for your introduction.'
    ),
    'superposition': (
        '## Superposition Circuit Analysis\n\n'
        'Apply the superposition theorem to the multi-source circuit:\n\n'
        '### Procedure\n\n'
        '- **Zero all but one source** at a time (voltage sources → short, current sources → open).\n'
        '- Solve the partial response with series/parallel reduction and KVL.\n'
        '- **Sum the partial responses** with their algebraic signs.\n\n'
        '### Draft guidance\n\n'
        '- State that superposition applies because the circuit is **linear and bilateral**.\n'
        '- Show at least two solved partial circuits in the appendix.'
    ),
    'iot': (
        '## Textile IoT Automation Models\n\n'
        'Comparing architectures for your proposal:\n\n'
        '### Model 1 — Centralized cloud\n'
        '- Strongest analytics, highest latency (~400 ms) and bandwidth cost.\n\n'
        '### Model 2 — Edge gateway (recommended)\n'
        '- Local inference with latency under **50 ms**; works offline.\n\n'
        '### Model 3 — Hybrid\n'
        '- Edge handles alarms in real time; cloud retrains models weekly.'
    ),
}

_RESEARCH_FALLBACK = (
    '## Here is how I can help\n\n'
    'I can assist with:\n\n'
    '- **Literature reviews** — ask for a draft on any topic.\n'
    '- **Methodology breakdowns** — request a step-by-step plan.\n'
    '- **Citation checking** — paste an excerpt and name your style (IEEE / APA 7 / Harvard / Chicago).\n'
    '- **Draft editing** — paste a paragraph for polish.\n\n'
    'Try: `Draft a literature review on IoT in textile manufacturing`'
)


# Two canonical references, formatted per citation style, so the endpoint
# returns structured, style-aware citations.
_REFERENCE_SOURCES = [
    ('M. H. Rahman and K. Ahmed', 'IoT-based automated loom monitoring for textile manufacturing',
     'IEEE Access', '9', '44210–44222', '2021'),
    ('S. N. Karim et al.', 'Edge computing for real-time defect detection in weaving',
     'Journal of Textile Automation', '12', '1102–1115', '2023'),
]


def _research_references(style):
    """Render the reference bank in the requested citation style."""
    refs = []
    for index, (authors, title, journal, volume, pages, year) in enumerate(_REFERENCE_SOURCES, start=1):
        # Markdown italics (*…*) so the client-side renderer styles journals
        # without needing raw HTML in the JSON payload.
        if style == 'APA 7':
            text = '%s. (%s). %s. *%s*, *%s*, %s.' % (
                authors.replace(' and ', ', & '),
                year, title, journal, volume, pages,
            )
        elif style == 'Harvard':
            text = '%s (%s) %s, *%s*, %s, pp. %s.' % (authors, year, title, journal, volume, pages)
        elif style == 'Chicago':
            text = '%s. "%s." *%s* %s (%s): %s.' % (authors, title, journal, volume, year, pages)
        else:  # IEEE (default)
            text = '[%d] %s, "%s," *%s*, vol. %s, pp. %s, %s.' % (
                index, authors, title, journal, volume, pages, year,
            )
        refs.append({'index': index, 'text': text})
    return refs


@login_required
def research_query(request):
    """Research AI query endpoint — returns a structured assistant response.

    Accepts ``prompt`` and an optional ``citation_style`` (IEEE / APA 7 /
    Harvard / Chicago). The response is routed server-side by prompt keywords
    and carries a ``topic`` id plus style-aware structured ``references``.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    prompt = request.POST.get('prompt', '').strip()
    if not prompt:
        return JsonResponse({'status': 'error', 'message': 'prompt is required.'}, status=400)

    style = request.POST.get('citation_style', 'IEEE').strip()
    lowered = prompt.lower()

    if lowered.startswith('/summarize') or 'summarize' in lowered or 'abstract' in lowered:
        topic = 'summary'
    elif 'literature' in lowered or 'review' in lowered:
        topic = 'literature'
    elif 'method' in lowered:
        topic = 'methodology'
    elif any(k in lowered for k in ('citation', 'cite', 'ieee', 'apa', 'harvard', 'chicago', 'reference')):
        topic = 'citation'
    elif 'superposition' in lowered:
        topic = 'superposition'
    elif 'iot' in lowered or 'textile' in lowered:
        topic = 'iot'
    else:
        topic = 'fallback'

    return JsonResponse({
        'status': 'success',
        'topic': topic,
        'response_markdown': _RESEARCH_RESPONSES.get(topic, _RESEARCH_FALLBACK),
        'references': _research_references(style),
        'citation_style': style,
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


def _color_palette():
    """64 curated swatches for the canvas style picker: 8 colour families
    (red, orange, amber, green, teal, blue, violet, neutral grey) x 8
    lightness steps from light to dark."""
    def _hsl_to_hex(hue, sat, light):
        r, g, b = colorsys.hls_to_rgb(hue / 360.0, light, sat)
        return '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))

    families = [
        (0, 0.62),     # red
        (30, 0.72),    # orange
        (48, 0.82),    # amber
        (125, 0.48),   # green
        (172, 0.55),   # teal
        (212, 0.62),   # blue
        (262, 0.58),   # violet
        (0, 0.0),      # neutral grey
    ]
    shades = (0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.28, 0.14)
    return [
        _hsl_to_hex(hue, sat, light)
        for hue, sat in families
        for light in shades
    ]


COLOR_PALETTE = _color_palette()


def editable_page_view(request, slug):
    """Public renderer for a builder-authored page and its ContentBlocks.

    Serves the page at ``/page/<slug>/``. Published pages are public;
    unpublished drafts 404 for everyone except super admins, who reach them
    from the builder to preview work in progress. Blocks are ordered by their
    ``order`` (stable pk order). Structured blocks (faq / stats / testimonials
    / cta) are rendered through their partials with the shared
    ``render_block_html`` helper, so the live page and the ``render_block``
    tag never drift apart.
    """
    # Published pages are public; drafts are only reachable by users with the
    # builder's ``change_editablepage`` permission (super admins and authorized
    # staff, so the builder can preview unpublished work) and 404 otherwise.
    qs = EditablePage.objects.filter(slug=slug)
    if not request.user.has_perm('core.change_editablepage'):
        qs = qs.filter(is_published=True)
    page = get_object_or_404(qs)
    blocks = [
        {
            'element_id': block.element_id,
            'block_type': block.block_type,
            # rendered_html is what the live page displays (partial output for
            # structured blocks, raw content_html otherwise).
            'rendered_html': render_block_html(block),
            'style_attr': _style_attr(block.style_json),
        }
        for block in page.content_blocks.order_by('order', 'id')
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

@change_editablepage_required
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


@change_editablepage_required
def visual_editor(request, page_slug):
    """Split-screen visual editor for a single page and its ContentBlocks."""
    page = get_object_or_404(EditablePage, slug=page_slug)
    blocks = [
        {
            'element_id': block.element_id,
            'block_type': block.block_type,
            'content_html': block.content_html,
            'content_json': block.content_json or {},
            'style': block.style_json or {},
            'order': block.order,
        }
        for block in page.content_blocks.order_by('order', 'id')
    ]
    return render(request, 'builder/editor.html', {
        'page': page,
        'blocks': blocks,
    })


@change_editablepage_required
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
        'edit_url': reverse('builder_editor', args=[page.slug]),
    })


@change_editablepage_required
def save_content_block(request):
    """JSON API: create / update / delete / re-order a ContentBlock.

    Modes (all scoped to ``page_slug``):

      * **create/update** — ``{page_slug, element_id, content_html,
        style_json, block_type?, content_json?, order?}``. HTML is sanitized
        before storage; a new block without an explicit ``order`` is appended
        after the page's current last block.
      * **delete** — ``{page_slug, element_id, delete: true}`` removes the
        block.
      * **reorder** — ``{page_slug, reorder: [{element_id, order}, …]}``
        updates every listed block's ``order`` inside a single transaction
        (atomic — either all orders change or none).

    The response is ``{'status': 'success'}`` (with the reordered/deleted
    counts when relevant).
    """
    data, error = _parse_json_body(request)
    if error is not None:
        return error

    page = _get_builder_page(data.get('page_slug'))
    if isinstance(page, JsonResponse):
        return page

    if data.get('reorder') is not None:
        ok, err = _reorder_content_blocks(page, data.get('reorder'))
        return ok if ok is not None else err
    return _save_content_block_data(page, data)


def _get_builder_page(page_slug):
    """Resolve a ``page_slug`` to an EditablePage, or a JSON error response.

    Returns either the page instance or a ``JsonResponse`` — never ``None``.
    """
    if not page_slug:
        return JsonResponse({'status': 'error', 'message': 'page_slug is required'}, status=400)
    try:
        return EditablePage.objects.get(slug=page_slug)
    except EditablePage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Page not found'}, status=404)


def _reorder_content_blocks(page, reorder):
    """Validate + atomically apply a reorder payload.

    Returns ``(ok_response, error_response)`` — exactly one is not ``None``.
    """
    if not isinstance(reorder, list) or not reorder:
        return None, JsonResponse(
            {'status': 'error', 'message': 'reorder must be a non-empty list'},
            status=400,
        )
    page_blocks = {b.element_id: b for b in ContentBlock.objects.filter(page=page)}
    entries = []
    for entry in reorder:
        if not isinstance(entry, dict):
            return None, JsonResponse(
                {'status': 'error', 'message': 'reorder entries must be objects'},
                status=400,
            )
        eid = entry.get('element_id')
        if eid not in page_blocks:
            return None, JsonResponse(
                {'status': 'error', 'message': 'Unknown block: %s' % eid},
                status=400,
            )
        try:
            order_value = max(int(entry.get('order')), 0)
        except (TypeError, ValueError):
            return None, JsonResponse(
                {'status': 'error', 'message': 'reorder entries need an integer order'},
                status=400,
            )
        entries.append((page_blocks[eid], order_value))
    with transaction.atomic():
        for block, order_value in entries:
            block.order = order_value
            block.save(update_fields=['order', 'updated_at'])
    return JsonResponse({'status': 'success', 'reordered': len(entries)}), None


def _save_content_block_data(page, data):
    """Create / update / delete a single ContentBlock from a payload dict."""
    element_id = data.get('element_id')
    if not element_id:
        return JsonResponse(
            {'status': 'error', 'message': 'page_slug and element_id are required'},
            status=400,
        )

    # ---- Delete ----
    if data.get('delete'):
        deleted = ContentBlock.objects.filter(page=page, element_id=element_id).delete()[0]
        return JsonResponse({'status': 'success', 'deleted': deleted})

    existing = ContentBlock.objects.filter(page=page, element_id=element_id).first()

    # Only the keys present in the payload are written; a partial update (an
    # inline style pick or a single edited field) must never wipe the rest.
    style_json = data.get('style_json') if 'style_json' in data else (existing.style_json if existing else {})
    if not isinstance(style_json, dict):
        style_json = {}

    valid_types = {code for code, _label in ContentBlock.BLOCK_TYPE_CHOICES}
    block_type = data.get('block_type')
    if block_type is not None:
        block_type = block_type if block_type in valid_types else 'html'
    else:
        block_type = existing.block_type if existing else 'html'
    content_json = data.get('content_json')
    if content_json is not None and not isinstance(content_json, dict):
        content_json = {}
    elif content_json is None:
        content_json = existing.content_json if existing else {}

    defaults = {
        'block_type': block_type,
        'content_html': sanitize_html(data.get('content_html', '')) if 'content_html' in data else (existing.content_html if existing else ''),
        'content_json': content_json,
        'style_json': style_json,
    }
    if existing is None:
        # New block: append after the current last block unless the payload
        # explicitly positions it.
        try:
            defaults['order'] = max(int(data.get('order')), 0)
        except (TypeError, ValueError):
            defaults['order'] = (
                ContentBlock.objects.filter(page=page)
                .aggregate(top=Max('order'))['top'] or 0
            ) + 1
    else:
        # Existing block: keep its position unless the payload moves it.
        try:
            defaults['order'] = max(int(data.get('order')), 0)
        except (TypeError, ValueError):
            pass

    ContentBlock.objects.update_or_create(
        page=page,
        element_id=element_id,
        defaults=defaults,
    )
    return JsonResponse({'status': 'success'})


@change_editablepage_required
def builder_editor(request, page_slug):
    """Frontend page builder: page-settings toolbar + drag-and-drop block manager.

    Renders ``builder/edit_page.html`` at ``/builder/edit/<slug>/``. The block
    list, type palette and toolbar are all server-rendered; the JS wires
    drag-and-drop reordering, inline block editing, and the Save Draft /
    Publish actions to the JSON endpoints below.
    """
    page = get_object_or_404(EditablePage, slug=page_slug)
    type_labels = dict(ContentBlock.BLOCK_TYPE_CHOICES)
    block_type_icons = {
        'html': 'fa-align-left',
        'hero': 'fa-bolt',
        'features': 'fa-table-cells-large',
        'split': 'fa-image',
        'links': 'fa-link',
        'staff': 'fa-user-tie',
        'faq': 'fa-circle-question',
        'stats': 'fa-chart-column',
        'testimonials': 'fa-quote-left',
        'cta': 'fa-bullhorn',
    }
    blocks = [
        {
            'pk': block.pk,
            'element_id': block.element_id,
            'block_type': block.block_type,
            'type_label': type_labels.get(block.block_type, block.block_type),
            'content_html': block.content_html,
            'content_json': block.content_json or {},
            'order': block.order,
            # Server-rendered section markup for the inline canvas.
            'rendered_html': render_block_html(block),
            # Flattened style_json (color / background / …) for the canvas.
            'style_attr': _style_attr(block.style_json),
        }
        for block in page.content_blocks.order_by('order', 'id')
    ]
    block_types = [
        {'code': code, 'label': label, 'icon': block_type_icons.get(code, 'fa-cube')}
        for code, label in ContentBlock.BLOCK_TYPE_CHOICES
    ]
    # The block library drawer (modal) — the four curated section templates.
    # Samples are derived from ``_BLOCK_TEMPLATES`` (the same defaults the
    # create endpoint seeds), so the preview always matches what gets created.
    _LIBRARY_TEMPLATES = (
        ('hero', 'Hero Section', 'Big headline, subtitle and a call-to-action button.', 'builder/blocks/hero_section.html'),
        ('features', 'Feature Grid', 'A three-column grid of icon and text cards.', 'builder/blocks/features_grid.html'),
        ('split', 'Text & Image Split', 'Rich text on the left with a media image on the right.', 'builder/blocks/split_section.html'),
        ('links', 'Link Hub', 'A grid of quick links to pages across the portal.', 'builder/blocks/links_grid.html'),
        ('staff', 'Staff Grid', 'A grid of staff cards with photos, names and roles.', 'builder/blocks/staff_grid.html'),
        ('cta', 'Announcement Banner / CTA', 'Full-width banner with a headline and action buttons.', 'builder/blocks/cta_section.html'),
    )
    block_templates = []
    for code, label, description, partial in _LIBRARY_TEMPLATES:
        sample = dict(_BLOCK_TEMPLATES.get(code, {}).get('content_json', {}))
        if code == 'features':
            # Richer modal preview: show the full three-column grid.
            sample['items'] = [
                {'icon': 'fa-star', 'title': 'Quality', 'text': 'Description one.'},
                {'icon': 'fa-bolt', 'title': 'Speed', 'text': 'Description two.'},
                {'icon': 'fa-heart', 'title': 'Care', 'text': 'Description three.'},
            ]
        block_templates.append({
            'code': code,
            'label': label,
            'description': description,
            'partial': partial,
            'sample': sample,
        })
    return render(request, 'builder/edit_page.html', {
        'page': page,
        'blocks': blocks,
        'block_types': block_types,
        'block_templates': block_templates,
        'color_palette': COLOR_PALETTE,
    })
    return render(request, 'builder/edit_page.html', {
        'page': page,
        'blocks': blocks,
        'block_types': block_types,
    })


@change_editablepage_required
def builder_blocks_reorder(request):
    """JSON API: atomic drag-and-drop block reorder for the page builder.

    Expects ``{page_slug, reorder: [{element_id, order}, …]}``. Every listed
    block's ``order`` changes inside one transaction — either all or none.
    """
    data, error = _parse_json_body(request)
    if error is not None:
        return error
    page = _get_builder_page(data.get('page_slug'))
    if isinstance(page, JsonResponse):
        return page
    ok, err = _reorder_content_blocks(page, data.get('reorder'))
    return ok if ok is not None else err


@change_editablepage_required
def builder_blocks_save(request):
    """JSON API: create / update / delete a ContentBlock for the page builder.

    Expects ``{page_slug, element_id, block_type?, content_html?,
    content_json?, style_json?, order?, delete?}``.
    """
    data, error = _parse_json_body(request)
    if error is not None:
        return error
    page = _get_builder_page(data.get('page_slug'))
    if isinstance(page, JsonResponse):
        return page
    return _save_content_block_data(page, data)


@change_editablepage_required
def builder_page_save(request):
    """JSON API: persist page-level settings from the page builder toolbar.

    Expects ``{page_slug, title, is_published?, show_in_nav?, seo_description?}``
    — Save Draft sends ``is_published: false``, Publish sends ``true``. Only
    keys present in the payload are written; the rest keep their values.
    """
    data, error = _parse_json_body(request)
    if error is not None:
        return error
    page = _get_builder_page(data.get('page_slug'))
    if isinstance(page, JsonResponse):
        return page

    title = (data.get('title') or '').strip()
    if not title:
        return JsonResponse({'status': 'error', 'message': 'title is required'}, status=400)

    page.title = title[:200]
    update_fields = ['title', 'is_published', 'show_in_nav', 'seo_description', 'updated_at']
    if 'is_published' in data:
        page.is_published = _as_bool(data.get('is_published'))
    if 'show_in_nav' in data:
        page.show_in_nav = _as_bool(data.get('show_in_nav'))
    if 'seo_description' in data:
        page.seo_description = (data.get('seo_description') or '').strip()
    page.save(update_fields=update_fields)
    return JsonResponse({
        'status': 'success',
        'page_slug': page.slug,
        'is_published': page.is_published,
        'show_in_nav': page.show_in_nav,
    })


def _as_bool(value):
    """Coerce a JSON/form value to a boolean without string truthiness traps."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ('1', 'true', 'yes', 'on')
    return bool(value)


# Default content seeded when a block is instantiated from the library.
# Mirrors the client-side ``DEFAULTS`` map in static/js/builder/page_manager.js
# (keep the two in sync when a type is added).
_BLOCK_TEMPLATES = {
    'html': {'content_html': '<h2>New section</h2><p>Write your content here.</p>', 'content_json': {}},
    'hero': {'content_html': '', 'content_json': {
        'headline': 'A bold headline',
        'subheadline': 'Supporting line',
        'primary_label': 'Learn More',
        'primary_url': '/departments/',
    }},
    'features': {'content_html': '', 'content_json': {
        'title': 'Why choose us',
        'items': [{'icon': 'fa-star', 'title': 'Feature', 'text': 'Describe it here.'}],
    }},
    'split': {'content_html': '', 'content_json': {
        'heading': 'Our mission',
        'text': 'Rich text content goes here.',
        'image_url': '',
        'image_alt': '',
    }},
    'links': {'content_html': '', 'content_json': {
        'title': 'Explore',
        'subtitle': 'Quick links across the portal.',
        'items': [
            {'label': 'Admissions', 'url': '/admissions/'},
            {'label': 'Departments', 'url': '/departments/'},
            {'label': 'Notices', 'url': '/notices/'},
        ],
    }},
    'staff': {'content_html': '', 'content_json': {
        'title': 'Our team',
        'subtitle': 'Meet the people behind the campus.',
        'items': [
            {'name': 'Jane Doe', 'role': 'Dean', 'photo_url': ''},
            {'name': 'John Smith', 'role': 'Registrar', 'photo_url': ''},
            {'name': 'Sam Lee', 'role': 'Librarian', 'photo_url': ''},
        ],
    }},
    'faq': {'content_html': '', 'content_json': {
        'title': 'FAQs',
        'items': [{'question': 'A question?', 'answer': 'An answer.'}],
    }},
    'stats': {'content_html': '', 'content_json': {
        'title': 'At a glance',
        'items': [{'value': '100+', 'label': 'Highlight', 'icon': 'fa-chart-simple'}],
    }},
    'testimonials': {'content_html': '', 'content_json': {
        'title': 'What people say',
        'items': [{'quote': 'A quote worth sharing.', 'author': 'Name', 'title': 'Role'}],
    }},
    'cta': {'content_html': '', 'content_json': {
        'headline': 'Ready to start?',
        'subtext': 'Join us today.',
        'primary_label': 'Apply Now',
        'primary_url': '/signup/',
    }},
}


@change_editablepage_required
def builder_block_create(request):
    """JSON API: instantiate a new ContentBlock from the block library.

    Expects ``{page_id, block_type, order_index?}``. The block is seeded with
    default content for its type (see ``_BLOCK_TEMPLATES``) and inserted at
    ``order_index`` — existing blocks at that position and beyond shift up by
    one inside a single transaction. Without an index the block is appended
    to the end of the page.
    """
    data, error = _parse_json_body(request)
    if error is not None:
        return error

    raw_page_id = data.get('page_id')
    if raw_page_id in (None, ''):
        return JsonResponse({'status': 'error', 'message': 'page_id is required'}, status=400)
    try:
        page = EditablePage.objects.get(pk=int(raw_page_id))
    except (TypeError, ValueError):
        return JsonResponse(
            {'status': 'error', 'message': 'page_id must be an integer'},
            status=400,
        )
    except EditablePage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Page not found'}, status=404)

    block_type = (data.get('block_type') or '').strip()
    valid_types = {code for code, _label in ContentBlock.BLOCK_TYPE_CHOICES}
    if block_type not in valid_types:
        return JsonResponse(
            {'status': 'error', 'message': 'Unknown block type: %s' % block_type},
            status=400,
        )

    # Insert position: explicit index shifts blocks up; otherwise append.
    order = (ContentBlock.objects.filter(page=page).aggregate(top=Max('order'))['top'] or 0) + 1
    order_index = data.get('order_index')
    if order_index is not None:
        try:
            order = max(int(order_index), 0)
        except (TypeError, ValueError):
            return JsonResponse(
                {'status': 'error', 'message': 'order_index must be an integer'},
                status=400,
            )

    defaults = _BLOCK_TEMPLATES.get(block_type, {'content_html': '', 'content_json': {}})
    element_id = '%s-%s' % (block_type, secrets.token_hex(4))
    with transaction.atomic():
        # Make room at the target index (no-op when appending).
        ContentBlock.objects.filter(page=page, order__gte=order).update(order=F('order') + 1)
        block = ContentBlock.objects.create(
            page=page,
            element_id=element_id,
            block_type=block_type,
            content_html=defaults.get('content_html', ''),
            content_json=defaults.get('content_json', {}),
            order=order,
        )
    return JsonResponse({
        'status': 'success',
        'block': {
            'id': block.pk,
            'element_id': block.element_id,
            'block_type': block.block_type,
            'order': block.order,
        },
    })


@change_editablepage_required
def builder_block_delete(request, block_id):
    """JSON API: remove a ContentBlock from the canvas by its database id.

    Called by the page builder's soft-confirmation modal (POST only).
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    try:
        block = ContentBlock.objects.get(pk=block_id)
    except (ContentBlock.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Block not found'}, status=404)
    block.delete()
    return JsonResponse({'status': 'success', 'deleted': block_id})


@change_editablepage_required
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
