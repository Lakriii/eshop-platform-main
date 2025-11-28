# cart/views/checkout.py

from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction

from .cart_core import get_or_create_cart
from orders.models import Order, OrderItem


class CheckoutView(View):
    def get(self, request):
        cart = get_or_create_cart(request)
        return render(request, "cart/checkout.html", {"cart": cart})

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)

        if not cart.items.exists():
            messages.error(request, "Košík je prázdny.")
            return redirect("cart:cart_detail")

        # Order používa TENTO model:
        # billing_name, billing_email, billing_phone, billing_address, shipping_address
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,

            billing_name=request.POST.get("billing_name", ""),
            billing_email=request.POST.get("billing_email", ""),
            billing_phone=request.POST.get("billing_phone", ""),
            billing_address=request.POST.get("billing_address", ""),
            shipping_address=request.POST.get("shipping_address", ""),

            total=cart.total_price,      #  <-- tvoje pole = total (nie total_price)
           status="pending_payment",    #  <-- alebo 'draft', podľa toho čo chceš
        )

        # OrderItem v modeli má polia: product, quantity, price
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.variant.product,       # ← tvoje CartItem má product alebo variant? (v teste máš variant)
                quantity=item.quantity,
                price=item.variant.price,   # alebo item.variant.price ak používaš varianty
            )

        # vymazanie košíka
        cart.items.all().delete()
        request.session.pop("cart_id", None)

        messages.success(request, f"Objednávka #{order.id} bola vytvorená!")
        return redirect("cart:cart_detail")
