import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()

@pytest.mark.django_db
class TestAuthentication:
    
    @pytest.fixture
    def create_user(self):
        """Vytvorí testovacieho používateľa."""
        return User.objects.create_user(username='testuser', password='password123')

    def test_login_returns_tokens(self, client, create_user):
        """Testuje získanie tokenov pri logine."""
        url = reverse('token_obtain_pair')
        payload = {
            "username": "testuser",
            "password": "password123"
        }
        response = client.post(url, payload, content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_access_protected_view_with_token(self, client, create_user):
        """Testuje prístup k chránenému API s platným tokenom."""
        # 1. Získame token
        login_url = reverse('token_obtain_pair')
        login_res = client.post(login_url, {"username": "testuser", "password": "password123"}, content_type='application/json')    
        token = login_res.data["access"]

        # 2. Skúsime prístup k test_auth
        protected_url = reverse('test_auth')
        client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        response = client.get(protected_url)

        assert response.status_code == status.HTTP_200_OK

    def test_access_denied_without_token(self, client):
        """Testuje, že bez tokenu je prístup zamietnutý."""
        protected_url = reverse('test_auth')
        response = client.get(protected_url)

        # Očakávame 401 Unauthorized, nie 404
        assert response.status_code == status.HTTP_401_UNAUTHORIZED