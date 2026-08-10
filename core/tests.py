import json
from datetime import timedelta
from unittest import mock

import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase, TransactionTestCase, override_settings
from django.urls import reverse, resolve
from django.utils import timezone

from core.models import (
    BusSchedule,
    ClassRoutine,
    Club,
    ClubEvent,
    ClubRegistration,
    ContentBlock,
    Course,
    CourseMaterial,
    Department,
    Driver,
    EditablePage,
    FacultyMember,
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


class StudentPagesSmokeTest(TestCase):
    """Every student page renders without error after the refactor.

    ``TestCase`` (not ``SimpleTestCase``) because the notices and academic
    notes pages query the database for live content.
    """

    PAGES = [
        'home',
        'dashboard',
        'academic_notes',
        'notices',
        'tickets',
        'medical',
        'notes',
        'clubs_dashboard',
        'transport_dashboard',
        'meal_dashboard',
        'checkout',
        'research_ai',
        'departments',
        'signup',
    ]

    def test_all_student_pages_render(self):
        for name in self.PAGES:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200, msg=name)

    def test_endpoint_registry_covers_all_routes(self):
        from core.context_processors import endpoints
        mapping = endpoints(None)['ENDPOINTS']
        # Every logical endpoint resolves to an existing URL pattern
        for name in self.PAGES + [
            'claim_meal_ticket', 'book_transport_ticket', 'book_appointment', 'login', 'logout',
            'settings', 'profile', 'sys_admin', 'cafeteria_admin', 'club_admin',
        ]:
            with self.subTest(endpoint=name):
                self.assertIn(name, mapping)
                resolve(mapping[name])


class UnifiedHeaderTest(TestCase):
    """Every standalone public page shares the exact same top navigation header.

    ``TestCase`` (not ``SimpleTestCase``) because the notices and academic
    notes pages query the database for live content.
    """

    PAGES = [
        'dashboard',
        'transport_dashboard',
        'meal_dashboard',
        'clubs_dashboard',
        'checkout',
        'medical',
        'notices',
        'academic_notes',
        'research_ai',
        'departments',
    ]

    NAV_LINKS = ['Dashboard', 'Academic Notes', 'Departments', 'Research AI', 'Notices', 'Transport', 'Meals', 'Medical', 'Clubs', 'Tickets']

    def test_pages_render_shared_header(self):
        for name in self.PAGES:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'CampusDash')
                self.assertContains(response, 'class="brand"')
                self.assertContains(response, 'href="/dashboard/" class="brand"')
                for label in self.NAV_LINKS:
                    self.assertContains(response, label + '</a>')
                self.assertContains(response, 'id="avatar-btn"')
                self.assertContains(response, 'id="profile-popover"')
                self.assertContains(response, 'data-component="topbar"')
                self.assertContains(response, 'class="navlinks"')
                self.assertContains(response, 'class="profile-actions"')
                # Top-left header group: profile avatar is anchored next to the brand
                self.assertContains(response, 'class="topbar-row"')
                self.assertContains(response, 'class="topbar-left"')
                # The standalone top-right settings gear is gone
                self.assertNotContains(response, 'class="settings-link"')

    def test_active_pill_tracks_current_page(self):
        expected = {
            'dashboard': '/dashboard/',
            'transport_dashboard': '/transport/',
            'meal_dashboard': '/meals/',
            'clubs_dashboard': '/clubs/',
            'medical': '/medical/',
            'notices': '/notices/',
            'academic_notes': '/notes/',
            'research_ai': '/research-ai/',
            'departments': '/departments/',
        }
        for name, url in expected.items():
            with self.subTest(page=name):
                html = self.client.get(reverse(name)).content.decode()
                self.assertIn('href="' + url + '" class="active"', html)


class ProfilePopoverAuthTest(TestCase):
    """The shared profile popover reflects the authenticated state."""

    def setUp(self):
        self.user = User.objects.create_user(username='rifat', password='x12345678')

    def test_popover_shows_user_and_sign_out_when_authenticated(self):
        self.client.login(username='rifat', password='x12345678')
        html = self.client.get(reverse('medical')).content.decode()
        self.assertIn('>rifat<', html)
        self.assertIn('Sign Out', html)
        self.assertIn(reverse('logout'), html)
        self.assertIn('Switch Account', html)
        self.assertIn('href="' + reverse('settings') + '"', html)
        self.assertIn('href="' + reverse('signup') + '"', html)
        # Notifications entry opens the bell dropdown from the profile menu
        self.assertIn('Notifications', html)
        self.assertIn('id="profile-notif-link"', html)

    def test_popover_shows_guest_and_sign_in_when_anonymous(self):
        html = self.client.get(reverse('medical')).content.decode()
        self.assertIn('>Guest<', html)
        self.assertIn('Not signed in', html)
        self.assertIn('Sign In', html)
        self.assertIn('> Sign Up</a>', html)
        self.assertIn('href="' + reverse('settings') + '"', html)
        self.assertIn('href="' + reverse('signup') + '"', html)
        # Guests have no bell, so the Notifications entry is not rendered in
        # the profile menu (only the JS helper references the id).
        self.assertNotIn('class="profile-notif-link"', html)


