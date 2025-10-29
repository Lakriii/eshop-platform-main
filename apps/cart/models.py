from django.db import models
from apps.catalog.models import ProductVariant
from apps.orders.models import Order
from django.conf import settings


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)

    # ✅ Oprava chyby - tieto polia automaticky pridajú dátum vytvorenia a aktualizácie
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart #{self.pk} for {self.user.username}"
        return f"Cart #{self.pk} (session: {self.session_key})"

    @property
    def total_price(self):
        """Spočíta celkovú cenu košíka."""
        return sum(item.line_total for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def line_total(self):
        """Cena za daný počet položiek."""
        return self.price * self.quantity

    def __str__(self):
        return f"{self.variant} × {self.quantity} (Cart #{self.cart.pk})"
