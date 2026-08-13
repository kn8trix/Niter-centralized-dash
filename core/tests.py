import json
from contextlib import contextmanager
from datetime import date, timedelta
from unittest import mock

import shutil
import tempfile

from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase, TestCase, TransactionTestCase, override_settings
from django.urls import reverse, resolve
from django.utils import timezone

from core.test_compat import apply_test_compat

apply_test_compat()

from core.context_processors import custom_pages_nav

from services.openrouter import call_openrouter
from services.parser import extract_document_text

from core.forms import SignUpForm
from core.models import (
    AcademicEvent,
    BusSchedule,
    ClassRoutine,
    Club,
    ClubAccount,
    ClubEvent,
    ClubRegistration,
    ClubSheetsConfig,
    ContentBlock,
    Course,
    CourseMaterial,
    Department,
    Doctor,
    DoctorSchedule,
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
    ResearchMessage,
    ResearchThread,
    Report,
    Routine,
    StudentProfile,
    TransportBooking,
    TransportRoute,
    UserNote,
    UserNotificationPreference,
)


def _http_error(status, reason='Error'):
    """Build a real ``googleapiclient.errors.HttpError`` with a fake transport
    response for service-layer tests (shared by the Drive/Sheets test classes)."""
    from googleapiclient.errors import HttpError
    resp = mock.Mock()
    resp.status = status
    resp.reason = reason
    return HttpError(
        resp, b'{"error": {"code": %d}}' % status,
        uri='https://www.googleapis.com/upload/drive/v3/files',
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
            'reports_student', 'reports_admin',
            'student_dashboard', 'club_dashboard', 'admin_dashboard', 'admin_users', 'admin_club_accounts',
            'admin_database', 'admin_content', 'admin_settings', 'admin_calendar',
            'api_club_accounts', 'api_admin_academic_calendar',
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
                # Top-right header group: profile avatar + bell away from the brand
                self.assertContains(response, 'class="topbar-row"')
                self.assertContains(response, 'class="topbar-right"')
                # The standalone settings gear is gone
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


class ResearchAIPageTest(TestCase):
    """Academic Research & Thesis Assistant page renders all core sections.

    TestCase (not SimpleTestCase): the shared topbar renders the DB-backed
    ``NAV_CUSTOM_PAGES`` context processor, so full page renders query the
    database."""

    def test_page_renders_core_sections(self):
        response = self.client.get(reverse('research_ai'))
        self.assertEqual(response.status_code, 200)
        for needle in [
            'Academic Research &amp; Thesis Assistant',
            'Brainstorm literature reviews, summarize methodology papers, analyze IEEE-style citations, and edit your academic draft.',
            'Upload Paper / Abstract',
            'Recent Research Threads',
            'No saved threads yet',
            'New Thread',
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


class RoleRoutingTest(TestCase):
    """RBAC — role dispatcher, area middleware, and club-role resolution.

    The bare /dashboard/ URL dispatches authenticated users to their role's
    home: admin → /dashboard/admin/, club → /clubs/manage/, student →
    /dashboard/student/. The RoleAccessMiddleware keeps students out of the
    /dashboard/admin/* area and club managers out of /dashboard/student/*.
    """

    def setUp(self):
        self.student = User.objects.create_user(username='stu_r', password='x12345678')
        self.staff = User.objects.create_user(username='adm_r', password='x12345678', is_staff=True)
        self.superuser = User.objects.create_user(
            username='sup_r', password='x12345678', is_staff=True, is_superuser=True,
        )
        self.club = Club.objects.create(name='RBAC Club', slug='rbac-club')

    def test_anonymous_dashboard_renders_student_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back')

    def test_student_redirected_to_student_dashboard(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_staff_redirected_to_admin_dashboard(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_superuser_redirected_to_admin_dashboard(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_club_manager_redirected_to_club_workspace(self):
        ClubAccount.objects.create(user=self.student, club=self.club, role='manager')
        self.client.force_login(self.student)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('club_dashboard'))

    def test_inactive_club_account_is_treated_as_student(self):
        ClubAccount.objects.create(
            user=self.student, club=self.club, role='manager', is_active=False,
        )
        self.client.force_login(self.student)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_student_blocked_from_admin_area(self):
        self.client.force_login(self.student)
        for url in (reverse('admin_dashboard'), reverse('admin_users'), reverse('admin_club_accounts')):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, reverse('student_dashboard'))

    def test_club_manager_blocked_from_student_and_admin_areas(self):
        ClubAccount.objects.create(user=self.student, club=self.club, role='executive')
        self.client.force_login(self.student)
        response = self.client.get(reverse('student_dashboard'))
        self.assertRedirects(response, reverse('club_dashboard'))
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, reverse('club_dashboard'))

    def test_student_blocked_from_club_area(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('club_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_club_manager_can_open_club_dashboard(self):
        ClubAccount.objects.create(user=self.student, club=self.club, role='president')
        self.client.force_login(self.student)
        response = self.client.get(reverse('club_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'club-sidebar')
        self.assertContains(response, 'data-app="campusdash-club"')

    def test_staff_can_open_club_area(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('club_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_blocked_from_club_area(self):
        response = self.client.get(reverse('club_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_staff_can_open_admin_area(self):
        self.client.force_login(self.staff)
        for url in (reverse('admin_dashboard'), reverse('admin_users'), reverse('admin_database')):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_club_manager_can_open_club_workspace(self):
        ClubAccount.objects.create(user=self.student, club=self.club, role='president')
        self.client.force_login(self.student)
        response = self.client.get(reverse('club_admin'))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_blocked_from_admin_area(self):
        for url in (reverse('admin_dashboard'), reverse('admin_users'), reverse('admin_club_accounts')):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)


class ToastPartialRenderTest(TestCase):
    """The shared toast partial must never render recursively.

    Regression guard: ``partials/toasts.html`` once infinite-looped when a
    base template included it while the partial (or another partial it pulled
    in) also included it — the engine re-rendered ``toasts.html`` forever.
    The partial must stay include-free and each layout must pull it in
    exactly once, at the outer shell level.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='toast_user', password='x12345678')
        self.club = Club.objects.create(name='Toast Club', slug='toast-club')

    def test_toasts_partial_has_no_self_include_or_extends(self):
        import re
        from django.template.loader import get_template
        source = get_template('partials/toasts.html').template.source
        # Ignore the usage docstring inside {% comment %} blocks — Django never
        # executes nested tags there, so only the live markup matters.
        source = re.sub(r'{%\s*comment\s*%}.*?{%\s*endcomment\s*%}', '', source, flags=re.S)
        self.assertNotIn("{% include 'partials/toasts.html' %}", source)
        self.assertNotIn('{% extends', source)

    def test_club_layout_renders_toast_host_exactly_once(self):
        ClubAccount.objects.create(user=self.user, club=self.club, role='president')
        self.client.force_login(self.user)
        html = self.client.get(reverse('club_dashboard')).content.decode()
        self.assertEqual(html.count('id="app-toasts"'), 1)

    def test_medical_layout_renders_toast_host_exactly_once(self):
        self.client.force_login(self.user)
        html = self.client.get(reverse('medical')).content.decode()
        self.assertEqual(html.count('id="app-toasts"'), 1)


class AdminDashboardPagesTest(TestCase):
    """The role-based admin dashboard (/dashboard/admin/*) pages render for
    staff with the distinct admin layout and admin-only sidebar."""

    def setUp(self):
        self.staff = User.objects.create_user(username='adm_pg', password='x12345678', is_staff=True)
        self.student = User.objects.create_user(username='stu_pg', password='x12345678')
        self.client.force_login(self.staff)

    def test_overview_renders_stats_and_quick_links(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        for needle in ['Admin Overview', 'Users &amp; Clubs', 'Club Accounts', 'Reports Inbox', 'Database Stats', 'Website Builder', 'System Settings']:
            self.assertContains(response, needle, msg_prefix=needle)
        self.assertContains(response, 'admin-sidebar')
        self.assertContains(response, 'data-app="campusdash-admin"')

    def test_users_page_lists_roles(self):
        response = self.client.get(reverse('admin_users'))
        self.assertEqual(response.status_code, 200)
        for needle in ['User &amp; Club Management', 'Students', 'Staff &amp; System Admins', 'Club Managers']:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_database_page_shows_row_counts(self):
        response = self.client.get(reverse('admin_database'))
        self.assertEqual(response.status_code, 200)
        for needle in ['Database Quick Stats', 'Accounts', 'Campus services', 'Clubs', 'Payments &amp; alerts']:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_content_page_links_builder(self):
        response = self.client.get(reverse('admin_content'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Website Builder')
        self.assertContains(response, 'Builder Pages')

    def test_settings_page_shows_env_summary(self):
        response = self.client.get(reverse('admin_settings'))
        self.assertEqual(response.status_code, 200)
        for needle in ['Platform Configuration', 'DEBUG', 'ALLOWED_HOSTS', 'Django Admin']:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_student_blocked_from_all_admin_pages(self):
        self.client.force_login(self.student)
        for name in ('admin_dashboard', 'admin_users', 'admin_club_accounts', 'admin_database', 'admin_content', 'admin_settings', 'admin_calendar'):
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, reverse('student_dashboard'))


class AdminCalendarApiTest(TestCase):
    """Academic Calendar Manager — admin page + CRUD API + role guards."""

    def setUp(self):
        self.staff = User.objects.create_user(username='cal_admin', password='x12345678', is_staff=True)
        self.student = User.objects.create_user(username='cal_student', password='x12345678')
        self.event = AcademicEvent.objects.create(
            title='Midterm Exams', category='exam', event_date=date(2026, 4, 12),
        )

    def test_calendar_page_renders_for_staff(self):
        self.client.force_login(self.staff)
        # The event was created for April 2026; the page defaults to the
        # current month, so navigate to the event's month.
        response = self.client.get(reverse('admin_calendar'), {'month': '2026-04'})
        self.assertEqual(response.status_code, 200)
        for needle in ['Academic Calendar Manager', 'Add an Event', 'Midterm Exams']:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_calendar_page_blocked_for_student(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('admin_calendar'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_api_list_requires_login(self):
        response = self.client.get(reverse('api_admin_academic_calendar'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_api_list_requires_admin(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('api_admin_academic_calendar'))
        self.assertEqual(response.status_code, 403)

    def test_api_create_and_envelope(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('api_admin_academic_calendar'), {
            'title': 'Assignment Deadline',
            'category': 'assignment',
            'event_date': '2026-05-01',
            'description': 'Submit by midnight',
        })
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['category'], 'assignment')
        self.assertTrue(body['message'])
        self.assertTrue(AcademicEvent.objects.filter(title='Assignment Deadline').exists())

    def test_api_create_rejects_bad_input(self):
        self.client.force_login(self.staff)
        # Missing title
        response = self.client.post(
            reverse('api_admin_academic_calendar'),
            {'title': '', 'category': 'exam', 'event_date': '2026-05-01'},
        )
        self.assertEqual(response.status_code, 400)
        # Invalid category
        response = self.client.post(
            reverse('api_admin_academic_calendar'),
            {'title': 'X', 'category': 'bogus', 'event_date': '2026-05-01'},
        )
        self.assertEqual(response.status_code, 400)
        # Malformed date
        response = self.client.post(
            reverse('api_admin_academic_calendar'),
            {'title': 'X', 'category': 'exam', 'event_date': '01-05-2026'},
        )
        self.assertEqual(response.status_code, 400)

    def test_api_delete(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('api_admin_academic_calendar_item', args=[self.event.pk]),
            {'action': 'delete'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertFalse(AcademicEvent.objects.filter(pk=self.event.pk).exists())

    def test_api_update(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('api_admin_academic_calendar_item', args=[self.event.pk]),
            {'action': 'update', 'title': 'Final Exams', 'category': 'exam', 'event_date': '2026-04-20'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Final Exams')
        self.assertEqual(self.event.event_date, date(2026, 4, 20))

    def test_api_update_delete_require_admin(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('api_admin_academic_calendar_item', args=[self.event.pk]),
            {'action': 'delete'},
        )
        self.assertEqual(response.status_code, 403)


class ClubsPublicPageTest(TestCase):
    """The public /clubs/ page must not expose the club executive workspace."""

    def test_public_page_has_no_executive_workspace(self):
        response = self.client.get(reverse('clubs_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Club Executive Workspace')
        self.assertNotContains(response, 'panel-exec')
        self.assertNotContains(response, 'Executive Overview')

    def test_public_page_shows_clubs_and_events(self):
        club = Club.objects.create(name='Computer Club', slug='pc-club')
        ClubEvent.objects.create(
            title='CodeStorm', club=club, event_date=date(2026, 9, 10),
        )
        response = self.client.get(reverse('clubs_dashboard'))
        self.assertContains(response, 'Featured Clubs')
        self.assertContains(response, 'Upcoming Events')


class MedicalBookingFormTest(TestCase):
    """The medical booking page renders the persisted Doctor catalog."""

    def setUp(self):
        self.user = User.objects.create_user(username='med_form', password='x12345678')
        self.client.force_login(self.user)

    def test_page_lists_active_doctors_from_db(self):
        Doctor.objects.create(name='Dr. Test Doc', specialty='General Physician')
        response = self.client.get(reverse('medical'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Test Doc')
        self.assertContains(response, 'name="doctor_name"')
        self.assertContains(response, 'err-doctor')

    # ------------------------------------------------------------------
    # book_appointment — POST /book-appointment/ (AJAX booking backend)
    # ------------------------------------------------------------------
    def test_book_appointment_creates_row_and_returns_success(self):
        doctor = Doctor.objects.create(name='Dr. Test Doc', specialty='General Physician')
        response = self.client.post(reverse('book_appointment'), {
            'doctor_name': doctor.name,
            'appointment_date': '2026-09-01',
            'time_slot': '10:00',
            'reason': 'Fever',
        })
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['doctor_name'], doctor.name)
        self.assertEqual(body['data']['appointment_date'], '2026-09-01')
        self.assertEqual(body['data']['time_slot'], '10:00')
        self.assertTrue(MedicalAppointment.objects.filter(
            user=self.user, doctor_name=doctor.name,
            appointment_date=date(2026, 9, 1), time_slot='10:00',
        ).exists())
        # The student is notified in real time
        self.assertTrue(Notification.objects.filter(
            user=self.user, category='medical',
        ).exists())

    def test_book_appointment_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('book_appointment'), {
            'doctor_name': 'Dr. Test Doc',
            'appointment_date': '2026-09-01',
            'time_slot': '10:00',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_book_appointment_rejects_missing_fields(self):
        response = self.client.post(reverse('book_appointment'), {
            'doctor_name': 'Dr. Test Doc',
            'appointment_date': '2026-09-01',
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_book_appointment_conflict_returns_409(self):
        doctor = Doctor.objects.create(name='Dr. Test Doc')
        payload = {
            'doctor_name': doctor.name,
            'appointment_date': '2026-09-01',
            'time_slot': '10:00',
        }
        self.assertEqual(self.client.post(reverse('book_appointment'), payload).status_code, 200)
        # Double-booking the same doctor slot is rejected atomically (409)
        response = self.client.post(reverse('book_appointment'), payload)
        self.assertEqual(response.status_code, 409)

    # ------------------------------------------------------------------
    # Upcoming Appointments side panel — real rows, not mock markup
    # ------------------------------------------------------------------
    def test_medical_page_renders_real_upcoming_appointments(self):
        Doctor.objects.create(name='Dr. Test Doc', specialty='General Physician')
        MedicalAppointment.objects.create(
            user=self.user, doctor_name='Dr. Test Doc',
            appointment_date=date(2026, 9, 1), time_slot='10:00', reason='Fever',
        )
        response = self.client.get(reverse('medical'))
        self.assertContains(response, 'Fever')  # reason only renders in the side list
        self.assertContains(response, 'Tue, Sep 1')  # date via |date:"D, M j"
        self.assertContains(response, '10:00 AM')  # time via |fmt_slot
        self.assertNotContains(response, 'No appointments yet')

    def test_medical_page_shows_empty_state_without_appointments(self):
        response = self.client.get(reverse('medical'))
        self.assertContains(response, 'No appointments yet')

    # ------------------------------------------------------------------
    # Regression guards for the booking form state-binding bugs
    # ------------------------------------------------------------------
    def test_validation_error_css_respects_hidden_attribute(self):
        # .field-error used display:flex, which overrode the UA's
        # [hidden] { display:none } — the "Please choose a doctor" etc.
        # warnings were permanently visible and JS hidden toggling was a no-op.
        from django.conf import settings
        css = (settings.BASE_DIR / 'static' / 'css' / 'medical.css').read_text()
        self.assertIn('.field-error[hidden]', css)

    def test_time_slot_error_listeners_bind_each_radio(self):
        # form.elements['time_slot'] is a RadioNodeList with no
        # addEventListener — the TypeError used to kill the whole booking
        # script (native form POST). The fix binds each radio input instead.
        html = self.client.get(reverse('medical')).content.decode()
        self.assertIn('input[name="time_slot"]', html)
        self.assertIn('Array.from(form.querySelectorAll', html)


class ClubAccountApiTest(TestCase):
    """Club Account Management APIs — create, assign, reset, toggle, perms."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='sys_admin', password='x12345678', is_staff=True, is_superuser=True,
        )
        self.staff = User.objects.create_user(username='plain_staff', password='x12345678', is_staff=True)
        self.student = User.objects.create_user(username='stu_ca', password='x12345678')
        # The 0009 seed migration already creates Computer Club (slug
        # computer-club), so reuse it rather than tripping the unique slug.
        self.club, _ = Club.objects.get_or_create(name='Computer Club', slug='computer-club')

    def _post(self, url, data):
        return self.client.post(url, data)

    def test_create_requires_admin(self):
        self.client.force_login(self.student)
        response = self._post(reverse('api_club_accounts'), {'mode': 'create', 'username': 'new_mgr', 'club_id': self.club.pk, 'role': 'manager'})
        self.assertEqual(response.status_code, 403)

    def test_create_requires_login(self):
        response = self._post(reverse('api_club_accounts'), {'mode': 'create', 'username': 'new_mgr', 'club_id': self.club.pk, 'role': 'manager'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_staff_can_create_club_account(self):
        self.client.force_login(self.staff)
        response = self._post(reverse('api_club_accounts'), {
            'mode': 'create', 'username': 'new_mgr', 'full_name': 'Nadia Manager',
            'email': 'nadia@niter.edu.bd', 'password': 'secretpass1',
            'club_id': self.club.pk, 'role': 'manager',
            'can_post_events': '1', 'can_manage_members': '1', 'is_active': '1',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        account = ClubAccount.objects.get(user__username='new_mgr')
        self.assertEqual(account.club, self.club)
        self.assertEqual(account.role, 'manager')
        self.assertTrue(account.can_post_events)
        self.assertTrue(account.user.check_password('secretpass1'))

    def test_create_rejects_duplicate_username(self):
        User.objects.create_user(username='taken', password='x12345678')
        self.client.force_login(self.staff)
        response = self._post(reverse('api_club_accounts'), {
            'mode': 'create', 'username': 'taken', 'club_id': self.club.pk, 'role': 'manager',
        })
        self.assertEqual(response.status_code, 409)

    def test_create_rejects_unknown_club(self):
        self.client.force_login(self.staff)
        response = self._post(reverse('api_club_accounts'), {
            'mode': 'create', 'username': 'new_mgr', 'club_id': 9999, 'role': 'manager',
        })
        self.assertEqual(response.status_code, 404)

    def test_assign_existing_user(self):
        self.client.force_login(self.staff)
        response = self._post(reverse('api_club_accounts'), {
            'mode': 'assign', 'user_id': self.student.pk, 'club_id': self.club.pk, 'role': 'executive',
        })
        self.assertEqual(response.status_code, 200)
        account = ClubAccount.objects.get(user=self.student)
        self.assertEqual(account.role, 'executive')
        # The assigned user becomes a club-role user at the dashboard dispatcher
        # and is redirected to the protected club workspace.
        self.client.force_login(self.student)
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('club_dashboard'))

    def test_assign_rejects_double_assignment(self):
        ClubAccount.objects.create(user=self.student, club=self.club)
        self.client.force_login(self.staff)
        response = self._post(reverse('api_club_accounts'), {
            'mode': 'assign', 'user_id': self.student.pk, 'club_id': self.club.pk, 'role': 'manager',
        })
        self.assertEqual(response.status_code, 409)

    def test_reset_password(self):
        account = ClubAccount.objects.create(user=self.student, club=self.club)
        self.client.force_login(self.staff)
        response = self._post(reverse('api_club_account_password', args=[account.pk]), {'password': 'brandnewpass1'})
        self.assertEqual(response.status_code, 200)
        # check_password compares against the in-memory hash — reload the row.
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password('brandnewpass1'))

    def test_reset_password_generates_when_blank(self):
        account = ClubAccount.objects.create(user=self.student, club=self.club)
        self.client.force_login(self.staff)
        response = self._post(reverse('api_club_account_password', args=[account.pk]), {})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['generated_password'])
        # check_password compares against the in-memory hash — reload the row.
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password(data['generated_password']))

    def test_toggle_status(self):
        account = ClubAccount.objects.create(user=self.student, club=self.club, is_active=True)
        self.client.force_login(self.staff)
        response = self._post(reverse('api_club_account_status', args=[account.pk]), {})
        self.assertEqual(response.status_code, 200)
        account.refresh_from_db()
        self.assertFalse(account.is_active)

    def test_update_permissions(self):
        account = ClubAccount.objects.create(user=self.student, club=self.club, role='manager')
        self.client.force_login(self.staff)
        response = self._post(reverse('api_club_account_permissions', args=[account.pk]), {
            'role': 'president', 'can_manage_finances': '1', 'can_manage_members': '', 'can_post_events': '1',
        })
        self.assertEqual(response.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.role, 'president')
        self.assertTrue(account.can_manage_finances)
        self.assertFalse(account.can_manage_members)

    def test_club_accounts_page_renders_for_staff(self):
        ClubAccount.objects.create(user=self.student, club=self.club, role='manager')
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin_club_accounts'))
        self.assertEqual(response.status_code, 200)
        for needle in ['Club Account Management', 'Create a Club Account', 'Assign an Existing Account', 'Club Manager Accounts']:
            self.assertContains(response, needle, msg_prefix=needle)
        self.assertContains(response, self.student.username)

    def test_club_accounts_page_blocked_for_students(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('admin_club_accounts'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('student_dashboard'))


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
        for name in ['sys_admin', 'cafeteria_admin', 'club_admin', 'reports_admin']:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)

    def test_admin_pages_require_staff(self):
        # Logged-in non-staff users are sent back to the login page for the
        # legacy staff dashboards (kept on staff_member_required)…
        self.client.login(username='S1001', password='student123')
        for name in ['sys_admin', 'cafeteria_admin']:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)
        # …the club workspace 403s students without club access
        # (club_access_required fails closed instead of looping to login)…
        response = self.client.get(reverse('club_admin'))
        self.assertEqual(response.status_code, 403)
        # …and the admin area (/dashboard/admin/*) bounces students to their
        # own dashboard via the RoleAccessMiddleware, never the login loop.
        response = self.client.get(reverse('reports_admin'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(reverse('login'), response.url)

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
        # Sign-in lands on /dashboard/ which the role dispatcher routes to the
        # new student's area.
        self.assertRedirects(response, reverse('student_dashboard'))
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


class SignUpFormTest(TestCase):
    """SignUpForm validation + persistence (duplicate checks, password rules)."""

    def _data(self, **overrides):
        data = {
            'student_id': 'S3001',
            'full_name': 'Rifat Hasan',
            'department': 'CSE',
            'email': 'rifat@niter.edu.bd',
            'password': 'secretpass1',
            'confirm_password': 'secretpass1',
        }
        data.update(overrides)
        return data

    def test_valid_form_creates_user_and_profile(self):
        form = SignUpForm(self._data())
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, 'S3001')
        self.assertEqual(user.first_name, 'Rifat')
        self.assertEqual(user.last_name, 'Hasan')
        # Password is hashed with Django's standard auth hashing
        self.assertTrue(user.check_password('secretpass1'))
        self.assertNotEqual(user.password, 'secretpass1')
        profile = StudentProfile.objects.get(student_id='S3001')
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.department, 'CSE')

    def test_duplicate_student_id_rejected(self):
        User.objects.create_user(username='S3001', password='x12345678')
        form = SignUpForm(self._data())
        self.assertFalse(form.is_valid())
        self.assertIn('already exists', form.errors['student_id'][0])

    def test_duplicate_email_rejected(self):
        User.objects.create_user(username='someone', email='rifat@niter.edu.bd', password='x12345678')
        form = SignUpForm(self._data())
        self.assertFalse(form.is_valid())
        self.assertIn('already exists', form.errors['email'][0])

    def test_duplicate_email_rejected_case_insensitively(self):
        User.objects.create_user(username='someone', email='RIFAT@niter.edu.bd', password='x12345678')
        form = SignUpForm(self._data())
        self.assertFalse(form.is_valid())
        self.assertIn('already exists', form.errors['email'][0])

    def test_password_confirmation_mismatch_rejected(self):
        form = SignUpForm(self._data(confirm_password='different1'))
        self.assertFalse(form.is_valid())
        self.assertIn('Passwords do not match.', form.errors['confirm_password'][0])

    def test_short_password_rejected(self):
        form = SignUpForm(self._data(password='short', confirm_password='short'))
        self.assertFalse(form.is_valid())
        self.assertIn('at least 8 characters', form.errors['password'][0])

    def test_invalid_department_rejected(self):
        form = SignUpForm(self._data(department='BOGUS'))
        self.assertFalse(form.is_valid())
        self.assertIn('department', form.errors)


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
        # LOGIN_REDIRECT_URL → /dashboard/ → role dispatcher → student home.
        response = self.client.post(reverse('login'), {
            'username': 'student',
            'password': 'student123',
        })
        self.assertRedirects(response, reverse('student_dashboard'))

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
        self.assertRedirects(response, reverse('student_dashboard'))

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

    def test_staff_without_superuser_cannot_view_draft(self):
        self.page.is_published = False
        self.page.save()
        self.client.force_login(User.objects.create_user(
            username='staff_nav', password='staffpass123', is_staff=True,
        ))
        response = self.client.get(reverse('editable_page', args=[self.page.slug]))
        self.assertEqual(response.status_code, 404)

    def test_superuser_can_preview_unpublished_draft(self):
        self.page.is_published = False
        self.page.save()
        self.client.force_login(User.objects.create_superuser(
            username='root_preview', email='rp@niter.edu.bd', password='rootpass123',
        ))
        response = self.client.get(reverse('editable_page', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello from the database')

    def test_seo_description_renders_in_meta(self):
        self.page.seo_description = 'NITER research assistant page.'
        self.page.save()
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        self.assertIn('name="description" content="NITER research assistant page."', html)

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

    # ------------------------------------------------------------------
    # Public /pages/<slug>/ route (canonical alias of /page/<slug>/)
    # ------------------------------------------------------------------
    def test_public_pages_slug_route_renders_published_page(self):
        response = self.client.get(reverse('editable_page_public', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello from the database')
        self.assertContains(response, 'data-page-slug="research-ai"')

    def test_public_pages_slug_route_404s_for_draft_and_unknown(self):
        self.page.is_published = False
        self.page.save()
        response = self.client.get(reverse('editable_page_public', args=[self.page.slug]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse('editable_page_public', args=['does-not-exist']))
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # Render-time sanitization (defense-in-depth on top of save-time)
    # ------------------------------------------------------------------
    def test_render_time_sanitizes_legacy_html_blocks(self):
        # A row created straight through the ORM (bypassing the save-time
        # sanitizer) must still render clean: scripts, event handlers and
        # unsafe URL schemes are stripped by the render-time pass.
        ContentBlock.objects.create(
            page=self.page,
            element_id='legacy-raw',
            content_html=(
                '<script>alert(1)</script><p onclick="alert(2)">Keep me</p>'
                '<a href="javascript:alert(3)">bad</a>'
                '<img src="x" onerror="alert(4)">'
            ),
        )
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        self.assertIn('Keep me', html)
        # The malicious payload is gone; the <a> lost its javascript: href and
        # the <img> its onerror handler. (Assert the payload itself, not raw
        # ``<script`` — the page's shared topbar legitimately embeds its own
        # trusted inline JS.)
        self.assertNotIn('alert(1)', html)
        self.assertNotIn('onclick', html)
        self.assertNotIn('onerror', html)
        self.assertNotIn('javascript:', html)
        self.assertIn('<a>bad</a>', html)

    def test_style_json_values_cannot_break_out_of_style_attribute(self):
        # A quote inside a style value must be escaped so it can never forge
        # new attributes (e.g. onmouseover) on the live page.
        ContentBlock.objects.create(
            page=self.page,
            element_id='stylish',
            content_html='<p>styled</p>',
            style_json={'fontSize': '12px"; onmouseover="alert(1)'},
        )
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        # Django autoescaping is the safety boundary for style values: the raw
        # quote becomes &quot; so the attribute can never close early and forge
        # an ``onmouseover="..."`` attribute.
        self.assertNotIn('12px";', html)
        self.assertNotIn('onmouseover="', html)

    def test_custom_css_breakout_guarded_at_render_time(self):
        # custom_css is injected with |safe inside a <style> tag; the render-
        # time guard strips anything that could close the tag, even when the
        # row was hand-edited after the save-time guard ran.
        self.page.custom_css = '</style><script>alert(1)</script><!--'
        self.page.save(update_fields=['custom_css'])
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        # The injected break-out is neutralized: no ``</style>`` followed by
        # content, and the <script> payload never reaches the page. (The page's
        # own topbar legitimately emits its own ``<script>``/``<!--`` markers.)
        self.assertNotIn('</style><script', html)
        self.assertNotIn('<script>alert', html)

    def test_structured_block_trusted_inline_js_survives_render(self):
        # Structured blocks render through their partials, which embed trusted
        # inline JS (stats/testimonial animations). The render-time sanitizer
        # must only ever touch raw ``content_html`` — never partial output.
        ContentBlock.objects.create(
            page=self.page,
            element_id='metrics',
            block_type='stats',
            content_json={'title': 'Campus metrics'},
        )
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        self.assertIn('Campus metrics', html)
        self.assertIn('IntersectionObserver', html)
        self.assertIn('easeOutCubic', html)


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
        for name in ['builder_dashboard', 'visual_editor', 'builder_editor']:
            with self.subTest(page=name):
                kwargs = {'page_slug': 'research-ai'} if name in ('visual_editor', 'builder_editor') else {}
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
        # New pages land in the frontend page builder (the primary editor).
        self.assertEqual(data['edit_url'], reverse('builder_editor', args=['about-us']))
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
    # Club sheets (delegates to the Sheets v4 layer in core.club_sheets)
    # ------------------------------------------------------------------
    def test_get_club_sheet_data_returns_records(self):
        from core.google_service import get_club_sheet_data
        with mock.patch('core.club_sheets.read_rows', return_value=[
            {'Name': 'Alice', 'Amount': '200'},
        ]) as read:
            rows = get_club_sheet_data('https://docs.google.com/spreadsheets/d/abc', self.user)
            read.assert_called_once_with(self.user, 'https://docs.google.com/spreadsheets/d/abc')
        self.assertEqual(rows, [{'Name': 'Alice', 'Amount': '200'}])

    def test_append_club_sheet_row_appends(self):
        from core.google_service import append_club_sheet_row
        with mock.patch('core.club_sheets.append_rows', return_value=1) as append:
            append_club_sheet_row('https://docs.google.com/spreadsheets/d/abc', ['Fahim', '200'], self.user)
            append.assert_called_once_with(
                self.user, 'https://docs.google.com/spreadsheets/d/abc', [['Fahim', '200']],
            )

    def test_sheets_wrap_api_failures_in_service_error(self):
        from core.google_service import GoogleServiceError, get_club_sheet_data
        with mock.patch('core.club_sheets.read_rows', side_effect=GoogleServiceError('no network')):
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
        # Tokens are encrypted at rest — decrypt for the round-trip comparison.
        from core.crypto import decrypt_secret
        self.assertEqual(decrypt_secret(token.access_token), 'ya29.refreshed')
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

    def test_get_google_credentials_falls_back_to_allauth_when_legacy_stale(self):
        """An expired legacy row with no refresh token must not hard-fail when
        the user's allauth SocialToken is still refreshable — the recurring
        'Google session expired' popup on Render was caused by exactly this.
        """
        from core.google_service import get_google_credentials
        from google.oauth2.credentials import Credentials
        from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken

        token = self.user.google_token
        token.expiry = timezone.now() - timedelta(minutes=5)
        token.refresh_token = ''
        token.save()

        app = SocialApp.objects.create(
            provider='google', name='Google',
            client_id='app-id.apps.googleusercontent.com', secret='secret',
        )
        account = SocialAccount.objects.create(
            user=self.user, provider='google', uid='g-test-1',
        )
        SocialToken.objects.create(
            account=account, app=app,
            token='ya29.social-expired',
            token_secret='1//social-refresh',
            expires_at=timezone.now() - timedelta(minutes=5),
        )

        def fake_refresh(creds, request):
            creds.token = 'ya29.social-refreshed'
            creds.expiry = timezone.now() + timedelta(hours=1)

        with mock.patch.object(Credentials, 'refresh', fake_refresh):
            creds = get_google_credentials(self.user)

        self.assertEqual(creds.token, 'ya29.social-refreshed')
        # The refreshed allauth token is mirrored back into the legacy row.
        token.refresh_from_db()
        from core.crypto import decrypt_secret
        self.assertEqual(decrypt_secret(token.access_token), 'ya29.social-refreshed')
        self.assertFalse(token.is_expired)

    def test_upload_note_refresh_failure_wrapped_as_reauth(self):
        from core.google_service import GoogleReauthRequired, upload_note_to_user_drive
        from google.auth.exceptions import RefreshError
        upload = SimpleUploadedFile('note.txt', b'hello')
        with mock.patch('core.google_service.build', side_effect=RefreshError('revoked')):
            with self.assertRaises(GoogleReauthRequired):
                upload_note_to_user_drive(self.user, upload)

    def test_upload_note_http_401_wrapped_as_reauth(self):
        """A mid-call 401 'Invalid Credentials' must surface as a re-auth error
        (the frontend shows the reconnect modal) instead of a generic 500."""
        from core.google_service import GoogleReauthRequired, upload_note_to_user_drive
        upload = SimpleUploadedFile('note.txt', b'hello')
        with mock.patch('core.google_service.build', side_effect=_http_error(401, 'Unauthorized')):
            with self.assertRaises(GoogleReauthRequired):
                upload_note_to_user_drive(self.user, upload)

    def test_upload_note_non_401_http_error_stays_service_error(self):
        from core.google_service import GoogleServiceError, upload_note_to_user_drive
        upload = SimpleUploadedFile('note.txt', b'hello')
        with mock.patch('core.google_service.build', side_effect=_http_error(500, 'Server Error')):
            with self.assertRaises(GoogleServiceError):
                upload_note_to_user_drive(self.user, upload)

    def test_sheets_refresh_failure_wrapped_as_reauth(self):
        from core.google_service import GoogleReauthRequired, get_club_sheet_data
        with mock.patch('core.club_sheets.read_rows', side_effect=GoogleReauthRequired('revoked')):
            with self.assertRaises(GoogleReauthRequired):
                get_club_sheet_data('https://docs.google.com/spreadsheets/d/abc', self.user)


class GoogleApiViewsTest(TestCase):
    """Phase 4 — Google API endpoints (Drive upload + club sheets)."""

    def setUp(self):
        # Club sheet endpoints are staff-only (Club Management dashboard).
        self.user = User.objects.create_user(
            username='sheet_user', password='x12345678', is_staff=True,
        )
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
        with mock.patch('academic_notes.drive_service.upload_file_to_drive', return_value={
            'file_id': 'file-9',
            'web_view_link': 'https://drive.google.com/file/d/file-9/view',
            'web_content_link': 'https://drive.google.com/uc?id=file-9',
        }) as service:
            response = self.client.post(reverse('api_upload_note'), {'file': upload})
            service.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'status': 'success',
            'file_id': 'file-9',
            'web_view_link': 'https://drive.google.com/file/d/file-9/view',
            'web_content_link': 'https://drive.google.com/uc?id=file-9',
        })

    def test_upload_note_not_connected_returns_401_auth_required(self):
        from core.google_service import GoogleAccountNotConnected
        with mock.patch('academic_notes.drive_service.upload_file_to_drive', side_effect=GoogleAccountNotConnected('not connected')):
            response = self.client.post(
                reverse('api_upload_note'), {'file': SimpleUploadedFile('n.txt', b'x')},
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            'status': 'auth_required',
            'reason': 'not_connected',
            'redirect_url': reverse('google_login'),
            'drive_connect_url': reverse('drive_connect'),
        })

    def test_upload_note_reauth_required_returns_401(self):
        from core.google_service import GoogleReauthRequired
        with mock.patch('academic_notes.drive_service.upload_file_to_drive', side_effect=GoogleReauthRequired('session expired')):
            response = self.client.post(
                reverse('api_upload_note'), {'file': SimpleUploadedFile('n.txt', b'x')},
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            'status': 'auth_required',
            'reason': 'refresh_failed',
            'redirect_url': reverse('google_login'),
            'drive_connect_url': reverse('drive_connect'),
        })

    def test_upload_note_refresh_error_returns_401(self):
        from google.auth.exceptions import RefreshError
        with mock.patch('academic_notes.drive_service.upload_file_to_drive', side_effect=RefreshError('revoked')):
            response = self.client.post(
                reverse('api_upload_note'), {'file': SimpleUploadedFile('n.txt', b'x')},
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['status'], 'auth_required')
        self.assertEqual(response.json()['redirect_url'], reverse('google_login'))

    def test_upload_note_service_error_returns_500(self):
        from core.google_service import GoogleServiceError
        with mock.patch('academic_notes.drive_service.upload_file_to_drive', side_effect=GoogleServiceError('drive exploded')):
            response = self.client.post(
                reverse('api_upload_note'), {'file': SimpleUploadedFile('n.txt', b'x')},
            )
        self.assertEqual(response.status_code, 500)

    def test_upload_note_saves_drive_links_onto_usernote(self):
        note = UserNote.objects.create(user=self.user, title='Linked note', content='body')
        upload = SimpleUploadedFile('note.pdf', b'%PDF', content_type='application/pdf')
        with mock.patch('academic_notes.drive_service.upload_file_to_drive', return_value={
            'file_id': 'f1',
            'web_view_link': 'https://drive.google.com/file/d/f1/view',
            'web_content_link': 'https://drive.google.com/uc?id=f1',
        }):
            response = self.client.post(
                reverse('api_upload_note'), {'file': upload, 'note_id': note.pk},
            )
        self.assertEqual(response.status_code, 200)
        note.refresh_from_db()
        self.assertEqual(note.drive_view_link, 'https://drive.google.com/file/d/f1/view')
        self.assertEqual(note.drive_content_link, 'https://drive.google.com/uc?id=f1')

    # ------------------------------------------------------------------
    # fetch_club_sheet_view
    # ------------------------------------------------------------------
    def test_fetch_sheet_denied_for_non_staff(self):
        student = User.objects.create_user(username='plain_student', password='x12345678')
        self.client.logout()
        self.client.login(username='plain_student', password='x12345678')
        # club_access_required fails closed with 403 for authenticated users
        # with no staff flag and no active club account — sheet data never
        # reaches plain students.
        response = self.client.get(reverse('api_club_sheet_fetch'), {'sheet_url': 'https://x'})
        self.assertEqual(response.status_code, 403)

    def test_fetch_sheet_allowed_for_club_manager(self):
        # Active club accounts may use the club workspace (sheets + verify).
        club, _ = Club.objects.get_or_create(name='Computer Club', slug='computer-club')
        manager = User.objects.create_user(username='mgr_sheet', password='x12345678')
        ClubAccount.objects.create(user=manager, club=club, role='manager', is_active=True)
        self.client.logout()
        self.client.login(username='mgr_sheet', password='x12345678')
        response = self.client.get(reverse('api_club_sheet_fetch'), {'sheet_url': 'https://x'})
        # Passed the role gate — a non-403/non-302 status means the request
        # reached the view (a 401 here means Google not connected, which is
        # expected for a manager without Drive/Sheets scopes).
        self.assertNotIn(response.status_code, (302, 403))

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
            'reason': 'refresh_failed',
            'redirect_url': reverse('google_login'),
            'drive_connect_url': reverse('drive_connect'),
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
        self.assertEqual(data['data']['appointment_status'], 'pending')
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
        # The broadcast now runs as a Huey task (synchronous in immediate mode),
        # so the push helper is patched where the task lives.
        with mock.patch('core.tasks.notify_user') as mock_push:
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

    def test_upload_handler_binds_auth_status_and_redirect_guard(self):
        """Regression guard for the upload UX: the page probes Drive health via
        the auth-status endpoint (silent refresh) and the upload handler
        redirects to login when @login_required bounces the POST (expired
        Django session) instead of parsing the login HTML as JSON."""
        html = self.client.get(reverse('notes')).content.decode()
        self.assertIn(reverse('api_notes_auth_status'), html)
        self.assertIn('response.redirected', html)
        self.assertIn(reverse('api_upload_note'), html)


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
    """The /dashboard/student/ widgets — BST clock, routine, calendar, feeds.

    The canonical student dashboard URL is ``student_dashboard``; the bare
    ``/dashboard/`` dispatcher redirects authenticated users by role.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='widget_user', password='x12345678')

    @staticmethod
    def _full_week_schedule():
        """A schedule with one class on every weekday (the Dhaka weekday is
        always covered, so the today's-routine block is deterministic)."""
        return {'days': [
            {'day': day, 'slots': [
                {'start': '09:00', 'end': '10:30', 'course': 'CSE-1101', 'room': '201'},
            ]}
            for day in ('Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri')
        ]}

    def test_dashboard_embeds_bst_clock_widget(self):
        html = self.client.get(reverse('student_dashboard')).content.decode()
        self.assertIn('id="clock-time"', html)
        self.assertIn('Bangladesh Standard Time', html)
        self.assertIn('id="dash-data"', html)

    def test_dashboard_renders_todays_routine_slots(self):
        self.client.force_login(self.user)
        Routine.objects.create(
            user=self.user, schedule=self._full_week_schedule(), source_name='routine.png',
        )
        html = self.client.get(reverse('student_dashboard')).content.decode()
        self.assertIn('CSE-1101', html)
        self.assertIn('data-start="09:00"', html)
        self.assertIn('Room 201', html)
        self.assertIn('Synced from routine.png', html)

    def test_dashboard_shows_routine_setup_cta_when_missing(self):
        html = self.client.get(reverse('student_dashboard')).content.decode()
        self.assertIn('routine-cta', html)
        self.assertIn('Set up routine', html)

    def test_dashboard_lists_recent_activity(self):
        self.client.force_login(self.user)
        UserNote.objects.create(user=self.user, title='OOP Notes', content='x')
        html = self.client.get(reverse('student_dashboard')).content.decode()
        self.assertIn('Edited note', html)
        self.assertIn('OOP Notes', html)

    def test_dashboard_shows_quick_campus_notice(self):
        author = User.objects.create_user(username='admin_q', password='x12345678', is_staff=True)
        Notice.objects.create(
            author=author, title='Semester Fee Notice', category='academic',
            content='Fees due.', is_published=True,
        )
        html = self.client.get(reverse('student_dashboard')).content.decode()
        self.assertIn('Semester Fee Notice', html)
        self.assertIn('Quick Campus Info', html)

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
        html = self.client.get(reverse('student_dashboard')).content.decode()
        self.assertIn('Live Feed Notice', html)
        self.assertNotIn('Hidden Draft', html)

    def test_dashboard_quick_links_use_live_courses(self):
        Course.objects.create(code='WGT101', title='Widget Science', department='CSE')
        html = self.client.get(reverse('student_dashboard')).content.decode()
        self.assertIn('WGT101', html)
        self.assertNotIn('material_count', html)  # server-rendered, not raw JS

    def test_dashboard_renders_for_anonymous_users(self):
        response = self.client.get(reverse('student_dashboard'))
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
        prefs.theme = 'dark'
        prefs.compact_layout = True
        prefs.save()
        html = self.client.get(reverse('settings')).content.decode()
        # The sms toggle + dark theme + compact layout options render selected.
        self.assertIn('data-pref="sms_alerts" checked', html)
        self.assertIn('data-theme="dark" data-pref="theme" data-value="dark" aria-pressed="true"', html)
        self.assertIn('data-pref="email_alerts" checked', html)
        self.assertIn('data-layout="compact" data-pref="compact_layout" data-value="1" aria-pressed="true"', html)
        # All three theme options are offered (Light / Dark / System Default).
        self.assertIn('data-theme="light" data-pref="theme" data-value="light"', html)
        self.assertIn('data-theme="system" data-pref="theme" data-value="system"', html)
        self.assertIn('System Default', html)
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
        # The legacy dark_mode key still works and keeps theme in sync.
        self.assertIn('data-theme="dark" data-pref="theme" data-value="dark" aria-pressed="true"', html)

    def test_theme_and_layout_json_post_saves_to_database(self):
        response = self.client.post(
            reverse('settings'),
            data=json.dumps({'theme': 'system', 'compact_layout': True}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['theme'], 'system')
        self.assertTrue(data['compact_layout'])
        prefs = self.user.notification_prefs
        prefs.refresh_from_db()
        self.assertEqual(prefs.theme, 'system')
        self.assertTrue(prefs.compact_layout)
        # The legacy dark_mode flag stays in sync with the tri-state theme.
        self.assertFalse(prefs.dark_mode)

    def test_invalid_theme_rejected(self):
        response = self.client.post(
            reverse('settings'),
            data=json.dumps({'theme': 'neon'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        prefs = self.user.notification_prefs
        prefs.refresh_from_db()
        self.assertEqual(prefs.theme, 'system')  # unchanged

    def test_profile_form_updates_name_and_email(self):
        response = self.client.post(reverse('settings'), {
            'form': 'profile',
            'full_name': 'Rifat Hasan',
            'email': 'rifat@niter.edu.bd',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your account settings have been saved')
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Rifat')
        self.assertEqual(self.user.last_name, 'Hasan')
        self.assertEqual(self.user.email, 'rifat@niter.edu.bd')

    def test_profile_form_rejects_duplicate_email(self):
        User.objects.create_user(username='other', email='other@niter.edu.bd', password='x12345678')
        response = self.client.post(reverse('settings'), {
            'form': 'profile',
            'full_name': 'Rifat Hasan',
            'email': 'other@niter.edu.bd',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already used by another account')
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, 'other@niter.edu.bd')

    def test_profile_form_requires_valid_email(self):
        response = self.client.post(reverse('settings'), {
            'form': 'profile',
            'full_name': 'Rifat Hasan',
            'email': 'not-an-email',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid email address')
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, '')

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


class DisplayPreferencesIntegrationTest(TestCase):
    """Global display preferences — context processor, partial, and middleware.

    The Display tab (/settings/?tab=display) persists theme / timezone /
    density to ``UserNotificationPreference``; the ``display_prefs`` context
    processor + ``UserDisplayPreferencesMiddleware`` then serve those to every
    page (including the Website Builder and builder-authored public pages) via
    the ``partials/display_prefs.html`` no-flash driver.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='prefs_global', password='x12345678')
        self.client.force_login(self.user)

    def test_context_processor_exposes_saved_prefs(self):
        prefs = self.user.notification_prefs
        prefs.theme = 'dark'
        prefs.timezone = 'UTC'
        prefs.compact_layout = True
        prefs.save()

        response = self.client.get(reverse('student_dashboard'))
        data = response.context['DISPLAY_PREFS']
        self.assertEqual(data['theme'], 'dark')
        self.assertEqual(data['timezone'], 'UTC')
        self.assertEqual(data['density'], 'compact')
        self.assertTrue(data['authenticated'])
        self.assertEqual(data['saveUrl'], reverse('settings'))

        # The no-flash config payload is embedded for the driver.
        html = response.content.decode()
        self.assertIn('id="display-prefs-config"', html)
        self.assertIn('"theme": "dark"', html)
        self.assertIn('"density": "compact"', html)
        self.assertIn('"timezone": "UTC"', html)
        self.assertIn('js/display-preferences.js', html)

    def test_context_processor_defaults_for_rowless_user(self):
        orphan = User.objects.create_user(username='no_prefs_row', password='x12345678')
        UserNotificationPreference.objects.filter(user=orphan).delete()
        self.client.force_login(orphan)
        response = self.client.get(reverse('student_dashboard'))
        data = response.context['DISPLAY_PREFS']
        self.assertEqual(data['theme'], 'system')
        self.assertEqual(data['density'], 'comfortable')
        self.assertTrue(data['authenticated'])

    def test_anonymous_visitors_keep_device_local_prefs(self):
        self.client.logout()
        response = self.client.get(reverse('transport_dashboard'))
        self.assertEqual(response.status_code, 200)
        # No account payload → the driver falls back to localStorage.
        self.assertNotIn('authenticated', response.context['DISPLAY_PREFS'])
        html = response.content.decode()
        self.assertIn('id="display-prefs-config"', html)
        self.assertIn('js/display-preferences.js', html)

    def test_settings_page_includes_the_global_driver(self):
        response = self.client.get(reverse('settings') + '?tab=display')
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('id="display-prefs-config"', html)
        self.assertIn('js/display-preferences.js', html)
        # The settings UI still offers the tri-state theme options.
        self.assertIn('data-theme="dark" data-pref="theme" data-value="dark"', html)
        self.assertIn('data-pref="timezone"', html)
        self.assertIn('data-pref="compact_layout"', html)

    def test_builder_and_public_pages_include_the_driver(self):
        template = PageTemplate.objects.create(
            name='Prefs Page', layout_json={'sections': [{'name': 'hero'}]},
        )
        page = EditablePage.objects.create(
            title='Display Prefs Page', slug='display-prefs-page', template=template,
        )
        ContentBlock.objects.create(
            page=page, element_id='hero', content_html='<h1>Prefs aware</h1>',
        )
        # Public page (/pages/<slug>/) — the Website Builder's live canvas.
        response = self.client.get(reverse('editable_page_public', args=[page.slug]))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('id="display-prefs-config"', html)
        self.assertIn('js/display-preferences.js', html)
        # Builder consoles carry the driver too.
        self.client.force_login(User.objects.create_superuser(
            username='prefs_root', email='pr@niter.edu.bd', password='rootpass123',
        ))
        for name, kwargs in [
            ('builder_dashboard', {}),
            ('builder_editor', {'page_slug': page.slug}),
            ('visual_editor', {'page_slug': page.slug}),
        ]:
            response = self.client.get(reverse(name, kwargs=kwargs))
            self.assertEqual(response.status_code, 200, msg=name)
            html = response.content.decode()
            self.assertIn('id="display-prefs-config"', html, msg=name)
            self.assertIn('js/display-preferences.js', html, msg=name)

    def test_settings_json_save_still_survives(self):
        # The driver persists through the existing /settings/ JSON endpoint.
        response = self.client.post(
            reverse('settings'),
            data=json.dumps({'theme': 'system', 'timezone': 'Asia/Kolkata', 'compact_layout': False}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        prefs = self.user.notification_prefs
        prefs.refresh_from_db()
        self.assertEqual(prefs.theme, 'system')
        self.assertEqual(prefs.timezone, 'Asia/Kolkata')
        self.assertFalse(prefs.compact_layout)


class UserTimezoneMiddlewareTest(TestCase):
    """UserDisplayPreferencesMiddleware — per-request timezone activation."""

    def test_activates_the_users_timezone_during_the_request(self):
        from django.http import HttpResponse
        from core.middleware import UserDisplayPreferencesMiddleware

        user = User.objects.create_user(username='tz_user', password='x12345678')
        prefs = user.notification_prefs
        prefs.timezone = 'UTC'
        prefs.save()

        request = RequestFactory().get('/')
        request.user = user
        captured = {}

        def get_response(req):
            captured['zone'] = str(timezone.get_current_timezone())
            return HttpResponse('ok')

        response = UserDisplayPreferencesMiddleware(get_response)(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured['zone'], 'UTC')
        # request.display_prefs is cached for the context processor.
        self.assertEqual(request.display_prefs['timezone'], 'UTC')
        self.assertEqual(request.display_prefs['theme'], 'system')
        self.assertEqual(request.display_prefs['density'], 'comfortable')

    def test_anonymous_requests_are_left_untouched(self):
        from django.contrib.auth.models import AnonymousUser
        from django.http import HttpResponse
        from core.middleware import UserDisplayPreferencesMiddleware

        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        def get_response(req):
            return HttpResponse('ok')

        response = UserDisplayPreferencesMiddleware(get_response)(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.display_prefs['timezone'], None)


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


class NoteAnalysisAsyncTests(TestCase):
    """Huey-backed note analysis — queued rows, the worker task, poll endpoint.

    Huey runs in ``immediate`` mode under tests (DEBUG or no REDIS_URL), so
    ``analyze_note_content.delay()`` executes synchronously and the API keeps
    answering inline results, exactly as it did before the queue was added.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='async_notes', password='x12345678')
        self.client.login(username='async_notes', password='x12345678')
        self.SAMPLE = (
            'Divide and conquer breaks problems into subproblems. '
            'The master theorem solves recurrence relations. '
            'Recurrence relations appear in divide and conquer analysis.'
        )

    def test_summarize_returns_inline_result_in_immediate_mode(self):
        response = self.client.post(reverse('api_note_summarize'), {'content': self.SAMPLE})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('divide and conquer', data['summary'].lower())
        self.assertEqual(data['sentence_count'], 3)

    def test_keywords_returns_inline_result_in_immediate_mode(self):
        response = self.client.post(reverse('api_note_keywords'), {'content': self.SAMPLE})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('recurrence', data['keywords'])
        self.assertNotIn('the', data['keywords'])

    def test_worker_task_computes_summary_and_keywords(self):
        from core.models import NoteAnalysis
        from core.tasks import analyze_note_content
        analysis = NoteAnalysis.objects.create(user=self.user, content=self.SAMPLE)
        analyze_note_content(analysis.pk)
        analysis.refresh_from_db()
        self.assertEqual(analysis.status, 'done')
        self.assertIn('divide', analysis.keywords)
        self.assertIn('recurrence', analysis.keywords)
        self.assertEqual(analysis.sentence_count, 3)
        self.assertIsNotNone(analysis.completed_at)

    def test_status_endpoint_tracks_queued_then_done(self):
        from core.models import NoteAnalysis
        from core.tasks import analyze_note_content
        analysis = NoteAnalysis.objects.create(user=self.user, content=self.SAMPLE)
        url = reverse('api_note_analysis_status', args=[analysis.analysis_id])
        self.assertEqual(self.client.get(url).json()['status'], 'queued')
        analyze_note_content(analysis.pk)
        data = self.client.get(url).json()
        self.assertEqual(data['status'], 'done')
        self.assertIn('summary', data)
        self.assertIn('keywords', data)

    def test_status_endpoint_scoped_to_owner(self):
        from core.models import NoteAnalysis
        other = User.objects.create_user(username='async_other', password='x12345678')
        analysis = NoteAnalysis.objects.create(user=other, content='secret')
        response = self.client.get(reverse('api_note_analysis_status', args=[analysis.analysis_id]))
        self.assertEqual(response.status_code, 404)

    def test_worker_task_marks_failed_when_extraction_raises(self):
        from unittest import mock
        from core.models import NoteAnalysis
        from core.tasks import analyze_note_content
        analysis = NoteAnalysis.objects.create(user=self.user, content=self.SAMPLE)
        with mock.patch('core.tasks.extract_summary', side_effect=RuntimeError('boom')):
            analyze_note_content(analysis.pk)
        analysis.refresh_from_db()
        self.assertEqual(analysis.status, 'failed')
        self.assertTrue(analysis.error_message)

    def test_summarize_reports_failure_in_immediate_mode(self):
        from unittest import mock
        with mock.patch('core.tasks.extract_summary', side_effect=RuntimeError('boom')):
            response = self.client.post(reverse('api_note_summarize'), {'content': self.SAMPLE})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'failed')
        self.assertTrue(data['message'])

    def test_poll_endpoint_reports_failed_with_message(self):
        from core.models import NoteAnalysis
        analysis = NoteAnalysis.objects.create(
            user=self.user, content=self.SAMPLE, status='failed', error_message='Analysis failed — please try again.',
        )
        data = self.client.get(reverse('api_note_analysis_status', args=[analysis.analysis_id])).json()
        self.assertEqual(data['status'], 'failed')
        self.assertIn('failed', data['message'])

    def test_analysis_endpoints_require_login(self):
        from core.models import NoteAnalysis
        self.client.logout()
        response = self.client.post(reverse('api_note_summarize'), {'content': 'x'})
        self.assertEqual(response.status_code, 302)
        analysis = NoteAnalysis.objects.create(user=self.user, content='x')
        response = self.client.get(reverse('api_note_analysis_status', args=[analysis.analysis_id]))
        self.assertEqual(response.status_code, 302)


def _fake_openrouter_response(content='Mocked assistant reply.'):
    """A requests.Response stand-in for mocked OpenRouter HTTP calls."""
    response = mock.Mock()
    response.status_code = 200
    response.text = '{"choices": []}'
    response.json.return_value = {
        'choices': [{'message': {'content': content}}],
    }
    return response


class ResearchQueryApiTest(TestCase):
    """POST /research-ai/api/query/ — OpenRouter-backed chat with persisted
    threads, graceful offline fallback, and friendly provider error payloads.

    OpenRouter HTTP calls are mocked with ``unittest.mock.patch`` so the suite
    runs fully offline.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='researcher', password='x12345678')
        self.client.login(username='researcher', password='x12345678')

    def _query(self, **payload):
        return self.client.post(reverse('api_research_query'), payload)

    # ------------------------------------------------------------------
    # Request validation
    # ------------------------------------------------------------------

    def test_requires_login(self):
        self.client.logout()
        response = self._query(message='hello')
        self.assertEqual(response.status_code, 302)

    def test_requires_message(self):
        response = self._query(message='   ')
        self.assertEqual(response.status_code, 400)

    def test_legacy_prompt_alias_still_accepted(self):
        with override_settings(OPENROUTER_API_KEY=''):
            response = self._query(prompt='literature review')
        self.assertEqual(response.status_code, 200)

    def test_requires_post(self):
        response = self.client.get(reverse('api_research_query'))
        self.assertEqual(response.status_code, 405)

    # ------------------------------------------------------------------
    # Offline fallback (OPENROUTER_API_KEY empty/missing) — no crash
    # ------------------------------------------------------------------

    @override_settings(OPENROUTER_API_KEY='')
    def test_missing_key_degrades_to_offline_engine(self):
        """Empty/missing key → a well-formed success JSON from the offline
        engine (graceful fallback, never a crash)."""
        response = self._query(message='Draft a literature review on IoT in textiles', citation_style='APA 7')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['engine'], 'offline')
        self.assertIsNone(data['model'])
        self.assertTrue(data['response'].startswith('## '))
        self.assertIn('References (APA 7)', data['response'])
        self.assertTrue(data['thread_id'])

    @override_settings(OPENROUTER_API_KEY='')
    def test_offline_engine_routes_by_keyword(self):
        cases = {
            'Draft a literature review on IoT in textiles': 'IoT in Textile Manufacturing',
            'Break down the methodology section': 'Methodology Breakdown',
            'Check this citation in IEEE': 'Citation Formatting Check',
            '/summarize the abstract I pasted': 'Abstract Summary',
            'Explain the superposition theorem': 'Superposition Circuit Analysis',
            'Compare IoT architectures for looms': 'Textile IoT Automation Models',
            'Tell me about your day': 'Here is how I can help',
        }
        for prompt, heading in cases.items():
            with self.subTest(prompt=prompt):
                data = self._query(message=prompt).json()
                self.assertEqual(data['status'], 'success')
                self.assertIn(heading, data['response'])

    # ------------------------------------------------------------------
    # OpenRouter path (key configured, HTTP mocked)
    # ------------------------------------------------------------------

    @override_settings(
        OPENROUTER_API_KEY='test-key',
        OPENROUTER_DEFAULT_MODEL='nvidia/nemotron-3.5-lightning:free',
        OPENROUTER_FALLBACK_MODEL='openrouter/free',
        OPENROUTER_BASE_URL='https://openrouter.ai/api/v1/chat/completions',
    )
    def test_openrouter_used_when_key_configured(self):
        with mock.patch('services.openrouter.requests.post', return_value=_fake_openrouter_response('Real AI reply.')) as post:
            response = self._query(message='Explain superposition', citation_style='APA 7')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['engine'], 'openrouter')
        self.assertEqual(data['model'], 'nvidia/nemotron-3.5-lightning:free')
        self.assertEqual(data['response'], 'Real AI reply.')

        # Headers carry auth + branding + dynamic referer.
        args, kwargs = post.call_args
        headers = kwargs['headers']
        self.assertEqual(args[0], 'https://openrouter.ai/api/v1/chat/completions')
        self.assertEqual(headers['Authorization'], 'Bearer test-key')
        self.assertEqual(headers['X-Title'], 'NITER Centralized Dash')
        self.assertEqual(headers['HTTP-Referer'], 'https://testserver')
        self.assertEqual(kwargs['timeout'], 30)
        # Default free model sent to the provider.
        self.assertEqual(kwargs['json']['model'], 'nvidia/nemotron-3.5-lightning:free')
        # System prompt (prepended) injects the selected citation style.
        system = kwargs['json']['messages'][0]['content']
        self.assertEqual(kwargs['json']['messages'][0]['role'], 'system')
        self.assertIn('APA 7', system)

    @override_settings(
        OPENROUTER_API_KEY='test-key',
        OPENROUTER_DEFAULT_MODEL='nvidia/nemotron-3.5-lightning:free',
        OPENROUTER_FALLBACK_MODEL='openrouter/free',
    )
    def test_model_param_passed_to_provider(self):
        with mock.patch('services.openrouter.requests.post', return_value=_fake_openrouter_response('ok')) as post:
            response = self._query(message='hello', model='openrouter/free')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['model'], 'openrouter/free')
        _, kwargs = post.call_args
        self.assertEqual(kwargs['json']['model'], 'openrouter/free')

    @override_settings(
        OPENROUTER_API_KEY='test-key',
        OPENROUTER_DEFAULT_MODEL='nvidia/nemotron-3.5-lightning:free',
        OPENROUTER_FALLBACK_MODEL='openrouter/free',
    )
    def test_unknown_model_falls_back_to_default(self):
        with mock.patch('services.openrouter.requests.post', return_value=_fake_openrouter_response('ok')) as post:
            response = self._query(message='hello', model='openai/gpt-4o')  # not allowed
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['model'], 'nvidia/nemotron-3.5-lightning:free')
        _, kwargs = post.call_args
        self.assertEqual(kwargs['json']['model'], 'nvidia/nemotron-3.5-lightning:free')

    @override_settings(
        OPENROUTER_API_KEY='test-key',
        OPENROUTER_DEFAULT_MODEL='nvidia/nemotron-3.5-lightning:free',
        OPENROUTER_FALLBACK_MODEL='openrouter/free',
    )
    def test_rate_limit_retries_with_fallback_model(self):
        """429 on the primary model → one automatic retry with the fallback."""
        limited = mock.Mock()
        limited.status_code = 429
        limited.text = 'rate limited'
        with mock.patch(
            'services.openrouter.requests.post',
            side_effect=[limited, _fake_openrouter_response('fallback answered')],
        ) as post:
            response = self._query(message='hello')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['engine'], 'openrouter')
        self.assertEqual(data['model'], 'openrouter/free')
        self.assertEqual(post.call_count, 2)
        first_model = post.call_args_list[0][1]['json']['model']
        second_model = post.call_args_list[1][1]['json']['model']
        self.assertEqual(first_model, 'nvidia/nemotron-3.5-lightning:free')
        self.assertEqual(second_model, 'openrouter/free')

    @override_settings(
        OPENROUTER_API_KEY='test-key',
        OPENROUTER_DEFAULT_MODEL='nvidia/nemotron-3.5-lightning:free',
        OPENROUTER_FALLBACK_MODEL='openrouter/free',
    )
    def test_503_retries_with_fallback_model(self):
        """503 on the primary model → one automatic retry with the fallback."""
        unavailable = mock.Mock()
        unavailable.status_code = 503
        unavailable.text = 'service unavailable'
        with mock.patch(
            'services.openrouter.requests.post',
            side_effect=[unavailable, _fake_openrouter_response('recovered')],
        ) as post:
            response = self._query(message='hello')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['engine'], 'openrouter')
        self.assertEqual(response.json()['model'], 'openrouter/free')
        self.assertEqual(post.call_count, 2)

    @override_settings(
        OPENROUTER_API_KEY='test-key',
        OPENROUTER_DEFAULT_MODEL='nvidia/nemotron-3.5-lightning:free',
        OPENROUTER_FALLBACK_MODEL='openrouter/free',
    )
    def test_fallback_exhausted_returns_429_payload(self):
        """Both attempts rate-limited → friendly 429 error to the client."""
        limited = mock.Mock()
        limited.status_code = 429
        limited.text = 'still rate limited'
        with mock.patch('services.openrouter.requests.post', return_value=limited) as post:
            response = self._query(message='hello')
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json()['status'], 'error')
        self.assertEqual(post.call_count, 2)
        self.assertIn('thread_id', response.json())

    @override_settings(OPENROUTER_API_KEY='test-key')
    def test_503_exhausted_returns_503_payload(self):
        unavailable = mock.Mock()
        unavailable.status_code = 503
        unavailable.text = 'down'
        with mock.patch('services.openrouter.requests.post', return_value=unavailable):
            response = self._query(message='hello')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['status'], 'error')

    @override_settings(OPENROUTER_API_KEY='test-key')
    def test_rate_limit_returns_429_payload(self):
        response = mock.Mock()
        response.status_code = 429
        response.text = 'rate limited'
        with mock.patch('services.openrouter.requests.post', return_value=response):
            resp = self._query(message='hello')
        self.assertEqual(resp.status_code, 429)
        data = resp.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('rate-limited', data['message'].lower())
        self.assertIn('thread_id', data)

    @override_settings(OPENROUTER_API_KEY='test-key')
    def test_timeout_returns_504_payload(self):
        from requests.exceptions import Timeout
        with mock.patch('services.openrouter.requests.post', side_effect=Timeout('slow')):
            resp = self._query(message='hello')
        self.assertEqual(resp.status_code, 504)
        self.assertEqual(resp.json()['status'], 'error')

    @override_settings(OPENROUTER_API_KEY='bad-key')
    def test_auth_error_returns_502_payload(self):
        response = mock.Mock()
        response.status_code = 401
        response.text = 'invalid key'
        with mock.patch('services.openrouter.requests.post', return_value=response):
            resp = self._query(message='hello')
        self.assertEqual(resp.status_code, 502)
        self.assertEqual(resp.json()['status'], 'error')
        self.assertIn('API key', resp.json()['message'])

    @override_settings(OPENROUTER_API_KEY='test-key')
    def test_transport_error_returns_502_payload(self):
        from requests.exceptions import ConnectionError
        with mock.patch('services.openrouter.requests.post', side_effect=ConnectionError('no route')):
            resp = self._query(message='hello')
        self.assertEqual(resp.status_code, 502)
        self.assertEqual(resp.json()['status'], 'error')

    # ------------------------------------------------------------------
    # Persisted threads
    # ------------------------------------------------------------------

    @override_settings(OPENROUTER_API_KEY='')
    def test_creates_thread_and_persists_messages(self):
        data = self._query(message='First question').json()
        thread = ResearchThread.objects.get(pk=data['thread_id'])
        self.assertEqual(thread.user, self.user)
        self.assertEqual(thread.citation_style, 'IEEE')
        self.assertEqual(thread.title, 'First question')
        self.assertEqual(thread.messages.count(), 2)
        self.assertEqual(
            list(thread.messages.values_list('role', flat=True)),
            ['user', 'assistant'],
        )
        self.assertEqual(thread.messages.get(role='user').content, 'First question')

    @override_settings(OPENROUTER_API_KEY='')
    def test_reuses_thread_when_thread_id_sent(self):
        first = self._query(message='First').json()
        second = self._query(message='Second', thread_id=first['thread_id']).json()
        self.assertEqual(first['thread_id'], second['thread_id'])
        thread = ResearchThread.objects.get(pk=first['thread_id'])
        self.assertEqual(thread.messages.count(), 4)

    @override_settings(OPENROUTER_API_KEY='')
    def test_unknown_thread_returns_404(self):
        response = self._query(message='hello', thread_id=999999)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['status'], 'error')

    @override_settings(OPENROUTER_API_KEY='')
    def test_citation_style_updates_thread(self):
        first = self._query(message='First', citation_style='IEEE').json()
        self._query(message='Second', citation_style='Chicago', thread_id=first['thread_id'])
        thread = ResearchThread.objects.get(pk=first['thread_id'])
        self.assertEqual(thread.citation_style, 'Chicago')

    @override_settings(OPENROUTER_API_KEY='')
    def test_title_truncated_from_first_message(self):
        data = self._query(message='x' * 100).json()
        thread = ResearchThread.objects.get(pk=data['thread_id'])
        self.assertLessEqual(len(thread.title), 61)

    @override_settings(OPENROUTER_API_KEY='')
    def test_oversized_upload_rejected_with_400(self):
        big = SimpleUploadedFile(
            'big.pdf', b'x' * (10 * 1024 * 1024 + 1), content_type='application/pdf'
        )
        response = self._query(message='hello', file=big)
        self.assertEqual(response.status_code, 400)
        self.assertIn('10 MB', response.json()['message'])
        # Rejected before any row is created.
        self.assertEqual(ResearchThread.objects.count(), 0)

    @override_settings(OPENROUTER_API_KEY='')
    def test_active_thread_floats_to_top(self):
        first = self._query(message='First').json()
        second = self._query(message='Second').json()
        # Replying inside the older thread bumps its ``updated_at``.
        self._query(message='Third', thread_id=first['thread_id'])
        threads = self.client.get(reverse('api_research_threads')).json()
        self.assertEqual(threads['threads'][0]['id'], first['thread_id'])
        self.assertEqual(threads['threads'][0]['message_count'], 4)

    def test_thread_list_and_detail_owner_scoped(self):
        created = self._query(message='Hello world').json()
        thread_id = created['thread_id']

        threads = self.client.get(reverse('api_research_threads')).json()
        self.assertEqual(threads['status'], 'success')
        self.assertEqual(threads['threads'][0]['id'], thread_id)

        detail = self.client.get(reverse('api_research_thread_detail', args=[thread_id])).json()
        self.assertEqual(detail['thread']['id'], thread_id)
        self.assertEqual(len(detail['messages']), 2)
        self.assertEqual(detail['messages'][0]['role'], 'user')

        # Another user's threads are invisible (owner-scoped).
        other = User.objects.create_user(username='other-researcher', password='x12345678')
        ResearchThread.objects.create(user=other, title='Not yours')
        data = self.client.get(reverse('api_research_threads')).json()
        self.assertEqual([t['id'] for t in data['threads']], [thread_id])

    def test_thread_detail_404_for_foreign_thread(self):
        other = User.objects.create_user(username='stranger', password='x12345678')
        thread = ResearchThread.objects.create(user=other, title='Private')
        response = self.client.get(reverse('api_research_thread_detail', args=[thread.pk]))
        self.assertEqual(response.status_code, 404)

    def test_delete_thread(self):
        created = self._query(message='Bye').json()
        thread_id = created['thread_id']
        response = self.client.delete(reverse('api_research_thread_detail', args=[thread_id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ResearchThread.objects.filter(pk=thread_id).exists())
        self.assertFalse(ResearchMessage.objects.filter(thread_id=thread_id).exists())


class OpenRouterServiceTest(TestCase):
    """services.openrouter.call_openrouter — automatic free-model fallback."""

    @override_settings(
        OPENROUTER_API_KEY='key',
        OPENROUTER_DEFAULT_MODEL='primary-free-model',
        OPENROUTER_FALLBACK_MODEL='fallback-free-model',
    )
    def test_429_triggers_fallback_retry(self):
        limited = mock.Mock()
        limited.status_code = 429
        limited.text = 'rate limited'
        with mock.patch(
            'services.openrouter.requests.post',
            side_effect=[limited, _fake_openrouter_response('ok')],
        ) as post:
            text, model_used = call_openrouter([{'role': 'user', 'content': 'hi'}])
        self.assertEqual(text, 'ok')
        self.assertEqual(model_used, 'fallback-free-model')
        self.assertEqual(post.call_count, 2)
        models = [c[1]['json']['model'] for c in post.call_args_list]
        self.assertEqual(models, ['primary-free-model', 'fallback-free-model'])

    @override_settings(
        OPENROUTER_API_KEY='key',
        OPENROUTER_DEFAULT_MODEL='primary-free-model',
        OPENROUTER_FALLBACK_MODEL='fallback-free-model',
    )
    def test_system_prompt_prepended_and_no_retry_on_success(self):
        with mock.patch('services.openrouter.requests.post', return_value=_fake_openrouter_response('ok')) as post:
            text, model_used = call_openrouter(
                [{'role': 'user', 'content': 'hi'}],
                system_prompt='You are the NITER assistant.',
            )
        self.assertEqual(text, 'ok')
        self.assertEqual(model_used, 'primary-free-model')
        self.assertEqual(post.call_count, 1)
        _, kwargs = post.call_args
        messages = kwargs['json']['messages']
        self.assertEqual(messages[0], {'role': 'system', 'content': 'You are the NITER assistant.'})
        self.assertEqual(messages[1], {'role': 'user', 'content': 'hi'})


class ResearchDocumentTextTest(TestCase):
    """services.parser — plain-text extraction from PDF/DOCX uploads."""

    @staticmethod
    def _make_docx(text):
        from docx import Document
        import io
        buffer = io.BytesIO()
        document = Document()
        for line in text.split('\n'):
            document.add_paragraph(line)
        document.save(buffer)
        buffer.seek(0)
        return SimpleUploadedFile(
            'paper.docx',
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )

    @staticmethod
    def _make_pdf(text):
        """Build a minimal single-page PDF whose only text is ``text``."""
        content = b'BT /F1 12 Tf 72 720 Td (' + text.encode('ascii') + b') Tj ET'
        objects = [
            b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>',
            b'<< /Length %d >>\nstream\n%s\nendstream' % (len(content), content),
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
        ]
        out = [b'%PDF-1.4\n']
        offsets = []
        for index, obj in enumerate(objects, start=1):
            offsets.append(len(b''.join(out)))
            out.append(b'%d 0 obj\n%s\nendobj\n' % (index, obj))
        xref_pos = len(b''.join(out))
        out.append(b'xref\n0 %d\n' % (len(objects) + 1))
        out.append(b'0000000000 65535 f \n')
        for offset in offsets:
            out.append(b'%010d 00000 n \n' % offset)
        out.append(b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF' % (len(objects) + 1, xref_pos))
        return SimpleUploadedFile('paper.pdf', b''.join(out), content_type='application/pdf')

    def test_extracts_docx_paragraphs(self):
        upload = self._make_docx('Abstract: IoT looms with edge inference.\nKeywords: textile automation')
        text = extract_document_text(upload)
        self.assertIn('Abstract: IoT looms with edge inference.', text)
        self.assertIn('Keywords: textile automation', text)

    def test_extracts_pdf_text(self):
        upload = self._make_pdf('Hello Research AI')
        text = extract_document_text(upload)
        self.assertIsNotNone(text)
        self.assertIn('Hello Research AI', text)

    def test_unsupported_format_returns_none(self):
        upload = SimpleUploadedFile('notes.txt', b'plain', content_type='text/plain')
        self.assertIsNone(extract_document_text(upload))

    def test_query_endpoint_accepts_uploaded_docx(self):
        """The API extracts the attached reference and passes it to the prompt."""
        user = User.objects.create_user(username='paper-user', password='x12345678')
        self.client.login(username='paper-user', password='x12345678')
        upload = self._make_docx('This loom uses an edge gateway for vibration analysis.')
        with override_settings(OPENROUTER_API_KEY='test-key'):
            with mock.patch('services.openrouter.requests.post', return_value=_fake_openrouter_response('grounded answer')) as post:
                response = self.client.post(
                    reverse('api_research_query'),
                    {'message': 'summarize the paper', 'citation_style': 'IEEE', 'file': upload},
                )
        self.assertEqual(response.status_code, 200)
        _, kwargs = post.call_args
        system = kwargs['json']['messages'][0]['content']
        self.assertIn('edge gateway for vibration analysis', system)
        self.assertIn('uploaded a reference document', system)


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
        for block_type in ('hero', 'features', 'split', 'faq', 'stats', 'testimonials', 'cta'):
            self.assertIn(block_type, codes)

    def test_block_schemas_document_each_structured_type(self):
        for block_type in ('hero', 'features', 'split', 'faq', 'stats', 'testimonials', 'cta'):
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

    def test_sanitize_html_filter_strips_scripts_and_marks_safe(self):
        from django.template import Context, Template
        tpl = Template(
            "{% load builder_tags %}{{ value|sanitize_html }}"
        )
        html = tpl.render(Context({
            'value': '<b>ok</b><script>alert(1)</script><a href="javascript:x">x</a>',
        }))
        self.assertIn('<b>ok</b>', html)
        self.assertNotIn('<script', html)
        self.assertNotIn('javascript:', html)

    def test_sanitize_css_filter_blocks_style_breakout(self):
        from django.template import Context, Template
        tpl = Template(
            "{% load builder_tags %}{{ value|sanitize_css }}"
        )
        html = tpl.render(Context({
            'value': '.x{color:red}</style><script>alert(1)</script>',
        }))
        self.assertIn('.x{color:red}', html)
        self.assertNotIn('</style>', html)
        self.assertNotIn('</script>', html)

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


class BuilderBlockOrderingTest(TestCase):
    """Visual editor block management: ``order`` persistence, atomic reorder,
    delete, and ordered live-page rendering."""

    def setUp(self):
        self.page = EditablePage.objects.create(title='Ordered', slug='ordered')
        self.user = User.objects.create_superuser(
            username='root_order', email='ro@niter.edu.bd', password='rootpass123',
        )
        self.client.force_login(self.user)

    def _post_json(self, payload):
        return self.client.post(
            reverse('save_content_block'),
            data=json.dumps(payload),
            content_type='application/json',
        )

    def _create_block(self, element_id, html):
        response = self._post_json({
            'page_slug': self.page.slug,
            'element_id': element_id,
            'content_html': html,
        })
        self.assertEqual(response.status_code, 200)
        return ContentBlock.objects.get(page=self.page, element_id=element_id)

    def test_order_defaults_to_zero(self):
        block = ContentBlock.objects.create(page=self.page, element_id='plain')
        self.assertEqual(block.order, 0)

    def test_new_blocks_append_with_next_order(self):
        first = self._create_block('first', '<p>First</p>')
        second = self._create_block('second', '<p>Second</p>')
        self.assertEqual(first.order, 1)
        self.assertEqual(second.order, 2)

    def test_reorder_updates_orders_atomically(self):
        self._create_block('a', '<p>A</p>')
        self._create_block('b', '<p>B</p>')
        self._create_block('c', '<p>C</p>')
        response = self._post_json({
            'page_slug': self.page.slug,
            'reorder': [
                {'element_id': 'c', 'order': 0},
                {'element_id': 'a', 'order': 1},
                {'element_id': 'b', 'order': 2},
            ],
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['reordered'], 3)
        self.assertEqual(ContentBlock.objects.get(page=self.page, element_id='c').order, 0)
        self.assertEqual(ContentBlock.objects.get(page=self.page, element_id='a').order, 1)
        self.assertEqual(ContentBlock.objects.get(page=self.page, element_id='b').order, 2)

    def test_reorder_rejects_unknown_block_without_changes(self):
        self._create_block('a', '<p>A</p>')
        response = self._post_json({
            'page_slug': self.page.slug,
            'reorder': [
                {'element_id': 'a', 'order': 0},
                {'element_id': 'ghost', 'order': 1},
            ],
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Unknown block', response.json()['message'])
        # Nothing was persisted (atomic — the valid entry was not applied).
        self.assertEqual(ContentBlock.objects.get(page=self.page, element_id='a').order, 1)

    def test_reorder_rejects_bad_entry(self):
        self._create_block('a', '<p>A</p>')
        response = self._post_json({
            'page_slug': self.page.slug,
            'reorder': [{'element_id': 'a', 'order': 'up'}],
        })
        self.assertEqual(response.status_code, 400)

    def test_delete_removes_block(self):
        self._create_block('doomed', '<p>Bye</p>')
        response = self._post_json({
            'page_slug': self.page.slug,
            'element_id': 'doomed',
            'delete': True,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['deleted'], 1)
        self.assertFalse(ContentBlock.objects.filter(page=self.page, element_id='doomed').exists())

    def test_delete_missing_block_is_success(self):
        response = self._post_json({
            'page_slug': self.page.slug,
            'element_id': 'nope',
            'delete': True,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['deleted'], 0)

    def test_editable_page_renders_blocks_in_order(self):
        self._create_block('a', '<p>AAA</p>')
        self._create_block('b', '<p>BBB</p>')
        self._create_block('c', '<p>CCC</p>')
        self._post_json({
            'page_slug': self.page.slug,
            'reorder': [
                {'element_id': 'c', 'order': 0},
                {'element_id': 'a', 'order': 1},
                {'element_id': 'b', 'order': 2},
            ],
        })
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        self.assertLess(html.index('CCC'), html.index('AAA'))
        self.assertLess(html.index('AAA'), html.index('BBB'))

    def test_visual_editor_exposes_block_ids(self):
        self._create_block('alpha', '<p>Alpha</p>')
        response = self.client.get(reverse('visual_editor', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-block-id="alpha"')
        # Block management handles + instant CSS save UI render.
        self.assertContains(response, 'data-action="up"')
        self.assertContains(response, 'data-action="down"')
        self.assertContains(response, 'data-action="delete"')
        self.assertContains(response, 'id="save-css"')


class CustomPagesNavTest(TestCase):
    """Page lifecycle navigation: published pages flagged ``show_in_nav``
    surface in the shared topbar's Pages dropdown and the mobile profile
    menu; drafts and unflagged pages never appear anywhere."""

    def setUp(self):
        self.published_nav = EditablePage.objects.create(
            title='Admissions', slug='admissions', show_in_nav=True,
        )
        self.published_hidden = EditablePage.objects.create(
            title='Hidden', slug='hidden-page',
        )
        self.draft_nav = EditablePage.objects.create(
            title='Draft Nav', slug='draft-nav', show_in_nav=True, is_published=False,
        )

    def test_context_processor_filters_to_published_nav_pages(self):
        request = RequestFactory().get('/')
        pages = list(custom_pages_nav(request)['NAV_CUSTOM_PAGES'])
        slugs = {p.slug for p in pages}
        self.assertIn('admissions', slugs)
        self.assertNotIn('hidden-page', slugs)   # show_in_nav=False
        self.assertNotIn('draft-nav', slugs)     # unpublished
        self.assertEqual(len(pages), 1)

    def test_topbar_renders_pages_dropdown_with_custom_links(self):
        response = self.client.get(reverse('editable_page', args=['admissions']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'nav-dropdown')
        self.assertIn('/page/admissions/', response.content.decode())
        # Hidden + draft pages never appear in navigation.
        self.assertNotIn('/page/hidden-page/', response.content.decode())
        self.assertNotIn('/page/draft-nav/', response.content.decode())

    def test_draft_page_is_404_for_visitors(self):
        response = self.client.get(reverse('editable_page', args=['draft-nav']))
        self.assertEqual(response.status_code, 404)


class BuilderPageManagerTest(TestCase):
    """Frontend page builder (builder/edit_page.html): permission model, page
    toolbar, the drag-and-drop reorder / block save / page save endpoints, and
    draft preview for authorized builders."""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='root_pm', email='rpm@niter.edu.bd', password='rootpass123',
        )
        self.staff = User.objects.create_user(
            username='staff_pm', password='staffpass123', is_staff=True,
        )
        self.builder_staff = User.objects.create_user(
            username='builder_staff', password='builderpass123', is_staff=True,
        )
        self.builder_staff.user_permissions.add(
            Permission.objects.get(codename='change_editablepage')
        )
        self.page = EditablePage.objects.create(title='Landing', slug='landing-pm')
        ContentBlock.objects.create(
            page=self.page, element_id='hero', block_type='hero',
            content_json={'headline': 'Welcome', 'primary_label': 'Go', 'primary_url': '/departments/'},
        )
        ContentBlock.objects.create(
            page=self.page, element_id='body', content_html='<p>Body text</p>',
        )

    def _post_json(self, url_name, payload, username='root_pm', password='rootpass123'):
        self.client.login(username=username, password=password)
        return self.client.post(
            reverse(url_name), data=json.dumps(payload), content_type='application/json',
        )

    # ------------------------------------------------------------------
    # Access control
    # ------------------------------------------------------------------
    def test_builder_editor_redirects_anonymous(self):
        response = self.client.get(reverse('builder_editor', args=[self.page.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_builder_editor_forbids_staff_without_permission(self):
        self.client.login(username='staff_pm', password='staffpass123')
        response = self.client.get(reverse('builder_editor', args=[self.page.slug]))
        self.assertEqual(response.status_code, 403)

    def test_builder_editor_allows_staff_with_change_permission(self):
        self.client.login(username='builder_staff', password='builderpass123')
        response = self.client.get(reverse('builder_editor', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)

    def test_new_builder_apis_enforce_permissions(self):
        # Anonymous → redirect to login.
        response = self.client.post(
            reverse('builder_blocks_reorder'), data='{}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 302)
        # Staff without the permission → 403 on every new endpoint.
        self.client.login(username='staff_pm', password='staffpass123')
        for name in ('builder_blocks_reorder', 'builder_blocks_save', 'builder_page_save'):
            with self.subTest(api=name):
                response = self.client.post(reverse(name), data='{}', content_type='application/json')
                self.assertEqual(response.status_code, 403)

    # ------------------------------------------------------------------
    # Toolbar + markup
    # ------------------------------------------------------------------
    def test_builder_editor_renders_toolbar_and_blocks(self):
        self.client.login(username='root_pm', password='rootpass123')
        response = self.client.get(reverse('builder_editor', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        for needle in (
            'id="pb-title"', 'id="pb-published"', 'id="pb-nav"',
            'id="pb-save-draft"', 'id="pb-publish"', 'Save Draft',
            'id="pb-block-list"', 'data-block-id="hero"', 'data-block-id="body"',
            'data-block-type="hero"', 'id="pb-palette"', 'id="pb-blocks-data"',
            'Visual Editor', 'Publish',
        ):
            self.assertContains(response, needle, msg_prefix=needle)
        # The palette offers the standard section types.
        for code in ('html', 'hero', 'features', 'cta'):
            self.assertContains(response, 'data-block-type="%s"' % code)
        # Live preview iframe points at the public route.
        self.assertContains(response, reverse('editable_page', args=[self.page.slug]))

    def test_new_section_types_render_on_live_page(self):
        response = self.client.get(reverse('editable_page', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-builder-block="hero"')
        self.assertContains(response, 'Welcome')
        # HTML blocks render their raw content (no partial wrapper).
        self.assertContains(response, 'Body text')
        self.assertContains(response, 'id="body"')

    def test_features_type_is_registered_and_renders(self):
        ContentBlock.objects.create(
            page=self.page, element_id='features', block_type='features',
            content_json={'title': 'Why us', 'items': [{'icon': 'fa-star', 'title': 'Quality', 'text': 'Top-tier.'}]},
        )
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        self.assertIn('data-builder-block="features"', html)
        self.assertIn('Why us', html)
        self.assertIn('Quality', html)

    # ------------------------------------------------------------------
    # Drag-and-drop reorder endpoint
    # ------------------------------------------------------------------
    def test_blocks_reorder_is_atomic(self):
        response = self._post_json('builder_blocks_reorder', {
            'page_slug': self.page.slug,
            'reorder': [
                {'element_id': 'body', 'order': 0},
                {'element_id': 'hero', 'order': 1},
            ],
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        orders = dict(ContentBlock.objects.filter(page=self.page).values_list('element_id', 'order'))
        self.assertEqual(orders, {'body': 0, 'hero': 1})
        # The live page renders in the new order.
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        self.assertLess(html.index('Body text'), html.index('Welcome'))

    def test_blocks_reorder_rejects_unknown_block(self):
        response = self._post_json('builder_blocks_reorder', {
            'page_slug': self.page.slug,
            'reorder': [{'element_id': 'nope', 'order': 0}],
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Unknown block', response.json()['message'])

    # ------------------------------------------------------------------
    # Block save endpoint (create / update / delete)
    # ------------------------------------------------------------------
    def test_blocks_save_creates_and_updates(self):
        response = self._post_json('builder_blocks_save', {
            'page_slug': self.page.slug,
            'element_id': 'cta-new',
            'block_type': 'cta',
            'content_json': {'headline': 'Join us', 'primary_label': 'Sign Up', 'primary_url': '/signup/'},
        })
        self.assertEqual(response.status_code, 200)
        block = ContentBlock.objects.get(page=self.page, element_id='cta-new')
        self.assertEqual(block.block_type, 'cta')
        self.assertEqual(block.content_json['headline'], 'Join us')
        # Update the same block without touching its type.
        self._post_json('builder_blocks_save', {
            'page_slug': self.page.slug,
            'element_id': 'cta-new',
            'content_json': {'headline': 'Join us now'},
        })
        block.refresh_from_db()
        self.assertEqual(block.block_type, 'cta')
        self.assertEqual(block.content_json['headline'], 'Join us now')

    def test_blocks_save_deletes(self):
        response = self._post_json('builder_blocks_save', {
            'page_slug': self.page.slug,
            'element_id': 'body',
            'delete': True,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ContentBlock.objects.filter(page=self.page, element_id='body').exists())

    # ------------------------------------------------------------------
    # Page settings endpoint (Save Draft / Publish)
    # ------------------------------------------------------------------
    def test_page_save_publishes_with_title_and_flags(self):
        response = self._post_json('builder_page_save', {
            'page_slug': self.page.slug,
            'title': 'Renamed Landing',
            'is_published': True,
            'show_in_nav': True,
            'seo_description': 'A fresh landing page.',
        })
        self.assertEqual(response.status_code, 200)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, 'Renamed Landing')
        self.assertTrue(self.page.is_published)
        self.assertTrue(self.page.show_in_nav)
        self.assertEqual(self.page.seo_description, 'A fresh landing page.')

    def test_page_save_saves_draft(self):
        response = self._post_json('builder_page_save', {
            'page_slug': self.page.slug,
            'title': self.page.title,
            'is_published': False,
        })
        self.assertEqual(response.status_code, 200)
        self.page.refresh_from_db()
        self.assertFalse(self.page.is_published)
        # Drafts 404 for visitors but stay visible to authorized builders.
        self.client.logout()
        self.assertEqual(
            self.client.get(reverse('editable_page', args=[self.page.slug])).status_code,
            404,
        )

    def test_page_save_requires_title(self):
        response = self._post_json('builder_page_save', {
            'page_slug': self.page.slug,
            'title': '   ',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json()['message'])

    def test_builder_staff_can_preview_draft_page(self):
        self.page.is_published = False
        self.page.save()
        self.client.login(username='builder_staff', password='builderpass123')
        response = self.client.get(reverse('editable_page', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Body text')


class BuilderBlockLibraryDrawerTest(TestCase):
    """Block library drawer + create/delete endpoints + Text & Image Split type.

    Covers the on-canvas insert handles, the modal library (4 template cards),
    ``/builder/api/blocks/create/`` (insert vs append, defaults, validation,
    permissions) and ``/builder/api/blocks/<id>/delete/``.
    """

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='root_lib', email='rl@niter.edu.bd', password='rootpass123',
        )
        self.page = EditablePage.objects.create(title='Library', slug='library-page')
        self.hero = ContentBlock.objects.create(
            page=self.page, element_id='hero', block_type='hero', order=0,
            content_json={'headline': 'Welcome', 'primary_label': 'Go', 'primary_url': '/departments/'},
        )
        self.body = ContentBlock.objects.create(
            page=self.page, element_id='body', content_html='<p>Body</p>', order=1,
        )
        self.client.login(username='root_lib', password='rootpass123')

    def _post_json(self, url_name, payload):
        return self.client.post(
            reverse(url_name), data=json.dumps(payload), content_type='application/json',
        )

    # ------------------------------------------------------------------
    # Permissions
    # ------------------------------------------------------------------
    def test_create_delete_require_permission(self):
        # Anonymous → redirect to login.
        self.client.logout()
        response = self.client.post(
            reverse('builder_block_create'), data='{}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 302)
        # Staff without the permission → 403.
        staff = User.objects.create_user(username='staff_lib', password='staffpass123', is_staff=True)
        self.client.login(username='staff_lib', password='staffpass123')
        response = self.client.post(
            reverse('builder_block_create'), data='{}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('builder_block_delete', args=[self.hero.pk]), data='{}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    # ------------------------------------------------------------------
    # Create endpoint
    # ------------------------------------------------------------------
    def test_create_appends_block_with_defaults(self):
        response = self._post_json('builder_block_create', {
            'page_id': self.page.pk, 'block_type': 'cta',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        block = ContentBlock.objects.get(pk=data['block']['id'])
        self.assertEqual(block.block_type, 'cta')
        self.assertEqual(block.order, 2)
        self.assertEqual(block.content_json['headline'], 'Ready to start?')
        self.assertTrue(block.element_id.startswith('cta-'))

    def test_create_inserts_at_order_index(self):
        response = self._post_json('builder_block_create', {
            'page_id': self.page.pk, 'block_type': 'features', 'order_index': 1,
        })
        self.assertEqual(response.status_code, 200)
        new_block = ContentBlock.objects.get(pk=response.json()['block']['id'])
        self.assertEqual(new_block.order, 1)
        self.hero.refresh_from_db()
        self.body.refresh_from_db()
        self.assertEqual(self.hero.order, 0)
        self.assertEqual(self.body.order, 2)
        # Live page order: hero, features, body.
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        self.assertLess(html.index('Welcome'), html.index('Why choose us'))
        self.assertLess(html.index('Why choose us'), html.index('Body'))

    def test_create_validates_page_and_type(self):
        response = self._post_json('builder_block_create', {'page_id': 999999, 'block_type': 'hero'})
        self.assertEqual(response.status_code, 404)
        response = self._post_json('builder_block_create', {'page_id': self.page.pk, 'block_type': 'nope'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Unknown block type', response.json()['message'])
        response = self._post_json('builder_block_create', {'block_type': 'hero'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('page_id', response.json()['message'])

    # ------------------------------------------------------------------
    # Delete endpoint (by block id)
    # ------------------------------------------------------------------
    def test_delete_removes_block_by_id(self):
        response = self.client.post(
            reverse('builder_block_delete', args=[self.body.pk]), data='{}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertFalse(ContentBlock.objects.filter(pk=self.body.pk).exists())

    def test_delete_unknown_block_404(self):
        response = self.client.post(
            reverse('builder_block_delete', args=[999999]), data='{}', content_type='application/json',
        )
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # UI markup: canvas, insert handles, library drawer, confirm modal
    # ------------------------------------------------------------------
    def test_builder_renders_canvas_insert_buttons_and_library(self):
        response = self.client.get(reverse('builder_editor', args=[self.page.slug]))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        # One insert handle after each block (2) plus the bottom one.
        self.assertEqual(html.count('class="pb-insert" data-order'), 2)
        self.assertEqual(html.count('pb-insert--bottom'), 1)
        # Canvas sections carry pk + order for the toolbar/insert actions.
        self.assertIn('data-block-pk="%s"' % self.hero.pk, html)
        self.assertIn('data-order="1"', html)  # insert handle after the first block
        # The library drawer renders all six template cards with previews.
        for code in ('hero', 'features', 'split', 'cta', 'links', 'staff'):
            self.assertIn('data-block-type="%s"' % code, html)
        self.assertEqual(html.count('pb-lib-card'), 6)
        self.assertIn('id="pb-lib-modal"', html)
        self.assertIn('id="pb-confirm-modal"', html)
        # The canvas renders the block's partial markup server-side.
        self.assertIn('data-builder-block="hero"', html)
        self.assertIn('Welcome', html)

    def test_split_type_renders_on_live_page(self):
        ContentBlock.objects.create(
            page=self.page, element_id='split1', block_type='split',
            content_json={'heading': 'Our mission', 'text': 'Body copy.', 'image_url': '', 'image_alt': ''},
        )
        html = self.client.get(reverse('editable_page', args=[self.page.slug])).content.decode()
        self.assertIn('data-builder-block="split"', html)
        self.assertIn('Our mission', html)
        self.assertIn('Body copy.', html)


class BuilderDynamicRenderEditTest(TestCase):
    """Dynamic rendering + inline editing for all page template block types.

    Covers the Link Hub + Staff Grid types on the live page, complex-array
    content round-tripping through the block-save API (feature cards, staff
    grid items), inline style_json on the public render, and the editable
    canvas markup (data-edit-field bindings, 64-swatch palette,
    data-edit-html for text blocks).
    """

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='root_dyn', email='rd@niter.edu.bd', password='rootpass123',
        )
        self.page = EditablePage.objects.create(title='Dynamic', slug='dynamic-page')
        self.client.force_login(self.superuser)

    def _post_json(self, payload):
        return self.client.post(
            reverse('builder_blocks_save'),
            data=json.dumps(payload),
            content_type='application/json',
        )

    # ------------------------------------------------------------------
    # New types: Link Hub + Staff Grid render on the live page
    # ------------------------------------------------------------------
    def test_links_and_staff_types_in_choices_and_schemas(self):
        codes = {code for code, _label in ContentBlock.BLOCK_TYPE_CHOICES}
        self.assertIn('links', codes)
        self.assertIn('staff', codes)
        self.assertIn('items', ContentBlock.BLOCK_SCHEMAS['links'])
        self.assertIn('items', ContentBlock.BLOCK_SCHEMAS['staff'])

    def test_links_grid_renders_on_live_page(self):
        ContentBlock.objects.create(
            page=self.page, element_id='links1', block_type='links', order=0,
            content_json={
                'title': 'Explore NITER',
                'items': [
                    {'label': 'Admissions', 'url': '/admissions/'},
                    {'label': 'Departments', 'url': '/departments/'},
                ],
            },
        )
        html = self.client.get(
            reverse('editable_page', args=[self.page.slug])
        ).content.decode()
        self.assertIn('data-builder-block="links"', html)
        self.assertIn('Explore NITER', html)
        self.assertIn('Admissions', html)
        self.assertIn('href="/admissions/"', html)

    def test_staff_grid_renders_on_live_page(self):
        ContentBlock.objects.create(
            page=self.page, element_id='staff1', block_type='staff', order=0,
            content_json={
                'title': 'Leadership',
                'items': [
                    {'name': 'Jane Doe', 'role': 'Dean', 'photo_url': ''},
                    {'name': 'John Roe', 'role': 'Registrar', 'photo_url': ''},
                ],
            },
        )
        html = self.client.get(
            reverse('editable_page', args=[self.page.slug])
        ).content.decode()
        self.assertIn('data-builder-block="staff"', html)
        self.assertIn('Leadership', html)
        self.assertIn('Jane Doe', html)
        self.assertIn('Registrar', html)

    # ------------------------------------------------------------------
    # Complex-array content round-trip through the save API
    # ------------------------------------------------------------------
    def test_save_round_trips_complex_array_content(self):
        staff_items = [
            {'name': 'A', 'role': 'Dean', 'photo_url': 'https://example.com/a.jpg'},
            {'name': 'B', 'role': 'Registrar', 'photo_url': ''},
            {'name': 'C', 'role': 'Proctor', 'photo_url': 'https://example.com/c.jpg'},
        ]
        response = self._post_json({
            'page_slug': self.page.slug,
            'element_id': 'staff-multi',
            'block_type': 'staff',
            'content_json': {'title': 'Team', 'items': staff_items},
        })
        self.assertEqual(response.status_code, 200)
        block = ContentBlock.objects.get(page=self.page, element_id='staff-multi')
        self.assertEqual(block.content_json['items'], staff_items)

        features_items = [
            {'icon': 'fa-a', 'title': 'One', 'text': 'First'},
            {'icon': 'fa-b', 'title': 'Two', 'text': 'Second'},
        ]
        self._post_json({
            'page_slug': self.page.slug,
            'element_id': 'feat-multi',
            'block_type': 'features',
            'content_json': {'title': 'Why us', 'items': features_items},
        })
        block = ContentBlock.objects.get(page=self.page, element_id='feat-multi')
        self.assertEqual(len(block.content_json['items']), 2)
        self.assertEqual(block.content_json['items'][1]['title'], 'Two')

    def test_partial_save_keeps_untouched_fields(self):
        # Style-only save must not wipe content_json; field-only save must not
        # wipe style_json (the JS sends partial payloads per edit action).
        self._post_json({
            'page_slug': self.page.slug,
            'element_id': 'hero1',
            'block_type': 'hero',
            'content_json': {'headline': 'Hi', 'primary_label': 'Go', 'primary_url': '/departments/'},
            'style_json': {'color': '#1d4ed8'},
        })
        response = self._post_json({
            'page_slug': self.page.slug,
            'element_id': 'hero1',
            'style_json': {'color': '#1d4ed8', 'backgroundColor': '#111827'},
        })
        self.assertEqual(response.status_code, 200)
        block = ContentBlock.objects.get(page=self.page, element_id='hero1')
        self.assertEqual(block.content_json['headline'], 'Hi')
        self.assertEqual(block.style_json.get('color'), '#1d4ed8')
        self.assertEqual(block.style_json.get('backgroundColor'), '#111827')
        # Field-only save keeps the style untouched.
        self._post_json({
            'page_slug': self.page.slug,
            'element_id': 'hero1',
            'content_json': {'headline': 'Hi there'},
        })
        block.refresh_from_db()
        self.assertEqual(block.style_json.get('color'), '#1d4ed8')
        self.assertEqual(block.content_json['headline'], 'Hi there')

    # ------------------------------------------------------------------
    # Inline style_json on the public render
    # ------------------------------------------------------------------
    def test_style_json_applies_inline_on_live_page(self):
        block = ContentBlock.objects.create(
            page=self.page, element_id='hero-styled', block_type='hero', order=0,
            content_json={'headline': 'Styled', 'primary_label': 'Go', 'primary_url': '/departments/'},
            style_json={'backgroundColor': '#111827', 'color': '#f9fafb'},
        )
        html = self.client.get(
            reverse('editable_page', args=[self.page.slug])
        ).content.decode()
        # The block wrapper carries the flattened inline style on the live page.
        self.assertRegex(html, r'style="[^"]*background-color:\s*#111827')
        self.assertRegex(html, r'style="[^"]*color:\s*#f9fafb')
        # The rendered block itself is present.
        self.assertIn('Styled', html)

    # ------------------------------------------------------------------
    # Editable canvas markup
    # ------------------------------------------------------------------
    def test_canvas_has_inline_edit_bindings_and_style_palette(self):
        ContentBlock.objects.create(
            page=self.page, element_id='hero-canvas', block_type='hero', order=0,
            content_json={'headline': 'Canvas hero', 'primary_label': 'Go', 'primary_url': '/departments/'},
        )
        html = self.client.get(
            reverse('builder_editor', args=[self.page.slug])
        ).content.decode()
        # Section wrapper carries the block style + edit target for the JS.
        self.assertIn('data-block-pk="%s"' % ContentBlock.objects.get(element_id='hero-canvas').pk, html)
        self.assertIn('data-edit-field="headline"', html)
        self.assertIn('data-edit-field="primary_label"', html)
        # The 64-swatch style picker popover is present (text + background groups).
        self.assertEqual(html.count('pb-swatches'), 2)
        self.assertEqual(html.count('class="pb-swatch"'), 128)  # 64 swatches x 2 groups
        self.assertIn('id="pb-style-pop"', html)

    def test_text_block_gets_html_edit_surface(self):
        ContentBlock.objects.create(
            page=self.page, element_id='body1', block_type='html', order=0,
            content_html='<p>Raw paragraph</p>',
        )
        html = self.client.get(
            reverse('builder_editor', args=[self.page.slug])
        ).content.decode()
        # A Text Block's section body becomes the raw-HTML edit surface.
        self.assertIn('data-edit-html', html)
        self.assertIn('Raw paragraph', html)


class GoogleDriveOAuthTest(TestCase):
    """Google Drive API scopes + allauth SocialToken credential helper + UI.

    Covers ``get_user_google_credentials`` (credential reconstruction,
    auto-refresh on expiry, error paths), ``user_has_drive_access``, the
    configured OAuth scopes, and the Drive status card on the Account & Google
    settings tab.
    """

    DRIVE_FILE = 'https://www.googleapis.com/auth/drive.file'
    DRIVE_RO = 'https://www.googleapis.com/auth/drive.readonly'

    def setUp(self):
        self.user = User.objects.create_user(username='drive_user', password='x12345678')
        self.app = SocialApp.objects.create(
            provider='google', name='Google', client_id='app-id.apps.googleusercontent.com',
            secret='app-secret', key='',
        )
        self.account = SocialAccount.objects.create(
            user=self.user, provider='google', uid='1177', extra_data={'email': 'd@niter.edu.bd'},
        )

    def _make_token(self, access='ya29.access', refresh='1//refresh', expires_in=3600):
        return SocialToken.objects.create(
            app=self.app, account=self.account,
            token=access, token_secret=refresh,
            expires_at=timezone.now() + timedelta(seconds=expires_in),
        )

    # ------------------------------------------------------------------
    # OAuth scope configuration
    # ------------------------------------------------------------------
    def test_google_scopes_include_openid_profile_email_and_drive(self):
        from django.conf import settings as django_settings
        scopes = django_settings.SOCIALACCOUNT_PROVIDERS['google']['SCOPE']
        for expected in ('openid', 'profile', 'email', self.DRIVE_FILE, self.DRIVE_RO):
            self.assertIn(expected, scopes)
        auth_params = django_settings.SOCIALACCOUNT_PROVIDERS['google']['AUTH_PARAMS']
        # Offline access_type is what issues a refresh token for background ops.
        self.assertEqual(auth_params.get('access_type'), 'offline')
        # prompt=consent forces the consent screen on every authorization so
        # Google always hands back a fresh refresh token (re-connect too).
        self.assertEqual(auth_params.get('prompt'), 'consent')

    # ------------------------------------------------------------------
    # get_user_google_credentials
    # ------------------------------------------------------------------
    def test_get_user_google_credentials_builds_from_social_token(self):
        from core.google_service import get_user_google_credentials
        self._make_token()
        creds = get_user_google_credentials(self.user)
        self.assertEqual(creds.token, 'ya29.access')
        self.assertEqual(creds.refresh_token, '1//refresh')
        self.assertEqual(creds.client_id, 'app-id.apps.googleusercontent.com')
        self.assertEqual(creds.client_secret, 'app-secret')
        self.assertIn(self.DRIVE_FILE, creds.scopes)

    def test_get_user_google_credentials_mirrors_legacy_token(self):
        from core.crypto import decrypt_secret
        from core.google_service import get_user_google_credentials
        self._make_token()
        get_user_google_credentials(self.user)
        legacy = GoogleUserToken.objects.get(user=self.user)
        # Tokens are encrypted at rest — decrypt for the round-trip comparison.
        self.assertEqual(decrypt_secret(legacy.access_token), 'ya29.access')
        self.assertEqual(decrypt_secret(legacy.refresh_token), '1//refresh')
        self.assertIn(self.DRIVE_FILE, legacy.scopes)

    def test_get_user_google_credentials_refreshes_expired_token(self):
        from core.google_service import get_user_google_credentials
        self._make_token(expires_in=-60)  # already expired
        # Fake Credentials object whose ``refresh()`` issues a fresh token.
        fake_creds = mock.MagicMock()
        fake_creds.token = 'ya29.access'
        fake_creds.refresh_token = '1//refresh'
        fake_creds.expiry = timezone.now() + timedelta(hours=1)

        def _apply_refresh(*_args):
            fake_creds.token = 'ya29.fresh'
            fake_creds.expiry = timezone.now() + timedelta(hours=1)

        fake_creds.refresh.side_effect = _apply_refresh
        with mock.patch('core.google_service.GoogleAuthRequest'), \
                mock.patch('core.google_service.Credentials', return_value=fake_creds):
            creds = get_user_google_credentials(self.user)
            self.assertEqual(creds.token, 'ya29.fresh')
            # Refreshed token is persisted back to allauth + legacy storage
            # (the GoogleUserToken copy is encrypted at rest).
            from core.crypto import decrypt_secret
            legacy = GoogleUserToken.objects.get(user=self.user)
            self.assertEqual(decrypt_secret(legacy.access_token), 'ya29.fresh')
            social = SocialToken.objects.get(account=self.account)
            self.assertEqual(social.token, 'ya29.fresh')

    def test_get_user_google_credentials_raises_without_account(self):
        from core.google_service import GoogleAccountNotConnected, get_user_google_credentials
        orphan = User.objects.create_user(username='no_google_drive', password='x12345678')
        with self.assertRaises(GoogleAccountNotConnected):
            get_user_google_credentials(orphan)

    def test_get_user_google_credentials_raises_reauth_when_refresh_fails(self):
        from core.google_service import GoogleReauthRequired, get_user_google_credentials
        from google.auth.exceptions import RefreshError
        self._make_token(expires_in=-60)
        with mock.patch('core.google_service.GoogleAuthRequest'), \
                mock.patch('core.google_service.Credentials.refresh', side_effect=RefreshError('revoked')):
            with self.assertRaises(GoogleReauthRequired):
                get_user_google_credentials(self.user)

    # ------------------------------------------------------------------
    # user_has_drive_access
    # ------------------------------------------------------------------
    def test_user_has_drive_access_true_with_valid_token(self):
        from core.google_service import user_has_drive_access
        self._make_token()
        self.assertTrue(user_has_drive_access(self.user))

    def test_user_has_drive_access_false_without_token(self):
        from core.google_service import user_has_drive_access
        self.assertFalse(user_has_drive_access(self.user))

    def test_user_has_drive_access_false_when_token_expired_and_unrefreshable(self):
        from core.google_service import user_has_drive_access
        self._make_token(refresh='', expires_in=-60)
        self.assertFalse(user_has_drive_access(self.user))

    def test_user_has_drive_access_honours_legacy_token(self):
        from core.google_service import user_has_drive_access
        GoogleUserToken.objects.create(
            user=self.user, access_token='abc', refresh_token='def',
            client_id='x', client_secret='y',
            scopes=[self.DRIVE_FILE],
            expiry=timezone.now() + timedelta(hours=1),
        )
        self.assertTrue(user_has_drive_access(self.user))

    # ------------------------------------------------------------------
    # Settings UI — Drive status card
    # ------------------------------------------------------------------
    def test_settings_shows_drive_connected_status(self):
        self._make_token()
        self.client.force_login(self.user)
        html = self.client.get(reverse('settings')).content.decode()
        self.assertIn('Connected: Google Drive access granted', html)
        self.assertNotIn('Grant Google Drive Access', html)

    def test_settings_shows_drive_not_connected_with_grant_button(self):
        self.client.force_login(self.user)
        html = self.client.get(reverse('settings')).content.decode()
        self.assertIn('Not Connected', html)
        self.assertIn('Grant Google Drive Access', html)
        self.assertIn(reverse('google_login'), html)


class SecurityAuditTest(TestCase):
    """Production security audit — settings posture + endpoint authentication.

    Verifies the guarantees a production deployment depends on:
      * DEBUG hard-defaults to False, and the secure flags (SECURE_SSL_REDIRECT
        / SESSION_COOKIE_SECURE / CSRF_COOKIE_SECURE / HSTS) turn on only when
        DEBUG is off — never in dev/test runs,
      * production mode emits the security response headers,
      * AUTH_PASSWORD_VALIDATORS are configured and enforced,
      * every protected endpoint refuses anonymous access,
      * every public endpoint stays reachable without a session, and
      * the payment webhooks remain server-to-server reachable (no auth).
    """

    # ------------------------------------------------------------------
    # Settings posture (loaded fresh, like a real deploy)
    # ------------------------------------------------------------------
    def test_production_settings_force_secure_defaults(self):
        """Loading the real settings with DEBUG unset (a fresh production
        deploy) must yield DEBUG=False plus the hardened flags.

        The dev-only gitignored ``.env`` (which forces DEBUG=True) is set
        aside for the duration so the subprocess sees a genuinely bare
        environment — the same as CI / Render, where no .env exists.
        """
        import os
        import subprocess
        import sys

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_file = os.path.join(project_root, '.env')
        env_backup = env_file + '.audit.bak'
        renamed = False
        if os.path.exists(env_file):
            os.rename(env_file, env_backup)
            renamed = True
        try:
            code = (
                "import os, json\n"
                "os.environ.pop('DEBUG', None)\n"
                "os.environ.pop('RENDER', None)\n"
                "os.environ.pop('RENDER_BUILD', None)\n"
                "os.environ['SECRET_KEY'] = 'audit-test-key'\n"
                "os.environ['ALLOWED_HOSTS'] = 'audit.example'\n"
                "os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'\n"
                "import django; django.setup()\n"
                "from django.conf import settings\n"
                "print(json.dumps({\n"
                "    'debug': settings.DEBUG,\n"
                "    'ssl_redirect': settings.SECURE_SSL_REDIRECT,\n"
                "    'session_secure': settings.SESSION_COOKIE_SECURE,\n"
                "    'csrf_secure': settings.CSRF_COOKIE_SECURE,\n"
                "    'hsts': settings.SECURE_HSTS_SECONDS,\n"
                "    'referrer': settings.SECURE_REFERRER_POLICY,\n"
                "    'frame': settings.X_FRAME_OPTIONS,\n"
                "}))\n"
            )
            proc = subprocess.run(
                [sys.executable, '-c', code],
                capture_output=True, text=True, cwd=project_root,
            )
        finally:
            if renamed:
                os.rename(env_backup, env_file)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        values = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertFalse(values['debug'])
        self.assertTrue(values['ssl_redirect'])
        self.assertTrue(values['session_secure'])
        self.assertTrue(values['csrf_secure'])
        self.assertGreaterEqual(values['hsts'], 31536000)
        self.assertEqual(values['referrer'], 'same-origin')
        self.assertEqual(values['frame'], 'DENY')

    def test_debug_mode_does_not_force_secure_flags(self):
        """The hardened flags must never leak into DEBUG=True (dev/tests).

        SECURE_SSL_REDIRECT / SESSION_COOKIE_SECURE / CSRF_COOKIE_SECURE are
        Django *global defaults* (False / 0) even when undefined, so the
        assertions check the VALUES: in dev mode they must stay at their
        insecure Django defaults, never flip to True."""
        import os
        import subprocess
        import sys

        code = (
            "import os, json\n"
            "os.environ['DEBUG'] = 'True'\n"
            "os.environ['SECRET_KEY'] = 'dev-key'\n"
            "os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'\n"
            "import django; django.setup()\n"
            "from django.conf import settings\n"
            "print(json.dumps({\n"
            "    'debug': settings.DEBUG,\n"
            "    'ssl_redirect': settings.SECURE_SSL_REDIRECT,\n"
            "    'session_secure': settings.SESSION_COOKIE_SECURE,\n"
            "    'csrf_secure': settings.CSRF_COOKIE_SECURE,\n"
            "    'hsts': settings.SECURE_HSTS_SECONDS,\n"
            "}))\n"
        )
        proc = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        values = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertTrue(values['debug'])
        self.assertFalse(values['ssl_redirect'])
        self.assertFalse(values['session_secure'])
        self.assertFalse(values['csrf_secure'])
        self.assertEqual(values['hsts'], 0)

    @override_settings(
        DEBUG=False,
        ALLOWED_HOSTS=['testserver'],
        SECURE_SSL_REDIRECT=False,
        SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'),
        SECURE_HSTS_SECONDS=3600,
        SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
        SECURE_HSTS_PRELOAD=True,
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
    )
    def test_production_mode_emits_security_headers(self):
        # HSTS is only emitted on HTTPS responses — the proxy-ssl header makes
        # the test request count as HTTPS, exactly like Render's TLS terminator.
        response = self.client.get('/', HTTP_X_FORWARDED_PROTO='https')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Strict-Transport-Security'],
            'max-age=3600; includeSubDomains; preload',
        )
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')

    # ------------------------------------------------------------------
    # Password policy
    # ------------------------------------------------------------------
    def test_password_validators_configured_and_enforced(self):
        from django.conf import settings
        from django.contrib.auth.password_validation import validate_password

        names = [v['NAME'] for v in settings.AUTH_PASSWORD_VALIDATORS]
        for expected in (
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
            'django.contrib.auth.password_validation.MinimumLengthValidator',
            'django.contrib.auth.password_validation.CommonPasswordValidator',
            'django.contrib.auth.password_validation.NumericPasswordValidator',
        ):
            self.assertIn(expected, names)

        # Weak / common / numeric passwords are all rejected…
        for weak in ('password', '12345678', 'password123', 'qwerty123'):
            with self.assertRaises(Exception, msg=weak):
                validate_password(weak)
        # …while a genuinely strong password passes.
        validate_password('Niter#2026!StrongPass')

    # ------------------------------------------------------------------
    # Endpoint authentication matrix
    # ------------------------------------------------------------------
    def test_protected_endpoints_redirect_anonymous_users(self):
        """Every protected endpoint must refuse anonymous callers — bounced to
        the login page (302) or, for the one JSON endpoint that answers inline
        (google-unlink), a 401.

        The matrix is exhaustive: every @login_required, @staff_member_required
        and @change_editablepage_required view in the URLconf is exercised.
        Decorator guards fire before the view body, so path args are only there
        to let ``reverse()`` resolve."""
        cases = [
            # Student dashboards / account
            (reverse('settings'), 'GET'),
            (reverse('profile'), 'GET'),
            # Notes Engine + Google Drive/Sheets APIs
            (reverse('api_note_get', args=[1]), 'GET'),
            (reverse('api_note_save'), 'POST'),
            (reverse('api_note_summarize'), 'POST'),
            (reverse('api_note_keywords'), 'POST'),
            (reverse('api_note_analysis_status', args=['00000000-0000-0000-0000-000000000000']), 'GET'),
            (reverse('api_note_export'), 'POST'),
            (reverse('api_upload_note'), 'POST'),
            (reverse('api_notes_auth_status'), 'GET'),
            (reverse('api_club_sheet_fetch'), 'GET'),
            (reverse('api_club_sheet_append'), 'POST'),
            (reverse('api_google_unlink'), 'POST'),
            # Research AI
            (reverse('api_research_query'), 'POST'),
            (reverse('api_research_threads'), 'GET'),
            (reverse('api_research_thread_detail', args=[1]), 'GET'),
            # Notifications
            (reverse('api_notifications'), 'GET'),
            (reverse('api_notification_read', args=[1]), 'POST'),
            # Campus service actions
            (reverse('claim_meal_ticket'), 'POST'),
            (reverse('book_transport_ticket'), 'POST'),
            (reverse('book_appointment'), 'POST'),
            (reverse('api_club_join'), 'POST'),
            # Dashboard — AI routine extraction + academic calendar API
            (reverse('api_routine_extract'), 'POST'),
            (reverse('api_calendar_events'), 'GET'),
            # Medical chat (patient) + queue (staff)
            (reverse('api_medical_chat_threads'), 'GET'),
            (reverse('api_medical_chat_start'), 'POST'),
            (reverse('api_medical_chat_messages', args=[1]), 'GET'),
            (reverse('api_medical_queue'), 'GET'),
            # Staff dashboards + staff actions
            (reverse('sys_admin'), 'GET'),
            (reverse('cafeteria_admin'), 'GET'),
            (reverse('club_admin'), 'GET'),
            (reverse('medical_admin_dashboard'), 'GET'),
            (reverse('host:medical_host_dashboard'), 'GET'),
            (reverse('api_cafeteria_redeem'), 'POST'),
            (reverse('api_appointment_status', args=[1]), 'POST'),
            (reverse('api_club_verify_transaction'), 'POST'),
            (reverse('api_notices_create'), 'POST'),
            (reverse('api_admin_update_role'), 'POST'),
            # Admin Dashboard area (/dashboard/admin/*) + club account APIs
            (reverse('admin_dashboard'), 'GET'),
            (reverse('admin_users'), 'GET'),
            (reverse('admin_club_accounts'), 'GET'),
            (reverse('admin_database'), 'GET'),
            (reverse('admin_content'), 'GET'),
            (reverse('admin_settings'), 'GET'),
            (reverse('api_club_accounts'), 'GET'),
            (reverse('api_club_account_password', args=[1]), 'POST'),
            (reverse('api_club_account_status', args=[1]), 'POST'),
            (reverse('api_club_account_permissions', args=[1]), 'POST'),
            # Website Builder (permission-gated)
            (reverse('builder_dashboard'), 'GET'),
            (reverse('builder_editor', args=['x']), 'GET'),
            (reverse('visual_editor', args=['x']), 'GET'),
            (reverse('create_page'), 'POST'),
            (reverse('save_content_block'), 'POST'),
            (reverse('save_page_css'), 'POST'),
            (reverse('builder_blocks_reorder'), 'POST'),
            (reverse('builder_blocks_save'), 'POST'),
            (reverse('builder_page_save'), 'POST'),
            (reverse('builder_block_create'), 'POST'),
            (reverse('builder_block_delete', args=[1]), 'POST'),
        ]
        for url, method in cases:
            response = getattr(self.client, method.lower())(url)
            if url == reverse('api_google_unlink'):
                # Inline 401 (JSON) — the settings page consumes it via fetch.
                self.assertEqual(response.status_code, 401, url)
            else:
                self.assertEqual(response.status_code, 302, url)

    def test_public_endpoints_reachable_anonymously(self):
        public = [
            '/', reverse('dashboard'), reverse('student_dashboard'),
            reverse('tickets'), reverse('medical'),
            reverse('notes'), reverse('academic_notes'), reverse('notices'),
            reverse('clubs_dashboard'), reverse('transport_dashboard'),
            reverse('meal_dashboard'), reverse('checkout'), reverse('research_ai'),
            reverse('departments'), reverse('signup'), reverse('login'),
        ]
        for url in public:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)

    def test_payment_webhooks_accept_server_to_server_callbacks(self):
        """Gateway webhooks are intentionally unauthenticated (the gateway has
        no session) — they must answer a business status, never a redirect."""
        for url in (reverse('payments_bkash_webhook'), reverse('payments_nagad_webhook')):
            response = self.client.post(url, {})
            self.assertNotEqual(response.status_code, 302, url)
            self.assertIn(response.status_code, (200, 400, 404), url)


class PwaTests(TestCase):
    """PWA surface — web app manifest, service worker, template wiring."""

    def test_manifest_exposes_installable_metadata(self):
        response = self.client.get(reverse('pwa_manifest'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['start_url'], '/dashboard/')
        self.assertEqual(data['background_color'], '#FBF9F5')
        self.assertEqual(data['theme_color'], '#EADCC9')
        self.assertEqual(data['display'], 'standalone')
        sizes = {icon['sizes'] for icon in data['icons']}
        self.assertIn('192x192', sizes)
        self.assertIn('512x512', sizes)

    def test_service_worker_served_with_origin_scope(self):
        response = self.client.get(reverse('service_worker'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/javascript')
        self.assertEqual(response['Service-Worker-Allowed'], '/')
        body = response.content.decode()
        # The two offline routes + core CSS are precached by the worker.
        self.assertIn('/academic-notes/', body)
        self.assertIn('/transport/', body)
        self.assertIn('/static/css/theme.css', body)

    def test_dashboard_shell_links_manifest_and_registers_worker(self):
        html = self.client.get(reverse('dashboard')).content.decode()
        self.assertIn('rel="manifest" href="/manifest.json"', html)
        self.assertIn('pwa-register.js', html)
        self.assertIn('theme-color', html)

    def test_offline_routes_link_manifest_and_register_worker(self):
        for url in (reverse('academic_notes'), reverse('transport_dashboard')):
            html = self.client.get(url).content.decode()
            self.assertIn('rel="manifest" href="/manifest.json"', html)
            self.assertIn('pwa-register.js', html)


class SupabaseDatabaseConfigTest(SimpleTestCase):
    """config.settings._build_databases — SUPABASE_DB_URL wiring + sslmode."""

    def _build(self, supabase_url='', db_url=''):
        import config.settings as settings_mod

        def fake_env(name, default=''):
            if name == 'SUPABASE_DB_URL':
                return supabase_url
            if name == 'DATABASE_URL':
                return db_url
            return default

        with mock.patch.object(settings_mod, 'env', side_effect=fake_env):
            return settings_mod._build_databases()

    def test_supabase_url_gets_sslmode_require(self):
        engine = self._build(supabase_url='postgres://user:pass@host:5432/niter')['default']
        self.assertEqual(engine['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(engine['NAME'], 'niter')
        self.assertEqual(engine['OPTIONS'].get('sslmode'), 'require')

    def test_supabase_takes_precedence_over_datatabase_url(self):
        engine = self._build(
            supabase_url='postgres://u:p@supabase-host:5432/db',
            db_url='postgres://u:p@render-host:5432/other',
        )['default']
        self.assertEqual(engine['HOST'], 'supabase-host')

    def test_datatabase_url_fallback_also_gets_ssl(self):
        engine = self._build(db_url='postgres://u:p@render-host:5432/db')['default']
        self.assertEqual(engine['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(engine['OPTIONS'].get('sslmode'), 'require')

    def test_explicit_sslmode_is_left_untouched(self):
        engine = self._build(
            supabase_url='postgres://u:p@host:5432/db?sslmode=disable'
        )['default']
        self.assertEqual(engine['OPTIONS'].get('sslmode'), 'disable')

    def test_no_urls_fall_back_to_sqlite(self):
        engine = self._build()['default']
        self.assertEqual(engine['ENGINE'], 'django.db.backends.sqlite3')


class ClubSheetsModuleTest(TestCase):
    """core/club_sheets.py — read/write/verify helpers, Sheets v4 fully mocked."""

    def setUp(self):
        self.user = User.objects.create_user(username='club_sheets_user', password='x12345678')
        self.ref = 'https://docs.google.com/spreadsheets/d/1AbCxYz/edit'

    def _fake_sheets_service(self, values=None, titles=('Sheet1',), append_result=None):
        """A mocked Sheets v4 service exposing the call chain used by club_sheets."""
        service = mock.Mock()
        meta = {'sheets': [{'properties': {'title': title}} for title in titles]}
        service.spreadsheets().get.return_value.execute.return_value = meta
        service.spreadsheets().values().get.return_value.execute.return_value = {'values': values or []}
        service.spreadsheets().values().append.return_value.execute.return_value = (
            append_result or {'updates': {'updatedRows': 1}}
        )
        return service

    def _patch_service(self, service):
        return mock.patch('core.club_sheets._get_sheets_service', return_value=service)

    def test_normalize_sheet_ref_extracts_key_from_url(self):
        from core.club_sheets import normalize_sheet_ref
        self.assertEqual(normalize_sheet_ref(self.ref), '1AbCxYz')

    def test_normalize_sheet_ref_accepts_bare_id(self):
        from core.club_sheets import normalize_sheet_ref
        self.assertEqual(normalize_sheet_ref('1AbCxYz'), '1AbCxYz')

    def test_normalize_sheet_ref_rejects_empty(self):
        from core.club_sheets import normalize_sheet_ref
        from core.google_service import GoogleServiceError
        with self.assertRaises(GoogleServiceError):
            normalize_sheet_ref('   ')

    def test_read_rows_returns_header_keyed_records(self):
        from core.club_sheets import read_rows
        records = [['Name', 'Student ID'], ['Fahim', 'S1012']]
        service = self._fake_sheets_service(values=records)
        with self._patch_service(service):
            result = read_rows(self.user, self.ref)
        self.assertEqual(result, [{'Name': 'Fahim', 'Student ID': 'S1012'}])

    def test_get_members_targets_members_tab(self):
        from core.club_sheets import get_members
        service = self._fake_sheets_service(
            values=[['Name', 'Role'], ['Alice', 'Member']], titles=('Members', 'Registrations'),
        )
        with self._patch_service(service):
            rows = get_members(self.user, self.ref)
        self.assertEqual(rows[0]['Name'], 'Alice')

    def test_get_event_registrations_and_notices_target_tabs(self):
        from core.club_sheets import get_club_notices, get_event_registrations
        for fn, tab in ((get_event_registrations, 'Registrations'), (get_club_notices, 'Notices')):
            service = self._fake_sheets_service(titles=('Sheet1',))
            with self._patch_service(service):
                fn(self.user, self.ref)
            # The named tab is preferred, but a missing tab falls back to the
            # first worksheet — assert a call was made through values().get().
            self.assertTrue(service.spreadsheets().values().get.called)

    def test_append_member_writes_row(self):
        from core.club_sheets import append_member
        service = self._fake_sheets_service(titles=('Members',))
        with self._patch_service(service):
            count = append_member(
                self.user, self.ref, 'Fahim Chowdhury', 'S1012',
                email='f@niter.edu.bd', role='Member',
            )
        self.assertEqual(count, 1)
        append_body = service.spreadsheets().values().append.call_args.kwargs['body']
        self.assertEqual(
            append_body['values'], [['Fahim Chowdhury', 'S1012', 'f@niter.edu.bd', 'Member', '']],
        )

    def test_api_failure_wrapped_in_service_error(self):
        from core.club_sheets import read_rows
        from core.google_service import GoogleServiceError
        service = mock.Mock()
        service.spreadsheets().get.side_effect = RuntimeError('network down')
        with self._patch_service(service):
            with self.assertRaises(GoogleServiceError):
                read_rows(self.user, self.ref)

    def test_verify_and_setup_sheet_creates_missing_tabs_and_headers(self):
        from core.club_sheets import verify_and_setup_sheet
        service = self._fake_sheets_service(titles=('Sheet1',))
        # Existing first tab has no headers yet.
        service.spreadsheets().values().get.return_value.execute.return_value = {'values': []}
        with self._patch_service(service):
            summary = verify_and_setup_sheet(self.user, self.ref)
        # Members / Registrations / Notices tabs were created.
        batch = service.spreadsheets().batchUpdate.call_args.kwargs['body']
        self.assertEqual(len(batch['requests']), 3)
        self.assertEqual(summary['created'], ['Members', 'Registrations', 'Notices'])
        # Headers written into empty tabs.
        self.assertTrue(service.spreadsheets().values().update.called)

    def test_verify_and_setup_sheet_writes_headers_when_first_row_empty(self):
        from core.club_sheets import verify_and_setup_sheet
        service = self._fake_sheets_service(titles=('Members', 'Registrations', 'Notices'))
        service.spreadsheets().values().get.return_value.execute.return_value = {'values': []}
        with self._patch_service(service):
            summary = verify_and_setup_sheet(self.user, self.ref)
        self.assertEqual(summary['created'], [])
        update_calls = service.spreadsheets().values().update.call_count
        self.assertEqual(update_calls, 3)  # headers written into all three tabs


class GoogleCryptoTest(TestCase):
    """core/crypto.py — Fernet round-trip + legacy plaintext fallback."""

    def test_encrypt_decrypt_roundtrip(self):
        from core.crypto import decrypt_secret, encrypt_secret
        secret = 'ya29.long-access-token'
        encrypted = encrypt_secret(secret)
        self.assertNotEqual(encrypted, secret)
        self.assertEqual(decrypt_secret(encrypted), secret)

    def test_decrypt_passes_legacy_plaintext_through(self):
        from core.crypto import decrypt_secret
        self.assertEqual(decrypt_secret('ya29.legacy-plaintext'), 'ya29.legacy-plaintext')

    def test_empty_values_pass_through(self):
        from core.crypto import decrypt_secret, encrypt_secret
        self.assertEqual(encrypt_secret(''), '')
        self.assertEqual(decrypt_secret(None), None)

    def test_service_persistence_encrypts_tokens_at_rest(self):
        # The service layer (the only write path in production) stores tokens
        # encrypted — mirror the allauth token through get_user_google_credentials
        # and confirm the GoogleUserToken row holds ciphertext, not the token.
        from core.crypto import decrypt_secret
        from core.google_service import get_user_google_credentials
        user = User.objects.create_user(username='crypto_service_user', password='x12345678')
        app = SocialApp.objects.create(
            provider='google', name='Google', client_id='app-id', secret='app-secret', key='',
        )
        account = SocialAccount.objects.create(
            user=user, provider='google', uid='1177', extra_data={'email': 'c@niter.edu.bd'},
        )
        SocialToken.objects.create(
            app=app, account=account, token='ya29.access', token_secret='1//refresh',
            expires_at=timezone.now() + timedelta(hours=1),
        )
        get_user_google_credentials(user)
        stored = GoogleUserToken.objects.get(user=user)
        self.assertNotEqual(stored.access_token, 'ya29.access')
        self.assertEqual(decrypt_secret(stored.access_token), 'ya29.access')
        self.assertEqual(decrypt_secret(stored.refresh_token), '1//refresh')


class DriveOAuthFlowTest(TestCase):
    """/drive/connect/ + /drive/callback/ — google_auth_oauthlib Flow, mocked."""

    def setUp(self):
        self.user = User.objects.create_user(username='flow_user', password='x12345678')
        self.client.force_login(self.user)

    def test_connect_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('drive_connect'))
        self.assertEqual(response.status_code, 302)

    def test_callback_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('drive_callback'), {'state': 's', 'code': 'abc'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(GoogleUserToken.objects.filter(user=self.user).exists())

    def test_connect_redirects_to_google_with_state(self):
        from django.conf import settings as django_settings
        with mock.patch('google_auth_oauthlib.flow.Flow') as mock_flow_cls, \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_ID', 'app-id.apps.googleusercontent.com'), \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_SECRET', 'secret'), \
                mock.patch.object(django_settings, 'GOOGLE_REDIRECT_URI', 'https://niter.edu.bd/drive/callback/'):
            mock_flow = mock_flow_cls.from_client_config.return_value
            mock_flow.authorization_url.return_value = ('https://accounts.google.com/o/oauth2/auth?x', 'csrf-state-1')
            response = self.client.get(reverse('drive_connect'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('https://accounts.google.com/o/oauth2/auth', response.url)
        self.assertEqual(self.client.session['drive_oauth_state'], 'csrf-state-1')
        # Offline + forced-consent authorization is what guarantees Google
        # returns a refresh token for background Drive/Sheets operations.
        _, auth_kwargs = mock_flow.authorization_url.call_args
        self.assertEqual(auth_kwargs.get('access_type'), 'offline')
        self.assertEqual(auth_kwargs.get('prompt'), 'consent')
        self.assertEqual(auth_kwargs.get('include_granted_scopes'), 'true')

    def test_connect_without_env_creds_redirects_back(self):
        from django.conf import settings as django_settings
        with mock.patch.object(django_settings, 'GOOGLE_CLIENT_ID', ''), \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_SECRET', ''):
            response = self.client.get(reverse('drive_connect'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('settings'), response.url)

    def test_callback_state_mismatch_rejected(self):
        s = self.client.session
        s['drive_oauth_state'] = 'expected'
        s.save()
        response = self.client.get(reverse('drive_callback'), {'state': 'wrong', 'code': 'abc'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('settings'), response.url)
        self.assertFalse(GoogleUserToken.objects.filter(user=self.user).exists())

    def test_callback_denied_rejected(self):
        s = self.client.session
        s['drive_oauth_state'] = 's'
        s.save()
        response = self.client.get(reverse('drive_callback'), {'state': 's', 'error': 'access_denied'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(GoogleUserToken.objects.filter(user=self.user).exists())

    def test_callback_stores_encrypted_tokens(self):
        from core.crypto import decrypt_secret
        creds = mock.Mock()
        creds.token = 'ya29.flow-access'
        creds.refresh_token = '1//flow-refresh'
        creds.token_uri = 'https://oauth2.googleapis.com/token'
        creds.expiry = timezone.now() + timedelta(hours=1)
        creds.id_token = 'id-token' if False else None

        s = self.client.session
        s['drive_oauth_state'] = 's'
        s.save()
        from django.conf import settings as django_settings
        with mock.patch('google_auth_oauthlib.flow.Flow') as mock_flow_cls, \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_ID', 'app-id.apps.googleusercontent.com'), \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_SECRET', 'secret'):
            mock_flow_cls.from_client_config.return_value.fetch_token.return_value = None
            mock_flow_cls.from_client_config.return_value.credentials = creds
            response = self.client.get(
                reverse('drive_callback'), {'state': 's', 'code': 'auth-code'},
            )
        self.assertEqual(response.status_code, 302)
        self.assertIn('tab=account', response.url)
        stored = GoogleUserToken.objects.get(user=self.user)
        self.assertEqual(decrypt_secret(stored.access_token), 'ya29.flow-access')
        self.assertEqual(decrypt_secret(stored.refresh_token), '1//flow-refresh')

    def test_callback_exchange_failure_redirects_back(self):
        s = self.client.session
        s['drive_oauth_state'] = 's'
        s.save()
        with mock.patch('google_auth_oauthlib.flow.Flow') as mock_flow_cls:
            mock_flow_cls.from_client_config.side_effect = RuntimeError('bad config')
            response = self.client.get(
                reverse('drive_callback'), {'state': 's', 'code': 'auth-code'},
            )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(GoogleUserToken.objects.filter(user=self.user).exists())

    def test_connect_uses_request_origin_when_env_redirect_points_at_localhost(self):
        """A GOOGLE_REDIRECT_URI left pointing at localhost (the classic
        .env-copied-to-the-server mistake) must not break the OAuth callback
        on a real domain — the request origin is used instead."""
        from django.conf import settings as django_settings
        with mock.patch('google_auth_oauthlib.flow.Flow') as mock_flow_cls, \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_ID', 'app-id.apps.googleusercontent.com'), \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_SECRET', 'secret'), \
                mock.patch.object(django_settings, 'GOOGLE_REDIRECT_URI', 'http://localhost:8000/drive/callback/'), \
                mock.patch.object(django_settings, 'ALLOWED_HOSTS', ['*']):
            mock_flow = mock_flow_cls.from_client_config.return_value
            mock_flow.authorization_url.return_value = ('https://accounts.google.com/o/oauth2/auth?x', 's1')
            response = self.client.get(
                reverse('drive_connect'),
                HTTP_HOST='niter-centralized-dash.onrender.com',
            )
        self.assertEqual(response.status_code, 302)
        _, kwargs = mock_flow_cls.from_client_config.call_args
        self.assertEqual(
            kwargs['redirect_uri'],
            'http://niter-centralized-dash.onrender.com/drive/callback/',
        )

    def test_connect_keeps_production_env_redirect_uri(self):
        """A properly configured non-local redirect URI is honoured as-is."""
        from django.conf import settings as django_settings
        with mock.patch('google_auth_oauthlib.flow.Flow') as mock_flow_cls, \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_ID', 'app-id.apps.googleusercontent.com'), \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_SECRET', 'secret'), \
                mock.patch.object(django_settings, 'GOOGLE_REDIRECT_URI', 'https://niter.edu.bd/drive/callback/'):
            mock_flow = mock_flow_cls.from_client_config.return_value
            mock_flow.authorization_url.return_value = ('https://accounts.google.com/o/oauth2/auth?x', 's2')
            self.client.get(reverse('drive_connect'))
        _, kwargs = mock_flow_cls.from_client_config.call_args
        self.assertEqual(kwargs['redirect_uri'], 'https://niter.edu.bd/drive/callback/')


class NotesAuthStatusTest(TestCase):
    """GET /api/notes/auth-status/ — Drive connection health + env audit.

    The Notes Engine calls this on page load: the server silently renews an
    expired access token (so the re-auth popup stops recurring), and reports
    whether the deployment has Google credentials configured at all.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='authstatus', password='x12345678')
        self.client.force_login(self.user)

    @contextmanager
    def _google_env_configured(self):
        """Simulate a server with Google application credentials set."""
        from django.conf import settings as django_settings
        with mock.patch.object(django_settings, 'GOOGLE_CLIENT_ID', 'app-id.apps.googleusercontent.com'), \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_SECRET', 'secret'):
            yield

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('api_notes_auth_status'))
        self.assertEqual(response.status_code, 302)

    def test_reports_not_connected_without_any_token(self):
        with self._google_env_configured():
            response = self.client.get(reverse('api_notes_auth_status'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['connected'])
        self.assertEqual(data['status'], 'auth_required')
        self.assertEqual(data['reason'], 'not_connected')
        self.assertTrue(data['google_configured'])
        self.assertIn('google', data['redirect_url'])

    def test_reports_connected_with_valid_token(self):
        GoogleUserToken.objects.create(
            user=self.user,
            access_token='ya29.access',
            refresh_token='1//refresh',
            client_id='app-id.apps.googleusercontent.com',
            client_secret='secret',
            scopes=['email', 'https://www.googleapis.com/auth/drive.file'],
            expiry=timezone.now() + timedelta(hours=1),
        )
        with self._google_env_configured():
            response = self.client.get(reverse('api_notes_auth_status'))
        data = response.json()
        self.assertTrue(data['connected'])
        self.assertEqual(data['status'], 'ok')
        self.assertIsNone(data['reason'])
        self.assertTrue(data['google_configured'])

    def test_silently_refreshes_expired_token(self):
        from google.oauth2.credentials import Credentials
        token = GoogleUserToken.objects.create(
            user=self.user,
            access_token='ya29.expired',
            refresh_token='1//refresh',
            client_id='app-id.apps.googleusercontent.com',
            client_secret='secret',
            scopes=['email', 'https://www.googleapis.com/auth/drive.file'],
            expiry=timezone.now() - timedelta(minutes=5),
        )

        def fake_refresh(creds, request):
            creds.token = 'ya29.refreshed-status'
            creds.expiry = timezone.now() + timedelta(hours=1)

        with mock.patch.object(Credentials, 'refresh', fake_refresh):
            response = self.client.get(reverse('api_notes_auth_status'))
        data = response.json()
        self.assertTrue(data['connected'])
        self.assertEqual(data['status'], 'ok')
        # The silent refresh persisted the new access token.
        token.refresh_from_db()
        from core.crypto import decrypt_secret
        self.assertEqual(decrypt_secret(token.access_token), 'ya29.refreshed-status')

    def test_reports_refresh_failed_when_refresh_breaks(self):
        from google.auth.exceptions import RefreshError
        from google.oauth2.credentials import Credentials
        GoogleUserToken.objects.create(
            user=self.user,
            access_token='ya29.expired',
            refresh_token='1//refresh',
            client_id='app-id.apps.googleusercontent.com',
            client_secret='secret',
            scopes=['email', 'https://www.googleapis.com/auth/drive.file'],
            expiry=timezone.now() - timedelta(minutes=5),
        )
        with mock.patch.object(Credentials, 'refresh', side_effect=RefreshError('revoked')):
            response = self.client.get(reverse('api_notes_auth_status'))
        data = response.json()
        self.assertFalse(data['connected'])
        self.assertEqual(data['reason'], 'refresh_failed')

    def test_flags_missing_env_credentials(self):
        """A server without GOOGLE_CLIENT_ID/SECRET must be reported (and
        logged server-side) instead of failing into the generic popup."""
        from django.conf import settings as django_settings
        with mock.patch.object(django_settings, 'GOOGLE_CLIENT_ID', ''), \
                mock.patch.object(django_settings, 'GOOGLE_CLIENT_SECRET', ''), \
                self.assertLogs('core.views', level='WARNING'):
            response = self.client.get(reverse('api_notes_auth_status'))
        data = response.json()
        self.assertFalse(data['google_configured'])
        self.assertFalse(data['connected'])
        self.assertEqual(data['reason'], 'not_connected')


class VerifyClubSheetApiTest(TestCase):
    """POST /clubs/dashboard/sheets/verify/ — save + setup default tabs/headers."""

    def setUp(self):
        # Verify & Connect lives in the Club Management dashboard — staff or
        # active club-account holders (club_access_required).
        self.user = User.objects.create_user(
            username='verify_sheets_user', password='x12345678', is_staff=True,
        )
        self.client.force_login(self.user)

    def test_verify_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('api_club_sheet_verify'), data=json.dumps({'sheet_ref': 'x'}), content_type='application/json')
        self.assertEqual(response.status_code, 302)

    def test_verify_denied_for_non_staff(self):
        student = User.objects.create_user(username='plain_student_v', password='x12345678')
        self.client.logout()
        self.client.login(username='plain_student_v', password='x12345678')
        # Same club gate as fetch/append — authenticated students without a
        # staff flag or active club account get a 403, never sheet setup.
        response = self.client.post(
            reverse('api_club_sheet_verify'),
            data=json.dumps({'sheet_ref': 'x'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_verify_rejects_missing_ref(self):
        response = self.client.post(reverse('api_club_sheet_verify'), data=json.dumps({'sheet_ref': '  '}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_verify_success_saves_config_and_returns_summary(self):
        with mock.patch('core.club_sheets.verify_and_setup_sheet', return_value={
            'title': 'Club Roster', 'tabs': ['Members', 'Registrations', 'Notices'], 'created': ['Members'],
        }) as verify:
            response = self.client.post(
                reverse('api_club_sheet_verify'),
                data=json.dumps({'sheet_ref': '1AbCxYz'}),
                content_type='application/json',
            )
            verify.assert_called_once_with(self.user, '1AbCxYz')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['title'], 'Club Roster')
        self.assertEqual(data['created'], ['Members'])
        self.assertEqual(
            ClubSheetsConfig.objects.get(user=self.user).sheet_ref, '1AbCxYz',
        )

    def test_verify_auth_required_returns_401(self):
        from core.google_service import GoogleAccountNotConnected
        with mock.patch('core.club_sheets.verify_and_setup_sheet', side_effect=GoogleAccountNotConnected('nope')):
            response = self.client.post(
                reverse('api_club_sheet_verify'),
                data=json.dumps({'sheet_ref': 'x'}),
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['status'], 'auth_required')

    def test_verify_service_error_returns_500(self):
        from core.google_service import GoogleServiceError
        with mock.patch('core.club_sheets.verify_and_setup_sheet', side_effect=GoogleServiceError('denied')):
            response = self.client.post(
                reverse('api_club_sheet_verify'),
                data=json.dumps({'sheet_ref': 'x'}),
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 500)


class DriveServiceModuleTest(TestCase):
    """academic_notes/drive_service.py — uploads + storage info, Drive v3 mocked."""

    def setUp(self):
        self.user = User.objects.create_user(username='drive_service_user', password='x12345678')

    def test_upload_returns_view_and_content_links(self):
        from academic_notes.drive_service import upload_file_to_drive
        upload = SimpleUploadedFile('cs101.pdf', b'%PDF-1.4', content_type='application/pdf')
        with mock.patch('academic_notes.drive_service.build') as mock_build, \
                mock.patch('academic_notes.drive_service.get_google_credentials') as mock_creds:
            mock_creds.return_value = mock.Mock()
            drive = mock_build.return_value
            drive.files().list().execute.return_value = {'files': []}
            drive.files().create.return_value.execute.return_value = {
                'id': 'file-1',
                'webViewLink': 'https://drive.google.com/file/d/file-1/view',
                'webContentLink': 'https://drive.google.com/uc?id=file-1',
            }
            result = upload_file_to_drive(self.user, upload)
        self.assertEqual(result['file_id'], 'file-1')
        self.assertEqual(result['web_view_link'], 'https://drive.google.com/file/d/file-1/view')
        self.assertEqual(result['web_content_link'], 'https://drive.google.com/uc?id=file-1')
        # Folder query targets the dedicated notes folder.
        list_kwargs = drive.files().list.call_args.kwargs
        self.assertIn('NITER Centralized Dash Notes', list_kwargs['q'])

    def test_storage_info_returns_email_and_quota(self):
        from academic_notes.drive_service import get_drive_storage_info
        with mock.patch('academic_notes.drive_service.build') as mock_build, \
                mock.patch('academic_notes.drive_service.get_google_credentials') as mock_creds:
            mock_creds.return_value = mock.Mock()
            mock_build.return_value.about().get().execute.return_value = {
                'user': {'emailAddress': 'd@niter.edu.bd'},
                'storageQuota': {'limit': '15', 'usage': '3'},
            }
            info = get_drive_storage_info(self.user)
        self.assertEqual(info['email'], 'd@niter.edu.bd')
        self.assertEqual(info['quota_total'], 15)
        self.assertEqual(info['quota_used'], 3)
        self.assertEqual(info['quota_remaining'], 12)

    def test_storage_info_none_without_connection(self):
        from academic_notes.drive_service import get_drive_storage_info
        from core.google_service import GoogleAccountNotConnected
        with mock.patch('academic_notes.drive_service.get_google_credentials', side_effect=GoogleAccountNotConnected('nope')):
            self.assertIsNone(get_drive_storage_info(self.user))

    def test_upload_http_401_wrapped_as_reauth(self):
        """The Notes upload path maps a mid-call 401 to the re-auth error so
        the view answers 401 auth_required (reconnect modal) — not a 500."""
        from academic_notes.drive_service import upload_file_to_drive
        from core.google_service import GoogleReauthRequired
        upload = SimpleUploadedFile('cs101.pdf', b'%PDF-1.4', content_type='application/pdf')
        with mock.patch('academic_notes.drive_service.build', side_effect=_http_error(401, 'Unauthorized')), \
                mock.patch('academic_notes.drive_service.get_google_credentials') as mock_creds:
            mock_creds.return_value = mock.Mock()
            with self.assertRaises(GoogleReauthRequired):
                upload_file_to_drive(self.user, upload)

    def test_folder_bootstrap_http_401_wrapped_as_reauth(self):
        from academic_notes.drive_service import get_or_create_notes_folder
        from core.google_service import GoogleReauthRequired
        with mock.patch('academic_notes.drive_service.build', side_effect=_http_error(401, 'Unauthorized')), \
                mock.patch('academic_notes.drive_service.get_google_credentials') as mock_creds:
            mock_creds.return_value = mock.Mock()
            with self.assertRaises(GoogleReauthRequired):
                get_or_create_notes_folder(self.user)

    def test_upload_http_500_stays_service_error(self):
        from academic_notes.drive_service import upload_file_to_drive
        from core.google_service import GoogleServiceError
        upload = SimpleUploadedFile('cs101.pdf', b'%PDF-1.4', content_type='application/pdf')
        with mock.patch('academic_notes.drive_service.build', side_effect=_http_error(500, 'Server Error')), \
                mock.patch('academic_notes.drive_service.get_google_credentials') as mock_creds:
            mock_creds.return_value = mock.Mock()
            with self.assertRaises(GoogleServiceError):
                upload_file_to_drive(self.user, upload)


class ClubSheetsConfigPrefillTest(TestCase):
    """Club Management dashboard — the saved club spreadsheet is prefilled
    from ``ClubSheetsConfig`` (the settings-side sheets tab was removed)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='sheets_tab_user', password='x12345678', is_staff=True,
        )
        self.client.force_login(self.user)

    def test_club_admin_prefills_saved_sheet(self):
        ClubSheetsConfig.objects.create(user=self.user, sheet_ref='1AbCxYz')
        html = self.client.get(reverse('club_admin')).content.decode()
        self.assertIn('value="1AbCxYz"', html)


class BatchRedemptionApiTest(TestCase):
    """/api/cafeteria/batch-redeem/ — bulk redemption of meal coupons."""

    def setUp(self):
        self.staff = User.objects.create_user(username='batch_staff', password='x12345678', is_staff=True)
        self.student = User.objects.create_user(username='batch_student', password='x12345678')

    def _make_ticket(self, token, **kwargs):
        defaults = {
            'user': self.student,
            'meal_type': 'lunch',
            'ticket_token': token,
            'claimed_at': timezone.now(),
        }
        defaults.update(kwargs)
        return MealTicket.objects.create(**defaults)

    def test_batch_redeem_requires_staff(self):
        response = self.client.post(
            reverse('api_cafeteria_batch_redeem'),
            data=json.dumps({'all_today': True}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 302)

    def test_batch_redeem_all_today_marks_tickets_redeemed(self):
        self._make_ticket('#MEAL-0001')
        self._make_ticket('#MEAL-0002')
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('api_cafeteria_batch_redeem'),
            data=json.dumps({'all_today': True}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['redeemed_count'], 2)
        self.assertTrue(
            MealTicket.objects.get(ticket_token='#MEAL-0001').is_redeemed
        )
        self.assertTrue(
            MealTicket.objects.get(ticket_token='#MEAL-0002').is_redeemed
        )

    def test_batch_redeem_explicit_tokens(self):
        self._make_ticket('#MEAL-0011')
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('api_cafeteria_batch_redeem'),
            data=json.dumps({'tokens': ['#MEAL-0011', '#MEAL-9999']}),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(data['redeemed'], ['#MEAL-0011'])
        self.assertEqual(data['failed'][0]['reason'], 'not found')

    def test_batch_redeem_skips_already_redeemed(self):
        self._make_ticket('#MEAL-0021', is_redeemed=True, redeemed_at=timezone.now())
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('api_cafeteria_batch_redeem'),
            data=json.dumps({'tokens': ['#MEAL-0021']}),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(data['failed_count'], 1)
        self.assertEqual(data['failed'][0]['reason'], 'already redeemed')

    def test_batch_redeem_empty_tokens_returns_400(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('api_cafeteria_batch_redeem'),
            data=json.dumps({'tokens': []}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class DoctorAvailabilityApiTest(TestCase):
    """/api/medical/doctor-availability/ — daily availability + slot caps."""

    def setUp(self):
        self.staff = User.objects.create_user(username='med_staff', password='x12345678', is_staff=True)
        self.student = User.objects.create_user(username='med_student', password='x12345678')
        self.doctor = Doctor.objects.create(
            name='Dr. Ava Testing',
            specialty='General Physician',
            working_days='Sunday - Thursday',
            start_time='10:00 AM',
            end_time='2:00 PM',
        )
        self.date = '2026-08-25'

    def _post(self, **overrides):
        payload = {
            'doctor': 'Dr. Ava Testing',
            'date': self.date,
            'is_available': True,
            'max_appointments': 15,
        }
        payload.update(overrides)
        return self.client.post(
            reverse('api_doctor_availability'),
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_requires_staff(self):
        response = self._post()
        self.assertEqual(response.status_code, 302)

    def test_upserts_schedule(self):
        self.client.force_login(self.staff)
        response = self._post()
        self.assertEqual(response.status_code, 200)
        schedule = DoctorSchedule.objects.get(doctor=self.doctor, date='2026-08-25')
        self.assertTrue(schedule.is_available)
        self.assertEqual(schedule.max_appointments, 15)

    def test_toggle_unavailable(self):
        self.client.force_login(self.staff)
        response = self._post(is_available=False)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertFalse(data['is_available'])

    def test_missing_fields_returns_400(self):
        self.client.force_login(self.staff)
        response = self._post(doctor='')
        self.assertEqual(response.status_code, 400)

    def test_unknown_doctor_returns_404(self):
        self.client.force_login(self.staff)
        response = self._post(doctor='Dr. Nope')
        self.assertEqual(response.status_code, 404)

    def test_booking_blocked_for_unavailable_doctor(self):
        self.client.force_login(self.staff)
        self._post(is_available=False)
        self.client.force_login(self.student)
        response = self.client.post(reverse('book_appointment'), {
            'doctor_name': 'Dr. Ava Testing',
            'appointment_date': self.date,
            'time_slot': '10:00',
            'reason': 'Checkup',
        })
        self.assertEqual(response.status_code, 409)
        self.assertIn('unavailable', response.json()['message'])

    def test_booking_enforces_daily_cap(self):
        self.client.force_login(self.staff)
        self._post(max_appointments=1)
        self.client.force_login(self.student)
        first = self.client.post(reverse('book_appointment'), {
            'doctor_name': 'Dr. Ava Testing',
            'appointment_date': self.date,
            'time_slot': '10:00',
            'reason': 'Checkup',
        })
        self.assertEqual(first.status_code, 200)

        second_student = User.objects.create_user(username='med_student2', password='x12345678')
        self.client.force_login(second_student)
        second = self.client.post(reverse('book_appointment'), {
            'doctor_name': 'Dr. Ava Testing',
            'appointment_date': self.date,
            'time_slot': '10:30',
            'reason': 'Checkup',
        })
        self.assertEqual(second.status_code, 409)
        self.assertIn('daily appointment limit', second.json()['message'])


class SeedDemoUsersCommandTest(TestCase):
    """The ``seed_demo_users`` management command creates the documented demo
    accounts and is idempotent (never resets existing users)."""

    def _run(self, *args, **kwargs):
        from django.core.management import call_command
        return call_command('seed_demo_users', *args, **kwargs)

    def test_creates_demo_users(self):
        self._run()
        admin = User.objects.get(username='admin')
        student = User.objects.get(username='student')
        self.assertTrue(admin.check_password('admin123'))
        self.assertTrue(admin.is_staff and admin.is_superuser)
        self.assertTrue(student.check_password('student123'))
        self.assertFalse(student.is_staff or student.is_superuser)

    def test_idempotent_and_keeps_password(self):
        self._run()
        admin = User.objects.get(username='admin')
        admin.set_password('changed-pass-1')
        admin.save()
        self._run()  # second run must not reset the password
        admin.refresh_from_db()
        self.assertTrue(admin.check_password('changed-pass-1'))
        self.assertEqual(User.objects.filter(username='admin').count(), 1)

    def test_extra_staff(self):
        self._run(extra_staff=2)
        for i in (1, 2):
            staff = User.objects.get(username='staff%d' % i)
            self.assertTrue(staff.is_staff)
            self.assertFalse(staff.is_superuser)
            self.assertTrue(staff.check_password('admin123'))
        self.assertFalse(User.objects.filter(username='staff3').exists())

    def test_password_override(self):
        self._run(password='S3cret!x')
        self.assertTrue(User.objects.get(username='admin').check_password('S3cret!x'))
        # student keeps its documented password
        self.assertTrue(User.objects.get(username='student').check_password('student123'))


class RoutineParserTest(SimpleTestCase):
    """services.routine_parser — schedule normalisation helpers."""

    def test_to_24h_converts_am_pm(self):
        from services.routine_parser import to_24h
        self.assertEqual(to_24h('8:30 AM'), '08:30')
        self.assertEqual(to_24h('3:00 PM'), '15:00')
        self.assertEqual(to_24h('12:00 AM'), '00:00')
        self.assertEqual(to_24h('12:30 PM'), '12:30')
        self.assertEqual(to_24h('14:05'), '14:05')
        self.assertEqual(to_24h('9.30'), '09:30')
        self.assertIsNone(to_24h('noon'))
        self.assertIsNone(to_24h(''))

    def test_normalize_schedule_canonical(self):
        from services.routine_parser import normalize_schedule
        raw = {'days': [{'day': 'Sunday', 'slots': [
            {'start': '8:30 AM', 'end': '10:00 AM', 'course': 'CSE-1101', 'room': '201'},
        ]}]}
        out = normalize_schedule(raw)
        self.assertEqual(out['days'][0]['day'], 'Sun')
        self.assertEqual(out['days'][0]['slots'][0]['start'], '08:30')
        self.assertEqual(out['days'][0]['slots'][0]['end'], '10:00')
        self.assertEqual(out['days'][0]['slots'][0]['course'], 'CSE-1101')
        self.assertEqual(out['days'][0]['slots'][0]['room'], '201')

    def test_normalize_schedule_accepts_day_keyed_dict(self):
        from services.routine_parser import normalize_schedule
        raw = {'Mon': [{'start': '09:00', 'end': '10:30', 'course': 'MATH-101'}]}
        out = normalize_schedule(raw)
        self.assertEqual(out['days'][0]['day'], 'Mon')
        self.assertEqual(out['days'][0]['slots'][0]['course'], 'MATH-101')

    def test_normalize_schedule_orders_days_saturday_first(self):
        from services.routine_parser import normalize_schedule
        raw = {'days': [
            {'day': 'Mon', 'slots': [{'start': '09:00', 'end': '10:00', 'course': 'A'}]},
            {'day': 'Sat', 'slots': [{'start': '09:00', 'end': '10:00', 'course': 'B'}]},
        ]}
        out = normalize_schedule(raw)
        self.assertEqual([d['day'] for d in out['days']], ['Sat', 'Mon'])

    def test_normalize_schedule_rejects_garbage(self):
        from services.routine_parser import normalize_schedule
        self.assertIsNone(normalize_schedule(None))
        self.assertIsNone(normalize_schedule('nonsense'))
        self.assertIsNone(normalize_schedule({'days': []}))
        self.assertIsNone(normalize_schedule({'days': [
            {'day': 'Mon', 'slots': [{'start': 'x', 'end': 'y'}]},
        ]}))

    def test_normalize_schedule_drops_bad_slots_keeps_good(self):
        from services.routine_parser import normalize_schedule
        raw = {'days': [{'day': 'Sun', 'slots': [
            {'start': 'bad', 'end': '10:00', 'course': 'A'},
            {'start': '11:00', 'end': '12:30', 'course': 'B'},
        ]}]}
        out = normalize_schedule(raw)
        self.assertEqual(len(out['days'][0]['slots']), 1)
        self.assertEqual(out['days'][0]['slots'][0]['course'], 'B')


class RoutineExtractApiTest(TestCase):
    """POST /api/routine/extract/ — AI routine extraction + persistence."""

    def setUp(self):
        self.user = User.objects.create_user(username='routine_ai', password='x12345678')
        self.client.force_login(self.user)

    def _image(self, name='routine.png'):
        return SimpleUploadedFile(name, b'\x89PNG\r\n\x1a\n' + b'0' * 64, content_type='image/png')

    SCHEDULE = {'days': [{'day': 'Sun', 'slots': [
        {'start': '08:30', 'end': '10:00', 'course': 'CSE-1101', 'room': '201'},
    ]}]}

    @override_settings(OPENROUTER_API_KEY='test-key')
    def test_extract_returns_schedule_without_saving(self):
        with mock.patch('core.views.extract_routine_schedule', return_value=self.SCHEDULE) as extractor:
            response = self.client.post(reverse('api_routine_extract'), {'file': self._image()})
        extractor.assert_called_once()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertFalse(data['saved'])
        self.assertEqual(data['schedule']['days'][0]['day'], 'Sun')
        self.assertFalse(Routine.objects.filter(user=self.user).exists())

    @override_settings(OPENROUTER_API_KEY='test-key')
    def test_extract_with_save_persists_routine(self):
        with mock.patch('core.views.extract_routine_schedule', return_value=self.SCHEDULE):
            response = self.client.post(
                reverse('api_routine_extract'), {'file': self._image(), 'save': '1'},
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['saved'])
        routine = Routine.objects.get(user=self.user)
        self.assertEqual(routine.schedule['days'][0]['slots'][0]['course'], 'CSE-1101')
        self.assertEqual(routine.source_name, 'routine.png')

    @override_settings(OPENROUTER_API_KEY='')
    def test_extract_requires_provider(self):
        response = self.client.post(reverse('api_routine_extract'), {'file': self._image()})
        self.assertEqual(response.status_code, 503)

    def test_extract_rejects_bad_extension(self):
        bad = SimpleUploadedFile('notes.txt', b'hello', content_type='text/plain')
        response = self.client.post(reverse('api_routine_extract'), {'file': bad})
        self.assertEqual(response.status_code, 400)

    def test_extract_requires_file(self):
        response = self.client.post(reverse('api_routine_extract'), {})
        self.assertEqual(response.status_code, 400)

    def test_extract_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('api_routine_extract'), {})
        self.assertEqual(response.status_code, 302)

    @override_settings(OPENROUTER_API_KEY='test-key')
    def test_extract_handles_provider_failure(self):
        from services.openrouter import OpenRouterRateLimitError
        with mock.patch(
            'core.views.extract_routine_schedule',
            side_effect=OpenRouterRateLimitError('slow down'),
        ):
            response = self.client.post(reverse('api_routine_extract'), {'file': self._image()})
        self.assertEqual(response.status_code, 502)


class CalendarApiTest(TestCase):
    """GET /api/calendar/events/ — month-scoped academic events."""

    def setUp(self):
        self.user = User.objects.create_user(username='cal_user', password='x12345678')
        self.client.force_login(self.user)

    def test_returns_events_for_requested_month(self):
        AcademicEvent.objects.create(title='Midterm Exams', category='exam', event_date=date(2026, 4, 12))
        AcademicEvent.objects.create(title='Other Month', category='event', event_date=date(2026, 5, 3))
        response = self.client.get(reverse('api_calendar_events'), {'month': '2026-04'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['month_name'], 'April')
        self.assertEqual(data['year'], 2026)
        self.assertEqual(data['month'], 4)
        self.assertEqual(data['days_in_month'], 30)
        self.assertIn('12', data['events_by_day'])
        self.assertNotIn('3', data['events_by_day'])
        self.assertEqual(data['events_by_day']['12'][0]['category'], 'exam')

    def test_invalid_month_falls_back_to_current(self):
        response = self.client.get(reverse('api_calendar_events'), {'month': 'garbage'})
        data = response.json()
        self.assertIn('month_name', data)
        self.assertIn('events_by_day', data)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('api_calendar_events'))
        self.assertEqual(response.status_code, 302)


class RoutineSettingsTabTest(TestCase):
    """Settings Routine tab — preview, manual JSON save, clear."""

    def setUp(self):
        self.user = User.objects.create_user(username='routine_settings', password='x12345678')
        self.client.force_login(self.user)

    def test_routine_tab_renders(self):
        html = self.client.get(reverse('settings') + '?tab=routine').content.decode()
        self.assertIn('id="tab-routine"', html)
        self.assertIn('routine-upload-form', html)
        self.assertIn('Paste Schedule JSON', html)

    def test_manual_json_save(self):
        payload = json.dumps({'days': [{'day': 'Sun', 'slots': [
            {'start': '09:00', 'end': '10:30', 'course': 'CSE-1101', 'room': '201'},
        ]}]})
        response = self.client.post(
            reverse('settings'), {'form': 'routine_json', 'schedule_json': payload},
        )
        self.assertEqual(response.status_code, 200)
        routine = Routine.objects.get(user=self.user)
        self.assertEqual(routine.schedule['days'][0]['slots'][0]['course'], 'CSE-1101')
        self.assertEqual(routine.source_name, 'manual')
        self.assertContains(response, 'Your class routine has been saved.')

    def test_manual_json_rejects_invalid(self):
        response = self.client.post(
            reverse('settings'), {'form': 'routine_json', 'schedule_json': 'not-json'},
        )
        self.assertFalse(Routine.objects.filter(user=self.user).exists())
        self.assertContains(response, 'not valid JSON')

    def test_clear_routine(self):
        Routine.objects.create(user=self.user, schedule={'days': []}, source_name='manual')
        response = self.client.post(reverse('settings'), {'form': 'routine_clear'})
        self.assertFalse(Routine.objects.filter(user=self.user).exists())
        self.assertContains(response, 'has been removed')


class ReportModelTest(TestCase):
    """Report model — fields, defaults, ordering, and cascade delete."""

    def setUp(self):
        self.user = User.objects.create_user(username='report_user', password='x12345678')
        self.report = Report.objects.create(
            user=self.user,
            title='Broken projector',
            category='facility',
            description='Room D-205 projector is not working.',
        )

    def test_str_returns_title(self):
        self.assertEqual(str(self.report), 'Broken projector')

    def test_default_status_is_pending(self):
        self.assertEqual(self.report.status, 'pending')
        self.assertEqual(self.report.get_status_display(), 'Pending')

    def test_default_severity_is_medium(self):
        self.assertEqual(self.report.severity, 'medium')
        self.assertEqual(self.report.get_severity_display(), 'Medium')

    def test_attachment_defaults_blank(self):
        self.assertFalse(self.report.attachment)
        self.assertEqual(self.report.attachment_name, '')

    def test_admin_notes_default_blank(self):
        self.assertEqual(self.report.admin_notes, '')

    def test_ordering_newest_first(self):
        older = Report.objects.create(
            user=self.user, title='Older', category='academic', description='x',
        )
        newer = Report.objects.create(
            user=self.user, title='Newer', category='general', description='y',
        )
        ids = list(Report.objects.values_list('id', flat=True))
        self.assertEqual(ids[0], newer.id)
        self.assertIn(older.id, ids)

    def test_cascade_delete_on_user(self):
        user_id = self.user.id
        self.user.delete()
        self.assertFalse(Report.objects.filter(user_id=user_id).exists())


class ReportsModuleTest(TestCase):
    """Reports & Feedback — student submission/history, staff inbox, PATCH updates."""

    def setUp(self):
        self.staff = User.objects.create_user(username='staff', password='staffpass123', is_staff=True)
        self.student_a = User.objects.create_user(
            username='S1001', password='student123',
            first_name='Alice', last_name='Johnson', email='alice@niter.edu.bd',
        )
        StudentProfile.objects.create(user=self.student_a, student_id='S1001', department='CSE')
        self.student_b = User.objects.create_user(username='S1002', password='student123')

    def _submit(self, **overrides):
        data = {
            'title': 'Broken projector',
            'category': 'facility',
            'description': 'Room D-205 projector is not working.',
        }
        data.update(overrides)
        return self.client.post(reverse('api_reports'), data=json.dumps(data), content_type='application/json')

    # ------------------------------------------------------------------
    # Pages
    # ------------------------------------------------------------------
    def test_student_page_requires_login(self):
        response = self.client.get(reverse('reports_student'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_student_page_renders_history(self):
        Report.objects.create(
            user=self.student_a, title='Broken projector', category='facility',
            description='Not working.', admin_notes='Replaced the bulb.', status='resolved',
        )
        self.client.login(username='S1001', password='student123')
        response = self.client.get(reverse('reports_student'))
        self.assertEqual(response.status_code, 200)
        for needle in ['Reports & Feedback', 'Submit a new report', 'Broken projector', 'Replaced the bulb.', 'Resolved']:
            self.assertContains(response, needle, msg_prefix=needle)

    def test_admin_page_requires_staff(self):
        self.client.login(username='S1001', password='student123')
        response = self.client.get(reverse('reports_admin'))
        # The RoleAccessMiddleware redirects students away from the admin area.
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(reverse('login'), response.url)

    def test_admin_page_renders_inbox(self):
        Report.objects.create(
            user=self.student_a, title='Broken projector', category='facility',
            description='Not working.', status='pending',
        )
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get(reverse('reports_admin'))
        self.assertEqual(response.status_code, 200)
        for needle in ['Report Inbox', 'Broken projector', 'Alice Johnson', 'S1001', 'Pending']:
            self.assertContains(response, needle, msg_prefix=needle)

    # ------------------------------------------------------------------
    # Student submit (POST /api/reports/)
    # ------------------------------------------------------------------
    def test_submit_requires_login(self):
        response = self._submit()
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_student_submits_report(self):
        self.client.login(username='S1001', password='student123')
        response = self._submit()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        report_data = data['data']['report']
        self.assertEqual(report_data['title'], 'Broken projector')
        self.assertEqual(report_data['category'], 'facility')
        self.assertEqual(report_data['severity'], 'medium')
        self.assertEqual(report_data['severity_label'], 'Medium')
        self.assertEqual(report_data['status'], 'pending')
        report = Report.objects.get(user=self.student_a)
        self.assertEqual(report.category, 'facility')
        self.assertEqual(report.severity, 'medium')
        self.assertEqual(report.status, 'pending')
        self.assertEqual(report.admin_notes, '')

    def test_submit_accepts_medical_category_and_high_severity(self):
        self.client.login(username='S1001', password='student123')
        response = self._submit(category='medical', severity='high')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['report']['category'], 'medical')
        self.assertEqual(data['data']['report']['severity'], 'high')

    def test_submit_rejects_invalid_severity(self):
        self.client.login(username='S1001', password='student123')
        response = self._submit(severity='apocalyptic')
        self.assertEqual(response.status_code, 400)
        self.assertIn('severity', response.json()['message'].lower())
        self.assertFalse(Report.objects.filter(user=self.student_a).exists())

    def test_submit_rejects_oversized_attachment(self):
        self.client.login(username='S1001', password='student123')
        big = SimpleUploadedFile(
            'screenshot.png', b'x' * (10 * 1024 * 1024 + 1),
            content_type='image/png',
        )
        response = self.client.post(reverse('api_reports'), {
            'title': 'With attachment', 'category': 'technical',
            'description': 'see file', 'attachment': big,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('10 MB', response.json()['message'])
        self.assertFalse(Report.objects.filter(user=self.student_a).exists())

    def test_submit_rejects_unsupported_attachment_type(self):
        self.client.login(username='S1001', password='student123')
        bad = SimpleUploadedFile('virus.exe', b'evil', content_type='application/x-msdownload')
        response = self.client.post(reverse('api_reports'), {
            'title': 'With attachment', 'category': 'technical',
            'description': 'see file', 'attachment': bad,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('not allowed', response.json()['message'])
        self.assertFalse(Report.objects.filter(user=self.student_a).exists())

    def test_submit_accepts_attachment_multipart(self):
        self.client.login(username='S1001', password='student123')
        shot = SimpleUploadedFile('proof.png', b'\x89PNG\r\n\x1a\n', content_type='image/png')
        response = self.client.post(reverse('api_reports'), {
            'title': 'With attachment', 'category': 'general',
            'description': 'see file', 'severity': 'critical', 'attachment': shot,
        })
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(user=self.student_a)
        self.assertTrue(report.attachment)
        self.assertEqual(report.attachment_name, 'proof.png')
        self.assertEqual(report.severity, 'critical')
        data = response.json()
        self.assertEqual(data['data']['report']['attachment_name'], 'proof.png')
        self.assertTrue(data['data']['report']['attachment'])

    def test_submit_rejects_dangerous_extension_even_with_spoofed_type(self):
        """A .html/.svg file claiming image/png is rejected by the extension check."""
        self.client.login(username='S1001', password='student123')
        for name, ctype in [
            ('evil.html', 'image/png'),
            ('bad.svg', 'image/png'),
            ('script.js', 'text/plain'),
        ]:
            spoofed = SimpleUploadedFile(name, b'<script>alert(1)</script>', content_type=ctype)
            response = self.client.post(reverse('api_reports'), {
                'title': 'Spoof', 'category': 'technical',
                'description': 'x', 'attachment': spoofed,
            })
            self.assertEqual(response.status_code, 400, msg=name)
            self.assertIn('not allowed', response.json()['message'], msg=name)
        self.assertFalse(Report.objects.filter(user=self.student_a).exists())

    def test_submit_truncates_long_attachment_name(self):
        self.client.login(username='S1001', password='student123')
        long_name = 'x' * 300 + '.png'
        shot = SimpleUploadedFile(long_name, b'\x89PNG\r\n\x1a\n', content_type='image/png')
        response = self.client.post(reverse('api_reports'), {
            'title': 'Long name', 'category': 'general',
            'description': 'see file', 'attachment': shot,
        })
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(user=self.student_a)
        self.assertLessEqual(len(report.attachment_name), 255)
        self.assertTrue(report.attachment_name.endswith('.png'))
        self.assertEqual(report.attachment_name, response.json()['data']['report']['attachment_name'])

    def test_submit_accepts_form_encoding(self):
        self.client.login(username='S1001', password='student123')
        response = self.client.post(reverse('api_reports'), {
            'title': 'Form report', 'category': 'academic', 'description': 'via form',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Report.objects.filter(user=self.student_a, title='Form report').exists())

    def test_submit_rejects_missing_title(self):
        self.client.login(username='S1001', password='student123')
        response = self._submit(title='   ')
        self.assertEqual(response.status_code, 400)
        self.assertIn('title is required', response.json()['message'])

    def test_submit_rejects_missing_description(self):
        self.client.login(username='S1001', password='student123')
        response = self._submit(description='')
        self.assertEqual(response.status_code, 400)
        self.assertIn('description is required', response.json()['message'])

    def test_submit_rejects_invalid_category(self):
        self.client.login(username='S1001', password='student123')
        response = self._submit(category='bogus')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid report category', response.json()['message'])

    def test_api_reports_rejects_put(self):
        self.client.login(username='S1001', password='student123')
        response = self.client.put(reverse('api_reports'), data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 405)

    # ------------------------------------------------------------------
    # Student list (GET /api/reports/) — own reports only
    # ------------------------------------------------------------------
    def test_student_list_returns_only_own_reports(self):
        mine = Report.objects.create(
            user=self.student_a, title='Mine', category='general', description='a',
        )
        Report.objects.create(
            user=self.student_b, title='Theirs', category='general', description='b',
        )
        self.client.login(username='S1001', password='student123')
        response = self.client.get(reverse('api_reports'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        titles = [r['title'] for r in data['data']['reports']]
        self.assertEqual(titles, ['Mine'])
        self.assertNotIn('Theirs', titles)
        # Own serialization never leaks the user block
        self.assertNotIn('user', data['data']['reports'][0])
        self.assertEqual(data['data']['reports'][0]['id'], mine.id)
        self.assertEqual(data['data']['count'], 1)

    # ------------------------------------------------------------------
    # Admin inbox (GET /api/admin/reports/)
    # ------------------------------------------------------------------
    def test_admin_list_requires_staff(self):
        self.client.login(username='S1001', password='student123')
        response = self.client.get(reverse('api_admin_reports'))
        self.assertEqual(response.status_code, 302)

    def test_admin_list_returns_all_with_user_details(self):
        Report.objects.create(
            user=self.student_a, title='From Alice', category='academic', description='x',
        )
        Report.objects.create(
            user=self.student_b, title='From Bob', category='technical', description='y',
        )
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get(reverse('api_admin_reports'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['count'], 2)
        users = {r['title']: r['user'] for r in data['data']['reports']}
        self.assertEqual(users['From Alice']['full_name'], 'Alice Johnson')
        self.assertEqual(users['From Alice']['student_id'], 'S1001')
        self.assertEqual(users['From Alice']['department'], 'CSE')
        self.assertEqual(users['From Bob']['full_name'], 'S1002')

    def test_admin_list_filters_by_status_and_category(self):
        Report.objects.create(
            user=self.student_a, title='Pending one', category='facility', description='x',
        )
        Report.objects.create(
            user=self.student_a, title='Resolved one', category='facility',
            description='y', status='resolved',
        )
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get(reverse('api_admin_reports'), {'status': 'resolved'})
        self.assertEqual(response.json()['data']['count'], 1)
        self.assertEqual(response.json()['data']['reports'][0]['title'], 'Resolved one')
        response = self.client.get(reverse('api_admin_reports'), {'category': 'facility', 'status': 'pending'})
        self.assertEqual(response.json()['data']['count'], 1)
        self.assertEqual(response.json()['data']['reports'][0]['title'], 'Pending one')

    # ------------------------------------------------------------------
    # Admin update (PATCH /api/admin/reports/<id>/)
    # ------------------------------------------------------------------
    def _make_report(self, **kwargs):
        defaults = {
            'user': self.student_a, 'title': 'Broken projector',
            'category': 'facility', 'description': 'Not working.',
        }
        defaults.update(kwargs)
        return Report.objects.create(**defaults)

    def _patch(self, report_id, payload):
        return self.client.patch(
            reverse('api_admin_report_update', args=[report_id]),
            data=json.dumps(payload), content_type='application/json',
        )

    def test_update_requires_staff(self):
        report = self._make_report()
        self.client.login(username='S1001', password='student123')
        response = self._patch(report.id, {'status': 'resolved'})
        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.status, 'pending')

    def test_update_changes_status_and_notes_and_notifies_student(self):
        report = self._make_report()
        self.client.login(username='staff', password='staffpass123')
        response = self._patch(report.id, {'status': 'resolved', 'admin_notes': 'Bulb replaced.'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['report']['status'], 'resolved')
        self.assertEqual(data['data']['report']['admin_notes'], 'Bulb replaced.')
        report.refresh_from_db()
        self.assertEqual(report.status, 'resolved')
        self.assertEqual(report.admin_notes, 'Bulb replaced.')
        # The student receives a real-time Notification (category 'report')
        notification = Notification.objects.get(user=self.student_a, category='report')
        self.assertIn('now resolved', notification.message)

    def test_update_accepts_post_fallback(self):
        report = self._make_report()
        self.client.login(username='staff', password='staffpass123')
        response = self.client.post(
            reverse('api_admin_report_update', args=[report.id]),
            {'status': 'in_progress'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        report.refresh_from_db()
        self.assertEqual(report.status, 'in_progress')

    def test_update_rejects_invalid_status(self):
        report = self._make_report()
        self.client.login(username='staff', password='staffpass123')
        response = self._patch(report.id, {'status': 'bogus'})
        self.assertEqual(response.status_code, 400)
        report.refresh_from_db()
        self.assertEqual(report.status, 'pending')

    def test_update_404_for_unknown_report(self):
        self.client.login(username='staff', password='staffpass123')
        response = self._patch(99999, {'status': 'resolved'})
        self.assertEqual(response.status_code, 404)

    def test_update_rejects_get(self):
        report = self._make_report()
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get(reverse('api_admin_report_update', args=[report.id]))
        self.assertEqual(response.status_code, 405)

    def test_update_does_not_notify_when_nothing_changes(self):
        report = self._make_report(status='resolved', admin_notes='Bulb replaced.')
        self.client.login(username='staff', password='staffpass123')
        response = self._patch(report.id, {'status': 'resolved', 'admin_notes': 'Bulb replaced.'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Notification.objects.filter(user=self.student_a, category='report').exists())

    def test_submit_rejects_overlong_title(self):
        self.client.login(username='S1001', password='student123')
        response = self._submit(title='x' * 201)
        self.assertEqual(response.status_code, 400)
        self.assertIn('200 characters', response.json()['message'])
        self.assertFalse(Report.objects.filter(user=self.student_a).exists())

    def test_notes_only_update_uses_response_wording(self):
        report = self._make_report()
        self.client.login(username='staff', password='staffpass123')
        response = self._patch(report.id, {'admin_notes': 'We are looking into it.'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(report.status, 'pending')
        notification = Notification.objects.get(user=self.student_a, category='report')
        self.assertIn('added a response', notification.message)
        self.assertNotIn('now pending', notification.message)
