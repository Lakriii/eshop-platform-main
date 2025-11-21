# catalog/tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from catalog.models import Category, Product

User = get_user_model()


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


@pytest.fixture
def category():
    return Category.objects.create(name="Test kategória", slug="test-kategoria", is_active=True)


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Super produkt",
        slug="super-produkt",
        category=category,
        price=9990,
        is_active=True,
    )