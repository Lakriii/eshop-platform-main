"""# apps/orders/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Coupon

User = get_user_model()

class CouponTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")
        self.c = Coupon.objects.create(code="PROMO10", discount_percentage=10, max_uses_per_user=2, max_uses_total=5)

    def test_user_can_use_twice(self):
        ok, _ = self.c.use_by(self.user)
        self.assertTrue(ok)
        ok2, _ = self.c.use_by(self.user)
        self.assertTrue(ok2)
        # third use should fail
        ok3, reason = self.c.use_by(self.user)
        self.assertFalse(ok3)
        self.assertIn("Maximálny počet", reason)
"""