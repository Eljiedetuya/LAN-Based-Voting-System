from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Course(models.TextChoices):
        BSIT = 'BSIT', 'BSIT'
        BIT = 'BIT', 'BIT'

    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        ADMIN = 'ADMIN', 'Administrator'
        MONITOR = 'MONITOR', 'Election monitor'

    student_id = models.CharField(max_length=32, unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=150)
    course = models.CharField(max_length=4, choices=Course.choices, blank=True, default='')
    year_level = models.PositiveSmallIntegerField(null=True, blank=True, choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4')])
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.STUDENT)
    must_change_password = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if self.role == self.Role.STUDENT and not self.student_id:
            from django.core.exceptions import ValidationError
            raise ValidationError({'student_id': 'Students require a student ID.'})

    def __str__(self):
        return self.username
