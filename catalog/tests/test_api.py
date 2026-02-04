import pytest
from django.urls import reverse
from django.utils.text import slugify
from catalog.models import Product, ProductVariant

@pytest.mark.django_db
def test_products_list_api(client):
    product1 = Product.objects.create(
        name="Test Product 1",
        slug=slugify("Test Product 1"),
        price=100,
        is_active=True
    )
    ProductVariant.objects.create(product=product1, price=110)

    product2 = Product.objects.create(
        name="Test Product 2",
        slug=slugify("Test Product 2"),
        price=200,
        is_active=True
    )
    ProductVariant.objects.create(product=product2, price=220)

    url = reverse("catalog:product-list")  # použiť správny namespace
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(p["name"] == "Test Product 1" for p in data)
    assert any(p["name"] == "Test Product 2" for p in data)


@pytest.mark.django_db
def test_product_detail_api(client):
    product = Product.objects.create(
        name="Detail Product",
        slug=slugify("Detail Product"),
        price=150,
        is_active=True
    )
    ProductVariant.objects.create(product=product, price=160)

    url = reverse("catalog:product-detail", kwargs={"pk": product.id})
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Detail Product"
    assert "variants" in data
    assert len(data["variants"]) == 1
    assert data["variants"][0]["price"] == 160
