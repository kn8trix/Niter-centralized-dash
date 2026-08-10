"""Seed the department hubs and club directory with starter content.

Departments, faculty, and class routines mirror the showcase data the hub
pages previously shipped as frontend mock JS — now as real database rows.
Club events are dated relative to the migration run time so the /clubs/ page
always shows upcoming events.

Reverse deletes exactly what this migration created.
"""

from datetime import timedelta

from django.db import migrations
from django.utils import timezone

DEPARTMENTS = [
    {
        'name': 'Computer Science & Engineering',
        'code': 'CSE',
        'slug': 'cse',
        'head_of_dept': 'Prof. Dr. Md. Ashraful Alam',
        'office_location': 'Room D-205, Academic Block D',
        'description': (
            'Programming, artificial intelligence, software engineering, and '
            'computer networks — NITER’s largest undergraduate program. '
            'Learning by building: every theory course has a companion '
            'project track so the classroom and the lab stay connected.'
        ),
    },
    {
        'name': 'Textile Engineering',
        'code': 'TEX',
        'slug': 'tex',
        'head_of_dept': 'Prof. Dr. Kazi Abu Bakar Siddique',
        'office_location': 'Room E-210, Academic Block E',
        'description': (
            'Fiber to fabric — yarn manufacturing, weaving, knitting, wet '
            'processing, and quality control across the textile value chain, '
            'with mills-scale laboratories that give students hands-on '
            'exposure long before graduation.'
        ),
    },
    {
        'name': 'Industrial & Production Engineering',
        'code': 'IPE',
        'slug': 'ipe',
        'head_of_dept': 'Prof. Dr. Mahmudul Hasan',
        'office_location': 'Room G-210, Academic Block G',
        'description': (
            'Operations research, lean manufacturing, supply chain '
            'management, and ergonomics for efficient industrial systems — '
            'the department that optimizes everything else.'
        ),
    },
    {
        'name': 'Fashion Design & Apparel Engineering',
        'code': 'FDAE',
        'slug': 'fde',
        'head_of_dept': 'Prof. Dr. Farhana Yasmin',
        'office_location': 'Room B-204, Academic Block B',
        'description': (
            'Where design creativity meets apparel engineering — pattern '
            'drafting, garment construction, and product innovation, with a '
            'CAD lab that treats the studio as a second classroom.'
        ),
    },
    {
        'name': 'Electrical & Electronic Engineering',
        'code': 'EEE',
        'slug': 'eee',
        'head_of_dept': 'Prof. Dr. Sultana Parvin',
        'office_location': 'Room F-205, Academic Block F',
        'description': (
            'Circuits, power systems, control engineering, and renewable '
            'energy with hands-on laboratory practice from the first year.'
        ),
    },
]

