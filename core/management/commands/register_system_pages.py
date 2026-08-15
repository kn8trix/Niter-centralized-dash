"""Register core system pages + feature blocks + blueprints for the Website Builder.

Idempotent — safe to re-run any time:

    python manage.py register_system_pages
"""

from django.core.management.base import BaseCommand

from core.system_pages import SYSTEM_PAGES, register_system_pages


class Command(BaseCommand):
    help = 'Register core system pages, their feature blocks and starter blueprints in the CMS.'

    def handle(self, *args, **options):
        created = register_system_pages()
        self.stdout.write(self.style.SUCCESS(
            'System pages registered: %d new page(s); %d total spec pages available.'
            % (created, len(SYSTEM_PAGES))
        ))
