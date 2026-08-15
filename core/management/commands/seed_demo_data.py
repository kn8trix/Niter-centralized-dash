"""Seed a realistic NITER campus demo dataset.

Populates the documented mock dataset — demo accounts, transport routes &
bookings, medical center, cafeteria menu & meal tokens, academic courses &
materials, and clubs — so a fresh environment (or the live Supabase DB)
immediately has believable content:

    python manage.py seed_demo_data

**Idempotent by design:** every row is created with ``get_or_create`` (keyed
on the natural unique fields), so re-running never duplicates rows or raises
``IntegrityError``. Existing users are never touched — passwords are **not**
reset on re-runs.

Accounts created (password ``password123`` unless already present):

- ``admin@niter.edu.bd``   — superuser + staff
- ``dr.chen@niter.edu.bd`` — staff + Teacher (CSE)
- ``prof.rahman@niter.edu.bd`` — staff + Teacher (EEE)
- ``kn8trix@niter.edu.bd`` — student (Ahsanul Haque, EEE, 2026-EEE-01)
- ``student2@niter.edu.bd`` — student (CSE)
"""

import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    BusSchedule,
    Club,
    ClubEvent,
    Course,
    CourseMaterial,
    Department,
    Doctor,
    Driver,
    MealMenu,
    MealSubscription,
    MealTicket,
    MedicalAppointment,
    Notice,
    StudentProfile,
    Teacher,
    TransportBooking,
    TransportRoute,
)

User = get_user_model()

DEMO_PASSWORD = 'password123'


def _placeholder_pdf(title):
    """A tiny but valid single-page PDF so seeded demo materials are
    downloadable instead of carrying an empty ``file`` field."""
    text = (title or 'Niter Hub demo material').encode('latin-1', 'replace')
    stream = b'BT /F1 14 Tf 72 720 Td (%s) Tj ET\n' % text
    content = (
        b'%PDF-1.4\n'
        b'1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n'
        b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n'
        b'3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n'
        b'4 0 obj<</Length '
        + str(len(stream)).encode('ascii')
        + b'>>stream\n'
        + stream
        + b'endstream\nendobj\n'
        b'5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n'
        b'trailer<</Root 1 0 R>>\n'
        b'%%EOF\n'
    )
    return content


