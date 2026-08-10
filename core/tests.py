import json
from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from django.utils import timezone

from core.models import (
    ContentBlock,
    EditablePage,
    GoogleUserToken,
    MedicalAppointment,
    MealSubscription,
    MealTicket,
    Notification,
    PageTemplate,
    StudentProfile,
    TransportBooking,
)


class StudentPagesSmokeTest(SimpleTestCase):
    """Every student page renders without error after the refactor."""

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


class UnifiedHeaderTest(SimpleTestCase):
    """Every standalone public page shares the exact same top navigation header."""

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

    def test_popover_shows_guest_and_sign_in_when_anonymous(self):
        html = self.client.get(reverse('medical')).content.decode()
        self.assertIn('>Guest<', html)
        self.assertIn('Not signed in', html)
        self.assertIn('Sign In', html)
        self.assertIn('> Sign Up</a>', html)
        self.assertIn('href="' + reverse('settings') + '"', html)
        self.assertIn('href="' + reverse('signup') + '"', html)


class CheckoutPageTest(SimpleTestCase):
    """Payment gateway & checkout page renders and is wired from clubs/transport/meals."""

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


class DepartmentsPageTest(SimpleTestCase):
    """Department Directory (/departments/) and Detail Hub (/departments/<slug>/)."""

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

    def test_directory_data_covers_all_departments(self):
        html = self.client.get(reverse('departments')).content.decode()
        for slug in self.SLUGS:
            self.assertIn("slug: '" + slug + "'", html)
            self.assertIn(slug, html)
        # Cards build their detail links from the resolved directory base URL
        self.assertIn('data-base="/departments/"', html)

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
                    'Upload New Notes',
                    'data-base="/departments/"',
                ]:
                    self.assertContains(response, needle, msg_prefix=slug + ':' + needle)

    def test_detail_hub_shows_mock_department_content(self):
        html = self.client.get(reverse('department_detail', args=['cse'])).content.decode()
        # Mock JS data carries the full department name, head, and hub sections
        self.assertIn('Computer Science & Engineering', html)
        self.assertIn('Prof. Dr. Md. Ashraful Alam', html)
        self.assertIn('hodName:', html)
        self.assertIn('schedule:', html)
        self.assertIn('faculty:', html)
        self.assertIn('announcements:', html)

    def test_detail_hub_uses_shared_header(self):
        html = self.client.get(reverse('department_detail', args=['fde'])).content.decode()
        self.assertIn('CampusDash', html)
        self.assertIn('id="avatar-btn"', html)
        self.assertIn('id="profile-popover"', html)
        self.assertIn('href="/departments/" class="active"', html)  # active Departments pill

    def test_unknown_slug_renders_fallback(self):
        response = self.client.get(reverse('department_detail', args=['unknown-dept']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Department not found')


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
