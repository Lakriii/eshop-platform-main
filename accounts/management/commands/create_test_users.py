from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = "Create test users with different roles"

    def handle(self, *args, **options):
        users_data = [
            {"username": "boss", "password": "test123", "role": "zamestnavatel", "is_staff": True},
            {"username": "teamleader", "password": "test123", "role": "leader", "is_staff": True},
            {"username": "worker", "password": "test123", "role": "employee", "is_staff": False},
            {"username": "client", "password": "test123", "role": "client", "is_staff": False},
        ]

        for data in users_data:
            if not User.objects.filter(username=data["username"]).exists():
                user = User.objects.create_user(
                    username=data["username"],
                    password=data["password"],
                    is_staff=data["is_staff"]
                )
                Profile.objects.filter(user=user).update(role=data["role"])
                self.stdout.write(self.style.SUCCESS(f"User '{data['username']}' created with role '{data['role']}'"))
            else:
                self.stdout.write(self.style.WARNING(f"User '{data['username']}' already exists"))
