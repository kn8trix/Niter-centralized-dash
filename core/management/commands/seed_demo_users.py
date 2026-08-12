"""Seed demo users so fresh environments can log in immediately.

``db.sqlite3`` is gitignored, so a fresh clone has **no** users until someone
creates them. This command recreates the documented demo accounts (the same
ones the handover describes):

    python manage.py seed_demo_users

Creates, when missing:

- ``admin`` / ``admin123``  — superuser + staff (every admin dashboard,
  Django admin, and the Website Builder).
- ``student`` / ``student123`` — regular student (all student-facing pages).

Idempotent: existing users are never touched (passwords are NOT reset), so
re-running after a password change keeps the new password.

Optional extra staff accounts for demos that need more than one admin
(``--extra-staff N``) and a ``--password`` override so the admin accounts
aren't stuck with the documented default on shared environments:

    python manage.py seed_demo_users --extra-staff 2 --password 'S3cret!x'

Note: ``--password`` applies to the admin/staff accounts only — the student
account always uses its documented password ``student123``.
"""

from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create the demo users (admin/admin123, student/student123) if missing.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            default='admin123',
            help='Password for the created admin/staff accounts (default: admin123). '
                 'The student account always uses its documented password '
                 'student123.',
        )
        parser.add_argument(
            '--extra-staff',
            type=int,
            default=0,
            help='Also create N extra staff accounts (staff1..staffN).',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        password = options['password']

        def ensure(username, password, is_staff, is_superuser, first_name='', last_name=''):
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING('exists (skipped): %s' % username))
                return
            User.objects.create_user(
                username=username,
                password=password,
                is_staff=is_staff,
                is_superuser=is_superuser,
                first_name=first_name,
                last_name=last_name,
            )
            self.stdout.write(self.style.SUCCESS('created: %s' % username))

        ensure('admin', password, is_staff=True, is_superuser=True,
               first_name='System', last_name='Admin')
        ensure('student', 'student123', is_staff=False, is_superuser=False,
               first_name='Demo', last_name='Student')

        for i in range(1, options['extra_staff'] + 1):
            ensure('staff%d' % i, password, is_staff=True, is_superuser=False,
                   first_name='Staff', last_name=str(i))
