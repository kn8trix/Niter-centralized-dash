from django.db import migrations, models


def backfill_theme(apps, schema_editor):
    """Map the legacy ``dark_mode`` boolean onto the new tri-state ``theme``.

    Users who had previously selected Dark keep it; everyone else gets Light
    (the historical default). New rows use the model default from now on.
    """
    UserNotificationPreference = apps.get_model('core', 'UserNotificationPreference')
    UserNotificationPreference.objects.filter(dark_mode=True).update(theme='dark')
    UserNotificationPreference.objects.filter(dark_mode=False).update(theme='light')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_usernotificationpreference_notify_meals_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernotificationpreference',
            name='compact_layout',
            field=models.BooleanField(
                default=False,
                help_text='Use a more compact, denser layout',
            ),
        ),
        migrations.AddField(
            model_name='usernotificationpreference',
            name='theme',
            field=models.CharField(
                choices=[
                    ('light', 'Light Mode'),
                    ('dark', 'Dark Mode'),
                    ('system', 'System Default'),
                ],
                default='light',
                help_text='Portal theme: light, dark, or follow the system preference',
                max_length=10,
            ),
        ),
        migrations.RunPython(backfill_theme, migrations.RunPython.noop),
    ]
