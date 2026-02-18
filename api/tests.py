import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from catalog.models import Product, Category

User = get_user_model()

@pytest.mark.django_db
class TestEshopAPI:
    
    # --- FIXTURES (Príprava dát pre testy) ---
    
    @pytest.fixture
    def create_user(self):
        """Vytvorí testovacieho používateľa pre auth testy."""
        return User.objects.create_user(
            username='testuser', 
            password='password123', 
            first_name="PôvodnéMeno"
        )

    @pytest.fixture
    def setup_products(self):
        """Vytvorí produkty s unikátnymi slugmi, aby nepadala DB."""
        cat = Category.objects.create(name="Oblečenie", slug="oblecenie")
        
        p1 = Product.objects.create(
            name="Čierne Tričko", 
            slug="cierne-tricko", # UNIKÁTNY SLUG
            price=15, 
            category=cat, 
            is_active=True
        )
        p2 = Product.objects.create(
            name="Biela Mikina", 
            slug="biela-mikina", # UNIKÁTNY SLUG
            price=30, 
            category=cat, 
            is_active=True
        )
        return [p1, p2]

    @pytest.fixture
    def auth_client(self, client, create_user):
        """Vráti klienta, ktorý je už prihlásený cez Bearer token."""
        login_url = reverse('token_obtain_pair')
        login_res = client.post(
            login_url, 
            {"username": "testuser", "password": "password123"}, 
            content_type='application/json'
        )
        token = login_res.data["access"]
        client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return client

    # --- 1. TESTY AUTENTIFIKÁCIE ---

    def test_login_returns_tokens(self, client, create_user):
        """Overí, že login vráti JWT tokeny."""
        url = reverse('token_obtain_pair')
        payload = {"username": "testuser", "password": "password123"}
        response = client.post(url, payload, content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_access_protected_view(self, auth_client):
        """Overí prístup k chránenému endpointu s tokenom."""
        url = reverse('test_auth')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"] == "testuser"

    # --- 2. TESTY VYHĽADÁVANIA A NÁVRHOV (DID YOU MEAN) ---

    def test_search_suggestions_when_no_results(self, client, setup_products):
        """Testuje návrhy, ak sa nič presne nenašlo (napr. preklep)."""
        # Hľadáme "BieX" namiesto "Biela"
        url = reverse('product-list') + "?search=BieX"
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0
        assert "suggestions" in response.data
        # Skontrolujeme, či navrhlo Biela Mikina (lebo začína na Bie)
        assert any("Biela" in s for s in response.data['suggestions'])

    def test_search_filtering_works(self, client, setup_products):
        """Overí, že vyhľadávanie vráti správne výsledky."""
        url = reverse('product-list') + "?search=Tričko"
        response = client.get(url)
        assert len(response.data['results']) == 1
        assert "Čierne Tričko" in response.data['results'][0]['name']

    # --- 3. TESTY PROFILU A ZMENY ÚDAJOV ---

    def test_update_profile_name(self, auth_client):
        """Testuje zmenu mena používateľa cez PATCH."""
        url = reverse('profile_update')
        payload = {"first_name": "NovéMeno"}
        response = auth_client.patch(url, payload, content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK
        
        user = User.objects.get(username="testuser")
        assert user.first_name == "NovéMeno"

    # --- 4. TESTY PLATBY / CHECKOUTU ---

    def test_simulate_checkout_success(self, auth_client, setup_products):
        """Testuje úspešnú simuláciu platby."""
        product = setup_products[0]
        url = reverse('simulate_checkout')
        payload = {
            "items": [{"id": product.id, "quantity": 1}],
            "total_price": 15.0
        }
        response = auth_client.post(url, payload, content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        assert "order_id" in response.data

    def test_checkout_fails_without_token(self, client):
        """Overí, že neprihlásený používateľ nemôže zaplatiť."""
        url = reverse('simulate_checkout')
        response = client.post(url, {"items": []}, content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED