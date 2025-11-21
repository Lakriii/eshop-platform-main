# cart/tests/test_models.py
import pytest
from decimal import Decimal

@pytest.mark.django_db
def test_cart_total_price(cart, cart_item):
    # cart fixture tu používa reálny user → žiadna chyba
    assert cart.total_price == Decimal("1998")