FACULTY = [
    # CSE
    ('cse', 'Prof. Dr. Md. Ashraful Alam', 'Professor & Head', 'cse.hod@niter.edu.bd', 'Sun–Wed · 10:00 AM – 12:00 PM'),
    ('cse', 'Dr. Tanvir Ahmed', 'Associate Professor', 'tanvir.ahmed@niter.edu.bd', 'Sat–Tue · 1:00 – 3:00 PM'),
    ('cse', 'Sabrina Haque', 'Assistant Professor', 'sabrina.haque@niter.edu.bd', 'Sun & Tue · 11:00 AM – 1:00 PM'),
    # TEX
    ('tex', 'Prof. Dr. Kazi Abu Bakar Siddique', 'Professor & Head', 'tex.hod@niter.edu.bd', 'Sun–Wed · 10:00 AM – 1:00 PM'),
    ('tex', 'Prof. Dr. Selina Akter', 'Professor', 'selina.akter@niter.edu.bd', 'Sat–Tue · 2:00 – 4:00 PM'),
    ('tex', 'Engr. Rafiqul Islam', 'Associate Professor', 'rafiqul.islam@niter.edu.bd', 'Sun & Wed · 11:00 AM – 1:00 PM'),
    # IPE
    ('ipe', 'Prof. Dr. Mahmudul Hasan', 'Professor & Head', 'ipe.hod@niter.edu.bd', 'Sun–Wed · 10:00 AM – 1:00 PM'),
    ('ipe', 'Dr. Fahmida Rahman', 'Associate Professor', 'fahmida.rahman@niter.edu.bd', 'Sat–Tue · 1:00 – 3:00 PM'),
    ('ipe', 'Tanvir Chowdhury', 'Assistant Professor', 'tanvir.chowdhury@niter.edu.bd', 'Sun & Wed · 11:00 AM – 1:00 PM'),
    # FDAE
    ('fde', 'Prof. Dr. Farhana Yasmin', 'Professor & Head', 'fde.hod@niter.edu.bd', 'Sun–Wed · 11:00 AM – 1:00 PM'),
    ('fde', 'Md. Shafiqul Islam', 'Associate Professor', 'shafiqul.islam@niter.edu.bd', 'Sat–Tue · 2:00 – 4:00 PM'),
    ('fde', 'Nusrat Jahan Mitu', 'Assistant Professor', 'nusrat.mitu@niter.edu.bd', 'Sun & Mon · 10:00 AM – 12:00 PM'),
    # EEE
    ('eee', 'Prof. Dr. Sultana Parvin', 'Professor & Head', 'eee.hod@niter.edu.bd', 'Sun–Wed · 11:00 AM – 1:00 PM'),
    ('eee', 'Dr. M. Kamruzzaman', 'Professor', 'kamruzzaman@niter.edu.bd', 'Sat–Tue · 10:00 AM – 12:00 PM'),
    ('eee', 'Ayesha Siddiqua', 'Assistant Professor', 'ayesha.siddiqua@niter.edu.bd', 'Sun & Tue · 2:00 – 4:00 PM'),
]

# (dept_slug, semester, day, subject, time_slot, room)
ROUTINES = [
    ('cse', 'Semester 1', 'Sun', 'CSE-101 Programming Fundamentals', '9:00 – 10:40 AM', 'Room D-205'),
    ('cse', 'Semester 1', 'Sun', 'CSE-101L Programming Lab', '11:00 AM – 1:40 PM', 'Lab D-302'),
    ('cse', 'Semester 1', 'Tue', 'CSE-103 Discrete Mathematics', '2:00 – 3:40 PM', 'Room D-205'),
    ('cse', 'Semester 1', 'Thu', 'MAT-201 Engineering Math', '11:00 AM – 12:40 PM', 'Room A-108'),
    ('tex', 'Semester 1', 'Sun', 'TEX-101 Yarn Manufacturing', '9:00 – 10:40 AM', 'Room E-205'),
    ('tex', 'Semester 1', 'Sun', 'TEX-103L Spinning Lab', '11:00 AM – 1:40 PM', 'Spinning Lab'),
    ('tex', 'Semester 1', 'Mon', 'TEX-201 Weaving Technology', '9:00 – 10:40 AM', 'Room E-210'),
    ('tex', 'Semester 1', 'Tue', 'TEX-205L Wet Processing Lab', '9:00 – 11:40 AM', 'Wet Processing Lab'),
    ('ipe', 'Semester 1', 'Sun', 'IPE-101 Engineering Materials', '9:00 – 10:40 AM', 'Room G-205'),
    ('ipe', 'Semester 1', 'Sun', 'IPE-103L Workshop Lab', '11:00 AM – 1:40 PM', 'Workshop Lab'),
    ('ipe', 'Semester 1', 'Tue', 'IPE-205L Simulation Lab', '9:00 – 11:40 AM', 'Simulation Lab G-203'),
    ('ipe', 'Semester 1', 'Thu', 'IPE-103L Workshop Lab', '9:00 – 11:40 AM', 'Workshop Lab'),
    ('fde', 'Semester 1', 'Sun', 'FDE-201 Pattern Drafting', '9:00 – 10:40 AM', 'Studio 1'),
    ('fde', 'Semester 1', 'Sun', 'FDE-203 Pattern CAD Lab', '11:00 AM – 1:40 PM', 'Studio 2'),
    ('fde', 'Semester 1', 'Tue', 'FDE-205 Fabric Science', '11:00 AM – 12:40 PM', 'Room C-112'),
    ('fde', 'Semester 1', 'Thu', 'FDE-209 Textile Testing Lab', '9:00 – 11:40 AM', 'Textile Testing Lab'),
    ('eee', 'Semester 1', 'Sun', 'EEE-101 Circuit Analysis', '9:00 – 10:40 AM', 'Room F-205'),
    ('eee', 'Semester 1', 'Sun', 'EEE-103L Circuit Lab', '11:00 AM – 1:40 PM', 'Circuit Lab F-202'),
    ('eee', 'Semester 1', 'Tue', 'EEE-205L Digital Logic Lab', '9:00 – 11:40 AM', 'Digital Lab F-204'),
    ('eee', 'Semester 1', 'Thu', 'EEE-201 Electrical Machines', '11:00 AM – 12:40 PM', 'Room F-208'),
]

