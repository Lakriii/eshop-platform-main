import pytest
from django.urls import reverse
from catalog.models import Product, ProductVariant


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
        response = client.get(self.url, {"category": subcategory.id})
        assert expensive_product in response.context["products"]
        assert cheap_product not in response.context["products"]

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
    # Vytvor 30 produktov, aby sa stránkovanie aktivovalo
            for i in range(30):
                product = Product.objects.create(
                    name=f"Test produkt paginácia {i+1}",
                    slug=f"test-produkt-pag-{i+1}",
                    price=500 + i * 20,  # ← všetky nad min_price=500
                    category=category,
                    is_active=True
                )
                ProductVariant.objects.create(product=product, sku=f"PAG-{i}", stock_quantity=10)

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
