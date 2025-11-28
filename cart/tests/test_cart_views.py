# cart/tests/test_cart_views.py
import pytest
from django.urls import reverse
from cart.models import CartItem


@pytest.mark.django_db
def test_cart_detail_renders(auth_client, cart_with_session, cart_item):
    response = auth_client.get(reverse("cart:cart_detail"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_to_cart_works(auth_client, variant, cart_with_session):
    url = reverse("cart:add_to_cart", kwargs={"product_id": variant.product.id})
    response = auth_client.post(
        url,
        {"variant_id": variant.id, "quantity": 3},
        follow=True,
    )
    assert response.status_code == 200
    assert CartItem.objects.filter(variant=variant, quantity=3).exists()


@pytest.mark.django_db
def test_update_quantity_works(auth_client, cart_with_session, cart_item):
    url = reverse("cart:cart_item_update", kwargs={"item_id": cart_item.id})
    response = auth_client.post(url, {"quantity": "7"}, follow=True)
    assert response.status_code == 200
    cart_item.refresh_from_db()
    assert cart_item.quantity == 7


@pytest.mark.django_db
def test_remove_item_works(auth_client, cart_with_session, cart_item):
    item_id = cart_item.id
    url = reverse("cart:cart_item_remove", kwargs={"item_id": item_id})
    response = auth_client.post(url, follow=True)
    assert response.status_code == 200
    assert not CartItem.objects.filter(id=item_id).exists()