# cart/tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from catalog.models import Product, ProductVariant, Stock
from cart.models import Cart, CartItem


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="testuser",
        password="pass123",
    )


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def product(db):
    return Product.objects.create(
        name="Super notebook",
        slug="super-notebook",
        price=999,
        is_active=True,
    )


@pytest.fixture
def variant(product):
    v = ProductVariant.objects.create(
        product=product,
        sku="NOTE-001",
        price=999,
    )
    Stock.objects.create(variant=v, quantity=100)
    return v


@pytest.fixture
def cart(user):
    return Cart.objects.create(user=user)


@pytest.fixture
def cart_with_session(auth_client, cart):
    session = auth_client.session
    session["cart_id"] = cart.pk
    session.save()
    return cart


@pytest.fixture
def cart_item(cart_with_session, variant):
    return CartItem.objects.create(
        cart=cart_with_session,
        variant=variant,
        quantity=2,
        price=999,
    )