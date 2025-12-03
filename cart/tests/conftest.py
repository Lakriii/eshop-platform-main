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


# cart/tests/conftest.py → NAHRAĎ tento fixture:

@pytest.fixture
def cart_with_session(auth_client, cart, variant):
    """
    Plne funkčný fixture pre modelový aj session-based cart.
    Toto je to, čo očakáva 99 % Django e-shopov.
    """
    # 1. Uložíme cart_id (pre modelový cart)
    session = auth_client.session
    session["cart_id"] = cart.pk

    # 2. NAPLNÍME session["cart"] – TO JE KĽÚČOVÉ PRE CHECKOUT!
    session["cart"] = {
        str(variant.id): {           # variant.id, nie product.id!
            "quantity": 2,
            "price": "999.00"        # musí byť string (JSON serializácia)
        }
    }
    session.save()

    # 3. Vytvoríme aj reálny CartItem v DB (pre testy, ktoré ho kontrolujú)
    CartItem.objects.create(
        cart=cart,
        variant=variant,
        quantity=2,
        price=999
    )

    return cart

@pytest.fixture
def cart_item(cart_with_session, variant):
    return CartItem.objects.create(
        cart=cart_with_session,
        variant=variant,
        quantity=2,
        price=999,
    )