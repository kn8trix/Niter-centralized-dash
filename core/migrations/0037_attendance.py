from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_mealsubscription_slots_remaining_mealticket_meal_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(db_index=True, max_length=20)),
                ('session_token', models.CharField(help_text='Short code embedded in the classroom QR, e.g. ATD-9F4A2C', max_length=20, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('expires_at', models.DateTimeField(db_index=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['course_code', '-created_at'], name='att_sess_course_created')],
            },
        ),
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('status', models.CharField(choices=[('present', 'Present')], default='present', help_text='Attendance status (Present today — future statuses can extend this)', max_length=10)),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='Client IP captured at scan time (campus Wi-Fi gate uses it)', null=True)),
                ('session', models.ForeignKey(db_index=True, on_delete=models.CASCADE, related_name='records', to='core.attendancesession')),
                ('student', models.ForeignKey(db_index=True, on_delete=models.CASCADE, related_name='attendance_records', to='auth.user')),
            ],
            options={
                'ordering': ['-timestamp'],
                'constraints': [models.UniqueConstraint(fields=['student', 'session'], name='uniq_attendance_student_session')],
            },
        ),
    ]
