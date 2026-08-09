from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve


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
        'settings',
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
        for name in self.PAGES + ['claim_meal_ticket', 'book_transport_ticket', 'book_appointment', 'login', 'logout']:
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

    NAV_LINKS = ['Dashboard', 'Academic Notes', 'Departments', 'Research AI', 'Notices', 'Transport', 'Meals', 'Medical', 'Clubs']

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
            'academic_notes': '/academic-notes/',
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
