import pytest
from django.contrib.auth import get_user_model
from catalog.models import Category, Product, ProductVariant

User = get_user_model()


# ----------------------
# Client fixtures
# ----------------------
@pytest.fixture
def client():
    from django.test import Client
    return Client()


@pytest.fixture
def regular_user():
    return User.objects.create_user(username="joe", password="pass")


@pytest.fixture
def staff_user():
    return User.objects.create_user(username="admin", password="pass", is_staff=True)


# ----------------------
# Category fixtures
# ----------------------
@pytest.fixture
def category(db):
    return Category.objects.create(
        name="Hlavná kategória",
        slug="hlavna-kategoria",
        is_active=True
    )


@pytest.fixture
def subcategory(db, category):
    return Category.objects.create(
        name="Podkategória mobilov",
        slug="podkategoria-mobilov",
        parent=category,
        is_active=True
    )


# ----------------------
# Product fixtures
# ----------------------
@pytest.fixture
def cheap_product(db, category):
    p = Product.objects.create(
        name="Lacný telefón A50",
        slug="lacny-telefon-a50",
        price=99.99,
        category=category,
        is_active=True
    )
    ProductVariant.objects.create(product=p, sku="TEL-001", stock_quantity=15)  # ← variant pridaný
    return p


@pytest.fixture
def expensive_product(db, subcategory):
    p = Product.objects.create(
        name="Prémiový iPhone 15 Pro",
        slug="iphone-15-pro",
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
        slug="vypredany-notebook",
        price=599.99,
        category=category,
        is_active=True
    )
    ProductVariant.objects.create(product=p, sku="NB-001", stock_quantity=0)
    return p


@pytest.fixture
def inactive_product(db, category):
    p = Product.objects.create(
        name="Skrytý produkt",
        slug="skryty-produkt",
        price=299.99,
        category=category,
        is_active=False
    )
    ProductVariant.objects.create(product=p, sku="SKR-001", stock_quantity=5)
    return p


# ----------------------
# Generic product fixture pre testy vo views
# ----------------------
@pytest.fixture
def product(db, category):
    p = Product.objects.create(
        name="Test Produkt",
        slug="test-produkt",
        price=100,
        category=category,
        is_active=True
    )
    ProductVariant.objects.create(product=p, sku="TEST-001", stock_quantity=10)
    return p
