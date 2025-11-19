import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_home_status_code(client):
    """Home page returns HTTP 200."""
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_uses_correct_template(client):
    """Home page uses template core/home.html."""
    url = reverse("home")
    response = client.get(url)
    assert "core/home.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_home_contains_expected_content(client):
    """Check if page contains expected content (optional)."""
    url = reverse("home")
    response = client.get(url)
    assert "<h1" in response.content.decode()  # uprav podľa svojho HTML