class CheckoutPageTest(TestCase):
    """Payment gateway & checkout page renders and is wired from clubs/transport/meals.

    ``TestCase`` because the clubs page now lists live ``Club`` / ``ClubEvent``
    rows from the database.
    """

    def test_checkout_page_renders_core_sections(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        for needle in [
            'Order Summary',
            'Student Verification',
            'bKash',
            'Nagad',
            'Rocket / Card',
            'Transaction ID (TrxID)',
            '9J32X8KL',
            '01712-345678',
            'Confirm &amp; Pay',
            'Payments are verified by the event coordinator or automated system.',
        ]:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_clubs_page_links_to_checkout(self):
        html = self.client.get(reverse('clubs_dashboard')).content.decode()
        self.assertIn(reverse('checkout'), html)

    def test_transport_page_links_to_checkout(self):
        html = self.client.get(reverse('transport_dashboard')).content.decode()
        self.assertIn(reverse('checkout'), html)

    def test_meals_page_links_to_checkout(self):
        html = self.client.get(reverse('meal_dashboard')).content.decode()
        self.assertIn(reverse('checkout'), html)

    def test_meals_page_shows_monthly_subscription(self):
        html = self.client.get(reverse('meal_dashboard')).content.decode()
        self.assertIn('meal-sub', html)
        self.assertIn('Monthly Meal Subscription', html)
        # Static banner text (rendered markup, not JS source)
        self.assertIn('Pay your monthly fee to claim tickets.', html)


class ResearchAIPageTest(SimpleTestCase):
    """Academic Research & Thesis Assistant page renders all core sections."""

    def test_page_renders_core_sections(self):
        response = self.client.get(reverse('research_ai'))
        self.assertEqual(response.status_code, 200)
        for needle in [
            'Academic Research &amp; Thesis Assistant',
            'Brainstorm literature reviews, summarize methodology papers, analyze IEEE-style citations, and edit your academic draft.',
            'Upload Paper / Abstract',
            'Recent Research Threads',
            'Superposition Circuit Analysis',
            'Textile IoT Automation Models',
            'IEEE',
            'APA 7',
            'Quick Prompt Starters',
            'Draft Literature Review',
            'Methodology Breakdown',
            'Check Citation Formatting',
            'Ready for Query',
            'Current Reference:',
            'Ask a thesis question, paste an excerpt, or type /summarize...',
            'Send',
        ]:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_upload_dropzone_present(self):
        response = self.client.get(reverse('research_ai'))
        self.assertContains(response, 'id="dropzone"')
        self.assertContains(response, 'accept=".pdf,.docx"')

    def test_citation_selector_offers_all_styles(self):
        response = self.client.get(reverse('research_ai'))
        for style in ['IEEE', 'APA 7', 'Harvard', 'Chicago']:
            self.assertContains(response, 'value="' + style + '"', msg_prefix=style)


class DepartmentsPageTest(TestCase):
    """Department Directory (/departments/) and Detail Hub (/departments/<slug>/)
    render live ``Department`` rows seeded by the data migration.
    """

    SLUGS = ['fde', 'cse', 'tex', 'eee', 'ipe']

    def test_directory_renders_hero_search_and_quick_jump(self):
        response = self.client.get(reverse('departments'))
        self.assertEqual(response.status_code, 200)
        for needle in [
            'Academic Departments &amp; Faculties',
            'id="dept-search"',
            'Search departments',
            'Jump to',
            'id="dept-grid"',
            'Explore Department',
            'Department Notes',
        ]:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_directory_lists_every_seeded_department(self):
        html = self.client.get(reverse('departments')).content.decode()
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                self.assertIn('data-slug="' + slug + '"', html)
                self.assertIn('href="/departments/' + slug + '/"', html)
        # Live data (not mock JS) drives the cards
        self.assertNotIn('const DEPARTMENTS', html)
        self.assertIn('Computer Science &amp; Engineering', html)
        self.assertIn('Prof. Dr. Md. Ashraful Alam', html)

    def test_every_slug_renders_detail_hub(self):
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                response = self.client.get(reverse('department_detail', args=[slug]))
                self.assertEqual(response.status_code, 200)
                for needle in [
                    'data-dept-slug="' + slug + '"',
                    'id="dept-head"',
                    'id="dept-tabs"',
                    'Overview &amp; Announcements',
                    'Faculty Directory',
                    'Class &amp; Lab Schedule',
                    'Department Notes',
                    'Browse All Notes',
                    'data-base="/departments/"',
                ]:
                    self.assertContains(response, needle, msg_prefix=slug + ':' + needle)

    def test_detail_hub_shows_live_department_content(self):
        html = self.client.get(reverse('department_detail', args=['cse'])).content.decode()
        # Seeded database rows — department, HOD, faculty, and class routine
        self.assertIn('Computer Science &amp; Engineering', html)
        self.assertIn('Prof. Dr. Md. Ashraful Alam', html)
        self.assertIn('CSE-101 Programming Fundamentals', html)
        self.assertIn('Dr. Tanvir Ahmed', html)
        self.assertIn('cse.hod@niter.edu.bd', html)
        self.assertIn('Room D-205, Academic Block D', html)
        self.assertNotIn('DEPT_DATA', html)  # no mock JS registry anymore

    def test_detail_hub_uses_shared_header(self):
        html = self.client.get(reverse('department_detail', args=['fde'])).content.decode()
        self.assertIn('CampusDash', html)
        self.assertIn('id="avatar-btn"', html)
        self.assertIn('id="profile-popover"', html)
        self.assertIn('href="/departments/" class="active"', html)  # active Departments pill

    def test_unknown_slug_returns_404(self):
        response = self.client.get(reverse('department_detail', args=['unknown-dept']))
        self.assertEqual(response.status_code, 404)

    def test_directory_does_not_show_departments_outside_the_db(self):
        html = self.client.get(reverse('departments')).content.decode()
        self.assertNotIn('does-not-exist', html)
        self.assertEqual(Department.objects.count(), len(self.SLUGS))


class AccountAndAdminPagesTest(TestCase):
    """Signup, settings, profile, and the three staff admin dashboards."""

    def setUp(self):
        self.staff = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        self.student = User.objects.create_user(
            username='S1001', password='student123',
            first_name='Alice', last_name='Johnson', email='alice@niter.edu.bd',
        )
        StudentProfile.objects.create(user=self.student, student_id='S1001', department='CSE')

    # ------------------------------------------------------------------
    # Access control
    # ------------------------------------------------------------------
    def test_admin_pages_redirect_anonymous_to_login(self):
        for name in ['sys_admin', 'cafeteria_admin', 'club_admin']:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)

    def test_admin_pages_require_staff(self):
        # Logged-in non-staff users are sent back to the login page
        self.client.login(username='S1001', password='student123')
        for name in ['sys_admin', 'cafeteria_admin', 'club_admin']:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)

    def test_profile_and_settings_redirect_anonymous_to_login(self):
        for name in ['profile', 'settings']:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)

    # ------------------------------------------------------------------
    # System admin dashboard
    # ------------------------------------------------------------------
    def test_system_admin_renders_all_four_tabs(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('sys_admin'))
        self.assertEqual(response.status_code, 200)
        for needle in [
            'System Admin Dashboard',
            'Users &amp; Roles',
            'Notices &amp; Materials',
            'Transport Management',
            'AI Vector DB &amp; Security',
            'Role &amp; Permission Matrix',
            'Live Bus Status',
            'Driver Updates',
            'Boarding Scans',
            'System Security Logs',
            'Local AI Vector DB',
        ]:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_cafeteria_admin_renders_core_sections(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('cafeteria_admin'))
        self.assertEqual(response.status_code, 200)
        for needle in [
            'Cafeteria Admin',
            'Daily Meal Slot Capacity',
            'Kitchen Inventory',
            'QR Token / Meal Coupon Redemption',
            'Breakfast',
            'Basmati Rice',
            'Redeemed At',
            'Active meal subscriptions',
        ]:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_club_admin_renders_core_sections(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('club_admin'))
        self.assertEqual(response.status_code, 200)
        for needle in [
            'Club Management',
            'Member Approvals',
            'Role Assignments',
            'Event Post Creator',
            'Transaction Verifier',
            'bKash',
            'Nagad',
            'Rocket',
        ]:
            self.assertContains(response, needle, msg_prefix=needle)

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------
    def test_profile_renders_id_card_and_activity(self):
        self.client.login(username='S1001', password='student123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        for needle in [
            'My Profile',
            'Virtual ID Card',
            'Booking &amp; Activity History',
            'Alice Johnson',
            'S1001',
            'Computer Science &amp; Engineering',
            'id-qr',
            'Active Medical Appointments',
            'Transport Tickets',
            'Meal Coupons',
        ]:
            self.assertContains(response, needle, msg_prefix=needle)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------
    def test_settings_renders_preferences(self):
        self.client.login(username='S1001', password='student123')
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        for needle in [
            'Account Settings',
            'Password Reset',
            'Notification Preferences',
            'Theme',
            'old_password',
            'new_password1',
            'new_password2',
        ]:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_settings_password_change(self):
        self.client.login(username='S1001', password='student123')
        response = self.client.post(reverse('settings'), {
            'old_password': 'student123',
            'new_password1': 'newpass1234',
            'new_password2': 'newpass1234',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'updated successfully')
        # Old password no longer works; the new one does
        self.client.logout()
        self.assertFalse(self.client.login(username='S1001', password='student123'))
        self.assertTrue(self.client.login(username='S1001', password='newpass1234'))

    # ------------------------------------------------------------------
    # Signup
    # ------------------------------------------------------------------
    def test_signup_page_renders_form(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        for needle in ['Create Account', 'Student ID', 'Full Name', 'Department', 'Email', 'Password']:
            self.assertContains(response, needle, msg_prefix=needle)
        for code in ['CSE', 'TEX', 'IPE', 'FDAE', 'EEE']:
            self.assertContains(response, 'value="' + code + '"', msg_prefix=code)

    def test_signup_creates_user_and_profile(self):
        response = self.client.post(reverse('signup'), {
            'student_id': 'S2001',
            'full_name': 'Rifat Hasan',
            'department': 'CSE',
            'email': 'rifat@niter.edu.bd',
            'password': 'secretpass1',
            'confirm_password': 'secretpass1',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='S2001').exists())
        profile = StudentProfile.objects.get(student_id='S2001')
        self.assertEqual(profile.user.username, 'S2001')
        self.assertEqual(profile.department, 'CSE')
        # The new student is signed in automatically
        self.assertEqual(int(self.client.session['_auth_user_id']), profile.user.id)

    def test_signup_rejects_duplicate_student_id(self):
        response = self.client.post(reverse('signup'), {
            'student_id': 'S1001',  # already taken by setUp
            'full_name': 'Someone Else',
            'department': 'TEX',
            'email': 'x@niter.edu.bd',
            'password': 'secretpass1',
            'confirm_password': 'secretpass1',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')

    def test_signup_rejects_short_password(self):
        response = self.client.post(reverse('signup'), {
            'student_id': 'S2002',
            'full_name': 'Short Pass',
            'department': 'EEE',
            'email': 'sp@niter.edu.bd',
            'password': 'short',
            'confirm_password': 'short',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'at least 8 characters')
        self.assertFalse(User.objects.filter(username='S2002').exists())


class StaffAdminBackendTest(TestCase):
    """Persistent staff/admin action endpoints — permissions and state changes.

    Covers QR meal redemption, medical appointment status transitions (with
    student notification), club transaction verification, and admin role
    updates — the four persistent backends behind the admin dashboards.
    """

    def setUp(self):
        self.superuser = User.objects.create_superuser(username='root', password='rootpass123')
        self.staff = User.objects.create_user(username='staff', password='staffpass123', is_staff=True)
        self.student = User.objects.create_user(
            username='S9001', password='x12345678',
            first_name='Rifat', last_name='Hasan', email='r@niter.edu.bd',
        )
        StudentProfile.objects.create(user=self.student, student_id='S9001', department='CSE')

    # ------------------------------------------------------------------
    # redeem_meal_ticket — /api/cafeteria/redeem/
    # ------------------------------------------------------------------
    def _make_ticket(self, **kwargs):
        defaults = {'user': self.student, 'meal_type': 'lunch', 'ticket_token': '#MEAL-1234'}
        defaults.update(kwargs)
        return MealTicket.objects.create(**defaults)

    def test_redeem_requires_staff(self):
        response = self.client.post(reverse('api_cafeteria_redeem'), {'token': '#MEAL-1234'})
        self.assertEqual(response.status_code, 302)
        # Authenticated non-staff student is also redirected (staff guard)
        self.client.login(username='S9001', password='x12345678')
        response = self.client.post(reverse('api_cafeteria_redeem'), {'token': '#MEAL-1234'})
        self.assertEqual(response.status_code, 302)

    def test_redeem_marks_ticket_redeemed(self):
        ticket = self._make_ticket()
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(reverse('api_cafeteria_redeem'), {'token': '#MEAL-1234'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['token'], '#MEAL-1234')
        self.assertEqual(data['student'], 'Rifat Hasan')
        self.assertEqual(data['meal'], 'Lunch')
        ticket.refresh_from_db()
        self.assertTrue(ticket.is_redeemed)
        self.assertIsNotNone(ticket.redeemed_at)

    def test_redeem_rejects_already_redeemed(self):
        self._make_ticket(is_redeemed=True, redeemed_at=timezone.now())
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(reverse('api_cafeteria_redeem'), {'token': '#MEAL-1234'})
        self.assertEqual(response.status_code, 409)

    def test_redeem_rejects_invalid_token_format(self):
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(reverse('api_cafeteria_redeem'), {'token': 'MEAL-1234'})
        self.assertEqual(response.status_code, 400)

    def test_redeem_404_for_unknown_token(self):
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(reverse('api_cafeteria_redeem'), {'token': '#MEAL-9999'})
        self.assertEqual(response.status_code, 404)

    def test_redeem_requires_post(self):
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get(reverse('api_cafeteria_redeem'))
        self.assertEqual(response.status_code, 405)

    # ------------------------------------------------------------------
    # update_appointment_status — /api/medical/appointments/<id>/status/
    # ------------------------------------------------------------------
    def _make_appointment(self, **kwargs):
        defaults = {
            'user': self.student,
            'doctor_name': 'Dr. Ahmed Khan',
            'appointment_date': timezone.now().date(),
            'time_slot': '10:00',
            'reason': 'Fever',
        }
        defaults.update(kwargs)
        return MedicalAppointment.objects.create(**defaults)

    def test_appointment_status_requires_staff(self):
        appt = self._make_appointment()
        response = self.client.post(
            reverse('api_appointment_status', args=[appt.pk]), {'status': 'confirmed'},
        )
        self.assertEqual(response.status_code, 302)

    def test_appointment_status_persists_and_notifies_student(self):
        appt = self._make_appointment()
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(
            reverse('api_appointment_status', args=[appt.pk]),
            {'status': 'confirmed'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'confirmed')
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'confirmed')
        notification = Notification.objects.get(user=self.student, category='medical')
        self.assertIn('now Confirmed', notification.message)

    def test_appointment_status_rejects_invalid_status(self):
        appt = self._make_appointment()
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(
            reverse('api_appointment_status', args=[appt.pk]), {'status': 'bogus'},
        )
        self.assertEqual(response.status_code, 400)

    def test_appointment_status_404_for_unknown(self):
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(
            reverse('api_appointment_status', args=[99999]), {'status': 'confirmed'},
        )
        self.assertEqual(response.status_code, 404)

    def test_appointment_status_form_post_redirects_back(self):
        appt = self._make_appointment()
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(
            reverse('api_appointment_status', args=[appt.pk]), {'status': 'completed'},
        )
        self.assertEqual(response.status_code, 302)
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'completed')

    # ------------------------------------------------------------------
    # verify_club_transaction_view — /api/clubs/verify-transaction/
    # ------------------------------------------------------------------
    def test_verify_transaction_requires_staff(self):
        response = self.client.post(
            reverse('api_club_verify_transaction'), {'sheet_url': 'x', 'trx': 'ABC123'},
        )
        self.assertEqual(response.status_code, 302)

    def test_verify_transaction_updates_sheet_and_notifies_student(self):
        matched = {'Name': 'Rifat Hasan', 'Student ID': 'S9001', 'TrxID': '9J32X8KL', 'Status': 'Pending'}
        self.client.login(username='staff', password='staffpass123')
        with mock.patch('core.views.verify_club_transaction', return_value=matched) as service:
            response = self.client.post(
                reverse('api_club_verify_transaction'),
                {'sheet_url': 'https://docs.google.com/spreadsheets/d/abc', 'trx': '9J32X8KL'},
            )
            service.assert_called_once_with(
                'https://docs.google.com/spreadsheets/d/abc', '9J32X8KL', self.staff,
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['notified'])
        self.assertEqual(data['student'], 'Rifat Hasan')
        notification = Notification.objects.get(user=self.student, category='club')
        self.assertIn('9J32X8KL', notification.message)

    def test_verify_transaction_auth_required_returns_401(self):
        from core.google_service import GoogleAccountNotConnected
        self.client.login(username='staff', password='staffpass123')
        with mock.patch('core.views.verify_club_transaction', side_effect=GoogleAccountNotConnected('nope')):
            response = self.client.post(
                reverse('api_club_verify_transaction'), {'sheet_url': 'x', 'trx': 'ABC123'},
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['status'], 'auth_required')

    def test_verify_transaction_no_match_returns_400(self):
        from core.google_service import GoogleServiceError
        self.client.login(username='staff', password='staffpass123')
        with mock.patch(
            'core.views.verify_club_transaction',
            side_effect=GoogleServiceError('No transaction with TrxID ABC123 found in the sheet.'),
        ):
            response = self.client.post(
                reverse('api_club_verify_transaction'), {'sheet_url': 'x', 'trx': 'ABC123'},
            )
        self.assertEqual(response.status_code, 400)

    def test_verify_transaction_requires_fields(self):
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(reverse('api_club_verify_transaction'), {'sheet_url': 'x'})
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------
    # update_user_role — /api/admin/update-role/
    # ------------------------------------------------------------------
    def test_update_role_requires_superuser(self):
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(
            reverse('api_admin_update_role'), {'user_id': self.student.pk, 'role': 'staff'},
        )
        self.assertEqual(response.status_code, 403)

    def test_update_role_promotes_student_to_staff(self):
        self.client.login(username='root', password='rootpass123')
        response = self.client.post(
            reverse('api_admin_update_role'), {'user_id': self.student.pk, 'role': 'staff'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_staff)
        self.assertFalse(self.student.is_superuser)

    def test_update_role_toggles_superuser_and_back(self):
        self.client.login(username='root', password='rootpass123')
        self.client.post(reverse('api_admin_update_role'), {'user_id': self.staff.pk, 'role': 'superuser'})
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_staff)
        self.assertTrue(self.staff.is_superuser)
        self.client.post(reverse('api_admin_update_role'), {'user_id': self.staff.pk, 'role': 'student'})
        self.staff.refresh_from_db()
        self.assertFalse(self.staff.is_staff)
        self.assertFalse(self.staff.is_superuser)

    def test_update_role_blocks_self_change(self):
        self.client.login(username='root', password='rootpass123')
        response = self.client.post(
            reverse('api_admin_update_role'), {'user_id': self.superuser.pk, 'role': 'student'},
        )
        self.assertEqual(response.status_code, 400)
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.is_superuser)

    def test_update_role_blocks_demoting_last_superuser(self):
        self.client.login(username='root', password='rootpass123')
        response = self.client.post(
            reverse('api_admin_update_role'), {'user_id': self.superuser.pk, 'role': 'staff'},
        )
        self.assertEqual(response.status_code, 400)

    def test_update_role_rejects_invalid_role(self):
        self.client.login(username='root', password='rootpass123')
        response = self.client.post(
            reverse('api_admin_update_role'), {'user_id': self.student.pk, 'role': 'admin'},
        )
        self.assertEqual(response.status_code, 400)


class LoginFlowTests(TestCase):
    """Authentication routes: login page, sign-in, and logout."""

    def setUp(self):
        self.user = User.objects.create_user(username='student', password='student123')

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Niter Hub')
        self.assertContains(response, 'Skip login')
        self.assertContains(response, reverse('dashboard'))

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': 'student',
            'password': 'student123',
        })
        self.assertRedirects(response, '/dashboard/')

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse('login'), {
            'username': 'student',
            'password': 'wrong-password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'auth-alert')

    def test_login_redirects_authenticated_user(self):
        self.client.login(username='student', password='student123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, '/dashboard/')

    def test_logout_redirects_home(self):
        self.client.login(username='student', password='student123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')


class EditablePageRenderTest(TestCase):
    """Public renderer for builder-authored pages at /page/<slug>/."""

    def setUp(self):
        self.template = PageTemplate.objects.create(
            name='Standard Page',
            layout_json={'sections': [{'name': 'hero'}, {'name': 'body'}]},
        )
        self.page = EditablePage.objects.create(
            title='Research AI',
            slug='research-ai',
            page_type='global',
            template=self.template,
            custom_css='.content-block { margin-bottom: 2rem; }',
        )
        self.hero = ContentBlock.objects.create(
            page=self.page,
            element_id='hero-title',
            content_html='<h1>Hello from the database</h1>',
            style_json={'textAlign': 'center', 'paddingTop': '24px'},
        )

    def test_published_page_renders_blocks(self):
        response = self.client.get(reverse('editable_page', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Research AI')
        self.assertContains(response, 'Hello from the database')
        self.assertContains(response, 'id="hero-title"')
        self.assertContains(response, 'data-editable-id="hero-title"')
        self.assertContains(response, 'data-page-slug="research-ai"')
        # Shared top navigation is present
        self.assertContains(response, 'CampusDash')
        self.assertContains(response, 'id="avatar-btn"')

    def test_camel_case_styles_are_flattened_to_css(self):
        response = self.client.get(reverse('editable_page', args=[self.page.slug]))
        self.assertContains(response, 'style="text-align: center; padding-top: 24px"')

    def test_custom_css_is_injected(self):
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        self.assertIn('.content-block { margin-bottom: 2rem; }', html)

    def test_unpublished_page_returns_404(self):
        self.page.is_published = False
        self.page.save()
        response = self.client.get(reverse('editable_page', args=[self.page.slug]))
        self.assertEqual(response.status_code, 404)

    def test_unknown_slug_returns_404(self):
        response = self.client.get(reverse('editable_page', args=['does-not-exist']))
        self.assertEqual(response.status_code, 404)

    def test_page_without_blocks_shows_empty_state(self):
        empty = EditablePage.objects.create(title='Empty', slug='empty-page')
        response = self.client.get(reverse('editable_page', args=['empty-page']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'has no content yet')

    def test_multiple_blocks_render_in_creation_order(self):
        ContentBlock.objects.create(
            page=self.page,
            element_id='hero-subtitle',
            content_html='<p>Built by the Website Builder.</p>',
        )
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        # hero-title (created first) appears before hero-subtitle
        self.assertLess(html.index('id="hero-title"'), html.index('id="hero-subtitle"'))


class BuilderBackendTest(TestCase):
    """Phase 2 — Website Builder backend: permission guard, template tag, API."""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='root', email='root@niter.edu.bd', password='rootpass123',
        )
        self.staff = User.objects.create_user(
            username='staff', password='staffpass123', is_staff=True,
        )
        self.template = PageTemplate.objects.create(name='Standard', layout_json={'sections': [{'name': 'hero'}]})
        self.page = EditablePage.objects.create(
            title='Research AI', slug='research-ai', template=self.template,
        )
        ContentBlock.objects.create(
            page=self.page, element_id='hero', content_html='<h1>Saved hero</h1>',
        )

    # ------------------------------------------------------------------
    # superuser_required permission guard
    # ------------------------------------------------------------------
    def test_builder_pages_redirect_anonymous_to_login(self):
        for name in ['builder_dashboard', 'visual_editor']:
            with self.subTest(page=name):
                kwargs = {'page_slug': 'research-ai'} if name == 'visual_editor' else {}
                response = self.client.get(reverse(name, kwargs=kwargs))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)

    def test_builder_pages_return_403_for_non_superuser_staff(self):
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get(reverse('builder_dashboard'))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('visual_editor', args=[self.page.slug]))
        self.assertEqual(response.status_code, 403)

    def test_save_apis_return_403_for_non_superusers(self):
        # Anonymous
        response = self.client.post(
            reverse('save_content_block'), data='{}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 302)
        # Authenticated non-superuser
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(
            reverse('save_content_block'), data='{}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    # ------------------------------------------------------------------
    # builder_dashboard & visual_editor
    # ------------------------------------------------------------------
    def test_builder_dashboard_lists_pages_and_templates(self):
        self.client.login(username='root', password='rootpass123')
        response = self.client.get(reverse('builder_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Website Builder')
        self.assertContains(response, 'Research AI')
        self.assertContains(response, 'Standard')
        self.assertContains(response, reverse('visual_editor', args=['research-ai']))

    def test_builder_dashboard_has_create_page_modal(self):
        self.client.login(username='root', password='rootpass123')
        response = self.client.get(reverse('builder_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Page')
        self.assertContains(response, 'id="create-page-form"')
        self.assertContains(response, 'name="template_id"')
        self.assertContains(response, 'Template Blueprints')

    # ------------------------------------------------------------------
    # create_page API
    # ------------------------------------------------------------------
    def test_create_page_creates_page_with_template(self):
        response = self._post_json('create_page', {
            'title': 'About Us', 'slug': 'about-us', 'template_id': self.template.id,
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['page_slug'], 'about-us')
        self.assertEqual(data['edit_url'], reverse('visual_editor', args=['about-us']))
        page = EditablePage.objects.get(slug='about-us')
        self.assertEqual(page.title, 'About Us')
        self.assertEqual(page.template, self.template)

    def test_create_page_allows_no_template(self):
        response = self._post_json('create_page', {'title': 'Bare', 'slug': 'bare'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EditablePage.objects.get(slug='bare').template, None)

    def test_create_page_rejects_duplicate_slug(self):
        response = self._post_json('create_page', {'title': 'Dup', 'slug': 'research-ai'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('already exists', response.json()['message'])

    def test_create_page_rejects_missing_fields(self):
        response = self._post_json('create_page', {'title': ''})
        self.assertEqual(response.status_code, 400)

    def test_create_page_rejects_invalid_slug(self):
        response = self._post_json('create_page', {'title': 'Bad Slug', 'slug': 'My Page!'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(EditablePage.objects.filter(slug='My Page!').exists())

    def test_create_page_rejects_unknown_template(self):
        response = self._post_json('create_page', {
            'title': 'X', 'slug': 'x-page', 'template_id': 99999,
        })
        self.assertEqual(response.status_code, 400)

    def test_create_page_forbids_non_superuser(self):
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(
            reverse('create_page'), data='{}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_visual_editor_renders_blocks(self):
        self.client.login(username='root', password='rootpass123')
        response = self.client.get(reverse('visual_editor', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editing Research AI')
        self.assertContains(response, 'data-block-id="hero"')
        self.assertContains(response, 'Saved hero')

    def test_visual_editor_404_for_unknown_page(self):
        self.client.login(username='root', password='rootpass123')
        response = self.client.get(reverse('visual_editor', args=['missing']))
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # save_content_block API
    # ------------------------------------------------------------------
    def _post_json(self, name, payload, user='root'):
        self.client.login(username=user, password={'root': 'rootpass123', 'staff': 'staffpass123'}[user])
        return self.client.post(
            reverse(name), data=json.dumps(payload), content_type='application/json',
        )

    def test_save_block_creates_and_updates_block(self):
        response = self._post_json('save_content_block', {
            'page_slug': 'research-ai', 'element_id': 'hero',
            'content_html': '<h1>Updated</h1>', 'style_json': {'textAlign': 'center'},
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        block = ContentBlock.objects.get(page=self.page, element_id='hero')
        self.assertEqual(block.content_html, '<h1>Updated</h1>')
        self.assertEqual(block.style_json, {'textAlign': 'center'})

    def test_save_block_creates_new_element(self):
        response = self._post_json('save_content_block', {
            'page_slug': 'research-ai', 'element_id': 'brand-new',
            'content_html': '<p>Fresh</p>', 'style_json': {},
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContentBlock.objects.filter(page=self.page, element_id='brand-new').exists())

    def test_save_block_sanitizes_html(self):
        response = self._post_json('save_content_block', {
            'page_slug': 'research-ai', 'element_id': 'hero',
            'content_html': '<p>ok</p><script>alert(1)</script><img src="x" onerror="alert(2)"><a href="javascript:alert(3)">link</a><span style="color:red">x</span>',
            'style_json': {},
        })
        self.assertEqual(response.status_code, 200)
        block = ContentBlock.objects.get(page=self.page, element_id='hero')
        self.assertIn('<p>ok</p>', block.content_html)
        self.assertNotIn('<script', block.content_html)
        self.assertNotIn('alert(', block.content_html)
        self.assertNotIn('onerror', block.content_html)
        self.assertNotIn('style=', block.content_html)

    def test_save_block_rejects_missing_fields(self):
        response = self._post_json('save_content_block', {'page_slug': 'research-ai'})
        self.assertEqual(response.status_code, 400)

    def test_save_block_rejects_bad_json(self):
        self.client.login(username='root', password='rootpass123')
        response = self.client.post(
            reverse('save_content_block'), data='not-json', content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_save_block_404_for_unknown_page(self):
        response = self._post_json('save_content_block', {
            'page_slug': 'nope', 'element_id': 'x', 'content_html': '',
        })
        self.assertEqual(response.status_code, 404)

    def test_save_block_requires_post(self):
        self.client.login(username='root', password='rootpass123')
        response = self.client.get(reverse('save_content_block'))
        self.assertEqual(response.status_code, 405)

    # ------------------------------------------------------------------
    # save_page_css API
    # ------------------------------------------------------------------
    def test_save_css_updates_page(self):
        response = self._post_json('save_page_css', {
            'page_slug': 'research-ai', 'custom_css': '.content-block { color: red; }',
        })
        self.assertEqual(response.status_code, 200)
        self.page.refresh_from_db()
        self.assertEqual(self.page.custom_css, '.content-block { color: red; }')

    def test_save_css_strips_style_breakout(self):
        response = self._post_json('save_page_css', {
            'page_slug': 'research-ai',
            'custom_css': '.x{color:red}</style><script>alert(1)</script><!-- boom',
        })
        self.assertEqual(response.status_code, 200)
        self.page.refresh_from_db()
        self.assertIn('.x{color:red}', self.page.custom_css)
        self.assertNotIn('</style', self.page.custom_css)
        self.assertNotIn('</script', self.page.custom_css)
        self.assertNotIn('<!--', self.page.custom_css)

    # ------------------------------------------------------------------
    # render_block template tag
    # ------------------------------------------------------------------
    def _render_tag(self, args):
        tpl = Template("{% load builder_tags %}{% render_block " + args + " %}")
        return tpl.render(Context({}))

    def test_render_block_uses_saved_html(self):
        self.assertEqual(
            self._render_tag("'research-ai' 'hero' 'fallback text'"),
            '<h1>Saved hero</h1>',
        )

    def test_render_block_falls_back_to_default(self):
        self.assertEqual(
            self._render_tag("'research-ai' 'missing' 'fallback text'"),
            'fallback text',
        )

    def test_render_block_falls_back_when_html_is_blank(self):
        ContentBlock.objects.create(page=self.page, element_id='blank', content_html='   ')
        self.assertEqual(
            self._render_tag("'research-ai' 'blank' 'fallback text'"),
            'fallback text',
        )

    def test_render_block_empty_default(self):
        self.assertEqual(self._render_tag("'research-ai' 'missing'"), '')


class GoogleUserTokenTest(TestCase):
    """Google OAuth token persistence (Drive/Sheets backend Phase 1-2)."""

    def setUp(self):
        self.user = User.objects.create_user(username='tania', password='x12345678')
        self.token = GoogleUserToken.objects.create(
            user=self.user,
            access_token='ya29.access',
            refresh_token='1//refresh',
            client_id='app-id.apps.googleusercontent.com',
            client_secret='secret',
            scopes=['email', 'https://www.googleapis.com/auth/drive.file'],
            expiry=timezone.now() + timedelta(hours=1),
        )

    def test_str_reports_username(self):
        self.assertEqual(str(self.token), 'Google OAuth Token - tania')

    def test_is_expired_reflects_expiry(self):
        self.assertFalse(self.token.is_expired)
        self.token.expiry = timezone.now() - timedelta(minutes=1)
        self.token.save()
        self.assertTrue(self.token.is_expired)

    def test_one_to_one_related_name(self):
        self.assertEqual(self.user.google_token, self.token)

    def test_default_token_uri_and_scopes(self):
        self.assertEqual(self.token.token_uri, 'https://oauth2.googleapis.com/token')
        self.assertEqual(self.token.scopes, ['email', 'https://www.googleapis.com/auth/drive.file'])


class GoogleServiceTest(TestCase):
    """Google service layer (Phase 3) with mocked Drive/Sheets APIs."""

    def setUp(self):
        self.user = User.objects.create_user(username='google_user', password='x12345678')
        GoogleUserToken.objects.create(
            user=self.user,
            access_token='ya29.access',
            refresh_token='1//refresh',
            client_id='app-id.apps.googleusercontent.com',
            client_secret='secret',
            scopes=['email', 'https://www.googleapis.com/auth/drive.file'],
            expiry=timezone.now() + timedelta(hours=1),
        )

    # ------------------------------------------------------------------
    # Credential reconstruction
    # ------------------------------------------------------------------
    def test_get_google_credentials_reconstructs_from_token(self):
        from core.google_service import get_google_credentials
        creds = get_google_credentials(self.user)
        self.assertEqual(creds.token, 'ya29.access')
        self.assertEqual(creds.refresh_token, '1//refresh')
        self.assertEqual(creds.token_uri, 'https://oauth2.googleapis.com/token')
        self.assertEqual(creds.client_id, 'app-id.apps.googleusercontent.com')
        self.assertEqual(creds.client_secret, 'secret')
        self.assertIn('https://www.googleapis.com/auth/drive.file', creds.scopes)

    def test_get_google_credentials_raises_without_token(self):
        from core.google_service import GoogleServiceError, get_google_credentials
        orphan = User.objects.create_user(username='no_google', password='x12345678')
        with self.assertRaises(GoogleServiceError):
            get_google_credentials(orphan)

    # ------------------------------------------------------------------
    # Drive notes upload
    # ------------------------------------------------------------------
    def test_upload_note_creates_folder_and_uploads(self):
        from core.google_service import upload_note_to_user_drive
        upload = SimpleUploadedFile('cs101-notes.pdf', b'%PDF-1.4 fake', content_type='application/pdf')
        with mock.patch('core.google_service.build') as mock_build:
            drive = mock_build.return_value
            drive.files().list().execute.return_value = {'files': []}
            # Configure via create.return_value so the setup itself never
            # records a phantom create() call.
            drive.files().create.return_value.execute.side_effect = [
                {'id': 'folder-1'},
                {'id': 'file-1', 'webViewLink': 'https://drive.google.com/file/d/file-1/view'},
            ]
            result = upload_note_to_user_drive(self.user, upload)

            mock_build.assert_called_once_with('drive', 'v3', credentials=mock.ANY)
            list_kwargs = drive.files().list.call_args.kwargs
            self.assertIn("name='CampusDash Notes'", list_kwargs['q'])
            self.assertIn("mimeType='application/vnd.google-apps.folder'", list_kwargs['q'])
            self.assertEqual(drive.files().create.call_count, 2)  # folder + file
            self.assertEqual(result, {
                'file_id': 'file-1',
                'web_link': 'https://drive.google.com/file/d/file-1/view',
            })

    def test_upload_note_reuses_existing_folder(self):
        from core.google_service import upload_note_to_user_drive
        upload = SimpleUploadedFile('note.txt', b'hello', content_type='text/plain')
        with mock.patch('core.google_service.build') as mock_build:
            drive = mock_build.return_value
            drive.files().list().execute.return_value = {
                'files': [{'id': 'folder-1', 'name': 'CampusDash Notes'}],
            }
            drive.files().create.return_value.execute.return_value = {
                'id': 'file-1', 'webViewLink': 'https://drive.google.com/file/d/file-1/view',
            }
            result = upload_note_to_user_drive(self.user, upload)
            self.assertEqual(result['file_id'], 'file-1')
            self.assertEqual(drive.files().create.call_count, 1)  # file only — folder reused

    def test_upload_note_places_file_in_folder(self):
        from core.google_service import upload_note_to_user_drive
        upload = SimpleUploadedFile('note.txt', b'hello')
        with mock.patch('core.google_service.build') as mock_build:
            drive = mock_build.return_value
            drive.files().list().execute.return_value = {'files': []}
            drive.files().create.return_value.execute.side_effect = [
                {'id': 'folder-1'},
                {'id': 'file-1', 'webViewLink': 'https://drive.google.com/file/d/file-1/view'},
            ]
            upload_note_to_user_drive(self.user, upload)
            create_kwargs = drive.files().create.call_args.kwargs
            self.assertEqual(create_kwargs['body']['name'], 'note.txt')
            self.assertEqual(create_kwargs['body']['parents'], ['folder-1'])

    def test_upload_note_wraps_api_failures_in_service_error(self):
        from core.google_service import GoogleServiceError, upload_note_to_user_drive
        upload = SimpleUploadedFile('note.txt', b'hello')
        with mock.patch('core.google_service.build') as mock_build:
            mock_build.side_effect = RuntimeError('network down')
            with self.assertRaises(GoogleServiceError):
                upload_note_to_user_drive(self.user, upload)

    def test_upload_note_accepts_upload_without_content_type(self):
        from core.google_service import upload_note_to_user_drive
        # Bare UploadedFile has no content_type attribute — must not crash.
        upload = SimpleUploadedFile('note.txt', b'hello')
        del upload.content_type
        with mock.patch('core.google_service.build') as mock_build:
            drive = mock_build.return_value
            drive.files().list().execute.return_value = {'files': []}
            drive.files().create.return_value.execute.side_effect = [
                {'id': 'folder-1'},
                {'id': 'file-1', 'webViewLink': 'https://drive.google.com/file/d/file-1/view'},
            ]
            result = upload_note_to_user_drive(self.user, upload)
            self.assertEqual(result['file_id'], 'file-1')
            self.assertEqual(drive.files().create.call_count, 2)

    # ------------------------------------------------------------------
    # Club sheets (gspread)
    # ------------------------------------------------------------------
    def test_get_club_sheet_data_returns_records(self):
        from core.google_service import get_club_sheet_data
        with mock.patch('core.google_service.gspread') as mock_gspread:
            client = mock_gspread.authorize.return_value
            client.open_by_url.return_value.sheet1.get_all_records.return_value = [
                {'Name': 'Alice', 'Amount': '200'},
            ]
            rows = get_club_sheet_data('https://docs.google.com/spreadsheets/d/abc', self.user)
            mock_gspread.authorize.assert_called_once()
            client.open_by_url.assert_called_once_with('https://docs.google.com/spreadsheets/d/abc')
            self.assertEqual(rows, [{'Name': 'Alice', 'Amount': '200'}])

    def test_append_club_sheet_row_appends(self):
        from core.google_service import append_club_sheet_row
        with mock.patch('core.google_service.gspread') as mock_gspread:
            worksheet = mock_gspread.authorize.return_value.open_by_url.return_value.sheet1
            append_club_sheet_row('https://docs.google.com/spreadsheets/d/abc', ['Fahim', '200'], self.user)
            worksheet.append_row.assert_called_once_with(['Fahim', '200'])

    def test_sheets_wrap_api_failures_in_service_error(self):
        from core.google_service import GoogleServiceError, get_club_sheet_data
        with mock.patch('core.google_service.gspread') as mock_gspread:
            mock_gspread.authorize.side_effect = RuntimeError('no network')
            with self.assertRaises(GoogleServiceError):
                get_club_sheet_data('https://docs.google.com/spreadsheets/d/abc', self.user)

    def test_missing_token_raises_not_connected_subclass(self):
        from core.google_service import GoogleAccountNotConnected, get_google_credentials
        orphan = User.objects.create_user(username='no_google_2', password='x12345678')
        with self.assertRaises(GoogleAccountNotConnected):
            get_google_credentials(orphan)

    # ------------------------------------------------------------------
    # Phase 6 — proactive refresh & re-auth
    # ------------------------------------------------------------------
    def test_get_google_credentials_skips_refresh_when_valid(self):
        from core.google_service import get_google_credentials
        from google.oauth2.credentials import Credentials
        with mock.patch.object(Credentials, 'refresh') as mock_refresh:
            creds = get_google_credentials(self.user)
        mock_refresh.assert_not_called()
        self.assertEqual(creds.token, 'ya29.access')

    def test_get_google_credentials_refreshes_expired_token_and_persists(self):
        from core.google_service import get_google_credentials
        from google.oauth2.credentials import Credentials
        token = self.user.google_token
        token.expiry = timezone.now() - timedelta(minutes=5)
        token.save()

        def fake_refresh(creds, request):
            creds.token = 'ya29.refreshed'
            creds.expiry = timezone.now() + timedelta(hours=1)

        with mock.patch.object(Credentials, 'refresh', fake_refresh):
            creds = get_google_credentials(self.user)

        token.refresh_from_db()
        self.assertEqual(creds.token, 'ya29.refreshed')
        self.assertEqual(token.access_token, 'ya29.refreshed')
        self.assertFalse(token.is_expired)

    def test_get_google_credentials_raises_when_expired_without_refresh_token(self):
        from core.google_service import GoogleReauthRequired, get_google_credentials
        token = self.user.google_token
        token.expiry = timezone.now() - timedelta(minutes=5)
        token.refresh_token = ''
        token.save()
        with self.assertRaises(GoogleReauthRequired):
            get_google_credentials(self.user)

    def test_get_google_credentials_wraps_refresh_failure(self):
        from core.google_service import GoogleReauthRequired, get_google_credentials
        from google.auth.exceptions import RefreshError
        from google.oauth2.credentials import Credentials
        token = self.user.google_token
        token.expiry = timezone.now() - timedelta(minutes=5)
        token.save()
        with mock.patch.object(Credentials, 'refresh', side_effect=RefreshError('revoked')):
            with self.assertRaises(GoogleReauthRequired):
                get_google_credentials(self.user)
        token.refresh_from_db()
        self.assertEqual(token.access_token, 'ya29.access')  # stale copy untouched

    def test_upload_note_refresh_failure_wrapped_as_reauth(self):
        from core.google_service import GoogleReauthRequired, upload_note_to_user_drive
        from google.auth.exceptions import RefreshError
        upload = SimpleUploadedFile('note.txt', b'hello')
        with mock.patch('core.google_service.build', side_effect=RefreshError('revoked')):
            with self.assertRaises(GoogleReauthRequired):
                upload_note_to_user_drive(self.user, upload)

    def test_sheets_refresh_failure_wrapped_as_reauth(self):
        from core.google_service import GoogleReauthRequired, get_club_sheet_data
        from google.auth.exceptions import RefreshError
        with mock.patch('core.google_service.gspread') as mock_gspread:
            mock_gspread.authorize.side_effect = RefreshError('revoked')
            with self.assertRaises(GoogleReauthRequired):
                get_club_sheet_data('https://docs.google.com/spreadsheets/d/abc', self.user)


class GoogleApiViewsTest(TestCase):
    """Phase 4 — Google API endpoints (Drive upload + club sheets)."""

    def setUp(self):
        self.user = User.objects.create_user(username='sheet_user', password='x12345678')
        self.client.login(username='sheet_user', password='x12345678')

    # ------------------------------------------------------------------
    # upload_note_view
    # ------------------------------------------------------------------
    def test_upload_note_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('api_upload_note'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_upload_note_requires_post(self):
        response = self.client.get(reverse('api_upload_note'))
        self.assertEqual(response.status_code, 405)

    def test_upload_note_rejects_missing_file(self):
        response = self.client.post(reverse('api_upload_note'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')

    def test_upload_note_rejects_empty_file(self):
        response = self.client.post(reverse('api_upload_note'), {'file': SimpleUploadedFile('empty.txt', b'')})
        self.assertEqual(response.status_code, 400)

    def test_upload_note_success(self):
        upload = SimpleUploadedFile('note.txt', b'hello', content_type='text/plain')
        with mock.patch('core.views.upload_note_to_user_drive', return_value={
            'file_id': 'file-9', 'web_link': 'https://drive.google.com/file/d/file-9/view',
        }) as service:
            response = self.client.post(reverse('api_upload_note'), {'file': upload})
            service.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'status': 'success',
            'file_id': 'file-9',
            'web_link': 'https://drive.google.com/file/d/file-9/view',
        })

    def test_upload_note_not_connected_returns_401_auth_required(self):
        from core.google_service import GoogleAccountNotConnected
        with mock.patch('core.views.upload_note_to_user_drive', side_effect=GoogleAccountNotConnected('not connected')):
            response = self.client.post(
                reverse('api_upload_note'), {'file': SimpleUploadedFile('n.txt', b'x')},
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            'status': 'auth_required',
            'redirect_url': reverse('google_login'),
        })

    def test_upload_note_reauth_required_returns_401(self):
        from core.google_service import GoogleReauthRequired
        with mock.patch('core.views.upload_note_to_user_drive', side_effect=GoogleReauthRequired('session expired')):
            response = self.client.post(
                reverse('api_upload_note'), {'file': SimpleUploadedFile('n.txt', b'x')},
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            'status': 'auth_required',
            'redirect_url': reverse('google_login'),
        })

    def test_upload_note_refresh_error_returns_401(self):
        from google.auth.exceptions import RefreshError
        with mock.patch('core.views.upload_note_to_user_drive', side_effect=RefreshError('revoked')):
            response = self.client.post(
                reverse('api_upload_note'), {'file': SimpleUploadedFile('n.txt', b'x')},
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['status'], 'auth_required')
        self.assertEqual(response.json()['redirect_url'], reverse('google_login'))

    def test_upload_note_service_error_returns_500(self):
        from core.google_service import GoogleServiceError
        with mock.patch('core.views.upload_note_to_user_drive', side_effect=GoogleServiceError('drive exploded')):
            response = self.client.post(
                reverse('api_upload_note'), {'file': SimpleUploadedFile('n.txt', b'x')},
            )
        self.assertEqual(response.status_code, 500)

    # ------------------------------------------------------------------
    # fetch_club_sheet_view
    # ------------------------------------------------------------------
    def test_fetch_sheet_success(self):
        records = [{'Name': 'Alice', 'Amount': '200'}]
        with mock.patch('core.views.get_club_sheet_data', return_value=records) as service:
            response = self.client.get(
                reverse('api_club_sheet_fetch'),
                {'sheet_url': 'https://docs.google.com/spreadsheets/d/abc'},
            )
            service.assert_called_once_with('https://docs.google.com/spreadsheets/d/abc', self.user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'records': records})

    def test_fetch_sheet_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('api_club_sheet_fetch'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_fetch_sheet_requires_url(self):
        response = self.client.get(reverse('api_club_sheet_fetch'))
        self.assertEqual(response.status_code, 400)

    def test_fetch_sheet_not_connected_returns_401_auth_required(self):
        from core.google_service import GoogleAccountNotConnected
        with mock.patch('core.views.get_club_sheet_data', side_effect=GoogleAccountNotConnected('nope')):
            response = self.client.get(reverse('api_club_sheet_fetch'), {'sheet_url': 'https://x'})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['status'], 'auth_required')
        self.assertEqual(response.json()['redirect_url'], reverse('google_login'))

    def test_fetch_sheet_reauth_required_returns_401(self):
        from core.google_service import GoogleReauthRequired
        with mock.patch('core.views.get_club_sheet_data', side_effect=GoogleReauthRequired('expired')):
            response = self.client.get(reverse('api_club_sheet_fetch'), {'sheet_url': 'https://x'})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['status'], 'auth_required')

    # ------------------------------------------------------------------
    # append_club_sheet_view
    # ------------------------------------------------------------------
    def test_append_sheet_success(self):
        with mock.patch('core.views.append_club_sheet_row') as service:
            response = self.client.post(
                reverse('api_club_sheet_append'),
                data=json.dumps({'sheet_url': 'https://docs.google.com/spreadsheets/d/abc', 'row_data': ['Fahim', '200']}),
                content_type='application/json',
            )
            service.assert_called_once_with(
                'https://docs.google.com/spreadsheets/d/abc', ['Fahim', '200'], self.user,
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Row added'})

    def test_append_sheet_requires_login(self):
        self.client.logout()
        response = self.client.post(
            reverse('api_club_sheet_append'),
            data=json.dumps({'sheet_url': 'https://x', 'row_data': []}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 302)

    def test_append_sheet_rejects_missing_row_data(self):
        response = self.client.post(
            reverse('api_club_sheet_append'),
            data=json.dumps({'sheet_url': 'https://x'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_append_sheet_rejects_non_list_row_data(self):
        response = self.client.post(
            reverse('api_club_sheet_append'),
            data=json.dumps({'sheet_url': 'https://x', 'row_data': 'nope'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_append_sheet_rejects_bad_json(self):
        response = self.client.post(
            reverse('api_club_sheet_append'), data='not-json', content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_append_sheet_reauth_required_returns_401(self):
        from core.google_service import GoogleReauthRequired
        with mock.patch('core.views.append_club_sheet_row', side_effect=GoogleReauthRequired('expired')):
            response = self.client.post(
                reverse('api_club_sheet_append'),
                data=json.dumps({'sheet_url': 'https://x', 'row_data': ['Fahim', '200']}),
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            'status': 'auth_required',
            'redirect_url': reverse('google_login'),
        })


class AllauthUrlsTest(TestCase):
    """allauth account URLs are mounted at /accounts/."""

    def test_account_login_url_resolves(self):
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)

    def test_google_login_route_resolves(self):
        # Resolve without hitting the view — GET would attempt to build a
        # Google auth URL, which needs a configured SocialApp.
        match = resolve('/accounts/google/login/')
        self.assertEqual(match.url_name, 'google_login')


class NotificationModelTest(TestCase):
    """Notification model — fields, ordering, cascade, and str()."""

    def setUp(self):
        self.user = User.objects.create_user(username='nuser', password='x12345678')

    def _create(self, title='Alert', category='academic', **kwargs):
        return Notification.objects.create(
            user=self.user, title=title, message='body text', category=category, **kwargs,
        )

    def test_str_reports_title(self):
        self.assertEqual(str(self._create(title='Exam Rescheduled')), 'Exam Rescheduled')

    def test_new_notifications_are_unread_by_default(self):
        self.assertFalse(self._create().is_read)

    def test_created_at_is_auto_set(self):
        self.assertIsNotNone(self._create().created_at)

    def test_category_choices_and_display_labels(self):
        for code, label in Notification.CATEGORY_CHOICES:
            with self.subTest(code=code):
                n = self._create(category=code)
                self.assertEqual(n.get_category_display(), label)

    def test_default_ordering_is_newest_first(self):
        first = self._create(title='First')
        second = self._create(title='Second')
        self.assertEqual(list(Notification.objects.all()), [second, first])

    def test_cascade_delete_with_user(self):
        n = self._create()
        self.user.delete()
        self.assertFalse(Notification.objects.filter(pk=n.pk).exists())


class NotificationApiTest(TestCase):
    """Notification JSON APIs — fetch list + mark-as-read."""

    def setUp(self):
        self.user = User.objects.create_user(username='alert_user', password='x12345678')
        self.other = User.objects.create_user(username='other_user', password='x12345678')
        self.client.login(username='alert_user', password='x12345678')

    def _make(self, user=None, title='Alert', category='academic', is_read=False):
        return Notification.objects.create(
            user=user or self.user, title=title, message='m', category=category, is_read=is_read,
        )

    # ------------------------------------------------------------------
    # fetch_notifications
    # ------------------------------------------------------------------
    def test_fetch_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('api_notifications'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_fetch_returns_unread_count_and_10_most_recent(self):
        for i in range(12):
            self._make(title='n%d' % i)
        self._make(title='read-me', is_read=True)  # newest
        response = self.client.get(reverse('api_notifications'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['unread_count'], 12)  # the read one is excluded
        self.assertEqual(len(data['notifications']), 10)
        titles = [n['title'] for n in data['notifications']]
        self.assertEqual(titles[0], 'read-me')  # newest first
        self.assertNotIn('n0', titles)  # oldest dropped by the :10 cap

    def test_fetch_serializes_notification_fields(self):
        n = self._make(title='Hello', category='meal')
        item = self.client.get(reverse('api_notifications')).json()['notifications'][0]
        self.assertEqual(item['id'], n.pk)
        self.assertEqual(item['title'], 'Hello')
        self.assertEqual(item['message'], 'm')
        self.assertEqual(item['category'], 'meal')
        self.assertIs(item['is_read'], False)
        self.assertIsNotNone(item['created_at'])

    def test_fetch_never_leaks_other_users_notifications(self):
        self._make(user=self.other, title='secret')
        data = self.client.get(reverse('api_notifications')).json()
        self.assertEqual(data['unread_count'], 0)
        self.assertEqual(data['notifications'], [])

    def test_fetch_requires_get(self):
        response = self.client.post(reverse('api_notifications'))
        self.assertEqual(response.status_code, 405)

    # ------------------------------------------------------------------
    # mark_notification_read
    # ------------------------------------------------------------------
    def test_mark_read_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('api_notification_read', args=[1]))
        self.assertEqual(response.status_code, 302)

    def test_mark_read_updates_flag_and_returns_success(self):
        n = self._make()
        response = self.client.post(reverse('api_notification_read', args=[n.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_mark_read_is_idempotent(self):
        n = self._make(is_read=True)
        response = self.client.post(reverse('api_notification_read', args=[n.pk]))
        self.assertEqual(response.status_code, 200)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_mark_read_404_for_other_users_notification(self):
        n = self._make(user=self.other)
        response = self.client.post(reverse('api_notification_read', args=[n.pk]))
        self.assertEqual(response.status_code, 404)
        n.refresh_from_db()
        self.assertFalse(n.is_read)  # untouched

    def test_mark_read_404_for_unknown_id(self):
        response = self.client.post(reverse('api_notification_read', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_mark_read_requires_post(self):
        n = self._make()
        response = self.client.get(reverse('api_notification_read', args=[n.pk]))
        self.assertEqual(response.status_code, 405)


class NotificationConsumerTest(TestCase):
    """Channels WebSocket consumer — user-group membership + payload relay.

    Tests are ``async def`` so the consumer lifecycle (connect, group
    membership, receive) and the push helper share a single event loop — the
    InMemoryChannelLayer only delivers within one loop.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='socket_user', password='x12345678')
        self.other = User.objects.create_user(username='socket_other', password='x12345678')

    async def _open_socket(self, user):
        """Connect a WebsocketCommunicator with an explicit scope user."""
        from channels.testing import WebsocketCommunicator
        from core.consumers import NotificationConsumer
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(), '/ws/notifications/'
        )
        communicator.scope['user'] = user
        connected, _ = await communicator.connect()
        return communicator, connected

    async def test_authenticated_user_connects(self):
        communicator, connected = await self._open_socket(self.user)
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_anonymous_connection_is_rejected(self):
        communicator, connected = await self._open_socket(None)
        self.assertFalse(connected)

    async def test_pushed_payload_is_relayed_to_user_group(self):
        from channels.layers import get_channel_layer
        communicator, connected = await self._open_socket(self.user)
        self.assertTrue(connected)
        payload = {'id': 1, 'title': 'Real-time!', 'category': 'urgent', 'is_read': False}
        await get_channel_layer().group_send(
            'user_%s' % self.user.pk, {'type': 'notification', 'payload': payload},
        )
        self.assertEqual(await communicator.receive_json_from(), payload)
        await communicator.disconnect()

    async def test_other_users_do_not_receive_push(self):
        from channels.layers import get_channel_layer
        communicator, connected = await self._open_socket(self.user)
        self.assertTrue(connected)
        layer = get_channel_layer()
        # Push to the *other* user's group first, then to this user's group:
        # only this user's payload may arrive on the socket.
        await layer.group_send(
            'user_%s' % self.other.pk, {'type': 'notification', 'payload': {'title': 'not yours'}},
        )
        await layer.group_send(
            'user_%s' % self.user.pk, {'type': 'notification', 'payload': {'title': 'mine'}},
        )
        self.assertEqual(await communicator.receive_json_from(), {'title': 'mine'})
        await communicator.disconnect()

    def test_notify_user_broadcasts_to_user_group(self):
        """Sync helper forwards to the correct channel group."""
        from core.consumers import notify_user
        with mock.patch('core.consumers.get_channel_layer') as mock_get_layer:
            mock_get_layer.return_value.group_send = mock.AsyncMock()
            notify_user(self.user.pk, {'title': 'helper'})
        mock_get_layer.return_value.group_send.assert_awaited_once_with(
            'user_%s' % self.user.pk,
            {'type': 'notification', 'payload': {'title': 'helper'}},
        )


class MealSubscriptionModelTest(TestCase):
    """MealSubscription + MealTicket models — fields, expiry, uniqueness."""

    def setUp(self):
        self.user = User.objects.create_user(username='meal_model', password='x12345678')
        self.sub = MealSubscription.objects.create(
            user=self.user,
            expires_at=timezone.now() + timedelta(days=30),
        )

    def test_str_reports_username(self):
        self.assertEqual(str(self.sub), 'Meal subscription - meal_model')

    def test_is_active_defaults_true(self):
        self.assertTrue(self.sub.is_active)

    def test_is_expired_reflects_expiry(self):
        self.assertFalse(self.sub.is_expired)
        self.sub.expires_at = timezone.now() - timedelta(days=1)
        self.sub.save()
        self.assertTrue(self.sub.is_expired)

    def test_meal_ticket_str_and_defaults(self):
        ticket = MealTicket.objects.create(
            user=self.user, meal_type='lunch', ticket_token='#MEAL-1234',
        )
        self.assertEqual(str(ticket), '#MEAL-1234')
        self.assertFalse(ticket.is_redeemed)

    def test_meal_ticket_token_is_unique(self):
        MealTicket.objects.create(user=self.user, meal_type='lunch', ticket_token='#MEAL-0001')
        with self.assertRaises(IntegrityError):
            MealTicket.objects.create(user=self.user, meal_type='dinner', ticket_token='#MEAL-0001')

    def test_meal_ticket_valid_meal_types(self):
        for code, _label in MealTicket.MEAL_TYPE_CHOICES:
            with self.subTest(meal_type=code):
                ticket = MealTicket.objects.create(
                    user=self.user, meal_type=code, ticket_token='#MEAL-' + code,
                )
                self.assertEqual(ticket.get_meal_type_display(), dict(MealTicket.MEAL_TYPE_CHOICES)[code])


class ClaimMealApiTest(TestCase):
    """claim_meal — subscription guard, daily capacity, tokens, notifications."""

    def setUp(self):
        self.user = User.objects.create_user(username='meal_user', password='x12345678')
        self.client.login(username='meal_user', password='x12345678')
        self.sub = MealSubscription.objects.create(
            user=self.user,
            expires_at=timezone.now() + timedelta(days=30),
        )

    def _claim(self, **overrides):
        data = {'meal_type': 'lunch'}
        data.update(overrides)
        return self.client.post(reverse('claim_meal_ticket'), data)

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------
    def test_claim_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('claim_meal_ticket'), {'meal_type': 'lunch'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_claim_requires_post(self):
        response = self.client.get(reverse('claim_meal_ticket'))
        self.assertEqual(response.status_code, 405)

    def test_claim_rejects_invalid_meal_type(self):
        response = self._claim(meal_type='brunch')
        self.assertEqual(response.status_code, 400)

    def test_claim_requires_active_subscription(self):
        self.sub.delete()
        response = self._claim()
        self.assertEqual(response.status_code, 403)
        self.assertFalse(MealTicket.objects.filter(user=self.user).exists())

    def test_claim_rejects_inactive_subscription(self):
        self.sub.is_active = False
        self.sub.save()
        response = self._claim()
        self.assertEqual(response.status_code, 403)

    def test_claim_rejects_expired_subscription(self):
        self.sub.expires_at = timezone.now() - timedelta(days=1)
        self.sub.save()
        response = self._claim()
        self.assertEqual(response.status_code, 403)

    # ------------------------------------------------------------------
    # Success path
    # ------------------------------------------------------------------
    def test_claim_creates_ticket_with_meal_token(self):
        response = self._claim()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertRegex(data['ticket_token'], r'^#MEAL-\d{4}$')
        ticket = MealTicket.objects.get(user=self.user, meal_type='lunch')
        self.assertEqual(ticket.ticket_token, data['ticket_token'])
        self.assertFalse(ticket.is_redeemed)

    def test_claim_creates_meal_notification(self):
        response = self._claim()
        self.assertEqual(response.status_code, 200)
        notification = Notification.objects.get(user=self.user, category='meal')
        self.assertIn('lunch', notification.message)
        self.assertIn('#MEAL-', notification.message)

    def test_claim_creates_websocket_push(self):
        with mock.patch('core.views.notify_user') as mock_push:
            response = self._claim()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_push.called)
        payload = mock_push.call_args[0][1]
        self.assertEqual(payload['category'], 'meal')
        self.assertEqual(payload['is_read'], False)

    # ------------------------------------------------------------------
    # Daily rules
    # ------------------------------------------------------------------
    def test_claim_same_meal_twice_in_day_rejected(self):
        self.assertEqual(self._claim().status_code, 200)
        response = self._claim()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(MealTicket.objects.filter(user=self.user, meal_type='lunch').count(), 1)

    def test_claim_different_meal_same_day_allowed(self):
        self.assertEqual(self._claim(meal_type='breakfast').status_code, 200)
        response = self._claim(meal_type='lunch')
        self.assertEqual(response.status_code, 200)

    def test_claim_respects_daily_capacity(self):
        # Fill the entire lunch capacity with other users, then our claim fails.
        for i in range(2):
            other = User.objects.create_user(username='full_%d' % i, password='x12345678')
            MealTicket.objects.create(
                user=other, meal_type='lunch', ticket_token='#MEAL-%04d' % (5000 + i),
            )
        with mock.patch('core.views.DAILY_MEAL_CAPACITY', {'breakfast': 80, 'lunch': 2, 'dinner': 160}):
            response = self._claim()
        self.assertEqual(response.status_code, 429)
        self.assertFalse(MealTicket.objects.filter(user=self.user, meal_type='lunch').exists())

    def test_claim_generates_unique_tokens(self):
        tokens = set()
        for i in range(5):
            other = User.objects.create_user(username='u_%d' % i, password='x12345678')
            MealSubscription.objects.create(user=other, expires_at=timezone.now() + timedelta(days=30))
            self.client.logout()
            self.client.login(username='u_%d' % i, password='x12345678')
            data = self._claim().json()
            tokens.add(data['ticket_token'])
        self.assertEqual(len(tokens), 5)


class TransportBookingModelTest(TestCase):
    """TransportBooking model — unique seat per route+time."""

    def setUp(self):
        self.user = User.objects.create_user(username='transport_model', password='x12345678')

    def _booking(self, seat=1, qr='TR-AAAA11'):
        return TransportBooking.objects.create(
            user=self.user,
            route_name='Route 1: Main Campus Loop',
            departure_time='08:00 AM',
            seat_number=seat,
            qr_token=qr,
        )

    def test_str_reports_route_and_seat(self):
        self.assertEqual(
            str(self._booking(seat=12)), 'Route 1: Main Campus Loop · seat 12',
        )

    def test_same_seat_same_route_rejected_by_db(self):
        self._booking(seat=3, qr='TR-AAAA11')
        with self.assertRaises(IntegrityError):
            self._booking(seat=3, qr='TR-BBBB22')

    def test_same_seat_different_route_allowed(self):
        self._booking(seat=3, qr='TR-AAAA11')
        TransportBooking.objects.create(
            user=self.user,
            route_name='Route 2: Sports Complex Shuttle',
            departure_time='09:30 AM',
            seat_number=3,
            qr_token='TR-BBBB22',
        )
        self.assertEqual(TransportBooking.objects.filter(seat_number=3).count(), 2)

    def test_qr_token_is_unique(self):
        self._booking(qr='TR-AAAA11')
        with self.assertRaises(IntegrityError):
            self._booking(seat=9, qr='TR-AAAA11')


class BookTransportApiTest(TestCase):
    """book_transport — seat availability, atomicity, and duplicate blocking."""

    def setUp(self):
        self.user = User.objects.create_user(username='transport_user', password='x12345678')
        self.client.login(username='transport_user', password='x12345678')

    def _book(self, **overrides):
        data = {
            'route_name': 'Route 1: Main Campus Loop',
            'departure_time': '08:00 AM',
            'seat_number': '7',
        }
        data.update(overrides)
        return self.client.post(reverse('book_transport_ticket'), data)

    def test_book_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('book_transport_ticket'), {'route_name': 'x', 'departure_time': 'y', 'seat_number': '1'})
        self.assertEqual(response.status_code, 302)

    def test_book_requires_post(self):
        response = self.client.get(reverse('book_transport_ticket'))
        self.assertEqual(response.status_code, 405)

    def test_book_rejects_missing_route(self):
        response = self._book(route_name='')
        self.assertEqual(response.status_code, 400)

    def test_book_rejects_non_numeric_seat(self):
        response = self._book(seat_number='12A')
        self.assertEqual(response.status_code, 400)

    def test_book_rejects_seat_out_of_range(self):
        for seat in ('0', '41', '-3'):
            with self.subTest(seat=seat):
                response = self._book(seat_number=seat)
                self.assertEqual(response.status_code, 400)

    def test_book_success_creates_booking_with_qr(self):
        response = self._book()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertRegex(data['qr_token'], r'^TR-[A-F0-9]{6}$')
        booking = TransportBooking.objects.get(user=self.user)
        self.assertEqual(booking.route_name, 'Route 1: Main Campus Loop')
        self.assertEqual(booking.seat_number, 7)
        self.assertEqual(booking.qr_token, data['qr_token'])

    def test_book_accepts_legacy_route_id(self):
        response = self._book(route_id='2', route_name='', departure_time='')
        self.assertEqual(response.status_code, 200)
        booking = TransportBooking.objects.get(user=self.user)
        self.assertEqual(booking.route_name, 'Route 2: Sports Complex Shuttle')
        self.assertEqual(booking.departure_time, '09:30 AM')

    def test_book_creates_transport_notification_and_push(self):
        with mock.patch('core.views.notify_user') as mock_push:
            response = self._book()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notification.objects.get(user=self.user, category='transport').title, 'Transport seat booked')
        self.assertEqual(mock_push.call_args[0][1]['category'], 'transport')

    # ------------------------------------------------------------------
    # Race condition / duplicate blocking
    # ------------------------------------------------------------------
    def test_duplicate_seat_same_route_returns_409(self):
        self.assertEqual(self._book().status_code, 200)
        response = self._book()  # same route, same time, same seat
        self.assertEqual(response.status_code, 409)
        self.assertIn('already taken', response.json()['message'])
        self.assertEqual(TransportBooking.objects.filter(seat_number=7).count(), 1)

    def test_duplicate_seat_does_not_create_notification(self):
        self.assertEqual(self._book().status_code, 200)
        with mock.patch('core.views.notify_user') as mock_push:
            response = self._book()
        self.assertEqual(response.status_code, 409)
        mock_push.assert_not_called()

    def test_same_seat_different_time_is_allowed(self):
        self.assertEqual(self._book().status_code, 200)
        response = self._book(departure_time='09:30 AM')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TransportBooking.objects.filter(seat_number=7).count(), 2)


class MedicalAppointmentModelTest(TestCase):
    """MedicalAppointment model — defaults, choices, and slot uniqueness."""

    def setUp(self):
        self.user = User.objects.create_user(username='medical_model', password='x12345678')

    def _appt(self, slot='10:00'):
        return MedicalAppointment.objects.create(
            user=self.user,
            doctor_name='Dr. Ahmed Khan',
            appointment_date='2026-08-20',
            time_slot=slot,
            reason='Fever',
        )

    def test_status_defaults_to_pending(self):
        self.assertEqual(self._appt().status, 'pending')

    def test_valid_status_choices(self):
        appt = self._appt()
        for code, _label in MedicalAppointment.STATUS_CHOICES:
            with self.subTest(status=code):
                appt.status = code
                appt.save()
                self.assertEqual(appt.get_status_display(), dict(MedicalAppointment.STATUS_CHOICES)[code])

    def test_same_doctor_slot_rejected_by_db(self):
        self._appt(slot='10:00')
        with self.assertRaises(IntegrityError):
            self._appt(slot='10:00')

    def test_same_slot_different_doctor_allowed(self):
        self._appt(slot='10:00')
        MedicalAppointment.objects.create(
            user=self.user,
            doctor_name='Dr. Sarah Smith',
            appointment_date='2026-08-20',
            time_slot='10:00',
            reason='Checkup',
        )
        self.assertEqual(MedicalAppointment.objects.filter(time_slot='10:00').count(), 2)


class BookAppointmentApiTest(TestCase):
    """book_appointment — field validation, atomic booking, slot conflicts."""

    def setUp(self):
        self.user = User.objects.create_user(username='medical_user', password='x12345678')
        self.client.login(username='medical_user', password='x12345678')

    def _book(self, **overrides):
        data = {
            'doctor_name': 'Dr. Ahmed Khan',
            'appointment_date': '2026-08-20',
            'time_slot': '10:00',
            'reason': 'Persistent headache',
        }
        data.update(overrides)
        return self.client.post(reverse('book_appointment'), data)

    def test_book_requires_login(self):
        self.client.logout()
        response = self.client.post(
            reverse('book_appointment'),
            {'doctor_name': 'x', 'appointment_date': '2026-08-20', 'time_slot': '10:00'},
        )
        self.assertEqual(response.status_code, 302)

    def test_book_requires_post(self):
        response = self.client.get(reverse('book_appointment'))
        self.assertEqual(response.status_code, 405)

    def test_book_rejects_missing_fields(self):
        for kwargs in (
            {'doctor_name': ''},
            {'appointment_date': ''},
            {'time_slot': ''},
        ):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self._book(**kwargs).status_code, 400)

    def test_book_rejects_malformed_date(self):
        response = self._book(appointment_date='20-08-2026')
        self.assertEqual(response.status_code, 400)

    def test_book_accepts_legacy_doctor_id(self):
        response = self._book(doctor_name='', doctor='2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            MedicalAppointment.objects.get(user=self.user).doctor_name, 'Dr. Sarah Smith',
        )

    def test_book_success_creates_pending_appointment(self):
        response = self._book()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['appointment_status'], 'pending')
        appointment = MedicalAppointment.objects.get(user=self.user)
        self.assertEqual(appointment.doctor_name, 'Dr. Ahmed Khan')
        self.assertEqual(appointment.reason, 'Persistent headache')

    def test_book_creates_medical_notification_and_push(self):
        with mock.patch('core.views.notify_user') as mock_push:
            response = self._book()
        self.assertEqual(response.status_code, 200)
        notification = Notification.objects.get(user=self.user, category='medical')
        self.assertIn('Dr. Ahmed Khan', notification.message)
        self.assertEqual(mock_push.call_args[0][1]['category'], 'medical')

    # ------------------------------------------------------------------
    # Double-booking conflict
    # ------------------------------------------------------------------
    def test_double_booked_slot_returns_409(self):
        self.assertEqual(self._book().status_code, 200)
        response = self._book()  # same doctor, date, slot
        self.assertEqual(response.status_code, 409)
        self.assertIn('already booked', response.json()['message'])
        self.assertEqual(MedicalAppointment.objects.count(), 1)

    def test_double_booked_slot_does_not_create_notification(self):
        self.assertEqual(self._book().status_code, 200)
        with mock.patch('core.views.notify_user') as mock_push:
            response = self._book()
        self.assertEqual(response.status_code, 409)
        mock_push.assert_not_called()

    def test_same_slot_different_doctor_allowed(self):
        self.assertEqual(self._book().status_code, 200)
        response = self._book(doctor_name='Dr. Sarah Smith')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MedicalAppointment.objects.count(), 2)


class NoticeModelTest(TestCase):
    """Notice model — fields, category labels, ordering, and author cascade."""

    def setUp(self):
        self.author = User.objects.create_user(username='registrar', password='x12345678')

    def _create(self, title='Midterm Schedule', category='academic', **kwargs):
        defaults = {'content': 'body text', 'is_published': True}
        defaults.update(kwargs)
        return Notice.objects.create(
            author=self.author, title=title, category=category, **defaults,
        )

    def test_str_reports_title(self):
        self.assertEqual(str(self._create(title='Exam Rescheduled')), 'Exam Rescheduled')

    def test_category_choices_and_display_labels(self):
        for code, label in Notice.CATEGORY_CHOICES:
            with self.subTest(code=code):
                notice = self._create(category=code)
                self.assertEqual(notice.get_category_display(), label)

    def test_unpublished_by_default(self):
        notice = Notice.objects.create(
            author=self.author, title='Draft', content='x', category='general',
        )
        self.assertFalse(notice.is_published)

    def test_default_ordering_is_newest_first(self):
        first = self._create(title='First')
        second = self._create(title='Second')
        self.assertEqual(list(Notice.objects.all()), [second, first])

    def test_author_cascade_delete(self):
        notice = self._create()
        self.author.delete()
        self.assertFalse(Notice.objects.filter(pk=notice.pk).exists())


class CourseMaterialModelTest(TestCase):
    """Course + CourseMaterial — catalog and file metadata helpers."""

    @classmethod
    def setUpClass(cls):
        cls.MEDIA_ROOT = tempfile.mkdtemp(prefix='niter-test-media-')
        cls._media_override = override_settings(MEDIA_ROOT=cls.MEDIA_ROOT)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.course = Course.objects.create(
            code='CS101', title='Introduction to Programming', department='CSE',
        )

    def test_course_str_and_unique_code(self):
        self.assertEqual(str(self.course), 'CS101 — Introduction to Programming')
        with self.assertRaises(IntegrityError):
            Course.objects.create(
                code='CS101', title='Duplicate', department='TEX',
            )

    def test_course_material_str_and_ordering(self):
        first = CourseMaterial.objects.create(
            course=self.course, title='Lecture 1',
            file=SimpleUploadedFile('lec1.pdf', b'%PDF-1.4 fake', content_type='application/pdf'),
        )
        second = CourseMaterial.objects.create(
            course=self.course, title='Lecture 2',
            file=SimpleUploadedFile('lec2.pdf', b'%PDF-1.4 fake', content_type='application/pdf'),
        )
        self.assertEqual(str(first), 'Lecture 1')
        self.assertEqual(list(CourseMaterial.objects.all()), [second, first])

    def test_display_type_falls_back_to_extension(self):
        material = CourseMaterial.objects.create(
            course=self.course, title='Slides',
            file=SimpleUploadedFile('slides.pptx', b'fake', content_type='application/octet-stream'),
        )
        self.assertEqual(material.display_type, 'PPTX')
        material.file_type = 'PDF'
        material.save()
        self.assertEqual(material.display_type, 'PDF')

    def test_size_display_formats_bytes(self):
        material = CourseMaterial.objects.create(
            course=self.course, title='Small',
            file=SimpleUploadedFile('small.txt', b'hello world'),
        )
        self.assertIn('B', material.size_display)

    def test_course_material_related_name(self):
        CourseMaterial.objects.create(
            course=self.course, title='Notes',
            file=SimpleUploadedFile('n.txt', b'x'),
        )
        self.assertEqual(self.course.materials.count(), 1)


class NoticesPageTest(TestCase):
    """/notices/ — only published Notice rows render, filterable by category."""

    def setUp(self):
        self.author = User.objects.create_user(username='reg', password='x12345678')
        self.published = Notice.objects.create(
            author=self.author, title='Midterm Rescheduled', content='See the portal.',
            category='academic', is_published=True,
        )
        Notice.objects.create(
            author=self.author, title='Secret Draft', content='Hidden.',
            category='general', is_published=False,
        )
        Notice.objects.create(
            author=self.author, title='Power Outage', content='Building A.',
            category='urgent', is_published=True,
        )

    def test_renders_only_published_notices(self):
        response = self.client.get(reverse('notices'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Midterm Rescheduled')
        self.assertContains(response, 'Power Outage')
        self.assertNotContains(response, 'Secret Draft')
        self.assertContains(response, 'Academic')
        self.assertContains(response, 'Urgent')

    def test_category_filter_narrows_results(self):
        response = self.client.get(reverse('notices'), {'category': 'academic'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Midterm Rescheduled')
        self.assertNotContains(response, 'Power Outage')
        # The active pill is marked for server-side filtering
        self.assertContains(response, '?category=academic')

    def test_unknown_category_shows_all(self):
        response = self.client.get(reverse('notices'), {'category': 'bogus'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Midterm Rescheduled')
        self.assertContains(response, 'Power Outage')

    def test_empty_feed_renders_empty_state(self):
        Notice.objects.all().delete()
        response = self.client.get(reverse('notices'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No published notices')

    def test_notice_card_shows_author_and_content(self):
        response = self.client.get(reverse('notices'), {'category': 'academic'})
        self.assertContains(response, 'reg')  # author username fallback
        self.assertContains(response, 'See the portal.')


class CreateNoticeApiTest(TestCase):
    """POST /api/notices/create/ — persistence + broadcast to all students."""

    def setUp(self):
        self.staff = User.objects.create_user(username='staff', password='staffpass123', is_staff=True)
        self.student = User.objects.create_user(username='student1', password='x12345678')
        User.objects.create_user(username='student2', password='x12345678')
        self.client.login(username='staff', password='staffpass123')

    def _post(self, **overrides):
        payload = {
            'title': 'Library Hours Extended',
            'content': 'The library stays open until 10 PM during exams.',
            'category': 'general',
            'status': 'published',
        }
        payload.update(overrides)
        return self.client.post(reverse('api_notices_create'), payload)

    def test_requires_staff(self):
        self.client.logout()
        response = self._post()
        self.assertEqual(response.status_code, 302)
        self.client.login(username='student1', password='x12345678')
        response = self._post()
        self.assertEqual(response.status_code, 302)

    def test_requires_post(self):
        response = self.client.get(reverse('api_notices_create'))
        self.assertEqual(response.status_code, 405)

    def test_creates_published_notice_and_notifies_all_users(self):
        with mock.patch('core.views.notify_user') as mock_push:
            response = self._post()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['is_published'])
        self.assertEqual(data['category'], 'General')
        self.assertEqual(data['notified'], 3)  # staff + 2 students (all active users)
        notice = Notice.objects.get(pk=data['notice_id'])
        self.assertEqual(notice.author, self.staff)
        self.assertEqual(notice.category, 'general')
        # One Notification per active user, all pushed in real time
        self.assertEqual(Notification.objects.filter(category='academic').count(), 3)
        self.assertEqual(mock_push.call_count, 3)
        pushed = mock_push.call_args_list[0][0][1]
        self.assertIn('Library Hours Extended', pushed['title'])

    def test_draft_is_stored_but_never_broadcast(self):
        with mock.patch('core.views.notify_user') as mock_push:
            response = self._post(status='draft')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_published'])
        self.assertEqual(response.json()['notified'], 0)
        self.assertTrue(Notice.objects.filter(title='Library Hours Extended', is_published=False).exists())
        self.assertEqual(Notification.objects.count(), 0)
        mock_push.assert_not_called()

    def test_requires_title_and_content(self):
        response = self._post(title='   ')
        self.assertEqual(response.status_code, 400)
        response = self._post(content='   ')
        self.assertEqual(response.status_code, 400)

    def test_rejects_invalid_category(self):
        response = self._post(category='workshop')
        self.assertEqual(response.status_code, 400)

    def test_urgent_notice_maps_to_urgent_bell_category(self):
        with mock.patch('core.views.notify_user'):
            self._post(title='Fire Drill', category='urgent')
        self.assertTrue(Notification.objects.filter(category='urgent').exists())


class AcademicNotesPageTest(TestCase):
    """/academic-notes/ — live Course folders and CourseMaterial documents."""

    def setUp(self):
        self.course = Course.objects.create(
            code='CS101', title='Intro to Programming', department='CSE',
        )
        Course.objects.create(code='TEX101', title='Fibre Science', department='TEX')

    def test_renders_course_folders_from_catalog(self):
        response = self.client.get(reverse('academic_notes'))
        self.assertEqual(response.status_code, 200)
        # Folder cards group by department code + display the full name.
        self.assertContains(response, 'CSE')
        self.assertContains(response, 'Computer Science &amp; Engineering')
        self.assertContains(response, 'TEX')
        self.assertContains(response, 'Textile Engineering')

    def test_renders_live_materials_with_metadata(self):
        material = CourseMaterial.objects.create(
            course=self.course, title='Lecture 1 Slides',
            file=SimpleUploadedFile('lec1.pdf', b'%PDF-1.4 fake', content_type='application/pdf'),
        )
        response = self.client.get(reverse('academic_notes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lecture 1 Slides')
        self.assertContains(response, 'PDF')  # display_type derived from extension
        self.assertContains(response, 'CS101')  # course code chip on the doc card
        # Material links to its real media URL (Django may dedupe the filename).
        self.assertContains(response, material.file.url)
        self.assertContains(response, '/media/course_materials/')

    def test_empty_catalog_renders_empty_states(self):
        Course.objects.all().delete()
        response = self.client.get(reverse('academic_notes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No courses in the catalog yet.')
        self.assertContains(response, 'No course materials uploaded yet')


class NotesEnginePageTest(TestCase):
    """Notes Engine sidebar is wired to live Course / Department / CourseMaterial
    rows (same catalog as /academic-notes/)."""

    def setUp(self):
        self.course = Course.objects.create(
            code='CS101', title='Intro to Programming', department='CSE',
        )
        self.user = User.objects.create_user(username='note_taker', password='x12345678')
        self.client.login(username='note_taker', password='x12345678')

    def test_renders_live_folders_with_course_counts(self):
        response = self.client.get(reverse('notes'))
        self.assertEqual(response.status_code, 200)
        # Folder name comes from the seeded Department row, count from Course.
        self.assertContains(response, 'Computer Science &amp; Engineering')
        self.assertContains(response, '1 course')

    def test_uses_campusdash_top_pill_header(self):
        # The Notes Engine shares the standalone CampusDash top-pill layout
        # (topbar partial, no left sidebar).
        response = self.client.get(reverse('notes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-component="topbar"')
        self.assertContains(response, 'CampusDash')
        self.assertContains(response, 'id="avatar-btn"')
        self.assertNotContains(response, 'data-region="sidebar"')

    def test_renders_live_materials_with_course_metadata(self):
        material = CourseMaterial.objects.create(
            course=self.course, title='Lecture 1 Slides',
            file=SimpleUploadedFile('lec1.pdf', b'%PDF-1.4 fake', content_type='application/pdf'),
        )
        response = self.client.get(reverse('notes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lecture 1 Slides')
        self.assertContains(response, 'CS101')  # course code chip on the PDF row
        self.assertContains(response, material.file.url)

    def test_empty_catalog_renders_empty_states(self):
        Course.objects.all().delete()
        response = self.client.get(reverse('notes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No course folders yet.')
        self.assertContains(response, 'No course materials uploaded yet.')


class ProfileActivityHistoryTest(TestCase):
    """Profile activity tab reflects the user's real booking rows."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='S1001', password='student123',
            first_name='Alice', last_name='Johnson',
        )
        StudentProfile.objects.create(user=self.user, student_id='S1001', department='CSE')
        self.client.login(username='S1001', password='student123')

    def test_profile_renders_live_activity_records(self):
        MealTicket.objects.create(
            user=self.user, meal_type='lunch', ticket_token='#MEAL-1001',
        )
        TransportBooking.objects.create(
            user=self.user, route_name='Route 1: Main Campus Loop',
            departure_time='08:00 AM', seat_number=7, qr_token='TR-ABCDEF',
        )
        MedicalAppointment.objects.create(
            user=self.user, doctor_name='Dr. Ahmed Khan',
            appointment_date=timezone.now().date(), time_slot='10:00 AM',
            reason='Checkup',
        )
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '#MEAL-1001')
        self.assertContains(response, 'Lunch')
        self.assertContains(response, 'Route 1: Main Campus Loop')
        self.assertContains(response, 'Seat 7')
        self.assertContains(response, 'Dr. Ahmed Khan')
        self.assertContains(response, 'Pending')
        self.assertContains(response, 'Unused')

    def test_profile_shows_empty_states_without_activity(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No medical appointments booked yet.')
        self.assertContains(response, 'No transport tickets booked yet.')
        self.assertContains(response, 'No meal coupons claimed yet.')

    def test_profile_never_leaks_other_users_activity(self):
        other = User.objects.create_user(username='S2002', password='x12345678')
        MealTicket.objects.create(user=other, meal_type='dinner', ticket_token='#MEAL-9999')
        response = self.client.get(reverse('profile'))
        self.assertNotContains(response, '#MEAL-9999')


class DepartmentHubBackendTest(TestCase):
    """Department / FacultyMember / ClassRoutine models + seeded hub data."""

    def test_seeded_departments_exist(self):
        self.assertEqual(Department.objects.count(), 5)
        cse = Department.objects.get(slug='cse')
        self.assertEqual(cse.code, 'CSE')
        self.assertEqual(cse.head_of_dept, 'Prof. Dr. Md. Ashraful Alam')
        self.assertIn('programming', cse.description.lower())

    def test_department_str_and_ordering(self):
        self.assertEqual(str(Department.objects.get(slug='cse')), 'Computer Science & Engineering')
        names = list(Department.objects.values_list('name', flat=True))
        self.assertEqual(names, sorted(names))

    def test_seeded_faculty_are_attached_to_departments(self):
        cse = Department.objects.get(slug='cse')
        self.assertEqual(cse.faculty.count(), 3)
        member = cse.faculty.get(name='Dr. Tanvir Ahmed')
        self.assertEqual(member.designation, 'Associate Professor')
        self.assertIn('@niter.edu.bd', member.email)
        self.assertTrue(member.office_hours)

    def test_faculty_cascade_deletes_with_department(self):
        cse = Department.objects.get(slug='cse')
        cse.delete()
        self.assertEqual(FacultyMember.objects.filter(department__slug='cse').count(), 0)

    def test_seeded_routines_group_by_department_and_day(self):
        cse = Department.objects.get(slug='cse')
        self.assertEqual(cse.class_routines.count(), 4)
        self.assertTrue(cse.class_routines.filter(day_of_week='Sun').exists())
        routine = cse.class_routines.get(subject='CSE-101 Programming Fundamentals')
        self.assertEqual(routine.semester, 'Semester 1')
        self.assertIn('AM', routine.time_slot)

    def test_routine_day_display_label(self):
        routine = ClassRoutine.objects.get(subject='CSE-101 Programming Fundamentals')
        self.assertEqual(routine.get_day_of_week_display(), 'Sunday')


class ClubModelsTest(TestCase):
    """Club / ClubEvent / ClubRegistration models + seeded club data."""

    def test_seeded_clubs_exist(self):
        self.assertEqual(Club.objects.count(), 4)
        computer = Club.objects.get(slug='computer-club')
        self.assertEqual(computer.name, 'Computer Club')
        self.assertIsNone(computer.lead_user)

    def test_club_str_and_unique_slug(self):
        self.assertEqual(str(Club.objects.get(slug='sports-club')), 'Sports Club')
        with self.assertRaises(IntegrityError):
            Club.objects.create(name='Dup', slug='sports-club')

    def test_seeded_events_are_upcoming_and_ordered(self):
        events = list(ClubEvent.objects.order_by('event_date'))
        self.assertEqual(len(events), 4)
        for event in events:
            self.assertGreaterEqual(event.event_date, timezone.now().date())
        dates = [e.event_date for e in events]
        self.assertEqual(dates, sorted(dates))

    def test_event_belongs_to_club(self):
        event = ClubEvent.objects.get(title='CodeStorm — Inter-University Hackathon')
        self.assertEqual(event.club.slug, 'computer-club')
        self.assertTrue(event.capacity > 0)

    def test_registration_unique_per_student_club(self):
        student = User.objects.create_user(username='clubber', password='x12345678')
        club = Club.objects.get(slug='sports-club')
        ClubRegistration.objects.create(student=student, club=club, status='pending')
        with self.assertRaises(IntegrityError):
            ClubRegistration.objects.create(student=student, club=club, status='active')

    def test_registration_defaults_to_pending(self):
        student = User.objects.create_user(username='clubber2', password='x12345678')
        registration = ClubRegistration.objects.create(
            student=student, club=Club.objects.get(slug='sports-club'),
        )
        self.assertEqual(registration.status, 'pending')
        self.assertIsNotNone(registration.joined_at)
        self.assertIn('Sports Club', str(registration))


class ClubsPageTest(TestCase):
    """The /clubs/ student view renders live clubs and upcoming events."""

    def test_clubs_page_lists_seeded_clubs_and_events(self):
        response = self.client.get(reverse('clubs_dashboard'))
        self.assertEqual(response.status_code, 200)
        for needle in [
            'Computer Club',
            'Cultural Society',
            'CodeStorm — Inter-University Hackathon',
            'Spring Cultural Night',
            'data-club-id=',
            'fa-laptop-code',
        ]:
            self.assertContains(response, needle, msg_prefix=needle)
        self.assertNotIn('const CLUBS', response.content.decode())  # no mock array

    def test_clubs_page_counts_active_members(self):
        student = User.objects.create_user(username='m1', password='x12345678')
        club = Club.objects.get(slug='computer-club')
        ClubRegistration.objects.create(student=student, club=club, status='active')
        html = self.client.get(reverse('clubs_dashboard')).content.decode()
        self.assertIn('1 member', html)  # seeded club starts at 0 active

    def test_clubs_page_hides_past_events(self):
        club = Club.objects.get(slug='computer-club')
        ClubEvent.objects.create(
            club=club, title='Old Event', event_date=timezone.now().date() - timedelta(days=1),
        )
        html = self.client.get(reverse('clubs_dashboard')).content.decode()
        self.assertNotIn('Old Event', html)

    def test_clubs_page_links_to_checkout(self):
        html = self.client.get(reverse('clubs_dashboard')).content.decode()
        self.assertIn(reverse('checkout'), html)

    def test_join_button_present_for_every_club(self):
        html = self.client.get(reverse('clubs_dashboard')).content.decode()
        for club in Club.objects.all():
            self.assertIn('data-club-id="%s"' % club.pk, html)


class JoinClubApiTest(TestCase):
    """POST /api/clubs/join/ — membership requests with lead notifications."""

    def setUp(self):
        self.student = User.objects.create_user(
            username='joiner', password='x12345678',
            first_name='Jo', last_name='Iner',
        )
        self.lead = User.objects.create_user(username='leadstaff', password='x12345678', is_staff=True)
        self.club = Club.objects.get(slug='computer-club')
        self.club.lead_user = self.lead
        self.club.save()

    def test_join_requires_login(self):
        response = self.client.post(reverse('api_club_join'), {'club_id': self.club.pk})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_join_requires_post(self):
        self.client.login(username='joiner', password='x12345678')
        response = self.client.get(reverse('api_club_join'))
        self.assertEqual(response.status_code, 405)

    def test_join_creates_pending_registration_and_notifies_lead(self):
        self.client.login(username='joiner', password='x12345678')
        with mock.patch('core.views.notify_user') as mock_push:
            response = self.client.post(reverse('api_club_join'), {'club_id': self.club.pk})
            mock_push.assert_called_once()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['club'], 'Computer Club')
        self.assertEqual(data['registration_status'], 'pending')
        registration = ClubRegistration.objects.get(student=self.student, club=self.club)
        self.assertEqual(registration.status, 'pending')
        notification = Notification.objects.get(user=self.lead, category='club')
        self.assertIn('Jo Iner', notification.message)
        self.assertIn('Computer Club', notification.message)

    def test_join_duplicate_returns_409(self):
        ClubRegistration.objects.create(student=self.student, club=self.club, status='active')
        self.client.login(username='joiner', password='x12345678')
        response = self.client.post(reverse('api_club_join'), {'club_id': self.club.pk})
        self.assertEqual(response.status_code, 409)
        self.assertIn('already requested', response.json()['message'])

    def test_join_unknown_club_returns_404(self):
        self.client.login(username='joiner', password='x12345678')
        response = self.client.post(reverse('api_club_join'), {'club_id': 99999})
        self.assertEqual(response.status_code, 404)

    def test_join_without_lead_still_succeeds(self):
        club = Club.objects.get(slug='sports-club')  # lead_user is None
        self.client.login(username='joiner', password='x12345678')
        response = self.client.post(reverse('api_club_join'), {'club_id': club.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(Notification.objects.filter(category='club').count(), 0)


class DashboardWidgetsTest(TestCase):
    """The /dashboard/ widgets aggregate real database counts (no hardcoding)."""

    def setUp(self):
        self.user = User.objects.create_user(username='widget_user', password='x12345678')

    def test_meal_widget_reflects_todays_claims(self):
        for token in ('#MEAL-1001', '#MEAL-1002'):
            MealTicket.objects.create(user=self.user, meal_type='lunch', ticket_token=token)
        html = self.client.get(reverse('dashboard')).content.decode()
        # 2 claims today → remaining = 440 - 2, used = 2
        self.assertIn('Used: 2', html)
        self.assertIn('Remaining: 438', html)
        self.assertIn('438 <small>/ 440</small>', html)

    def test_meal_widget_counts_only_todays_claims(self):
        ticket = MealTicket.objects.create(
            user=self.user, meal_type='dinner', ticket_token='#MEAL-2001',
        )
        # auto_now_add overrides on create, so move it to yesterday via update.
        MealTicket.objects.filter(pk=ticket.pk).update(
            claimed_at=timezone.now() - timedelta(days=1),
        )
        html = self.client.get(reverse('dashboard')).content.decode()
        self.assertIn('Used: 0', html)
        self.assertIn('Remaining: 440', html)

    def test_transport_widget_shows_available_seats(self):
        # Fill most of Route 1 (38/40) and Route 2 (30/40) so Route 3 is the
        # unique route with the most open seats → the widget must show it.
        for seat in range(1, 39):
            TransportBooking.objects.create(
                user=self.user, route_name='Route 1: Main Campus Loop',
                departure_time='08:00 AM', seat_number=seat,
                qr_token='TR-1AB%03d' % seat,
            )
        for seat in range(1, 31):
            TransportBooking.objects.create(
                user=self.user, route_name='Route 2: Sports Complex Shuttle',
                departure_time='09:30 AM', seat_number=seat,
                qr_token='TR-2AB%03d' % seat,
            )
        html = self.client.get(reverse('dashboard')).content.decode()
        self.assertIn('40 seats available', html)  # Route 3 still has all 40
        self.assertIn('Route 3: City Center Express', html)
        self.assertIn('10:00 AM', html)

    def test_medical_widget_counts_todays_slots(self):
        today = timezone.now().date()
        for slot in ('09:00 AM', '11:00 AM'):
            MedicalAppointment.objects.create(
                user=self.user, doctor_name='Dr. Ahmed Khan',
                appointment_date=today, time_slot=slot, reason='Checkup',
            )
        html = self.client.get(reverse('dashboard')).content.decode()
        # 16 total slots (4 doctors × 4), 2 booked today
        self.assertIn('14 open today', html)
        self.assertIn('In Session', html)
        self.assertIn('Dr. Ahmed Khan', html)
        self.assertIn('General Physician', html)

    def test_medical_widget_ignores_cancelled_appointments(self):
        today = timezone.now().date()
        MedicalAppointment.objects.create(
            user=self.user, doctor_name='Dr. Emily Johnson',
            appointment_date=today, time_slot='2:00 PM', reason='Checkup',
            status='cancelled',
        )
        html = self.client.get(reverse('dashboard')).content.decode()
        self.assertIn('16 open today', html)
        self.assertNotIn('In Session', html)

    def test_dashboard_lists_latest_published_notices(self):
        author = User.objects.create_user(username='admin_notice', password='x12345678', is_staff=True)
        Notice.objects.create(
            author=author, title='Live Feed Notice', category='urgent',
            content='Broadcast to every dashboard.', is_published=True,
        )
        Notice.objects.create(
            author=author, title='Hidden Draft', category='general',
            content='Should never appear.', is_published=False,
        )
        html = self.client.get(reverse('dashboard')).content.decode()
        self.assertIn('Live Feed Notice', html)
        self.assertNotIn('Hidden Draft', html)

    def test_dashboard_quick_links_use_live_courses(self):
        Course.objects.create(code='WGT101', title='Widget Science', department='CSE')
        html = self.client.get(reverse('dashboard')).content.decode()
        self.assertIn('WGT101', html)
        self.assertNotIn('material_count', html)  # server-rendered, not raw JS

    def test_dashboard_renders_for_anonymous_users(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back')


class PaymentTransactionModelTest(TestCase):
    """PaymentTransaction — fields, ordering, and unique transaction ids."""

    def setUp(self):
        self.user = User.objects.create_user(username='payer', password='x12345678')
        self.payment = PaymentTransaction.objects.create(
            user=self.user,
            amount='200.00',
            payment_method='bkash',
            transaction_id='NTR-4F2A1C',
            purpose='event',
            description='CodeStorm Ticket',
            wallet_trx='9J32X8KL',
        )

    def test_defaults_to_pending(self):
        self.assertEqual(self.payment.status, 'pending')
        self.assertIsNotNone(self.payment.created_at)

    def test_str_and_choice_labels(self):
        self.assertEqual(str(self.payment), 'NTR-4F2A1C · Event')
        self.assertEqual(self.payment.get_payment_method_display(), 'bKash')
        self.assertEqual(self.payment.get_purpose_display(), 'Event')

    def test_newest_first_ordering(self):
        older = PaymentTransaction.objects.create(
            user=self.user, amount='30.00', payment_method='nagad',
            transaction_id='NTR-OLD000', purpose='transport',
        )
        # auto_now_add overrides on create, so backdate it via update().
        PaymentTransaction.objects.filter(pk=older.pk).update(
            created_at=timezone.now() - timedelta(hours=1),
        )
        self.assertEqual(list(PaymentTransaction.objects.all()), [self.payment, older])

    def test_unique_transaction_id(self):
        with self.assertRaises(IntegrityError):
            PaymentTransaction.objects.create(
                user=self.user, amount='10', payment_method='card',
                transaction_id='NTR-4F2A1C', purpose='meal',
            )

    def test_cascade_delete_with_user(self):
        self.user.delete()
        self.assertFalse(PaymentTransaction.objects.filter(pk=self.payment.pk).exists())


class CheckoutPaymentApiTest(TestCase):
    """POST /checkout/ — server-backed payment recording with paid-item links."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='S3001', password='x12345678',
            first_name='Pay', last_name='User',
        )
        self.client.login(username='S3001', password='x12345678')

    def _pay(self, **overrides):
        data = {
            'type': 'event',
            'item': 'CodeStorm 2026 Ticket',
            'issuer': 'NITER Computer Club',
            'fee': '200',
            'method': 'bkash',
            'wallet_no': '01712345678',
            'trx_id': '9J32X8KL',
        }
        data.update(overrides)
        return self.client.post(reverse('checkout'), data)

    def test_checkout_get_stays_public(self):
        self.client.logout()
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_post_redirects_to_login(self):
        self.client.logout()
        response = self.client.post(reverse('checkout'), {'fee': '200'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_payment_persists_transaction_with_unique_id(self):
        response = self._pay()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['transaction_id'].startswith('NTR-'))
        payment = PaymentTransaction.objects.get(transaction_id=data['transaction_id'])
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.amount, 200)
        self.assertEqual(payment.payment_method, 'bkash')
        self.assertEqual(payment.purpose, 'event')
        self.assertEqual(payment.wallet_trx, '9J32X8KL')
        self.assertEqual(payment.status, 'pending')

    def test_payment_generates_unique_ids(self):
        first = self._pay(trx_id='AAAA1111').json()['transaction_id']
        second = self._pay(trx_id='BBBB2222').json()['transaction_id']
        self.assertNotEqual(first, second)

    def test_meal_payment_activates_subscription(self):
        response = self._pay(type='meal', item='Monthly Meal Subscription', fee='2000')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['purpose'], 'Meal Ticket')
        self.assertEqual(data['linked'], 'meal_subscription')
        subscription = self.user.meal_subscription
        self.assertTrue(subscription.is_active)
        self.assertGreater(subscription.expires_at, timezone.now())
        self.assertTrue(PaymentTransaction.objects.filter(user=self.user, purpose='meal').exists())

    def test_meal_payment_refreshes_existing_subscription(self):
        MealSubscription.objects.create(
            user=self.user, is_active=False, expires_at=timezone.now() - timedelta(days=5),
        )
        self._pay(type='meal', fee='2000')
        self.user.meal_subscription.refresh_from_db()
        self.assertTrue(self.user.meal_subscription.is_active)

    def test_payment_creates_notification(self):
        self._pay()
        notification = Notification.objects.get(user=self.user, category='club')
        self.assertIn('pending verification', notification.message)

    def test_invalid_amount_rejected(self):
        response = self._pay(fee='-5')
        self.assertEqual(response.status_code, 400)
        response = self._pay(fee='abc')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(PaymentTransaction.objects.exists())

    def test_non_finite_amount_rejected(self):
        for bad_fee in ('NaN', 'Infinity', '1e999'):
            with self.subTest(fee=bad_fee):
                response = self._pay(fee=bad_fee)
                self.assertEqual(response.status_code, 400)
        self.assertFalse(PaymentTransaction.objects.exists())

    def test_oversized_amount_rejected(self):
        response = self._pay(fee='999999999999999')
        self.assertEqual(response.status_code, 400)

    def test_invalid_method_rejected(self):
        response = self._pay(method='cheque')
        self.assertEqual(response.status_code, 400)

    def test_invalid_wallet_rejected(self):
        response = self._pay(wallet_no='12345')
        self.assertEqual(response.status_code, 400)

    def test_invalid_trx_rejected(self):
        response = self._pay(trx_id='ab')
        self.assertEqual(response.status_code, 400)

    def test_rocket_method_accepted(self):
        response = self._pay(method='rocket')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['payment_method'], 'Rocket')


class SettingsPreferencesTest(TestCase):
    """UserNotificationPreference — signal auto-create + /settings/ persistence."""

    def setUp(self):
        self.user = User.objects.create_user(username='prefs_user', password='x12345678')
        self.client.force_login(self.user)

    def test_signal_auto_creates_default_prefs(self):
        self.assertTrue(UserNotificationPreference.objects.filter(user=self.user).exists())
        prefs = self.user.notification_prefs
        self.assertTrue(prefs.email_alerts)
        self.assertFalse(prefs.sms_alerts)
        self.assertTrue(prefs.push_notifications)
        self.assertFalse(prefs.dark_mode)
        self.assertTrue(prefs.notify_meals)
        self.assertTrue(prefs.notify_transport)
        self.assertTrue(prefs.notify_medical)
        self.assertTrue(prefs.notify_notices)
        self.assertEqual(prefs.timezone, 'Asia/Dhaka')

    def test_settings_get_renders_saved_state(self):
        prefs = self.user.notification_prefs
        prefs.sms_alerts = True
        prefs.dark_mode = True
        prefs.save()
        html = self.client.get(reverse('settings')).content.decode()
        # The sms toggle + dark theme option render as selected.
        self.assertIn('data-pref="sms_alerts" checked', html)
        self.assertIn('data-theme="dark" data-pref="dark_mode" data-value="1" aria-pressed="true"', html)
        self.assertIn('data-pref="email_alerts" checked', html)
        # New per-category toggles render with default checked.
        self.assertIn('data-pref="notify_meals" checked', html)
        self.assertIn('data-pref="notify_notices" checked', html)
        self.assertIn('data-pref="timezone"', html)  # data-pref on the select element

    def test_settings_post_saves_prefs_to_database(self):
        response = self.client.post(reverse('settings'), {
            'email_alerts': 'on',
            'sms_alerts': '',
            'push_notifications': '',
            'dark_mode': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.user.notification_prefs.refresh_from_db()
        self.assertTrue(self.user.notification_prefs.email_alerts)
        self.assertFalse(self.user.notification_prefs.sms_alerts)
        self.assertFalse(self.user.notification_prefs.push_notifications)
        self.assertTrue(self.user.notification_prefs.dark_mode)
        # Default category toggles should be unchanged.
        self.assertTrue(self.user.notification_prefs.notify_meals)
        self.assertTrue(self.user.notification_prefs.notify_notices)

    def test_settings_json_post_updates_prefs(self):
        response = self.client.post(
            reverse('settings'),
            data=json.dumps({'email_alerts': False, 'sms_alerts': True, 'push_notifications': True, 'dark_mode': True}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertFalse(data['email_alerts'])
        self.assertTrue(data['sms_alerts'])
        self.assertTrue(data['dark_mode'])
        # The JSON response now includes the new fields.
        self.assertTrue(data['notify_meals'])
        self.assertEqual(data['timezone'], 'Asia/Dhaka')
        self.user.notification_prefs.refresh_from_db()
        self.assertFalse(self.user.notification_prefs.email_alerts)
        self.assertTrue(self.user.notification_prefs.sms_alerts)
        self.assertTrue(self.user.notification_prefs.dark_mode)

    def test_settings_json_updates_new_fields(self):
        response = self.client.post(
            reverse('settings'),
            data=json.dumps({
                'notify_meals': False,
                'notify_transport': False,
                'notify_medical': False,
                'notify_notices': False,
                'timezone': 'UTC',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.user.notification_prefs.refresh_from_db()
        self.assertFalse(self.user.notification_prefs.notify_meals)
        self.assertFalse(self.user.notification_prefs.notify_transport)
        self.assertFalse(self.user.notification_prefs.notify_medical)
        self.assertFalse(self.user.notification_prefs.notify_notices)
        self.assertEqual(self.user.notification_prefs.timezone, 'UTC')

    def test_settings_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_prefs_persist_across_sessions(self):
        self.client.post(
            reverse('settings'),
            data=json.dumps({'dark_mode': True}),
            content_type='application/json',
        )
        self.client.logout()
        self.client.login(username='prefs_user', password='x12345678')
        html = self.client.get(reverse('settings')).content.decode()
        self.assertIn('data-theme="dark" data-pref="dark_mode" data-value="1" aria-pressed="true"', html)

    def test_google_unlink_removes_token(self):
        """POST /api/settings/google-unlink/ deletes the user's GoogleUserToken."""
        self.client.force_login(self.user)
        GoogleUserToken.objects.create(
            user=self.user,
            access_token='abc', refresh_token='def',
            token_uri='https://oauth2.googleapis.com/token',
            client_id='x', client_secret='y',
            expiry=timezone.now() + timedelta(days=1),
        )
        response = self.client.post(reverse('api_google_unlink'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(GoogleUserToken.objects.filter(user=self.user).exists())

    def test_google_unlink_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('api_google_unlink'))
        self.assertEqual(response.status_code, 401)


class NotesEngineApiTest(TestCase):
    """Notes Engine server-side actions — save / summarize / keywords / export."""

    def setUp(self):
        self.user = User.objects.create_user(username='note_taker', password='x12345678')
        self.client.login(username='note_taker', password='x12345678')

    SAMPLE = (
        'Divide and conquer breaks a problem into smaller subproblems. '
        'The Master Theorem solves recurrence relations for recursive algorithms. '
        'Merge Sort applies divide and conquer to sort arrays efficiently. '
        'Recurrence relations describe the running time of recursive algorithms.'
    )

    def _post(self, name, **data):
        return self.client.post(reverse(name), data)

    def test_endpoints_require_login(self):
        self.client.logout()
        for name in ['api_note_save', 'api_note_summarize', 'api_note_keywords']:
            with self.subTest(endpoint=name):
                response = self._post(name, content='hello')
                self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('api_note_export'))
        self.assertEqual(response.status_code, 302)

    def test_save_note_creates_and_updates(self):
        response = self._post('api_note_save', title='Algorithms', content=self.SAMPLE)
        self.assertEqual(response.status_code, 200)
        note = UserNote.objects.get(user=self.user, title='Algorithms')
        self.assertEqual(note.content, self.SAMPLE)

        note_id = response.json()['note_id']
        response = self._post('api_note_save', note_id=str(note_id), title='Renamed', content='updated')
        self.assertEqual(response.status_code, 200)
        note.refresh_from_db()
        self.assertEqual(note.title, 'Renamed')
        self.assertEqual(note.content, 'updated')
        self.assertEqual(UserNote.objects.filter(user=self.user).count(), 1)

    def test_save_note_defaults_title(self):
        response = self._post('api_note_save', content='no title here')
        self.assertEqual(response.json()['title'], 'Untitled Note')

    def test_save_note_scoped_to_owner(self):
        other = User.objects.create_user(username='other_note', password='x12345678')
        note = UserNote.objects.create(user=other, title='Secret', content='private')
        response = self._post('api_note_save', note_id=str(note.pk), title='Hacked', content='x')
        self.assertEqual(response.status_code, 404)

    def test_get_note_returns_owner_note(self):
        note = UserNote.objects.create(user=self.user, title='Algorithms', content=self.SAMPLE)
        response = self.client.get(reverse('api_note_get', args=[note.pk]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['note_id'], note.pk)
        self.assertEqual(data['title'], 'Algorithms')
        self.assertEqual(data['content'], self.SAMPLE)

    def test_get_note_scoped_to_owner(self):
        other = User.objects.create_user(username='other_note2', password='x12345678')
        note = UserNote.objects.create(user=other, title='Secret', content='private')
        response = self.client.get(reverse('api_note_get', args=[note.pk]))
        self.assertEqual(response.status_code, 404)

    def test_get_note_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('api_note_get', args=[1]))
        self.assertEqual(response.status_code, 302)

    def test_summarize_extracts_high_value_sentences(self):
        response = self._post('api_note_summarize', content=self.SAMPLE)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('divide and conquer', data['summary'].lower())
        self.assertTrue(len(data['summary'].split('. ')) <= 3)

    def test_summarize_empty_content(self):
        response = self._post('api_note_summarize', content='')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['summary'], '')

    def test_keywords_rank_by_frequency(self):
        response = self._post('api_note_keywords', content=self.SAMPLE)
        self.assertEqual(response.status_code, 200)
        keywords = response.json()['keywords']
        self.assertIn('recurrence', keywords)
        self.assertIn('divide', keywords)
        self.assertTrue(len(keywords) <= 8)
        # Stopwords are excluded
        self.assertNotIn('the', keywords)

    def test_export_text(self):
        response = self._post('api_note_export', title='My Note', content='line one\nline two', format='text')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('line one', response.content.decode())

    def test_export_pdf_is_valid_pdf(self):
        response = self._post('api_note_export', title='My Note', content='line one\nline two', format='pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        payload = response.content
        self.assertTrue(payload.startswith(b'%PDF-1.4'))
        self.assertIn(b'startxref', payload)
        self.assertTrue(payload.endswith(b'%%EOF\n'))
        # Structural check: every xref offset points at its object header.
        self._assert_xref_offsets_valid(payload)

    def _assert_xref_offsets_valid(self, payload):
        text = payload.decode('latin-1')
        startxref = int(text.rsplit('startxref', 1)[1].strip().split('\n')[0])
        xref_section = text[startxref:]
        entries = xref_section.split('\n')[2:]  # skip "xref" + count line
        obj_number = 1
        for line in entries:
            line = line.strip()
            if not line or not line[0].isdigit():
                break  # reached the trailer
            parts = line.split()
            if parts[1] == '65535':
                continue  # the mandatory free entry (object 0)
            offset = int(parts[0])
            expected = ('%d 0 obj' % obj_number).encode('latin-1')
            self.assertTrue(
                payload.startswith(expected, offset),
                msg='xref offset %d should point at %s' % (offset, expected),
            )
            obj_number += 1

    def test_export_by_note_id(self):
        note = UserNote.objects.create(user=self.user, title='Saved Note', content='saved content here')
        response = self.client.get(reverse('api_note_export'), {'note_id': note.pk, 'format': 'text'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('saved content here', response.content.decode())

    def test_notes_page_lists_saved_notes(self):
        UserNote.objects.create(user=self.user, title='Sidebar Note', content='x')
        html = self.client.get(reverse('notes')).content.decode()
        self.assertIn('Sidebar Note', html)
        self.assertIn('data-note-id=', html)


class ResearchQueryApiTest(TestCase):
    """POST /api/research/query/ — structured server-side assistant responses."""

    def setUp(self):
        self.user = User.objects.create_user(username='researcher', password='x12345678')
        self.client.login(username='researcher', password='x12345678')

    def _query(self, prompt, style='IEEE'):
        return self.client.post(reverse('api_research_query'), {'prompt': prompt, 'citation_style': style})

    def test_requires_login(self):
        self.client.logout()
        response = self._query('hello')
        self.assertEqual(response.status_code, 302)

    def test_requires_prompt(self):
        response = self.client.post(reverse('api_research_query'), {'prompt': '   '})
        self.assertEqual(response.status_code, 400)

    def test_requires_post(self):
        response = self.client.get(reverse('api_research_query'))
        self.assertEqual(response.status_code, 405)

    def test_structured_response_routes_by_keyword(self):
        cases = {
            'Draft a literature review on IoT in textiles': 'literature',
            'Break down the methodology section': 'methodology',
            'Check this citation in IEEE': 'citation',
            '/summarize the abstract I pasted': 'summary',
            'Explain the superposition theorem': 'superposition',
            'Compare IoT architectures for looms': 'iot',
            'Tell me about your day': 'fallback',
        }
        for prompt, expected_topic in cases.items():
            with self.subTest(prompt=prompt):
                data = self._query(prompt).json()
                self.assertEqual(data['status'], 'success')
                self.assertEqual(data['topic'], expected_topic)
                self.assertTrue(data['response_markdown'].startswith('## '))

    def test_references_formatted_for_selected_style(self):
        data = self._query('check my citation', style='APA 7').json()
        self.assertEqual(data['citation_style'], 'APA 7')
        self.assertEqual(len(data['references']), 2)
        self.assertTrue(data['references'][0]['text'].startswith('M. H. Rahman, & K. Ahmed. (2021).'))

    def test_references_default_to_ieee(self):
        data = self._query('literature review').json()
        self.assertEqual(data['citation_style'], 'IEEE')
        self.assertTrue(data['references'][0]['text'].startswith('[1]'))


class NotificationPushResilienceTest(TestCase):
    """``notify_user`` must never raise when the channel layer is down.

    Deployment hardening: a Redis-backed channel layer can go offline after
    startup. Live pushes then degrade to poll-only delivery (the notification
    row is still persisted and picked up by ``fetch_notifications``) instead
    of failing the request that produced the alert.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='sock', password='x12345678')

    def test_notify_user_swallows_channel_layer_failures(self):
        from core import consumers

        class BoomLayer:
            async def group_send(self, group, event):
                raise ConnectionError('redis is down')

        notification = Notification.objects.create(
            user=self.user, title='Test', message='Hello', category='general',
        )
        with mock.patch.object(consumers, 'get_channel_layer', return_value=BoomLayer()):
            # Must not raise even though the live push fails.
            consumers.notify_user(self.user.id, {'id': notification.pk})

    def test_notify_user_is_noop_without_channel_layer(self):
        from core import consumers

        with mock.patch.object(consumers, 'get_channel_layer', return_value=None):
            consumers.notify_user(self.user.id, {'id': 1})  # no raise

    def test_notify_user_pushes_to_user_group_on_success(self):
        from core import consumers

        sent = {}

        class CaptureLayer:
            async def group_send(self, group, event):
                sent['group'] = group
                sent['event'] = event

        with mock.patch.object(consumers, 'get_channel_layer', return_value=CaptureLayer()):
            consumers.notify_user(42, {'id': 7})
        self.assertEqual(sent['group'], 'user_42')
        self.assertEqual(sent['event'], {'type': 'notification', 'payload': {'id': 7}})


# ============================================================================
# DB-backed transport catalog (routes/schedules/drivers) — section 39
# ============================================================================

class TransportCatalogModelTest(TestCase):
    """Driver / TransportRoute / BusSchedule — catalog rows and uniqueness."""

    def setUp(self):
        self.driver = Driver.objects.create(name='Test Driver', phone='+880 1712-000000')
        self.route = TransportRoute.objects.create(
            name='Route X: Test Loop', origin='A', destination='B',
            capacity=10, fare='15.00', driver=self.driver,
        )

    def test_route_str_and_default_capacity(self):
        self.assertEqual(str(self.route), 'Route X: Test Loop')
        self.assertEqual(TransportRoute.objects.create(name='Route Y').capacity, 40)

    def test_driver_str(self):
        self.assertEqual(str(self.driver), 'Test Driver')

    def test_schedule_unique_per_route(self):
        BusSchedule.objects.create(route=self.route, departure_time='08:00 AM')
        with self.assertRaises(IntegrityError):
            BusSchedule.objects.create(route=self.route, departure_time='08:00 AM')

    def test_inactive_routes_excluded_from_catalog(self):
        inactive = TransportRoute.objects.create(name='Route Z: Retired', is_active=False)
        from core.views import _transport_catalog
        self.assertNotIn(inactive.pk, _transport_catalog())

    def test_catalog_falls_back_to_legacy_constants_without_db_routes(self):
        # With every DB route gone, the catalog resolves from TRANSPORT_ROUTES
        # (legacy ids 1/2/3, 40-seat capacity) — pre-seed databases stay usable.
        from core.views import _transport_catalog
        TransportRoute.objects.all().delete()
        catalog = _transport_catalog()
        self.assertEqual(len(catalog), 3)
        self.assertEqual(catalog[1]['route_name'], 'Route 1: Main Campus Loop')
        self.assertEqual(catalog[2]['departure_time'], '09:30 AM')
        self.assertEqual(catalog[1]['capacity'], 40)


class TransportCatalogViewsTest(TestCase):
    """transport_dashboard + book_transport read the DB catalog (no mocks)."""

    def setUp(self):
        self.user = User.objects.create_user(username='catalog_user', password='x12345678')
        self.client.login(username='catalog_user', password='x12345678')
        # A small route with its own capacity — exercises the per-route bound
        # (the seeded 0013 routes are capacity 40).
        self.driver = Driver.objects.create(name='Shuttle Driver')
        self.route = TransportRoute.objects.create(
            name='Route 9: Test Shuttle', origin='Campus', destination='Gate',
            capacity=5, fare='10.00', driver=self.driver,
        )
        BusSchedule.objects.create(route=self.route, departure_time='07:00 AM')

    def test_transport_page_renders_db_routes_and_drivers(self):
        response = self.client.get(reverse('transport_dashboard'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('transport-data', html)
        self.assertIn('Route 9: Test Shuttle', html)
        self.assertIn('Route 1: Main Campus Loop', html)  # seeded catalog
        self.assertIn('Shuttle Driver', html)             # driver details

    def test_book_transport_uses_route_capacity(self):
        response = self.client.post(reverse('book_transport_ticket'), {
            'route_id': str(self.route.pk), 'seat_number': '6',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('between 1 and 5', response.json()['message'])

    def test_book_transport_accepts_seat_within_capacity(self):
        response = self.client.post(reverse('book_transport_ticket'), {
            'route_id': str(self.route.pk), 'seat_number': '3',
        })
        self.assertEqual(response.status_code, 200)
        booking = TransportBooking.objects.get(user=self.user)
        self.assertEqual(booking.route_name, 'Route 9: Test Shuttle')
        self.assertEqual(booking.departure_time, '07:00 AM')
        self.assertEqual(booking.seat_number, 3)


# ============================================================================
# Medical consultation chat (persistent patient ↔ doctor threads)
# ============================================================================

class MedicalChatApiTest(TestCase):
    """Threads — start, list scoping, messages, unread marking, access."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='chat_admin', password='x12345678', is_staff=True,
        )
        self.patient = User.objects.create_user(
            username='S2001', password='x12345678', first_name='Rina', last_name='Akter',
        )
        StudentProfile.objects.create(user=self.patient, student_id='S2001', department='CSE')
        self.other = User.objects.create_user(username='S2002', password='x12345678')
        StudentProfile.objects.create(user=self.other, student_id='S2002', department='EEE')
        self.appointment = MedicalAppointment.objects.create(
            user=self.patient, doctor_name='Dr. Sarah Smith',
            appointment_date='2026-09-01', time_slot='11:30', reason='Checkup',
        )

    def _start(self, client, appointment_id=None):
        return client.post(reverse('api_medical_chat_start'), {
            'appointment_id': str(appointment_id or self.appointment.pk),
        })

    def test_patient_starts_thread_for_own_appointment(self):
        self.client.login(username='S2001', password='x12345678')
        response = self._start(self.client)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['created'])
        thread = MedicalChatThread.objects.get(appointment=self.appointment)
        self.assertEqual(thread.patient, self.patient)
        self.assertEqual(thread.doctor_name, 'Dr. Sarah Smith')

    def test_start_is_idempotent(self):
        self.client.login(username='S2001', password='x12345678')
        self.assertEqual(self._start(self.client).status_code, 200)
        second = self._start(self.client)
        self.assertEqual(second.status_code, 200)
        self.assertFalse(second.json()['created'])

    def test_other_student_cannot_open_someone_elses_thread(self):
        self.client.login(username='S2002', password='x12345678')
        response = self._start(self.client)
        self.assertEqual(response.status_code, 403)

    def test_staff_can_start_thread_for_any_appointment(self):
        self.client.login(username='chat_admin', password='x12345678')
        response = self._start(self.client)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['created'])

    def test_thread_list_scoped_to_patient(self):
        self.client.login(username='S2001', password='x12345678')
        self._start(self.client)
        response = self.client.get(reverse('api_medical_chat_threads'))
        self.assertEqual(response.status_code, 200)
        threads = response.json()['threads']
        self.assertEqual(len(threads), 1)
        self.assertEqual(threads[0]['doctor_name'], 'Dr. Sarah Smith')
        self.assertEqual(threads[0]['unread'], 0)

    def test_staff_sees_all_threads(self):
        self.client.login(username='S2001', password='x12345678')
        self._start(self.client)
        self.client.login(username='chat_admin', password='x12345678')
        response = self.client.get(reverse('api_medical_chat_threads'))
        self.assertEqual(len(response.json()['threads']), 1)

    def test_messages_post_then_get_with_unread_marking(self):
        self.client.login(username='S2001', password='x12345678')
        thread_id = self._start(self.client).json()['thread']['id']
        response = self.client.post(
            reverse('api_medical_chat_messages', args=[thread_id]),
            {'content': 'I have a fever.'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message']['sender_id'], self.patient.pk)

        # Staff fetches history → the patient's message is now marked read.
        self.client.login(username='chat_admin', password='x12345678')
        response = self.client.get(reverse('api_medical_chat_messages', args=[thread_id]))
        self.assertEqual(response.status_code, 200)
        messages = response.json()['messages']
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['content'], 'I have a fever.')
        self.assertTrue(MedicalChatMessage.objects.get(thread_id=thread_id).is_read)

    def test_empty_message_rejected(self):
        self.client.login(username='S2001', password='x12345678')
        thread_id = self._start(self.client).json()['thread']['id']
        response = self.client.post(
            reverse('api_medical_chat_messages', args=[thread_id]), {'content': '   '},
        )
        self.assertEqual(response.status_code, 400)

    def test_other_student_cannot_read_thread(self):
        self.client.login(username='S2001', password='x12345678')
        thread_id = self._start(self.client).json()['thread']['id']
        self.client.login(username='S2002', password='x12345678')
        response = self.client.get(reverse('api_medical_chat_messages', args=[thread_id]))
        self.assertEqual(response.status_code, 404)

    def test_anonymous_threads_api_redirects_to_login(self):
        response = self.client.get(reverse('api_medical_chat_threads'))
        self.assertEqual(response.status_code, 302)


class MedicalChatConsumerTest(TransactionTestCase):
    """WebSocket chat consumer — membership checks + live message broadcast.

    ``TransactionTestCase`` (not ``TestCase``) because the consumer reads/writes
    through ``database_sync_to_async`` on a worker thread that must see the
    fixture rows, which requires committed (not in-transaction) data.
    """

    def setUp(self):
        self.patient = User.objects.create_user(username='chat_patient', password='x12345678')
        self.other = User.objects.create_user(username='chat_other', password='x12345678')
        self.staff = User.objects.create_user(
            username='chat_staff', password='x12345678', is_staff=True,
        )
        self.appointment = MedicalAppointment.objects.create(
            user=self.patient, doctor_name='Dr. Ahmed Khan',
            appointment_date='2026-09-01', time_slot='10:00', reason='Follow-up',
        )
        self.thread = MedicalChatThread.objects.create(
            appointment=self.appointment, patient=self.patient,
            doctor_name='Dr. Ahmed Khan',
        )

    async def _open_socket(self, user, thread_id=None):
        from channels.testing import WebsocketCommunicator
        from core.consumers import MedicalChatConsumer
        communicator = WebsocketCommunicator(
            MedicalChatConsumer.as_asgi(),
            '/ws/medical-chat/%s/' % (thread_id or self.thread.pk),
        )
        communicator.scope['user'] = user
        communicator.scope['url_route'] = {
            'kwargs': {'thread_id': str(thread_id or self.thread.pk)},
        }
        connected, _ = await communicator.connect()
        return communicator, connected

    async def test_patient_connects_to_own_thread(self):
        communicator, connected = await self._open_socket(self.patient)
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_staff_connects_to_any_thread(self):
        communicator, connected = await self._open_socket(self.staff)
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_other_patient_is_rejected(self):
        communicator, connected = await self._open_socket(self.other)
        self.assertFalse(connected)

    async def test_anonymous_is_rejected(self):
        communicator, connected = await self._open_socket(None)
        self.assertFalse(connected)

    async def test_message_persists_and_broadcasts(self):
        communicator, connected = await self._open_socket(self.patient)
        self.assertTrue(connected)
        await communicator.send_json_to({'type': 'message', 'content': 'Hello doctor!'})
        received = await communicator.receive_json_from()
        self.assertEqual(received['content'], 'Hello doctor!')
        self.assertEqual(received['sender_id'], self.patient.pk)
        await communicator.disconnect()
        from asgiref.sync import sync_to_async
        message = await sync_to_async(MedicalChatMessage.objects.get)(thread=self.thread)
        self.assertEqual(message.content, 'Hello doctor!')
        # sender_id is the FK column (no extra query in async context)
        self.assertEqual(message.sender_id, self.patient.pk)


# ============================================================================
# Medical live queue (staff) — section 39
# ============================================================================

class MedicalQueueApiTest(TestCase):
    """Live staff queue API — FIFO ordering, counts, and access control."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='queue_admin', password='x12345678', is_staff=True,
        )
        self.student = User.objects.create_user(
            username='Q1001', password='x12345678', first_name='Queue', last_name='Student',
        )
        StudentProfile.objects.create(user=self.student, student_id='Q1001', department='CSE')

    def _book(self, day_offset=0, **overrides):
        date = (timezone.now() + timedelta(days=day_offset)).date()
        defaults = {
            'user': self.student, 'doctor_name': 'Dr. Michael Chen',
            'appointment_date': date.isoformat(), 'time_slot': '14:00',
            'reason': 'Queue test',
        }
        defaults.update(overrides)
        return MedicalAppointment.objects.create(**defaults)

    def test_queue_lists_only_todays_pending_and_confirmed(self):
        today = self._book()
        self._book(day_offset=1)  # tomorrow — excluded
        self._book(status='cancelled', time_slot='15:00')  # cancelled — excluded
        self.client.login(username='queue_admin', password='x12345678')
        data = self.client.get(reverse('api_medical_queue')).json()
        self.assertEqual(data['counts']['total'], 1)
        self.assertEqual(data['queue'][0]['id'], today.pk)
        self.assertEqual(data['queue'][0]['position'], 1)
        self.assertEqual(data['counts']['waiting'], 1)
        self.assertEqual(data['counts']['in_consultation'], 0)

    def test_queue_is_fifo(self):
        first = self._book(time_slot='09:00')
        second = self._book(time_slot='10:00')
        self.client.login(username='queue_admin', password='x12345678')
        data = self.client.get(reverse('api_medical_queue')).json()
        self.assertEqual([q['id'] for q in data['queue']], [first.pk, second.pk])
        self.assertEqual([q['position'] for q in data['queue']], [1, 2])

    def test_queue_requires_staff(self):
        self.client.login(username='Q1001', password='x12345678')
        response = self.client.get(reverse('api_medical_queue'))
        self.assertEqual(response.status_code, 302)

    def test_status_change_notifies_other_staff_in_real_time(self):
        other_staff = User.objects.create_user(
            username='queue_other', password='x12345678', is_staff=True,
        )
        appointment = self._book()
        self.client.login(username='queue_admin', password='x12345678')
        with mock.patch('core.views.notify_user') as mock_push:
            response = self.client.post(
                reverse('api_appointment_status', args=[appointment.pk]),
                {'status': 'confirmed'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            )
        self.assertEqual(response.status_code, 200)
        notice = Notification.objects.get(user=other_staff, category='medical')
        self.assertIn('now Confirmed', notice.message)
        self.assertTrue(mock_push.called)


# ============================================================================
# Structured block library (FAQ / Stats / Testimonials / CTA) — section 40
# ============================================================================

class BuilderBlockLibraryTest(TestCase):
    """Structured ContentBlock types: model defaults, partial rendering via
    ``render_block`` and the live editable page, and fallback handling."""

    def setUp(self):
        self.page = EditablePage.objects.create(title='Landing', slug='landing')

    def _block(self, element_id='hero', block_type='html', content_html='', content_json=None):
        return ContentBlock.objects.create(
            page=self.page,
            element_id=element_id,
            block_type=block_type,
            content_html=content_html,
            content_json=content_json or {},
        )

    def _render_tag(self, element_id='hero', default='fallback text'):
        tpl = Template("{% load builder_tags %}{% render_block '" + self.page.slug + "' '" + element_id + "' '" + default + "' %}")
        return tpl.render(Context({}))

    # ------------------------------------------------------------------
    # Model: block_type defaults & schema documentation
    # ------------------------------------------------------------------
    def test_block_type_defaults_to_html(self):
        block = self._block()
        self.assertEqual(block.block_type, 'html')
        self.assertEqual(block.content_json, {})

    def test_block_type_choices_include_structured_types(self):
        codes = {code for code, _label in ContentBlock.BLOCK_TYPE_CHOICES}
        self.assertIn('faq', codes)
        self.assertIn('stats', codes)
        self.assertIn('testimonials', codes)
        self.assertIn('cta', codes)

    def test_block_schemas_document_each_structured_type(self):
        for block_type in ('faq', 'stats', 'testimonials', 'cta'):
            self.assertIn(block_type, ContentBlock.BLOCK_SCHEMAS)

    # ------------------------------------------------------------------
    # render_block → partial dispatch
    # ------------------------------------------------------------------
    def test_render_faq_partial(self):
        self._block(
            block_type='faq',
            content_json={'title': 'FAQs', 'items': [
                {'question': 'What are the admission requirements?', 'answer': 'Pass the admission test.'},
                {'question': 'When do classes start?', 'answer': 'January.'},
            ]},
        )
        html = self._render_tag()
        self.assertIn('data-builder-block="faq"', html)
        self.assertIn('What are the admission requirements?', html)
        self.assertIn('Pass the admission test.', html)
        self.assertIn('<details', html)

    def test_render_stats_partial(self):
        self._block(
            block_type='stats',
            content_json={'title': 'At a glance', 'items': [
                {'value': '4,500+', 'label': 'Students', 'icon': 'fa-user-graduate', 'highlight': True},
                {'value': '98%', 'label': 'Placement'},
            ]},
        )
        html = self._render_tag()
        self.assertIn('data-builder-block="stats"', html)
        self.assertIn('4,500+', html)
        self.assertIn('stat-card--highlight', html)
        self.assertIn('fa-user-graduate', html)

    def test_render_testimonials_partial(self):
        self._block(
            block_type='testimonials',
            content_json={'items': [
                {'quote': 'A transformative experience.', 'author': 'Jane Doe', 'title': 'CSE Alumna', 'avatar': 'https://example.com/jane.jpg'},
            ]},
        )
        html = self._render_tag()
        self.assertIn('data-builder-block="testimonials"', html)
        self.assertIn('A transformative experience.', html)
        self.assertIn('Jane Doe', html)
        self.assertIn('https://example.com/jane.jpg', html)

    def test_render_cta_partial(self):
        self._block(
            block_type='cta',
            content_json={
                'headline': 'Ready to join NITER?',
                'subtext': 'Applications open now.',
                'primary_label': 'Apply Now',
                'primary_url': '/signup/',
                'secondary_label': 'Learn More',
                'secondary_url': '/departments/',
            },
        )
        html = self._render_tag()
        self.assertIn('data-builder-block="cta"', html)
        self.assertIn('Ready to join NITER?', html)
        self.assertIn('href="/signup/"', html)
        self.assertIn('Apply Now', html)
        self.assertIn('Learn More', html)

    # ------------------------------------------------------------------
    # Fallback error handling
    # ------------------------------------------------------------------
    def test_unknown_block_type_falls_back_to_content_html(self):
        block = self._block(block_type='html', content_html='<p>plain fallback</p>')
        block.block_type = 'carousel'  # not a registered type
        block.save()
        self.assertEqual(self._render_tag(), '<p>plain fallback</p>')

    def test_structured_block_with_blank_json_falls_back_to_default(self):
        self._block(block_type='stats', content_json={})
        self.assertEqual(self._render_tag(), 'fallback text')

    def test_structured_block_with_non_dict_json_falls_back_to_default(self):
        # A hand-edited JSONField row that is not a dict must not crash.
        block = self._block(block_type='stats', content_json={'items': []})
        block.content_json = ['not', 'a', 'dict']
        block.save(update_fields=['content_json'])
        self.assertEqual(self._render_tag(), 'fallback text')

    def test_safe_url_filter_allows_relative_and_blocks_javascript(self):
        from django.template import Template, Context
        tpl = Template("{% load builder_tags %}{{ value|safe_url }}")
        render = lambda v: tpl.render(Context({'value': v}))
        self.assertEqual(render('/signup/'), '/signup/')
        self.assertEqual(render('https://niter.edu.bd'), 'https://niter.edu.bd')
        self.assertEqual(render('#top'), '#top')
        self.assertEqual(render('javascript:alert(1)'), '#')
        self.assertEqual(render('data:text/html,x'), '#')

    def test_structured_block_without_items_renders_empty_state(self):
        self._block(block_type='faq', content_json={'title': 'Empty FAQ'})
        html = self._render_tag()
        self.assertIn('No FAQ items have been added yet.', html)

    # ------------------------------------------------------------------
    # Live page rendering (editable_page_view uses the same helper)
    # ------------------------------------------------------------------
    def test_editable_page_renders_structured_blocks(self):
        self._block(
            block_type='cta',
            content_json={'headline': 'Live CTA', 'primary_label': 'Go', 'primary_url': '/signup/'},
        )
        response = self.client.get(reverse('editable_page', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Live CTA')
        self.assertContains(response, 'data-builder-block="cta"')

    def test_editable_page_html_blocks_still_render_raw(self):
        self._block(content_html='<h2>Raw HTML block</h2>')
        response = self.client.get(reverse('editable_page', args=[self.page.slug]))
        self.assertContains(response, '<h2>Raw HTML block</h2>')

    # ------------------------------------------------------------------
    # save_content_block API — structured fields
    # ------------------------------------------------------------------
    def test_save_block_accepts_block_type_and_content_json(self):
        self.client.force_login(User.objects.create_superuser(
            username='root2', email='r@niter.edu.bd', password='rootpass123',
        ))
        response = self.client.post(
            reverse('save_content_block'),
            data=json.dumps({
                'page_slug': 'landing',
                'element_id': 'faq-1',
                'block_type': 'faq',
                'content_json': {'title': 'T', 'items': [{'question': 'Q', 'answer': 'A'}]},
                'content_html': '',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        block = ContentBlock.objects.get(page=self.page, element_id='faq-1')
        self.assertEqual(block.block_type, 'faq')
        self.assertEqual(block.content_json['items'][0]['question'], 'Q')

    def test_save_block_rejects_invalid_block_type(self):
        self.client.force_login(User.objects.create_superuser(
            username='root3', email='r3@niter.edu.bd', password='rootpass123',
        ))
        response = self.client.post(
            reverse('save_content_block'),
            data=json.dumps({
                'page_slug': 'landing', 'element_id': 'x', 'block_type': 'nope', 'content_html': '',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        block = ContentBlock.objects.get(page=self.page, element_id='x')
        self.assertEqual(block.block_type, 'html')

    def test_save_block_preserves_existing_structured_type_on_plain_html_save(self):
        self._block(
            element_id='keep', block_type='stats',
            content_json={'items': [{'value': '1', 'label': 'One'}]},
        )
        self.client.force_login(User.objects.create_superuser(
            username='root4', email='r4@niter.edu.bd', password='rootpass123',
        ))
        # Editor sends only content_html — must NOT reset block_type/json.
        response = self.client.post(
            reverse('save_content_block'),
            data=json.dumps({'page_slug': 'landing', 'element_id': 'keep', 'content_html': '<p>edit</p>'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        block = ContentBlock.objects.get(page=self.page, element_id='keep')
        self.assertEqual(block.block_type, 'stats')
        self.assertEqual(block.content_json['items'][0]['label'], 'One')

    # ------------------------------------------------------------------
    # visual_editor exposes block_type for the inspector badge
    # ------------------------------------------------------------------
    def test_visual_editor_shows_block_type_badge(self):
        self._block(
            block_type='testimonials',
            content_json={'items': [{'quote': 'q', 'author': 'a'}]},
        )
        self.client.force_login(User.objects.create_superuser(
            username='root5', email='r5@niter.edu.bd', password='rootpass123',
        ))
        response = self.client.get(reverse('visual_editor', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'block-type-badge')
        self.assertContains(response, 'testimonials')
