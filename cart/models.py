# cart/models.py
from django.db import models
from django.conf import settings
from decimal import Decimal


class Cart(models.Model):
    # NAJLEPŠÍ A JEDINÝ SPRÁVNY SPÔSOB V DJANGO
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="carts",  # voliteľné, ale dobré
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.line_total() for item in self.items.all())

    def __str__(self):
        return f"Cart #{self.pk} for {self.user or 'guest'}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def line_total(self):
        return Decimal(self.price) * self.quantity

    def __str__(self):
        return f"{self.variant} × {self.quantity}"