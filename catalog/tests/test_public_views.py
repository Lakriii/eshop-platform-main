import pytest
from catalog.models import Product


@pytest.mark.django_db
def test_product_list_view(client, product):
    response = client.get("/catalog/")
    assert response.status_code == 200
    assert product.name.encode() in response.content


@pytest.mark.django_db
def test_product_detail_view(client, product):
    response = client.get(f"/catalog/product/{product.slug}/")
    assert response.status_code == 200
    assert product.name.encode() in response.content


@pytest.mark.django_db
def test_product_detail_404_when_inactive(client, product):
    product.is_active = False
    product.save()
    response = client.get(f"/catalog/product/{product.slug}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_category_detail_view(client, category, product):
    response = client.get(f"/catalog/category/{category.slug}/")
    assert response.status_code == 200
    assert category.name.encode() in response.content
    assert product.name.encode() in response.content


@pytest.mark.django_db
def test_category_shows_only_active_products(client, category, product):
    Product.objects.create(
        name="Tajný produkt",
        slug="tajny-produkt",
        category=category,
        price=999,
        is_active=False,
    )
    response = client.get(f"/catalog/category/{category.slug}/")
    assert response.status_code == 200
    assert "Tajný produkt".encode() not in response.content


@pytest.mark.django_db
def test_product_list_shows_only_active_products(client, product):
    Product.objects.create(
        name="Neaktívny v zozname",
        slug="neaktivny-v-zozname",
        category=product.category,
        price=1,
        is_active=False,
    )
    response = client.get("/catalog/")
    assert response.status_code == 200
    assert "Neaktívny v zozname".encode() not in response.content


@pytest.mark.django_db
def test_404_nonexistent_category(client):
    response = client.get("/catalog/category/toto-urcite-neexistuje-xyz/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_404_nonexistent_product(client):
    response = client.get("/catalog/product/toto-uz-vubec-neexistuje-12345/")
    assert response.status_code == 404
