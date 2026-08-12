# Seed data — default AcademicEvent rows for the dashboard calendar.
# A starter set of Bangladesh national holidays, the current exam windows and
# a few assignment deadlines so the interactive calendar has content from the
# very first deploy. Staff can add/edit/remove rows later (the model is
# regular CRUD; students only read the calendar).

from django.db import migrations

DEFAULT_ACADEMIC_EVENTS = [
    # --- Bangladesh national holidays (fixed civil dates) ---
    {
        'title': 'International Mother Language Day',
        'category': 'holiday',
        'event_date': '2026-02-21',
        'description': 'Shaheed Day — university closed.',
    },
    {
        'title': 'Independence Day',
        'category': 'holiday',
        'event_date': '2026-03-26',
        'description': 'University closed.',
    },
    {
        'title': 'Bengali New Year (Pohela Boishakh)',
        'category': 'holiday',
        'event_date': '2026-04-14',
        'description': 'University closed.',
    },
    {
        'title': 'International Labour Day',
        'category': 'holiday',
        'event_date': '2026-05-01',
        'description': 'University closed.',
    },
    {
        'title': 'Victory Day',
        'category': 'holiday',
        'event_date': '2026-12-16',
        'description': 'University closed.',
    },
    # --- Assessment windows ---
    {
        'title': 'Midterm Examinations',
        'category': 'exam',
        'event_date': '2026-04-12',
        'description': 'Midterm exams run April 12 – April 16.',
    },
    {
        'title': 'Final Examinations',
        'category': 'exam',
        'event_date': '2026-06-21',
        'description': 'Final exams run June 21 – June 30.',
    },
    # --- Assignment deadlines ---
    {
        'title': 'Project Proposal Due',
        'category': 'assignment',
        'event_date': '2026-04-20',
        'description': 'Submit your final-year project proposal to the department office.',
    },
    {
        'title': 'Lab Report Submission',
        'category': 'assignment',
        'event_date': '2026-05-25',
        'description': 'All lab reports for the current semester must be submitted.',
    },
]


def seed_academic_events(apps, schema_editor):
    AcademicEvent = apps.get_model('core', 'AcademicEvent')
    for data in DEFAULT_ACADEMIC_EVENTS:
        AcademicEvent.objects.update_or_create(
            title=data['title'],
            event_date=data['event_date'],
            defaults=data,
        )


def unseed_academic_events(apps, schema_editor):
    AcademicEvent = apps.get_model('core', 'AcademicEvent')
    AcademicEvent.objects.filter(
        title__in=[e['title'] for e in DEFAULT_ACADEMIC_EVENTS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_routine_academicevent'),
    ]

    operations = [
        migrations.RunPython(seed_academic_events, unseed_academic_events),
    ]
