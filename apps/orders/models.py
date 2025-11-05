from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    max_uses_total = models.PositiveIntegerField(default=0)  # 0 = neobmedzene
    max_uses_per_user = models.PositiveIntegerField(default=1)
    used_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def is_valid(self, user=None):
        """Overí, či je kupón platný."""
        now = timezone.now()

        # 1️⃣ Kupón musí byť aktívny
        if not self.active:
            return False

        # 2️⃣ Dátumová platnosť
        if self.valid_from and self.valid_from > now:
            return False
        if self.valid_to and self.valid_to < now:
            return False

        # 3️⃣ Celkový limit použitia
        if self.max_uses_total > 0 and self.used_by.count() >= self.max_uses_total:
            return False

        # 4️⃣ Len raz na jeden účet
        if user and self.used_by.filter(id=user.id).exists():
            return False

        return True

    def use(self, user):
        """Použije kupón pre daného používateľa, ak je platný."""
        if not self.is_valid(user):
            return False

        # ✅ Pridaj používateľa do použitia
        self.used_by.add(user)

        # Ak je definovaný max_uses_total a práve sa naplnil, deaktivuj
        if self.max_uses_total > 0 and self.used_by.count() >= self.max_uses_total:
            self.active = False
            self.save(update_fields=["active"])

        return True

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%)"


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
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    billing_name = models.CharField(max_length=255, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_phone = models.CharField(max_length=50, blank=True)
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)

    # 🟢 Kupón a vernostné body
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    used_loyalty_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Order {self.pk} - {self.status}"

    def calculate_discount(self):
        """Vypočíta zľavu podľa kupónu a vernostných bodov."""
        discount = 0

        # Vernostné body: 100 bodov = 10%, max 20%
        if hasattr(self.user, 'profile'):
            points = self.used_loyalty_points
            points_discount = min((points / 100) * 10, 20)
            discount += points_discount

        # Kupón
        if self.coupon and self.coupon.is_valid():
            discount += self.coupon.discount_percentage

        # Max zľava 50%
        return min(discount, 50)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def line_total(self):
        return self.price * self.quantity

class PaymentRecord(models.Model):
    order = models.ForeignKey(Order, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(max_length=32, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.pk} for Order {self.order.pk} - {self.status}"
