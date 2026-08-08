from django.test import SimpleTestCase
from django.urls import reverse, resolve


class StudentPagesSmokeTest(SimpleTestCase):
    """Every student page renders without error after the refactor."""

    PAGES = [
        'dashboard',
        'academic_notes',
        'notices',
        'tickets',
        'medical',
        'notes',
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
        for name in self.PAGES + ['claim_meal_ticket', 'book_transport_ticket', 'book_appointment']:
            with self.subTest(endpoint=name):
                self.assertIn(name, mapping)
                resolve(mapping[name])
