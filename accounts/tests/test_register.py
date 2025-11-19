import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


@pytest.mark.django_db
def test_register_success(client):
    url = reverse("accounts:register")

    response = client.post(url, {
        "username": "newuser",
        "email": "new@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!"
    })

    # redirect to home
    assert response.status_code == 302
    assert response.url == reverse("home")

    # user was created
    user = User.objects.get(username="newuser")
    assert user is not None

    # automatic login
    assert "_auth_user_id" in client.session

    # profile auto created? (ak máš signál doplnený)
    assert Profile.objects.filter(user=user).exists()
