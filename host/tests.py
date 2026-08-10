from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import MedicalAppointment, MedicalChatThread, StudentProfile


class MedicalAdminDashboardTests(TestCase):
    """Medical admin & host dashboards — staff access + real appointment data."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='hostadmin', password='admin123', is_staff=True,
        )
        self.student = User.objects.create_user(
            username='S1001', password='student123',
            first_name='Alice', last_name='Johnson',
        )
        StudentProfile.objects.create(user=self.student, student_id='S1001', department='CSE')
        self.appointment = MedicalAppointment.objects.create(
            user=self.student,
            doctor_name='Dr. Ahmed Khan',
            appointment_date='2026-08-12',
            time_slot='10:00',
            reason='Fever',
        )

    # ------------------------------------------------------------------
    # Access control
    # ------------------------------------------------------------------
    def test_medical_admin_dashboard_redirects_anonymous_to_login(self):
        response = self.client.get(reverse('medical_admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_medical_admin_dashboard_requires_staff(self):
        self.client.login(username='S1001', password='student123')
        response = self.client.get(reverse('medical_admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_medical_host_dashboard_requires_staff(self):
        response = self.client.get(reverse('host:medical_host_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    # ------------------------------------------------------------------
    # Real appointment data + filters
    # ------------------------------------------------------------------
    def test_medical_admin_dashboard_lists_real_appointments(self):
        self.client.login(username='hostadmin', password='admin123')
        response = self.client.get(reverse('medical_admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Medical Admin Dashboard')
        self.assertContains(response, 'Alice Johnson')
        self.assertContains(response, 'Dr. Ahmed Khan')
        self.assertContains(response, 'Pending')

    def test_medical_host_dashboard_lists_real_appointments(self):
        self.client.login(username='hostadmin', password='admin123')
        response = self.client.get(reverse('host:medical_host_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Johnson')
        self.assertContains(response, 'Dr. Ahmed Khan')

    def test_medical_admin_filters_by_status(self):
        # 'Fever' is the appointment's reason — it only appears in the table.
        self.client.login(username='hostadmin', password='admin123')
        response = self.client.get(reverse('medical_admin_dashboard'), {'status': 'pending'})
        self.assertContains(response, 'Fever')
        response = self.client.get(reverse('medical_admin_dashboard'), {'status': 'confirmed'})
        self.assertNotContains(response, 'Fever')

    def test_medical_admin_filters_by_doctor(self):
        self.client.login(username='hostadmin', password='admin123')
        response = self.client.get(reverse('medical_admin_dashboard'), {'doctor': 'dr. ahmed khan'})
        self.assertContains(response, 'Fever')
        response = self.client.get(reverse('medical_admin_dashboard'), {'doctor': 'dr. sarah smith'})
        self.assertNotContains(response, 'Fever')

    def test_student_medical_booking_page_still_works(self):
        response = self.client.get(reverse('medical'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book an Appointment')


class MedicalChatAndQueueDashboardTests(TestCase):
    """Admin chat list + host live queue render real DB data."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='hostadmin2', password='admin123', is_staff=True,
        )
        self.student = User.objects.create_user(
            username='S3001', password='student123', first_name='Bina', last_name='Rahman',
        )
        StudentProfile.objects.create(user=self.student, student_id='S3001', department='CSE')
        self.appointment = MedicalAppointment.objects.create(
            user=self.student, doctor_name='Dr. Ahmed Khan',
            appointment_date='2026-08-12', time_slot='10:00', reason='Follow-up',
        )

    def test_admin_dashboard_shows_real_chat_threads(self):
        thread = MedicalChatThread.objects.create(
            appointment=self.appointment, patient=self.student,
            doctor_name='Dr. Ahmed Khan',
        )
        self.client.login(username='hostadmin2', password='admin123')
        response = self.client.get(reverse('medical_admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Medical Chat Management')
        self.assertContains(response, 'chat-window')
        # Chat row button markup (unique to the chat list, not the appointments table)
        self.assertContains(response, 'data-thread-id="%d"' % thread.pk)
        self.assertContains(response, 'Bina Rahman')

    def test_host_dashboard_renders_live_queue(self):
        self.client.login(username='hostadmin2', password='admin123')
        response = self.client.get(reverse('host:medical_host_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Live Queue')
        self.assertContains(response, 'Bina Rahman')
        self.assertContains(response, 'queue-count')
