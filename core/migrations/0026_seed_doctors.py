# Seed data — default campus doctors for the Medical Admin dashboard.
# Mirrors the doctors previously shown as mock data (DOCTOR_SPECIALTIES) so the
# availability toggles / slot management have persisted rows to attach to from
# the very first deploy.

from django.db import migrations

DEFAULT_DOCTORS = [
    {
        'name': 'Dr. Ahmed Khan',
        'specialty': 'General Physician',
        'working_days': 'Sunday - Thursday',
        'start_time': '10:00 AM',
        'end_time': '2:00 PM',
    },
    {
        'name': 'Dr. Sarah Smith',
        'specialty': 'Orthopedic',
        'working_days': 'Monday - Friday',
        'start_time': '9:00 AM',
        'end_time': '1:00 PM',
    },
    {
        'name': 'Dr. Michael Chen',
        'specialty': 'Dermatology',
        'working_days': 'Tuesday - Saturday',
        'start_time': '11:00 AM',
        'end_time': '3:00 PM',
    },
    {
        'name': 'Dr. Emily Johnson',
        'specialty': 'General Physician',
        'working_days': 'Sunday - Thursday',
        'start_time': '12:00 PM',
        'end_time': '4:00 PM',
    },
]


def seed_doctors(apps, schema_editor):
    Doctor = apps.get_model('core', 'Doctor')
    for data in DEFAULT_DOCTORS:
        Doctor.objects.update_or_create(name=data['name'], defaults=data)


def unseed_doctors(apps, schema_editor):
    Doctor = apps.get_model('core', 'Doctor')
    Doctor.objects.filter(name__in=[d['name'] for d in DEFAULT_DOCTORS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_doctor_clubsheetsconfig_doctorschedule'),
    ]

    operations = [
        migrations.RunPython(seed_doctors, unseed_doctors),
    ]
