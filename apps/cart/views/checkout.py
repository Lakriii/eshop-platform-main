# apps/cart/views.py (relevantné časti)
from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib import messages
from django.db import transaction
from apps.catalog.models import ProductVariant
from apps.orders.models import Order, OrderItem, Coupon, CouponUsage
from apps.orders.forms import CheckoutForm
from apps.accounts.models import Profile
from apps.cart.models import Cart, CartItem
from .cart_core import get_or_create_cart
# ... get_or_create_cart, AddToCartView, ... zostáva


class CheckoutView(View):
    def get(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Váš košík je prázdny.")
            return redirect("cart:cart_detail")

        total = sum(item.line_total() for item in cart.items.all())
        form = CheckoutForm(user=request.user if request.user.is_authenticated else None, cart_total=total)
        return render(request, "cart/checkout.html", {"cart": cart, "form": form, "total": total})

    @transaction.atomic
    def post(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Váš košík je prázdny.")
            return redirect("cart:cart_detail")

        total = sum(item.line_total() for item in cart.items.all())
        form = CheckoutForm(request.POST, user=request.user if request.user.is_authenticated else None, cart_total=total)

        if not form.is_valid():
            messages.error(request, "Prosím opravte chyby vo formulári.")
            return render(request, "cart/checkout.html", {"cart": cart, "form": form, "total": total})

        # získaj coupon instance (ak zadaný)
        coupon = form.cleaned_data.get("coupon_instance", None)

        # kontrola skladu
        for item in cart.items.select_related("variant__stock"):
            stock_qty = getattr(getattr(item.variant, "stock", None), "quantity", getattr(item.variant, "stock_quantity", 0))
            if item.quantity > stock_qty:
                messages.error(request, f"Nedostatok skladom: {item.variant.product.name}. Max: {stock_qty}")
                return redirect("cart:cart_detail")

        # vytvorenie objednávky (uložíme coupon fk)
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            status='pending_payment',
            total=total,
            billing_name=form.cleaned_data['full_name'],
            billing_email=form.cleaned_data['email'],
            billing_phone=form.cleaned_data['phone'],
            billing_address=f"{form.cleaned_data['billing_street']}, {form.cleaned_data['billing_city']} {form.cleaned_data['billing_postcode']} {form.cleaned_data['billing_country']}",
            shipping_address=f"{form.cleaned_data['shipping_street']}, {form.cleaned_data['shipping_city']} {form.cleaned_data['shipping_postcode']} {form.cleaned_data['shipping_country']}",
            coupon=coupon if coupon else None,
        )

        # uloženie položiek a odpočet skladu
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_name=item.variant.product.name,
                sku=item.variant.sku,
                price=item.price,
                quantity=item.quantity
            )
            if hasattr(item.variant, "stock") and item.variant.stock:
                item.variant.stock.quantity = max(item.variant.stock.quantity - item.quantity, 0)
                item.variant.stock.save()
            else:
                item.variant.stock_quantity = max(getattr(item.variant, "stock_quantity", 0) - item.quantity, 0)
                item.variant.save()

        # vernostné body: najprv pridať za nákup
        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            earned_points = int(total // Decimal("10"))  # 10 EUR = 1 bod
            profile.loyalty_points += earned_points
            profile.save()
            messages.info(request, f"Získali ste {earned_points} vernostných bodov.")

        # použitie kupónu: označíme ho ako použité pre usera (zaznamenáme CouponUsage)
        if coupon and request.user.is_authenticated:
            used, result = coupon.use_by(request.user)
            if not used:
                # ak sa nepodarilo (napr. limit pre usera), rollback?
                messages.error(request, f"Kupón sa nepodarilo aplikovať: {result}")
            else:
                messages.success(request, f"Kupón {coupon.code} aplikovaný ({coupon.discount_percentage}%).")

        # použitie vernostných bodov (ak zvolené v rámci formu)
        if request.user.is_authenticated and form.cleaned_data.get("use_loyalty_points"):
            profile = Profile.objects.get(user=request.user)
            points = profile.loyalty_points
            # prepočet: 100 bodov -> 10% (1 bod = 0.1%)
            discount_pct = min((points / 100) * Decimal("10"), Decimal("20"))  # max 20%
            # spotrebujeme príslušné body (každých 10% = 100 bodov)
            points_to_consume = int((discount_pct // Decimal("10")) * 100)
            # Ak discount_pct nie je deliteľná 10, skonvertujeme logicky na celek (tu jednoznačná politika)
            profile.loyalty_points = max(profile.loyalty_points - points_to_consume, 0)
            profile.save()
            order.used_loyalty_points = points_to_consume
            order.save()
            messages.success(request, f"Použité vernostné body: {points_to_consume}, zľava: {discount_pct}%.")

        # vyprázdniť košík
        cart.items.all().delete()
        request.session["last_order_created_for_cart"] = cart.pk

        messages.success(request, "Objednávka vytvorená. Pokračujem na platbu.")
        return redirect("payments:payment_process", order_id=order.pk)
