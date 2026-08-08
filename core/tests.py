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
        'medical',
        'notices',
        'academic_notes',
    ]

    NAV_LINKS = ['Dashboard', 'Academic Notes', 'Notices', 'Transport', 'Meals', 'Medical', 'Clubs']

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
