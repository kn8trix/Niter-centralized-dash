"""Set show_in_nav=True for existing published custom pages.

Published builder pages that don't have system_key set (i.e. custom pages,
not system-registered pages) should appear in the top navigation bar by
default so admins don't have to manually toggle each one.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    EditablePage = apps.get_model('core', 'EditablePage')
    # Only touch custom pages (no system_key) that are published but
    # not yet flagged for navigation.
    EditablePage.objects.filter(
        is_published=True,
        system_key__isnull=True,
        show_in_nav=False,
    ).update(show_in_nav=True)


def backwards(apps, schema_editor):
    # Reverse is a no-op — we can't know which pages were auto-toggled.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_editablepage_nav_order_nav_icon'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
