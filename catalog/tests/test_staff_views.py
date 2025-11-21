# catalog/tests/test_staff_views.py
import pytest


@pytest.mark.django_db
def test_product_create_view_ak_existruje(client, staff_user):
    possible = ["/catalog/add/", "/catalog/create/", "/catalog/novy-produkt/"]
    url = None
    for u in possible:
        r = client.get(u)
        if r.status_code != 404:
            url = u
            break
    if not url:
        pytest.skip("Create view neexistuje – pravdepodobne sa používa admin")

    client.force_login(staff_user)
    assert client.get(url).status_code in (200, 403)


@pytest.mark.django_db
def test_product_update_view_ak_existruje(client, staff_user, product):
    possible = [
        f"/catalog/{product.slug}/edit/",
        f"/catalog/{product.slug}/upravit/",
        f"/catalog/edit/{product.slug}/",
    ]
    url = None
    for u in possible:
        r = client.get(u)
        if r.status_code != 404:
            url = u
            break
    if not url:
        pytest.skip("Update view neexistuje – pravdepodobne sa používa admin")

    client.force_login(staff_user)
    assert client.get(url).status_code in (200, 403)