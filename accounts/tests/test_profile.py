import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_profile_logged_in(client, user):
    client.force_login(user)

    url = reverse("accounts:profile")
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["user"] == user
    assert "profile" in response.context
    assert response.context["profile"].loyalty_points == 0

def test_profile_redirects_when_not_logged_in(client):
    url = reverse("accounts:profile")
    response = client.get(url)

    assert response.status_code == 302
    assert "/login/" in response.url
