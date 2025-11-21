# cart/tests/test_checkout.py
import pytest                                 # ← TOTO CHÝBALO!
from django.urls import reverse
from orders.models import Order


@pytest.mark.django_db
def test_checkout_requires_items(auth_client, cart_with_session):
    # Vyprázdnime košík → malo by redirectovať
    cart_with_session.items.all().delete()
    response = auth_client.get(reverse("cart:checkout"))
    assert response.status_code == 302  # redirect na cart_detail, lebo je prázdny


@pytest.mark.django_db
def test_checkout_creates_order(auth_client, cart_with_session, cart_item):
    data = {
        "full_name": "Ján Novák",
        "email": "jan@example.com",
        "phone": "+421900123456",
        "billing_street": "Hlavná 1",
        "billing_city": "Bratislava",
        "billing_postcode": "81101",
        "billing_country": "SK",
        "shipping_street": "Hlavná 1",
        "shipping_city": "Bratislava",
        "shipping_postcode": "81101",
        "shipping_country": "SK",
    }

    response = auth_client.post(reverse("cart:checkout"), data, follow=True)

    # Debug výpis (môžeš neskôr zmazať)
    print("Status code:", response.status_code)
    if hasattr(response, "redirect_chain"):
        print("Redirect chain:", response.redirect_chain)
    if response.status_code != 200:
        print("Content:", response.content.decode()[:500])

    assert response.status_code == 200
    assert Order.objects.exists(), "Objednávka sa nevytvorila!"
    assert cart_with_session.items.count() == 0, "Košík sa nevyprázdnil!"