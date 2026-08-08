from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date


def index(request):
    return redirect('host:medical_host_dashboard')


def medical_host_dashboard(request):
    # Mock data for summary cards and appointments
    today = date.today().strftime('%Y-%m-%d')

    appointments = [
        {"id": 1, "student_name": "Alice Johnson", "student_id": "S1001", "department": "Computer Science", "phone": "0123456789", "doctor": "Dr. Ahmed Khan", "date": today, "time": "10:00", "reason": "Fever and sore throat", "status": "Pending"},
        {"id": 2, "student_name": "Bob Williams", "student_id": "S1002", "department": "Mathematics", "phone": "0987654321", "doctor": "Dr. Sarah Smith", "date": today, "time": "11:30", "reason": "Back pain", "status": "Confirmed"},
        {"id": 3, "student_name": "Clara Oswald", "student_id": "S1003", "department": "Physics", "phone": "0112233445", "doctor": "Dr. Mike Johnson", "date": "2024-12-20", "time": "09:00", "reason": "Skin rash", "status": "Cancelled"},
        {"id": 4, "student_name": "David Tennant", "student_id": "S1004", "department": "Chemistry", "phone": "0223344556", "doctor": "Dr. Emily Johnson", "date": today, "time": "14:00", "reason": "Headache", "status": "Pending"},
        {"id": 5, "student_name": "Eve Parker", "student_id": "S1005", "department": "Biology", "phone": "0334455667", "doctor": "Dr. Michael Chen", "date": "2024-12-21", "time": "15:30", "reason": "Allergic reaction", "status": "Completed"},
    ]

    # Handle actions via query params (mock only, no DB changes)
    action = request.GET.get('action')
    appt_id = request.GET.get('id')
    if action and appt_id:
        label = ''
        if action == 'confirm':
            label = 'Appointment Confirmed Successfully'
            messages.success(request, label)
        elif action == 'cancel':
            label = 'Appointment Cancelled Successfully'
            messages.success(request, label)
        elif action == 'complete':
            label = 'Appointment Marked Completed'
            messages.success(request, label)
        elif action == 'return_pending':
            label = 'Appointment Returned to Pending'
            messages.success(request, label)
        else:
            messages.info(request, 'Action: %s' % action)

        # Redirect to clean URL (mock behavior)
        return redirect('host:medical_host_dashboard')

    # Filters and search
    q = request.GET.get('q', '').strip().lower()
    active_filter = request.GET.get('filter', 'all')

    filtered = appointments
    if q:
        filtered = [a for a in filtered if q in a['student_name'].lower() or q in a['student_id'].lower()]

    if active_filter == 'today':
        filtered = [a for a in filtered if a['date'] == today]
    elif active_filter in ['pending', 'confirmed', 'completed', 'cancelled']:
        status_map = {
            'pending': 'Pending',
            'confirmed': 'Confirmed',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        filtered = [a for a in filtered if a['status'] == status_map.get(active_filter)]

    # Summary counts
    total = len(appointments)
    pending = sum(1 for a in appointments if a['status'] == 'Pending')
    confirmed = sum(1 for a in appointments if a['status'] == 'Confirmed')
    completed = sum(1 for a in appointments if a['status'] == 'Completed')
    cancelled = sum(1 for a in appointments if a['status'] == 'Cancelled')
    todays_queue = sum(1 for a in appointments if a['date'] == today and a['status'] in ['Pending', 'Confirmed'])

    context = {
        'summaries': {
            'total': total,
            'pending': pending,
            'confirmed': confirmed,
            'completed': completed,
            'cancelled': cancelled,
            'todays_queue': todays_queue,
        },
        'appointments': filtered,
        'search_query': request.GET.get('q', ''),
        'active_filter': active_filter,
    }

    return render(request, 'host/medical/dashboard.html', context)


def medical_admin_dashboard(request):
    # Mock-only admin view for now; role-based authentication can be added later.
    today = date.today().strftime('%Y-%m-%d')
    appointments = [
        {"id": 1, "student_name": "Alice Johnson", "student_id": "S1001", "department": "Computer Science", "contact": "0123456789", "doctor": "Dr. Ahmed Khan", "date": today, "time": "10:00", "reason": "Fever and sore throat", "status": "Pending", "booking_time": "2026-08-07 08:15"},
        {"id": 2, "student_name": "Bob Williams", "student_id": "S1002", "department": "Mathematics", "contact": "0987654321", "doctor": "Dr. Sarah Smith", "date": today, "time": "11:30", "reason": "Back pain", "status": "Confirmed", "booking_time": "2026-08-07 09:00"},
        {"id": 3, "student_name": "Clara Oswald", "student_id": "S1003", "department": "Physics", "contact": "0112233445", "doctor": "Dr. Mike Johnson", "date": "2026-08-10", "time": "09:00", "reason": "Skin rash", "status": "Cancelled", "booking_time": "2026-08-06 16:40"},
        {"id": 4, "student_name": "David Tennant", "student_id": "S1004", "department": "Chemistry", "contact": "0223344556", "doctor": "Dr. Emily Johnson", "date": today, "time": "14:00", "reason": "Headache", "status": "Pending", "booking_time": "2026-08-07 11:20"},
        {"id": 5, "student_name": "Eve Parker", "student_id": "S1005", "department": "Biology", "contact": "0334455667", "doctor": "Dr. Michael Chen", "date": "2026-08-11", "time": "15:30", "reason": "Allergic reaction", "status": "Confirmed", "booking_time": "2026-08-06 14:10"},
    ]

    action = request.GET.get('action')
    appt_id = request.GET.get('id')
    selected_appointment = None

    if action == 'confirm' and appt_id:
        for appointment in appointments:
            if str(appointment['id']) == str(appt_id):
                appointment['status'] = 'Confirmed'
                break
        messages.success(request, 'Appointment confirmed successfully.')
        return redirect('medical_admin_dashboard')

    if action == 'cancel' and appt_id:
        for appointment in appointments:
            if str(appointment['id']) == str(appt_id):
                appointment['status'] = 'Cancelled'
                break
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('medical_admin_dashboard')

    if action == 'view' and appt_id:
        selected_appointment = next((appointment for appointment in appointments if str(appointment['id']) == str(appt_id)), None)

    q = request.GET.get('q', '').strip().lower()
    student_name_filter = request.GET.get('student', '').strip().lower()
    student_id_filter = request.GET.get('student_id', '').strip().lower()
    status_filter = request.GET.get('status', 'all').strip().lower()
    department_filter = request.GET.get('department', 'all').strip().lower()
    doctor_filter = request.GET.get('doctor', 'all').strip().lower()
    date_filter = request.GET.get('date', '').strip()

    filtered = appointments
    if q:
        filtered = [appointment for appointment in filtered if q in appointment['student_name'].lower() or q in appointment['student_id'].lower() or q in appointment['reason'].lower()]

    if student_name_filter:
        filtered = [appointment for appointment in filtered if student_name_filter in appointment['student_name'].lower()]

    if student_id_filter:
        filtered = [appointment for appointment in filtered if student_id_filter in appointment['student_id'].lower()]

    if status_filter != 'all':
        filtered = [appointment for appointment in filtered if appointment['status'].lower() == status_filter]

    if department_filter != 'all':
        filtered = [appointment for appointment in filtered if appointment['department'].lower() == department_filter]

    if doctor_filter != 'all':
        filtered = [appointment for appointment in filtered if appointment['doctor'].lower() == doctor_filter]

    if date_filter:
        filtered = [appointment for appointment in filtered if appointment['date'] == date_filter]

    total = len(appointments)
    pending = sum(1 for appointment in appointments if appointment['status'] == 'Pending')
    confirmed = sum(1 for appointment in appointments if appointment['status'] == 'Confirmed')
    cancelled = sum(1 for appointment in appointments if appointment['status'] == 'Cancelled')

    chats = [
        {"student_name": "Alice Johnson", "student_id": "S1001", "last_message": "Please share the prescription details.", "time": "10:15", "status": "Active"},
        {"student_name": "David Tennant", "student_id": "S1004", "last_message": "Waiting for doctor confirmation.", "time": "09:40", "status": "Waiting"},
        {"student_name": "Eve Parker", "student_id": "S1005", "last_message": "Thanks, the guidance was helpful.", "time": "08:20", "status": "Resolved"},
    ]

    doctors = [
        {"name": "Dr. Ahmed Khan", "specialty": "General Physician", "days": "Sunday - Thursday", "time": "10:00 AM - 2:00 PM", "status": "Available"},
        {"name": "Dr. Sarah Smith", "specialty": "Orthopedic", "days": "Monday - Friday", "time": "9:00 AM - 1:00 PM", "status": "Available"},
        {"name": "Dr. Michael Chen", "specialty": "Dermatology", "days": "Tuesday - Saturday", "time": "11:00 AM - 3:00 PM", "status": "Busy"},
    ]

    content_sections = [
        {"title": "Health Tips", "description": "Short wellness guidance for students.", "items": 5},
        {"title": "Disease Awareness", "description": "Seasonal and campus health alerts.", "items": 3},
        {"title": "First Aid", "description": "Immediate care guidance for common incidents.", "items": 4},
        {"title": "Medical Facilities", "description": "Updated campus support locations.", "items": 6},
        {"title": "Emergency Contacts", "description": "Fast access to urgent support.", "items": 7},
        {"title": "Medical News", "description": "Campus health updates and announcements.", "items": 2},
    ]

    home_page_sections = [
        {"title": "About Medical In-Charge", "detail": "Dr. Ahmed Khan leads the campus health team."},
        {"title": "Contact Information", "detail": "Call the medical office at 0123-456789."},
        {"title": "Medical Facilities", "detail": "Infirmary, ambulance coordination, and first aid room."},
        {"title": "Emergency Contacts", "detail": "Campus security and nearest hospital line available."},
        {"title": "Health Tips", "detail": "Weekly wellbeing reminders for students."},
    ]

    context = {
        'summaries': {
            'total': total,
            'pending': pending,
            'confirmed': confirmed,
            'cancelled': cancelled,
        },
        'appointments': filtered,
        'selected_appointment': selected_appointment,
        'search_query': request.GET.get('q', ''),
        'student_name_filter': student_name_filter,
        'student_id_filter': student_id_filter,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'doctor_filter': doctor_filter,
        'date_filter': date_filter,
        'chats': chats,
        'doctors': doctors,
        'content_sections': content_sections,
        'home_page_sections': home_page_sections,
        'departments': ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology'],
        'doctors_list': ['Dr. Ahmed Khan', 'Dr. Sarah Smith', 'Dr. Mike Johnson', 'Dr. Emily Johnson', 'Dr. Michael Chen'],
    }

    return render(request, 'host/medical/admin_dashboard.html', context)
