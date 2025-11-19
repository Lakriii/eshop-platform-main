# accounts/tests/test_login.py
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_success(client, user):
    """
    Test: Po logine sa presmeruje na profil.
    Django default: /accounts/profile/
    """
    login_url = reverse("accounts:login")

    response = client.post(login_url, {
        "username": user.username,
        "password": "password123"
    })

    # 1. Redirect 302
    assert response.status_code == 302

    # 2. Redirect na profil (Django default)
    assert response.url == "/accounts/profile/"

    # 3. Stránka profilu je prístupná a používateľ je prihlásený
    profile_response = client.get(response.url)
    assert profile_response.status_code == 200
    assert profile_response.context["user"].is_authenticated
    assert profile_response.context["user"] == user

    # 4. V šablóne je odkaz na logout
    assert 'name="logout"' in profile_response.content.decode()


@pytest.mark.django_db
def test_login_invalid_password(client, user):
    """Nesprávne heslo → zostane na login stránke"""
    response = client.post(reverse("accounts:login"), {
        "username": user.username,
        "password": "wrong"
    })

    assert response.status_code == 200  # Nie redirect
    assert "accounts/login.html" in [t.name for t in response.templates]
    assert "Nesprávne" in response.content.decode() or "invalid" in response.content.decode().lower()


@pytest.mark.django_db
def test_login_missing_fields(client):
    """Chýbajúce polia → formulár s chybami"""
    response = client.post(reverse("accounts:login"), {})

    assert response.status_code == 200
    assert "accounts/login.html" in [t.name for t in response.templates]
    form = response.context["form"]
    assert form.errors
    assert "username" in form.errors or "password" in form.errors