import pytest
from django.contrib.auth.models import User
from django.urls import reverse

@pytest.mark.django_db
def test_dashboard_access_by_role(client):
    roles = {
        'zamestnavatel': ['dashboard:home', 'dashboard:orders', 'dashboard:products', 'dashboard:customers', 'dashboard:charts'],
        'leader': ['dashboard:orders', 'dashboard:products', 'dashboard:customers', 'dashboard:charts'],
        'employee': ['dashboard:orders', 'dashboard:products'],
        'customer': []
    }

    users = {}
    for role in roles:
        user = User.objects.create_user(username=role, password='pass')
        user.profile.role = role
        user.profile.save()
        users[role] = user

    # test access
    for role, accessible_urls in roles.items():
        client.login(username=role, password='pass')
        all_urls = ['dashboard:home', 'dashboard:orders', 'dashboard:products', 'dashboard:customers', 'dashboard:charts']
        for url_name in all_urls:
            response = client.get(reverse(url_name))
            if url_name in accessible_urls:
                assert response.status_code == 200
            else:
                assert b'Access denied' in response.content
        client.logout()
