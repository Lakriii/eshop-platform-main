# catalog/tests/test_public_filter.py
import pytest
from django.urls import reverse
from catalog.models import Product, Category, ProductVariant


@pytest.fixture
def category(db):
    return Category.objects.create(name="Hlavná kategória", slug="hlavna-kategoria", is_active=True)


@pytest.fixture
def subcategory(db, category):
    return Category.objects.create(
        name="Podkategória mobilov",
        slug="podkategoria-mobilov",
        parent=category,
        is_active=True
    )


@pytest.fixture
def cheap_product(db, category):
    p = Product.objects.create(
        name="Lacný telefón A50",
        slug="lacny-telefon-a50",          # unikátny slug!
        price=99.99,
        category=category,
        is_active=True
    )
    ProductVariant.objects.create(product=p, sku="TEL-001", stock_quantity=15)
    return p


@pytest.fixture
def expensive_product(db, subcategory):
    p = Product.objects.create(
        name="Prémiový iPhone 15 Pro",
        slug="iphone-15-pro",             # unikátny slug!
        price=1299.99,
        category=subcategory,
        is_active=True
    )
    ProductVariant.objects.create(product=p, sku="IPH-001", stock_quantity=8)
    return p


@pytest.fixture
def out_of_stock_product(db, category):
    p = Product.objects.create(
        name="Vypredaný notebook",
        slug="vypredany-notebook",        # unikátny slug!
        price=599.99,
        category=category,
        is_active=True
    )
    ProductVariant.objects.create(product=p, sku="NB-001", stock_quantity=0)
    return p


@pytest.fixture
def inactive_product(db, category):
    return Product.objects.create(
        name="Skrytý produkt",
        slug="skryty-produkt",            # unikátny slug!
        price=299.99,
        category=category,
        is_active=False
    )


@pytest.mark.django_db
class TestProductListFilter:
    url = reverse("catalog:product_list")

    def test_default_view_shows_only_active_products(self, client, cheap_product, inactive_product):
        response = client.get(self.url)
        assert response.status_code == 200
        products = response.context["products"]
        assert cheap_product in products
        assert inactive_product not in products

    def test_search_by_name(self, client, cheap_product, expensive_product):
        response = client.get(self.url, {"name": "lacný"})
        assert cheap_product in response.context["products"]
        assert expensive_product not in response.context["products"]

        response = client.get(self.url, {"name": "iphone"})
        assert expensive_product in response.context["products"]

    def test_filter_by_category(self, client, cheap_product, expensive_product, subcategory):
        # Podkategória
        response = client.get(self.url, {"category": subcategory.id})
        assert expensive_product in response.context["products"]
        assert cheap_product not in response.context["products"]

        # Hlavná kategória – mal by nájsť oba
        response = client.get(self.url, {"category": subcategory.parent.id})
        assert cheap_product in response.context["products"]
        assert expensive_product in response.context["products"]

    def test_price_range_filter(self, client, cheap_product, expensive_product):
        response = client.get(self.url, {"min_price": "1000"})
        assert cheap_product not in response.context["products"]
        assert expensive_product in response.context["products"]

        response = client.get(self.url, {"max_price": "200"})
        assert cheap_product in response.context["products"]
        assert expensive_product not in response.context["products"]

    def test_in_stock_filter(self, client, cheap_product, out_of_stock_product):
        response = client.get(self.url, {"in_stock": "on"})
        assert cheap_product in response.context["products"]
        assert out_of_stock_product not in response.context["products"]

        response = client.get(self.url)
        assert out_of_stock_product in response.context["products"]

    def test_combined_filters(self, client, cheap_product, expensive_product, subcategory):
        response = client.get(self.url, {
            "name": "telefón",
            "category": subcategory.parent.id,
            "max_price": "150",
            "in_stock": "on"
        })
        products = response.context["products"]
        assert cheap_product in products
        assert expensive_product not in products

    def test_pagination_preserves_filters(self, client, category):
    # Vytvoríme 30 unikátnych produktov
        for i in range(30):
            Product.objects.create(
                name=f"Test produkt paginácia {i+1}",
                slug=f"test-produkt-pag-{i+1}",
                price=100 + i * 20,
                category=category,
                is_active=True
            ).variants.create(sku=f"PAG-{i}", stock_quantity=10)

        response = client.get(reverse("catalog:product_list"), {
            "min_price": "500",
            "page": "2"
        })
        assert response.status_code == 200
        assert "min_price=500" in response.content.decode()
        assert len(response.context["products"]) > 0

    def test_filter_form_is_present(self, client):
        response = client.get(self.url)
        html = response.content.decode()
        assert 'name="name"' in html
        assert 'name="category"' in html
        assert 'name="min_price"' in html
        assert 'name="max_price"' in html
        assert 'name="in_stock"' in html