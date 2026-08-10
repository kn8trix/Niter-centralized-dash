"""Unified application layout.

Every student subpage renders inside the ``templates/base.html`` left-sidebar
shell ("Niter Hub") instead of a standalone top-pill navigation header. These
tests guard that contract: the sidebar shell, its nav links, and the
per-page stylesheets are all present, and the old topbar is gone.
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class UnifiedSidebarLayoutTest(TestCase):
    """The Niter Hub left sidebar renders on every student subpage.

    ``TestCase`` (not ``SimpleTestCase``) because several of these pages query
    the database for live content (notices, clubs, transport routes, ...).
    """

    # route name -> (expected sidebar link href, page-specific stylesheet)
    PAGES = {
        'dashboard': ('/dashboard/', 'css/dashboard.css'),
        'academic_notes': ('/academic-notes/', 'css/notes.css'),
        'transport_dashboard': ('/transport/', 'css/transport.css'),
        'meal_dashboard': ('/meals/', 'css/meals.css'),
        'clubs_dashboard': ('/clubs/', 'css/clubs.css'),
        'medical': ('/medical/', 'css/medical.css'),
        'notices': ('/notices/', 'css/notices.css'),
        'research_ai': ('/research-ai/', 'css/research_ai.css'),
    }

    # Exact labels of the sidebar navigation in base.html
    SIDEBAR_LINKS = [
        'Dashboard',
        'Academic & Notes',
        'Official Notices',
        'Transport Tickets',
        'Meal System',
        'Medical Booking',
        'Clubs & Events',
        'Settings',
    ]

    def test_every_subpage_renders_inside_the_sidebar_shell(self):
        for route, (_, css) in self.PAGES.items():
            with self.subTest(page=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200, msg=route)
                html = response.content.decode()

                # Sidebar shell comes from base.html
                self.assertIn('data-region="sidebar"', html, msg=route)
                self.assertIn('Niter Hub', html, msg=route)
                self.assertIn('data-region="main"', html, msg=route)

                # Every sidebar nav link is rendered
                for label in self.SIDEBAR_LINKS:
                    self.assertIn(label, html, msg=route + ' :: ' + label)

                # Page-specific stylesheet is wired up via extra_head
                self.assertIn(css, html, msg=route)

                # No standalone top-pill navigation on any subpage
                self.assertNotIn('data-component="topbar"', html, msg=route)
                self.assertNotIn('id="avatar-btn"', html, msg=route)
                self.assertNotIn('id="profile-popover"', html, msg=route)

    # Routes whose page lives directly behind a sidebar link (Research AI is
    # reachable from the topbar only, so it has no sidebar entry of its own).
    SIDEBAR_LINKED_PAGES = {
        'dashboard',
        'academic_notes',
        'transport_dashboard',
        'meal_dashboard',
        'clubs_dashboard',
        'medical',
        'notices',
    }

    def test_sidebar_active_link_tracks_current_page(self):
        for route in self.SIDEBAR_LINKED_PAGES:
            url = self.PAGES[route][0]
            with self.subTest(page=route):
                html = self.client.get(reverse(route)).content.decode()
                self.assertIn('href="' + url + '"', html, msg=route)

    def test_notes_engine_lives_in_the_sidebar_shell(self):
        response = self.client.get(reverse('notes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-region="sidebar"')
        self.assertNotContains(response, 'data-component="topbar"')

    def test_settings_renders_sidebar_for_authenticated_user(self):
        user = User.objects.create_user(username='S1001', password='student123')
        self.client.login(username='S1001', password='student123')
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-region="sidebar"')
        self.assertContains(response, 'css/settings.css')
        self.assertContains(response, 'href="' + reverse('settings') + '"')
