from django.test import SimpleTestCase
from django.urls import reverse


class MedicalAdminDashboardTests(SimpleTestCase):
    def test_medical_admin_dashboard_is_accessible(self):
        response = self.client.get(reverse('medical_admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Medical Admin Dashboard')
        self.assertContains(response, 'Manage medical services, appointments, doctors, and student health information.')

    def test_student_medical_booking_page_still_works(self):
        response = self.client.get(reverse('medical'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book an Appointment')
