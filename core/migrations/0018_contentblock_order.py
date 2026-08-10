from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_usernotificationpreference_theme_compact_layout'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contentblock',
            options={'ordering': ['order', 'id']},
        ),
        migrations.AddField(
            model_name='contentblock',
            name='order',
            field=models.PositiveIntegerField(
                db_index=True,
                default=0,
                help_text='Display order within the page (lowest first)',
            ),
        ),
    ]
