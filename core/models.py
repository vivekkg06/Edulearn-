from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_STUDENT = 'student'
    ROLE_INSTRUCTOR = 'instructor'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_INSTRUCTOR, 'Instructor'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    headline = models.CharField(max_length=150, blank=True, null=True, help_text="e.g. Senior Python Developer")
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True, help_text="Direct photo URL if no local file uploaded")

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    @property
    def is_instructor(self):
        return self.role == self.ROLE_INSTRUCTOR or self.is_staff or self.is_superuser

    def get_avatar(self):
        if self.avatar:
            try:
                return self.avatar.url
            except Exception:
                pass
        if self.avatar_url:
            return self.avatar_url
        name = f"{self.first_name} {self.last_name}".strip() or self.username
        return f"https://ui-avatars.com/api/?name={name}&background=4f46e5&color=fff&size=128"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
