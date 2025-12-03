from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardTestCase(TestCase):

    def setUp(self):
        # employer (staff)
        self.staff_user = User.objects.create_user(
            username="boss",
            password="test123",
            is_staff=True,
        )

        # normal user
        self.normal_user = User.objects.create_user(
            username="employee",
            password="test123",
            is_staff=False,
        )

    def test_dashboard_home_access_for_staff(self):
        self.client.login(username="boss", password="test123")
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_home_redirects_if_not_staff(self):
        self.client.login(username="employee", password="test123")
        response = self.client.get(reverse("dashboard:home"))
        self.assertTemplateUsed(response, "dashboard/login_error.html")

    def test_dashboard_home_anonymous_redirect(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertTemplateUsed(response, "dashboard/login_error.html")

    def test_all_dashboard_urls_protected(self):
        urls = [
            "dashboard:home",
            "dashboard:orders",
            "dashboard:products",
            "dashboard:customers",
        ]

        for url in urls:
            response = self.client.get(reverse(url))
            self.assertTemplateUsed(response, "dashboard/login_error.html")
