from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=30, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_users',  # unikátne meno
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # unikátne meno
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
