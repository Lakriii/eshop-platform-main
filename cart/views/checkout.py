# cart/views/checkout.py
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from orders.models import Order, OrderItem
from .cart_core import get_or_create_cart


class CheckoutView(TemplateView):
    template_name = "cart/checkout.html"

    def dispatch(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.error(request, "Košík je prázdny.")
            return redirect("cart:cart_detail")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)

        # Bezpečnostná kontrola
        if not cart.items.exists():
            return redirect("cart:cart_detail")

        # Vytvoríme objednávku – toto test očakáva
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.POST.get("full_name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            billing_street=request.POST.get("billing_street"),
            billing_city=request.POST.get("billing_city"),
            billing_postcode=request.POST.get("billing_postcode"),
            billing_country=request.POST.get("billing_country"),
            shipping_street=request.POST.get("shipping_street", request.POST.get("billing_street")),
            shipping_city=request.POST.get("shipping_city", request.POST.get("billing_city")),
            shipping_postcode=request.POST.get("shipping_postcode", request.POST.get("billing_postcode")),
            shipping_country=request.POST.get("shipping_country", request.POST.get("billing_country")),
            total_price=cart.total_price,
            status="new",
        )

        # Prenesieme položky
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                quantity=item.quantity,
                price=item.variant.price,  # alebo item.price, podľa tvojho modelu
            )

        # Vyprázdnime košík
        cart.items.all().delete()
        request.session.pop("cart_id", None)

        messages.success(request, f"Objednávka #{order.id} bola vytvorená!")
        return redirect("cart:cart_detail")