class Command(BaseCommand):
    help = 'Seed a realistic NITER campus demo dataset (idempotent).'

    def _created(self, label):
        self.stdout.write(self.style.SUCCESS('created: %s' % label))

    def _skipped(self, label):
        self.stdout.write(self.style.WARNING('exists (skipped): %s' % label))

    def _report(self, obj, label):
        if obj:
            self._created(label)
        else:
            self._skipped(label)
        return obj

    def _updated(self, label):
        self.stdout.write(self.style.SUCCESS('updated: %s' % label))

    # -- Accounts -----------------------------------------------------------
    def _ensure_user(self, username, email, first_name='', last_name='',
                     is_staff=False, is_superuser=False):
        """get_or_create a user by username; never resets existing passwords."""
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': is_staff,
                'is_superuser': is_superuser,
            },
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=['password'])
        elif not user.email:
            # Clean update only: fill a missing email, never reset passwords.
            user.email = email
            user.save(update_fields=['email'])
        return user, created

    def _seed_accounts(self):
        admin, created = self._ensure_user(
            'admin', 'admin@niter.edu.bd',
            first_name='System', last_name='Admin',
            is_staff=True, is_superuser=True,
        )
        self._report(created, 'admin / admin@niter.edu.bd')

        dr_chen, created = self._ensure_user(
            'dr.chen', 'dr.chen@niter.edu.bd',
            first_name='Michael', last_name='Chen', is_staff=True,
        )
        self._report(created, 'dr.chen / dr.chen@niter.edu.bd')

        prof_rahman, created = self._ensure_user(
            'prof.rahman', 'prof.rahman@niter.edu.bd',
            first_name='Rafiq', last_name='Rahman', is_staff=True,
        )
        self._report(created, 'prof.rahman / prof.rahman@niter.edu.bd')

        kn8trix, created = self._ensure_user(
            'kn8trix', 'kn8trix@niter.edu.bd',
            first_name='Ahsanul', last_name='Haque',
        )
        self._report(created, 'kn8trix / kn8trix@niter.edu.bd')
        profile, created = StudentProfile.objects.get_or_create(
            user=kn8trix,
            defaults={'student_id': '2026-EEE-01', 'department': 'EEE'},
        )
        self._report(created, 'StudentProfile 2026-EEE-01 (kn8trix)')

        student2, created = self._ensure_user(
            'student2', 'student2@niter.edu.bd',
            first_name='Fatema', last_name='Khan',
        )
        self._report(created, 'student2 / student2@niter.edu.bd')
        profile, created = StudentProfile.objects.get_or_create(
            user=student2,
            defaults={'student_id': '2026-CSE-02', 'department': 'CSE'},
        )
        self._report(created, 'StudentProfile 2026-CSE-02 (student2)')

        return admin, dr_chen, prof_rahman, kn8trix, student2

    # -- Departments + Teachers --------------------------------------------
    def _seed_departments(self):
        cse, created = Department.objects.get_or_create(
            code='CSE',
            defaults={
                'name': 'Computer Science & Engineering',
                'slug': 'cse',
                'head_of_dept': 'Prof. Dr. Nusrat Jahan',
            },
        )
        self._report(created, 'Department CSE')
        eee, created = Department.objects.get_or_create(
            code='EEE',
            defaults={
                'name': 'Electrical & Electronic Engineering',
                'slug': 'eee',
                'head_of_dept': 'Prof. Dr. Selim Reza',
            },
        )
        self._report(created, 'Department EEE')
        return cse, eee

    def _seed_teachers(self, dr_chen, prof_rahman, cse, eee, courses):
        teacher, created = Teacher.objects.get_or_create(
            email='dr.chen@niter.edu.bd',
            defaults={
                'name': 'Dr. Michael Chen',
                'department': cse,
                'designation': 'Assistant Professor',
                'phone_number': '01700-000101',
            },
        )
        self._report(created, 'Teacher Dr. Michael Chen (CSE)')

        teacher2, created = Teacher.objects.get_or_create(
            email='prof.rahman@niter.edu.bd',
            defaults={
                'name': 'Prof. Rafiq Rahman',
                'department': eee,
                'designation': 'Professor',
                'phone_number': '01700-000102',
            },
        )
        self._report(created, 'Teacher Prof. Rafiq Rahman (EEE)')

        # Link teachers to their courses (idempotent M2M adds).
        eee2101 = courses.get('EEE-2101')
        eee3105 = courses.get('EEE-3105')
        cse1101 = courses.get('CSE-1101')
        if eee2101 and eee3105:
            teacher.courses.add(eee2101, eee3105)
        if cse1101:
            teacher2.courses.add(cse1101)

    # -- Transport ----------------------------------------------------------
    def _seed_transport(self, kn8trix, student2):
        drivers = []
        for name, phone in (
            ('Md. Karim', '01700-000201'),
            ('Abdul Hossain', '01700-000202'),
            ('Jahangir Islam', '01700-000203'),
        ):
            driver, created = Driver.objects.get_or_create(
                name=name,
                defaults={'phone': phone, 'license_number': 'DL-4%02d-2025' % (len(drivers) + 1)},
            )
            self._report(created, 'Driver %s' % name)
            drivers.append(driver)

        routes = []
        route_specs = [
            ('NITER Campus ↔ Mirpur 10 / Farmgate (Bus #01)',
             'NITER Campus, Savar', 'Mirpur 10 / Farmgate', 40, '50.00', drivers[0],
             ['07:30 AM', '04:30 PM']),
            ('NITER Campus ↔ Uttara / Gazipur (Bus #02)',
             'NITER Campus, Savar', 'Uttara / Gazipur', 40, '60.00', drivers[1],
             ['08:00 AM', '05:00 PM']),
            ('NITER Campus ↔ Baipal / Nabinagar Local Shuttle (Bus #03)',
             'NITER Campus, Savar', 'Baipal / Nabinagar', 30, '30.00', drivers[2],
             ['09:00 AM', '06:00 PM']),
        ]
        for name, origin, destination, capacity, fare, driver, departures in route_specs:
            route, created = TransportRoute.objects.get_or_create(
                name=name,
                defaults={
                    'origin': origin,
                    'destination': destination,
                    'capacity': capacity,
                    'fare': fare,
                    'driver': driver,
                },
            )
            self._report(created, 'Route %s' % name)
            for dep in departures:
                schedule, sched_created = BusSchedule.objects.get_or_create(
                    route=route,
                    departure_time=dep,
                    defaults={'is_active': True},
                )
                self._report(sched_created, 'Schedule %s @ %s' % (route.name, dep))
            routes.append(route)

        # 3 active sample seat reservations (paid, with boarding QR).
        bookings = [
            (kn8trix, 'NITER Campus ↔ Mirpur 10 / Farmgate (Bus #01)', '07:30 AM', 5),
            (student2, 'NITER Campus ↔ Mirpur 10 / Farmgate (Bus #01)', '04:30 PM', 8),
            (kn8trix, 'NITER Campus ↔ Uttara / Gazipur (Bus #02)', '08:00 AM', 12),
        ]
        for user, route_name, departure_time, seat in bookings:
            booking, created = TransportBooking.objects.get_or_create(
                route_name=route_name,
                departure_time=departure_time,
                seat_number=seat,
                defaults={
                    'user': user,
                    'qr_token': 'TR-SEED%03d' % seat,
                    'payment_status': 'paid',
                    'paid_at': timezone.now(),
                },
            )
            self._report(created, 'Booking %s · seat %s' % (route_name, seat))
        return routes

    # -- Medical center -----------------------------------------------------
    def _seed_medical(self, kn8trix, student2):
        doctors = []
        # ``update_or_create`` (clean update) — the data migration seeds these
        # names with different specialties/hours, so converge them to the
        # requested clinic spec (Sun–Thu 09:00 AM – 05:00 PM) on every run.
        for name, specialty in (
            ('Dr. Michael Chen', 'General Physician'),
            ('Dr. Emily Johnson', 'Dentist'),
        ):
            doctor, created = Doctor.objects.update_or_create(
                name=name,
                defaults={
                    'specialty': specialty,
                    'working_days': 'Sunday - Thursday',
                    'start_time': '09:00 AM',
                    'end_time': '05:00 PM',
                },
            )
            label = 'Doctor %s (%s)' % (name, specialty)
            if created:
                self._created(label)
            else:
                self._updated(label)
            doctors.append(doctor)

        today = timezone.now().date()
        appointments = [
            (kn8trix, 'Dr. Michael Chen', today + timedelta(days=1), '10:00 AM',
             'Seasonal fever and headache', 'confirmed'),
            (student2, 'Dr. Emily Johnson', today + timedelta(days=2), '11:00 AM',
             'Tooth pain check-up', 'pending'),
            (kn8trix, 'Dr. Michael Chen', today - timedelta(days=3), '09:30 AM',
             'General check-up for campus medical form', 'completed'),
        ]
        for user, doctor_name, appt_date, slot, reason, status in appointments:
            appt, created = MedicalAppointment.objects.get_or_create(
                doctor_name=doctor_name,
                appointment_date=appt_date,
                time_slot=slot,
                defaults={
                    'user': user,
                    'reason': reason,
                    'status': status,
                },
            )
            self._report(created, 'Appointment %s %s %s' % (doctor_name, appt_date, slot))
        return doctors

    # -- Cafeteria ----------------------------------------------------------
    def _seed_cafeteria(self, kn8trix, student2):
        menus = [
            ('breakfast', 'Paratha, Egg (fried/boiled), Khichuri, Tea'),
            ('lunch', 'Rice, Fish Curry, Chicken Curry, Dal, Mixed Vegetables'),
            ('snacks', 'Muri, Samosa, Singara, Banana, Tea/Coffee'),
        ]
        for meal_type, items in menus:
            menu, created = MealMenu.objects.get_or_create(
                day='Daily',
                meal_type=meal_type,
                defaults={'items': items, 'is_active': True},
            )
            self._report(created, 'MealMenu %s' % meal_type)

        # Active monthly subscriptions for both demo students.
        today = timezone.now().date()
        month_start = today.replace(day=1)
        for user in (kn8trix, student2):
            sub, created = MealSubscription.objects.get_or_create(
                user=user,
                defaults={
                    'is_active': True,
                    'expires_at': timezone.now() + timedelta(days=30),
                    'month_start': month_start,
                    'slots_remaining': 40,
                },
            )
            self._report(created, 'MealSubscription %s' % user.username)

        # 4 digital meal tokens — fixed tokens keep re-runs idempotent.
        tokens = [
            (kn8trix, 'lunch', '#MEAL-1001'),
            (kn8trix, 'dinner', '#MEAL-1002'),
            (student2, 'lunch', '#MEAL-2001'),
            (student2, 'dinner', '#MEAL-2002'),
        ]
        for user, meal_type, token in tokens:
            ticket, created = MealTicket.objects.get_or_create(
                ticket_token=token,
                defaults={
                    'user': user,
                    'meal_type': meal_type,
                    'meal_date': today,
                    'is_redeemed': False,
                    'payment_status': 'paid',
                    'paid_at': timezone.now(),
                },
            )
            self._report(created, 'MealTicket %s (%s)' % (token, user.username))

    # -- Academic notes & materials -----------------------------------------
    def _seed_academic(self):
        course_specs = [
            ('EEE-2101', 'Circuit Analysis & Superposition Theorem', 'EEE', 'Summer 2026'),
            ('CSE-1101', 'Structured C Programming & Digital Logic', 'CSE', 'Summer 2026'),
            ('EEE-3105', 'Power Systems & BMS Configurations', 'EEE', 'Summer 2026'),
        ]
        courses = {}
        for code, title, department, semester in course_specs:
            course, created = Course.objects.get_or_create(
                code=code,
                defaults={
                    'title': title,
                    'department': department,
                    'semester': semester,
                },
            )
            self._report(created, 'Course %s' % code)
            courses[code] = course

        material_specs = [
            ('EEE-2101', 'Circuit Analysis Lecture Notes (Superposition)', 'PDF'),
            ('EEE-2101', 'Circuit Analysis Lab Manual', 'PDF'),
            ('CSE-1101', 'C Programming Lecture Slides — Arrays & Pointers', 'SLIDES'),
            ('CSE-1101', 'Digital Logic Design Notes', 'PDF'),
            ('EEE-3105', 'Power Systems Study Guide (BMS Configurations)', 'PDF'),
        ]
        for code, title, file_type in material_specs:
            material, created = CourseMaterial.objects.get_or_create(
                course=courses[code],
                title=title,
                defaults={'file_type': file_type},
            )
            # Attach a real placeholder file so the Study Corner drive never
            # renders a material with an empty ``file`` (which would crash
            # ``material.file.url`` in the templates). Rows that already have
            # a file (real uploads) are never touched; the check is on the
            # file field, not ``created``, so re-running the seed also
            # backfills files onto older fileless demo rows.
            if not material.file:
                slug = re.sub(r'[^A-Za-z0-9]+', '-', title.lower()).strip('-')
                material.file.save(
                    '%s-%s.pdf' % (code.replace('-', '').lower(), slug[:40]),
                    ContentFile(_placeholder_pdf(title)),
                    save=False,
                )
                material.save(update_fields=['file'])
            self._report(created, 'Material %s — %s' % (code, title))
        return courses

    # -- Clubs & community --------------------------------------------------
    def _seed_clubs(self, admin, kn8trix):
        clubs = []
        club_specs = [
            ('NITER Computer Club (NCC)',
             'The official programming & tech community of NITER — hackathons, '
             'competitive programming practice, and industry workshops.'),
            ('NITER Robotics Society',
             'Hands-on robotics, IoT, and automation projects — from line '
             'followers to campus automation demos.'),
        ]
        slugs = ['niter-computer-club', 'niter-robotics-society']
        for (name, description), slug in zip(club_specs, slugs):
            club, created = Club.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': description,
                    'lead_user': admin,
                },
            )
            self._report(created, 'Club %s' % name)
            clubs.append(club)

        today = timezone.now().date()
        events = [
            (clubs[0], 'NCC Annual Hackathon 2026',
             '24-hour coding marathon — form teams of up to 4 and build for '
             'the campus.', today + timedelta(days=14), 'NITER Campus, Savar', 120),
            (clubs[1], 'Robotics Workshop: Line Follower Basics',
             'Intro session on sensors, motor drivers, and building a line '
             'follower from scratch.', today + timedelta(days=7),
             'EEE Lab 2, NITER Campus', 60),
        ]
        for club, title, description, event_date, location, capacity in events:
            event, created = ClubEvent.objects.get_or_create(
                club=club,
                title=title,
                defaults={
                    'description': description,
                    'event_date': event_date,
                    'location': location,
                    'capacity': capacity,
                },
            )
            self._report(created, 'Event %s — %s' % (club.name, title))

        notices = [
            ('Hackathon 2026: registrations now open',
             'NITER Computer Club invites all students to register for the '
             'annual 24-hour Hackathon 2026. Teams of up to 4. Register at '
             'the club desk before the deadline.', 'event'),
            ('Robotics workshop: line follower basics',
             'Join the NITER Robotics Society this Saturday for a hands-on '
             'workshop on building line-follower robots. No prior experience '
             'required.', 'event'),
            ('Mid-term examination schedule published',
             'The mid-term exam schedule for Summer 2026 has been published. '
             'Students are advised to check the routine and contact their '
             'department office for conflicts.', 'academic'),
        ]
        for title, content, category in notices:
            notice, created = Notice.objects.get_or_create(
                title=title,
                author=admin,
                defaults={
                    'content': content,
                    'category': category,
                    'is_published': True,
                },
            )
            self._report(created, 'Notice %s' % title)

    def handle(self, *args, **options):
        admin, dr_chen, prof_rahman, kn8trix, student2 = self._seed_accounts()
        cse, eee = self._seed_departments()
        courses = self._seed_academic()
        self._seed_teachers(dr_chen, prof_rahman, cse, eee, courses)
        self._seed_transport(kn8trix, student2)
        self._seed_medical(kn8trix, student2)
        self._seed_cafeteria(kn8trix, student2)
        self._seed_clubs(admin, kn8trix)

        self.stdout.write(self.style.SUCCESS(
            'Demo dataset seeded — all rows created idempotently (re-run safe).'
        ))
