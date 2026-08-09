from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve

from core.models import StudentProfile


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
            '#MEAL-8921',
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
