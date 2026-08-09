from django.contrib.auth.models import User
from django.db import models


class StudentProfile(models.Model):
    """Extra student identity fields (student ID + department) tied to a User.

    The Django ``User`` model only carries username/name/email; the portal also
    needs the institutional student ID and department, so they live here on a
    one-to-one profile record.
    """

    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science & Engineering'),
        ('TEX', 'Textile Engineering'),
        ('IPE', 'Industrial & Production Engineering'),
        ('FDAE', 'Fashion Design & Technology'),
        ('EEE', 'Electrical & Electronic Engineering'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES)

    def get_department_display_name(self):
        return dict(self.DEPARTMENT_CHOICES).get(self.department, self.department)

    def __str__(self):
        return self.student_id
