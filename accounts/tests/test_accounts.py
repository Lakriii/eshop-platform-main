from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

User = get_user_model()


@pytest.mark.django_db
def test_register_invalid_password_mismatch(client):
    url = reverse("accounts:register")

    resp = client.post(url, {
        "username": "testuser",
        "password1": "Heslo12345",
        "password2": "Heslo99999",
    })

    assert User.objects.filter(username="testuser").exists() is False
    assert resp.status_code == 200
    assert "password2" in resp.context["form"].errors


@pytest.mark.django_db
def test_register_invalid_existing_username(client):
    User.objects.create_user(username="miso", password="xxxx")

    url = reverse("accounts:register")

    resp = client.post(url, {
        "username": "miso",
        "password1": "Heslo12345",
        "password2": "Heslo12345",
    })

    assert resp.status_code == 200
    assert "username" in resp.context["form"].errors


@pytest.mark.django_db
def test_register_invalid_weak_password(client):
    url = reverse("accounts:register")

    resp = client.post(url, {
        "username": "weakuser",
        "password1": "123",
        "password2": "123",
    })

    assert resp.status_code == 200
    assert "password2" in resp.context["form"].errors
