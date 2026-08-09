from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .models import StudentProfile


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


def claim_meal_ticket(request):
    return render(request, 'ticketing/tickets.html')

def book_transport_ticket(request):
    return render(request, 'ticketing/tickets.html')

def book_appointment(request):
    return render(request, 'medical/booking.html')


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
# Staff / admin dashboards
# ============================================================================

@staff_member_required(login_url=settings.LOGIN_URL)
def system_admin_view(request):
    """System Admin Dashboard — transport management consolidated here
    alongside user & role management, notices/materials, and the AI/security
    consoles. All data is mock (frontend-only) until backend models land.
    """
    students = [
        {'name': 'Alice Johnson', 'student_id': 'S1001', 'department': 'CSE', 'status': 'Active'},
        {'name': 'Bob Williams', 'student_id': 'S1002', 'department': 'TEX', 'status': 'Active'},
        {'name': 'Clara Oswald', 'student_id': 'S1003', 'department': 'FDAE', 'status': 'Suspended'},
        {'name': 'David Tennant', 'student_id': 'S1004', 'department': 'IPE', 'status': 'Active'},
        {'name': 'Eve Parker', 'student_id': 'S1005', 'department': 'EEE', 'status': 'Active'},
    ]
    staff = [
        {'name': 'Dr. Ahmed Khan', 'role': 'Chief Medical Officer', 'department': 'Medical Center', 'status': 'Active'},
        {'name': 'Rahat Karim', 'role': 'Transport Coordinator', 'department': 'Administration', 'status': 'Active'},
        {'name': 'Sadia Islam', 'role': 'Cafeteria Manager', 'department': 'Administration', 'status': 'Active'},
        {'name': 'Tanvir Ahmed', 'role': 'Host Admin', 'department': 'IT', 'status': 'Inactive'},
    ]

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

    # --- Transport Management (consolidated from /transport/) ---
    buses = [
        {'route': 'Route 1 · Campus → Town Center', 'driver': 'Abdul Karim', 'status': 'On Time', 'next_stop': 'Main Gate', 'eta': '8:00 AM'},
        {'route': 'Route 2 · Campus → Savar Bazar', 'driver': 'Rafiq Uddin', 'status': 'In Transit', 'next_stop': 'Savar Bazar', 'eta': '8:15 AM'},
        {'route': 'Route 3 · Campus → Mirpur', 'driver': 'Jamal Hossain', 'status': 'Arriving in 10 mins', 'next_stop': 'Campus Drop-off', 'eta': '5:30 PM'},
    ]
    driver_updates = [
        {'route': 'Route 1', 'driver': 'Abdul Karim', 'update': 'Departed campus on time', 'time': '7:45 AM'},
        {'route': 'Route 2', 'driver': 'Rafiq Uddin', 'update': 'Heavy traffic near Savar bypass', 'time': '7:58 AM'},
        {'route': 'Route 3', 'driver': 'Jamal Hossain', 'update': 'Boarding complete, closing doors', 'time': '5:20 PM'},
    ]
    boarding_scans = [
        {'token': 'TR-4F2A1', 'route': 'Route 1', 'time': '7:48 AM', 'status': 'Valid'},
        {'token': 'TR-9K7B3', 'route': 'Route 1', 'time': '7:50 AM', 'status': 'Valid'},
        {'token': 'TR-2M8C5', 'route': 'Route 3', 'time': '5:22 PM', 'status': 'Valid'},
        {'token': 'TR-7X1D9', 'route': 'Route 2', 'time': '7:55 AM', 'status': 'Invalid'},
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
    security_logs = [
        {'time': '08:12 AM', 'user': 'admin', 'action': 'Role updated for sadia.islam', 'ip': '10.0.4.12', 'status': 'Success'},
        {'time': '08:01 AM', 'user': 'student.s1001', 'action': 'Login from new device', 'ip': '10.0.8.44', 'status': 'Success'},
        {'time': '07:48 AM', 'user': 'system', 'action': 'Boarding scan — invalid token TR-7X1D9', 'ip': '10.0.2.7', 'status': 'Flagged'},
        {'time': '07:30 AM', 'user': 'host.tanvir', 'action': 'Content edited: Health Tips', 'ip': '10.0.3.21', 'status': 'Success'},
        {'time': '07:12 AM', 'user': 'unknown', 'action': 'Failed login attempt ×5', 'ip': '203.0.113.9', 'status': 'Blocked'},
    ]

    return render(request, 'sys_admin.html', {
        'students': students,
        'staff': staff,
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
    """Cafeteria admin — daily slot capacity, kitchen inventory, and QR
    token / meal coupon redemption (mock).
    """
    slots = [
        {'meal': 'Breakfast', 'capacity': 80, 'claimed': 62},
        {'meal': 'Lunch', 'capacity': 200, 'claimed': 142},
        {'meal': 'Dinner', 'capacity': 160, 'claimed': 97},
    ]
    inventory = [
        {'item': 'Basmati Rice', 'category': 'Grains', 'stock': 320, 'unit': 'kg', 'status': 'In Stock'},
        {'item': 'Lentils (Daal)', 'category': 'Grains', 'stock': 85, 'unit': 'kg', 'status': 'In Stock'},
        {'item': 'Chicken (dressed)', 'category': 'Protein', 'stock': 24, 'unit': 'kg', 'status': 'Low'},
        {'item': 'Cooking Oil', 'category': 'Staples', 'stock': 18, 'unit': 'L', 'status': 'Low'},
        {'item': 'Potatoes', 'category': 'Vegetables', 'stock': 210, 'unit': 'kg', 'status': 'In Stock'},
        {'item': 'Milk Powder', 'category': 'Dairy', 'stock': 6, 'unit': 'kg', 'status': 'Out'},
        {'item': 'Eggs', 'category': 'Protein', 'stock': 480, 'unit': 'pcs', 'status': 'In Stock'},
    ]
    redemptions = [
        {'token': '#MEAL-8921', 'student': 'Alice Johnson', 'meal': 'Lunch', 'time': '12:05 PM', 'status': 'Redeemed'},
        {'token': '#MEAL-8917', 'student': 'David Tennant', 'meal': 'Lunch', 'time': '12:11 PM', 'status': 'Redeemed'},
        {'token': '#MEAL-8930', 'student': 'Eve Parker', 'meal': 'Dinner', 'time': '—', 'status': 'Unused'},
    ]
    return render(request, 'cafeteria_admin.html', {
        'slots': slots,
        'inventory': inventory,
        'redemptions': redemptions,
    })


@staff_member_required(login_url=settings.LOGIN_URL)
def club_admin_view(request):
    """Club admin — member approvals, role assignments, event posts, and
    bKash/Nagad/Rocket transaction verification (mock).
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
    return render(request, 'club_admin.html', {
        'pending_members': pending_members,
        'members': members,
        'events': events,
        'transactions': transactions,
    })
