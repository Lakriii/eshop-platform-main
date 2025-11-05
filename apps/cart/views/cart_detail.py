from django.views import View
from django.shortcuts import render
from .cart_core import get_or_create_cart

class CartDetailView(View):
    """Zobrazenie košíka."""
    def get(self, request):
        cart = get_or_create_cart(request)
        total = sum(item.line_total() for item in cart.items.all())
        return render(request, "cart/cart_detail.html", {"cart": cart, "total": total})
