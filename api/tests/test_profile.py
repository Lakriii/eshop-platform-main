from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()

class ProfileTests(APITestCase):

    def setUp(self):
        # -------------------------
        # Používateľ
        # -------------------------
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            first_name="OldName"
        )
        self.token = Token.objects.create(user=self.user)

    # -------------------------
    # LOGIN
    # -------------------------
    def test_login_success(self):
        response = self.client.post("/api/login/", {
            "username": "testuser",
            "password": "testpassword"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_fail(self):
        response = self.client.post("/api/login/", {
            "username": "testuser",
            "password": "wrong"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------
    # PROFILE
    # -------------------------
    def test_protected_endpoint_requires_auth(self):
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -------------------------
    # PATCH USER NAME
    # -------------------------
    def test_patch_user_first_name(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.patch("/api/profile/", {"first_name": "NewName"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "NewName")