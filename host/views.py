from datetime import date

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import redirect, render

from core.models import MedicalAppointment, MedicalChatThread, StudentProfile
from core.views import _chat_thread_serialize as _serialize_chat_thread

# Fallback catalog shown in the filter dropdown when no appointments exist yet.
DOCTOR_NAMES = [
    'Dr. Ahmed Khan',
    'Dr. Sarah Smith',
    'Dr. Michael Chen',
    'Dr. Emily Johnson',
]


def _serialize_appointment(appointment):
    """Shape a MedicalAppointment row for the admin/host dashboard templates."""
    profile = getattr(appointment.user, 'student_profile', None)
    return {
        'id': appointment.pk,
        'student_name': appointment.user.get_full_name() or appointment.user.username,
        'student_id': getattr(profile, 'student_id', appointment.user.username),
        'department': getattr(profile, 'department', '—'),
        'contact': '—',  # no phone field on the student profile yet
        'phone': '—',
        'doctor': appointment.doctor_name,
        'date': appointment.appointment_date.isoformat(),
        'time': appointment.time_slot,
        'reason': appointment.reason,
        'status': appointment.get_status_display(),
        'status_code': appointment.status,
        'booking_time': appointment.created_at.strftime('%Y-%m-%d %H:%M'),
    }


def _appointment_summaries(queryset, today):
    """Summary counts over the *unfiltered* appointment set."""
    return {
        'total': queryset.count(),
        'pending': queryset.filter(status='pending').count(),
        'confirmed': queryset.filter(status='confirmed').count(),
        'completed': queryset.filter(status='completed').count(),
        'cancelled': queryset.filter(status='cancelled').count(),
        'todays_queue': queryset.filter(
            appointment_date=today, status__in=['pending', 'confirmed']
        ).count(),
    }


def _serialize_queue(appointments):
    """Shape today's pending/confirmed appointments into a numbered FIFO queue."""
    items = []
    for position, appointment in enumerate(appointments, start=1):
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
        })
    return items


def index(request):
    return redirect('host:medical_host_dashboard')


@staff_member_required
def medical_host_dashboard(request):
    """Medical host dashboard — live MedicalAppointment records with search
    and status/date filters, plus real status actions via the shared API.
    """
    today = date.today()
    base = MedicalAppointment.objects.select_related('user').all()

    q = request.GET.get('q', '').strip().lower()
    queryset = base
    if q:
        queryset = queryset.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__username__icontains=q)
            | Q(reason__icontains=q)
        )

    active_filter = request.GET.get('filter', 'all')
    if active_filter == 'today':
        queryset = queryset.filter(appointment_date=today)
    elif active_filter in ('pending', 'confirmed', 'completed', 'cancelled'):
        queryset = queryset.filter(status=active_filter)

    appointments = [_serialize_appointment(a) for a in queryset]

    # Live FIFO queue for today (pending + confirmed) — polled client-side for
    # updates, and pushed to staff in real time via update_appointment_status.
    queue = _serialize_queue(
        MedicalAppointment.objects.filter(
            appointment_date=today, status__in=['pending', 'confirmed'],
        ).select_related('user').order_by('created_at', 'id')
    )

    context = {
        'summaries': _appointment_summaries(base, today),
        'appointments': appointments,
        'queue': queue,
        'search_query': request.GET.get('q', ''),
        'active_filter': active_filter,
    }

    return render(request, 'host/medical/dashboard.html', context)


