from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_report_severity_attachment_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealsubscription',
            name='month_start',
            field=models.DateField(blank=True, help_text='First day of the paid billing month', null=True),
        ),
        migrations.AddField(
            model_name='mealsubscription',
            name='slots_remaining',
            field=models.PositiveIntegerField(default=0, help_text='Unused meal slots in the current billing month — claimed tickets decrement, cancellations refund'),
        ),
        migrations.AddField(
            model_name='mealticket',
            name='meal_date',
            field=models.DateField(blank=True, db_index=True, help_text='The calendar date this meal is for — defaults to the claim date for legacy rows', null=True),
        ),
    ]