CLUBS = [
    ('Computer Club', 'computer-club', 'Code · Hack · Innovate — programming contests, workshops, and the annual hackathon.'),
    ('Electronics Club', 'electronics-club', 'Circuits · Robotics · IoT — hands-on builds from breadboards to embedded systems.'),
    ('Cultural Society', 'cultural-society', 'Music · Dance · Drama — the creative heartbeat of campus, all departments welcome.'),
    ('Sports Club', 'sports-club', 'Cricket · Football · Athletics — inter-department leagues and annual sports week.'),
]

# Club events are seeded relative to the migration run date so the /clubs/
# page always lists upcoming events regardless of when it is applied.
EVENTS = [
    ('computer-club', 'CodeStorm — Inter-University Hackathon', 14, 'Innovation Lab, Building C', 200),
    ('computer-club', 'Tech Talk: AI in the Textile Industry', 18, 'Central Auditorium', 150),
    ('cultural-society', 'Spring Cultural Night', 21, 'Main Auditorium, Block A', 300),
    ('sports-club', 'Inter-Department Football Cup', 25, 'Main Field, Sports Complex', 400),
]


def seed(apps, schema_editor):
    Department = apps.get_model('core', 'Department')
    FacultyMember = apps.get_model('core', 'FacultyMember')
    ClassRoutine = apps.get_model('core', 'ClassRoutine')
    Club = apps.get_model('core', 'Club')
    ClubEvent = apps.get_model('core', 'ClubEvent')

    depts = {}
    for item in DEPARTMENTS:
        dept, _ = Department.objects.get_or_create(
            slug=item['slug'],
            defaults={
                'name': item['name'],
                'code': item['code'],
                'head_of_dept': item['head_of_dept'],
                'office_location': item['office_location'],
                'description': item['description'],
            },
        )
        depts[item['slug']] = dept

    for slug, name, designation, email, office_hours in FACULTY:
        FacultyMember.objects.get_or_create(
            department=depts[slug], name=name,
            defaults={
                'designation': designation,
                'email': email,
                'office_hours': office_hours,
            },
        )

    for slug, semester, day, subject, time_slot, room in ROUTINES:
        ClassRoutine.objects.get_or_create(
            department=depts[slug], semester=semester, day_of_week=day,
            subject=subject, time_slot=time_slot, room=room,
        )

    clubs = {}
    for name, slug, description in CLUBS:
        club, _ = Club.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'description': description},
        )
        clubs[slug] = club

    base = timezone.now().date()
    for club_slug, title, days_ahead, location, capacity in EVENTS:
        ClubEvent.objects.get_or_create(
            club=clubs[club_slug], title=title,
            defaults={
                'event_date': base + timedelta(days=days_ahead),
                'location': location,
                'capacity': capacity,
            },
        )


def unseed(apps, schema_editor):
    Department = apps.get_model('core', 'Department')
    FacultyMember = apps.get_model('core', 'FacultyMember')
    ClassRoutine = apps.get_model('core', 'ClassRoutine')
    Club = apps.get_model('core', 'Club')
    ClubEvent = apps.get_model('core', 'ClubEvent')

    Department.objects.filter(slug__in=[d['slug'] for d in DEPARTMENTS]).delete()
    FacultyMember.objects.filter(
        department__slug__in=[d['slug'] for d in DEPARTMENTS]
    ).delete()
    ClassRoutine.objects.filter(
        department__slug__in=[d['slug'] for d in DEPARTMENTS]
    ).delete()
    Club.objects.filter(slug__in=[c[1] for c in CLUBS]).delete()
    ClubEvent.objects.filter(club__slug__in=[c[1] for c in CLUBS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_club_department_facultymember_clubevent_classroutine_and_more'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
