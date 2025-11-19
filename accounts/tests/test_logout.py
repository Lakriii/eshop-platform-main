import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_logout(client, user):
    client.login(username="tester", password="password123")

    url = reverse("accounts:logout")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse("accounts:login")
    assert "_auth_user_id" not in client.session