@staff_member_required
def medical_admin_dashboard(request):
    """Medical admin dashboard — live MedicalAppointment records filtered by
    student, status, department, doctor, and date, with real status actions.
    """
    today = date.today()
    base = MedicalAppointment.objects.select_related('user').all()

    q = request.GET.get('q', '').strip().lower()
    student_name_filter = request.GET.get('student', '').strip().lower()
    student_id_filter = request.GET.get('student_id', '').strip().lower()
    status_filter = request.GET.get('status', 'all').strip().lower()
    department_filter = request.GET.get('department', 'all').strip().lower()
    doctor_filter = request.GET.get('doctor', 'all').strip().lower()
    date_filter = request.GET.get('date', '').strip()

    queryset = base
    if q:
        queryset = queryset.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__username__icontains=q)
            | Q(reason__icontains=q)
        )
    if student_name_filter:
        queryset = queryset.filter(
            Q(user__first_name__icontains=student_name_filter)
            | Q(user__last_name__icontains=student_name_filter)
        )
    if student_id_filter:
        queryset = queryset.filter(user__username__icontains=student_id_filter)
    if status_filter != 'all':
        queryset = queryset.filter(status=status_filter)
    if department_filter != 'all':
        queryset = queryset.filter(user__student_profile__department__iexact=department_filter)
    if doctor_filter != 'all':
        queryset = queryset.filter(doctor_name__iexact=doctor_filter)
    if date_filter:
        queryset = queryset.filter(appointment_date=date_filter)

    appointments = [_serialize_appointment(a) for a in queryset]

    # "View details" is read-only — status changes go through the POST API.
    selected_appointment = None
    view_id = request.GET.get('id')
    if request.GET.get('action') == 'view' and view_id:
        try:
            selected_appointment = _serialize_appointment(
                MedicalAppointment.objects.get(pk=view_id)
            )
        except (MedicalAppointment.DoesNotExist, ValueError):
            selected_appointment = None

    summaries = _appointment_summaries(base, today)

    # Filter dropdown data — real doctors/departments when available.
    real_doctors = list(
        MedicalAppointment.objects.values_list('doctor_name', flat=True).distinct()
    )
    doctors_list = real_doctors or DOCTOR_NAMES
    departments = [code for code, _label in StudentProfile.DEPARTMENT_CHOICES]

    # Real consultation threads — created by patients/staff via the chat API
    # (one thread per appointment, persisted in MedicalChatThread).
    chat_threads = [
        _serialize_chat_thread(thread, request.user)
        for thread in MedicalChatThread.objects
        .select_related('patient', 'appointment')
        .prefetch_related('messages')
        .order_by('-updated_at', '-id')[:30]
    ]
    doctors = [
        {'name': 'Dr. Ahmed Khan', 'specialty': 'General Physician', 'days': 'Sunday - Thursday', 'time': '10:00 AM - 2:00 PM', 'status': 'Available'},
        {'name': 'Dr. Sarah Smith', 'specialty': 'Orthopedic', 'days': 'Monday - Friday', 'time': '9:00 AM - 1:00 PM', 'status': 'Available'},
        {'name': 'Dr. Michael Chen', 'specialty': 'Dermatology', 'days': 'Tuesday - Saturday', 'time': '11:00 AM - 3:00 PM', 'status': 'Busy'},
    ]
    content_sections = [
        {'title': 'Health Tips', 'description': 'Short wellness guidance for students.', 'items': 5},
        {'title': 'Disease Awareness', 'description': 'Seasonal and campus health alerts.', 'items': 3},
        {'title': 'First Aid', 'description': 'Immediate care guidance for common incidents.', 'items': 4},
        {'title': 'Medical Facilities', 'description': 'Updated campus support locations.', 'items': 6},
        {'title': 'Emergency Contacts', 'description': 'Fast access to urgent support.', 'items': 7},
        {'title': 'Medical News', 'description': 'Campus health updates and announcements.', 'items': 2},
    ]
    home_page_sections = [
        {'title': 'About Medical In-Charge', 'detail': 'Dr. Ahmed Khan leads the campus health team.'},
        {'title': 'Contact Information', 'detail': 'Call the medical office at 0123-456789.'},
        {'title': 'Medical Facilities', 'detail': 'Infirmary, ambulance coordination, and first aid room.'},
        {'title': 'Emergency Contacts', 'detail': 'Campus security and nearest hospital line available.'},
        {'title': 'Health Tips', 'detail': 'Weekly wellbeing reminders for students.'},
    ]

    context = {
        'summaries': summaries,
        'appointments': appointments,
        'selected_appointment': selected_appointment,
        'search_query': request.GET.get('q', ''),
        'student_name_filter': student_name_filter,
        'student_id_filter': student_id_filter,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'doctor_filter': doctor_filter,
        'date_filter': date_filter,
        'chat_threads': chat_threads,
        'doctors': doctors,
        'content_sections': content_sections,
        'home_page_sections': home_page_sections,
        'departments': departments,
        'doctors_list': doctors_list,
    }

    return render(request, 'host/medical/admin_dashboard.html', context)
