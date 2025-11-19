# accounts/tests/conftest.py
import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    """
    Vytvorí používateľa s profilom.
    Ak už existuje, vráti existujúceho (bez chyby).
    """
    User = get_user_model()

    # Použi get_or_create namiesto create_user, aby si sa vyhol duplikátom
    user, created = User.objects.get_or_create(
        username="tester",
        defaults={
            "email": "tester@example.com",
        }
    )

    if created:
        user.set_password("password123")
        user.save()

    # Importuj Profile až tu (keď je Django ready)
    from accounts.models import Profile

    # Vytvor profil len raz (OneToOneField s unique=True)
    Profile.objects.get_or_create(
        user=user,
        defaults={"loyalty_points": 0}
    )

    return user