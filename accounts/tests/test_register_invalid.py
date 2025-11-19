import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_register_passwords_do_not_match(client):
    url = reverse("accounts:register")

    response = client.post(url, {
        "username": "baduser",
        "email": "bad@example.com",
        "password1": "Password123!",
        "password2": "Different456!"
    })

    # stránka sa znova načíta
    assert response.status_code == 200

    # používateľ sa nevytvoril
    assert not User.objects.filter(username="baduser").exists()

    # vo formulári musí byť chyba
    form = response.context["form"]
    assert "password2" in form.errors
@pytest.mark.django_db
def test_register_weak_password(client):
    url = reverse("accounts:register")

    response = client.post(url, {
        "username": "weakpass",
        "email": "weak@example.com",
        "password1": "123",
        "password2": "123",
    })

    assert response.status_code == 200
    assert not User.objects.filter(username="weakpass").exists()

    form = response.context["form"]
    assert "password2" in form.errors or "password1" in form.errors
@pytest.mark.django_db
def test_register_duplicate_username(client, user):
    url = reverse("accounts:register")

    response = client.post(url, {
        "username": "tester",   # už existuje vo fixture
        "email": "duplicate@example.com",
        "password1": "Password321!",
        "password2": "Password321!",
    })

    assert response.status_code == 200
    assert User.objects.filter(email="duplicate@example.com").count() == 0

    form = response.context["form"]
    assert "username" in form.errors
@pytest.mark.django_db
def test_register_missing_required_field(client):
    url = reverse("accounts:register")

    response = client.post(url, {
        "username": "",
        "email": "nope@example.com",
        "password1": "Pass12345!",
        "password2": "Pass12345!",
    })

    assert response.status_code == 200
    assert not User.objects.filter(email="nope@example.com").exists()

    form = response.context["form"]
    assert "username" in form.errors
@pytest.mark.django_db
def test_register_does_not_auto_login_when_invalid(client):
    url = reverse("accounts:register")

    response = client.post(url, {
        "username": "testx",
        "email": "test@example.com",
        "password1": "abc",
        "password2": "xyz",
    })

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session
