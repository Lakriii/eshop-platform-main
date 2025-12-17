# apps/orders/models.py
from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from catalog.models import Product



User = get_user_model()

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percent
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    max_uses_total = models.PositiveIntegerField(default=0)   # 0 = unlimited
    max_uses_per_user = models.PositiveIntegerField(default=1)  # how many times one user can use this coupon
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                           help_text="Ak je nastavené, len tieto účty môžu použiť kupón.")
    min_order_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"),
                                          help_text="Minimálna hodnota objednávky pre použitie kupónu.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.code} — {self.discount_percentage}%"

    def total_uses(self):
        return self.usages.count()

    def user_uses(self, user):
        if not user or not user.is_authenticated:
            return 0
        return self.usages.filter(user=user).count()

    def is_within_dates(self):
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True

    def is_allowed_for_user(self, user):
        if self.allowed_users.exists():
            if not user or not user.is_authenticated:
                return False
            return self.allowed_users.filter(pk=user.pk).exists()
        return True

    def is_valid_for_user(self, user, order_total=Decimal("0.00")):
        """Komplexné overenie: aktivita, dátumy, min order, total limit, per-user limit, allow list."""
        if not self.active:
            return False, "Kupón nie je aktívny."
        if not self.is_within_dates():
            return False, "Kupón nie je v platnom časovom rozsahu."
        if order_total < self.min_order_total:
            return False, f"Minimálna hodnota pre tento kupón je {self.min_order_total} €."
        if self.max_uses_total > 0 and self.total_uses() >= self.max_uses_total:
            return False, "Kupón bol vyčerpaný."
        if not self.is_allowed_for_user(user):
            return False, "Tento kupón nie je pre váš účet povolený."
        if user and user.is_authenticated:
            if self.user_uses(user) >= self.max_uses_per_user:
                return False, f"Maximálny počet použití kupónu pre váš účet je {self.max_uses_per_user}."
        return True, "OK"

    @transaction.atomic
    def use_by(self, user):
        """
        Attempt to mark coupon used by `user`.
        Returns (True, usage_instance) on success, (False, reason_string) on failure.
        Atomic to avoid race conditions.
        """
        valid, reason = self.is_valid_for_user(user)
        if not valid:
            return False, reason

        # create usage
        usage = CouponUsage.objects.create(coupon=self, user=user)
        # If total limit reached, optionally deactivate
        if self.max_uses_total > 0 and self.total_uses() >= self.max_uses_total:
            self.active = False
            self.save(update_fields=["active"])
        return True, usage


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, related_name="usages", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="coupon_usages", on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("coupon", "user", "used_at")  # allows multiple rows but ensures meaningful uniqueness

    def __str__(self):
        return f"{self.user} used {self.coupon.code} on {self.used_at}"


# Order + OrderItem (ak ich ešte nemáš alebo ak chceš upraviť)
class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_payment', 'Pending Payment'),
        ('paid', 'Paid'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    billing_name = models.CharField(max_length=255, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_phone = models.CharField(max_length=50, blank=True)
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)

    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    used_loyalty_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Order {self.pk} - {self.status}"

    def calculate_coupon_discount_amount(self):
        if self.coupon:
            pct = (self.coupon.discount_percentage or 0) / Decimal("100")
            return (self.total * pct).quantize(Decimal("0.01"))
        return Decimal("0.00")

    def calculate_loyalty_discount_amount(self):
        # Example: 100 points = 10%, max 20%
        if not hasattr(self.user, "profile"):
            return Decimal("0.00")
        points = Decimal(self.used_loyalty_points or 0)
        pct = min((points / Decimal("100")) * Decimal("10"), Decimal("20"))
        return (self.total * pct / Decimal("100")).quantize(Decimal("0.01"))

    def calculate_total_after_discounts(self):
        coupon_amount = self.calculate_coupon_discount_amount()
        loyalty_amount = self.calculate_loyalty_discount_amount()
        total = self.total - coupon_amount - loyalty_amount
        return max(total, Decimal("0.00"))
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, default=1)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def product_name(sf2elf):
        return self.product.name

    def sku(self):
        return self.product.sku



class PaymentRecord(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def amount(self):
        return self.total_amount
