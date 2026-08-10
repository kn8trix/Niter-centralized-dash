"""Seed the transport catalog (drivers, routes, schedules).

Route names and the primary departure times intentionally mirror the legacy
hardcoded ``TRANSPORT_ROUTES`` constant so pre-existing ``TransportBooking``
rows, the student dashboard widget, and the legacy ``route_id``-based booking
forms all keep resolving to the same routes after the DB migration.

Reverse deletes exactly what this migration created (the seeded drivers).
"""

from django.db import migrations

DRIVERS = [
    {'name': 'Abdul Karim', 'phone': '+880 1712-345601', 'license_number': 'DL-112233'},
    {'name': 'Rashed Mia', 'phone': '+880 1712-345602', 'license_number': 'DL-445566'},
    {'name': 'Faruk Hossain', 'phone': '+880 1712-345603', 'license_number': 'DL-778899'},
]

ROUTES = [
    {
        'name': 'Route 1: Main Campus Loop',
        'origin': 'Campus Main Gate',
        'destination': 'Town Center Bus Stand',
        'capacity': 40,
        'fare': '20.00',
        'driver': 'Abdul Karim',
        'departures': ['08:00 AM', '01:00 PM', '05:00 PM'],
    },
    {
        'name': 'Route 2: Sports Complex Shuttle',
        'origin': 'Campus Main Gate',
        'destination': 'Savar Bazar',
        'capacity': 40,
        'fare': '15.00',
        'driver': 'Rashed Mia',
        'departures': ['09:30 AM', '03:00 PM'],
    },
    {
        'name': 'Route 3: City Center Express',
        'origin': 'Campus Main Gate',
        'destination': 'Mirpur 10',
        'capacity': 40,
        'fare': '30.00',
        'driver': 'Faruk Hossain',
        'departures': ['10:00 AM', '05:00 PM'],
    },
]


def seed_transport_catalog(apps, schema_editor):
    Driver = apps.get_model('core', 'Driver')
    TransportRoute = apps.get_model('core', 'TransportRoute')
    BusSchedule = apps.get_model('core', 'BusSchedule')

    drivers = {d['name']: Driver.objects.create(**d) for d in DRIVERS}
    for route_data in ROUTES:
        departures = route_data.pop('departures')
        route = TransportRoute.objects.create(
            driver=drivers[route_data.pop('driver')],
            **route_data,
        )
        for departure in departures:
            BusSchedule.objects.create(route=route, departure_time=departure)


def unseed_transport_catalog(apps, schema_editor):
    """Remove exactly what this migration created (schedules cascade)."""
    TransportRoute = apps.get_model('core', 'TransportRoute')
    Driver = apps.get_model('core', 'Driver')
    TransportRoute.objects.filter(name__in=[r['name'] for r in ROUTES]).delete()
    Driver.objects.filter(name__in=[d['name'] for d in DRIVERS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_driver_transportroute_medicalchatthread_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_transport_catalog, unseed_transport_catalog),
    ]
