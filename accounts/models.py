# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=30, blank=True)

class Profile(models.Model):
    ROLE_CHOICES = [
        ('zamestnavatel', 'Zamestnávateľ'),
        ('leader', 'Leader'),
        ('employee', 'Zamestnanec'),
        ('customer', 'Kupec'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    loyalty_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
