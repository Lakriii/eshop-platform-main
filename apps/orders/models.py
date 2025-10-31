from django.db import models
from django.conf import settings
from django.utils import timezone

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="created_coupons"
    )

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}%"

    def is_valid(self):
        return self.active


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
