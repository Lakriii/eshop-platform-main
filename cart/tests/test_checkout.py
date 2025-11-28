# cart/tests/test_checkout.py

import pytest
from django.urls import reverse
from orders.models import Order, OrderItem


@pytest.mark.django_db
def test_checkout_creates_order(client, user, cart_with_session, cart_item):
    client.force_login(user)

    data = {
        "billing_name": "Ján Testovací",
        "billing_email": "jan@test.sk",
        "billing_phone": "+421900123456",
        "billing_address": "Testovacia 1, 811 01 Bratislava",
        "shipping_address": "Testovacia 1, 811 01 Bratislava",
    }

    response = client.post(reverse("cart:checkout"), data, follow=True)
    assert response.status_code == 200
    assert Order.objects.count() == 1

    order = Order.objects.first()
    assert order.user == user
    assert order.billing_name == "Ján Testovací"
    assert order.total > 0

