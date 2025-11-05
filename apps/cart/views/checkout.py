from decimal import Decimal
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.db import transaction
from apps.orders.models import Order, OrderItem, Coupon
from apps.cart.models import Cart
from apps.orders.forms import CheckoutForm
from apps.accounts.models import Profile
from .cart_core import get_or_create_cart


class CheckoutView(View):
    """Dokončenie objednávky + kupóny + vernostné body."""
    template_name = "cart/checkout.html"

    def get(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Váš košík je prázdny.")
            return redirect("cart:cart_detail")

        form = CheckoutForm(user=request.user)
        total = sum(item.line_total() for item in cart.items.all())
        return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

    @transaction.atomic
    def post(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Váš košík je prázdny.")
            return redirect("cart:cart_detail")

        form = CheckoutForm(request.POST, user=request.user)
        total = sum(item.line_total() for item in cart.items.all())

        if not form.is_valid():
            messages.error(request, "Prosím vyplňte všetky povinné polia.")
            return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

        # --- Kupón
        coupon_code = form.cleaned_data.get("coupon_code", "").strip()
        discount = Decimal("0.00")
        coupon = None

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
            except Coupon.DoesNotExist:
                messages.error(request, "❌ Neplatný alebo neaktívny kupón.")
                return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

            # Overenie, či tento používateľ už kupón použil
            if request.user.is_authenticated and coupon.used_by.filter(id=request.user.id).exists():
                messages.warning(request, "⚠️ Tento kupón si už použil.")
                return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

            # Overenie celkového limitu použitia
            if coupon.max_uses_total > 0 and coupon.used_by.count() >= coupon.max_uses_total:
                coupon.active = False
                coupon.save()
                messages.error(request, "❌ Tento kupón už bol použitý maximálny počet krát.")
                return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

            # Aplikácia zľavy
            pct = Decimal(coupon.discount_percentage) / Decimal("100")
            discount = (total * pct).quantize(Decimal("0.01"))
            total -= discount
            messages.success(request, f"🎉 Zľava {coupon.discount_percentage}% aplikovaná (-{discount} €).")

            # Označiť, že tento používateľ kupón použil
            if request.user.is_authenticated:
                coupon.used_by.add(request.user)

            # Ak sa dosiahol limit, deaktivovať kupón
            if coupon.max_uses_total > 0 and coupon.used_by.count() >= coupon.max_uses_total:
                coupon.active = False
                coupon.save()

        # --- Sklad
        for item in cart.items.select_related("variant__stock"):
            stock_qty = getattr(getattr(item.variant, "stock", None), "quantity", getattr(item.variant, "stock_quantity", 0))
            if item.quantity > stock_qty:
                messages.error(request, f"Nedostatok skladom: {item.variant.product.name}. Max: {stock_qty}")
                return redirect("cart:cart_detail")

        # --- Objednávka
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            status='pending_payment',
            total=total,
            billing_name=form.cleaned_data['full_name'],
            billing_email=form.cleaned_data['email'],
            billing_phone=form.cleaned_data['phone'],
            billing_address=f"{form.cleaned_data['billing_street']}, {form.cleaned_data['billing_city']} {form.cleaned_data['billing_postcode']} {form.cleaned_data['billing_country']}",
            shipping_address=f"{form.cleaned_data['shipping_street']}, {form.cleaned_data['shipping_city']} {form.cleaned_data['shipping_postcode']} {form.cleaned_data['shipping_country']}",
            coupon=coupon,
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_name=item.variant.product.name,
                sku=item.variant.sku,
                price=item.price,
                quantity=item.quantity,
            )
            if hasattr(item.variant, "stock") and item.variant.stock:
                item.variant.stock.quantity = max(item.variant.stock.quantity - item.quantity, 0)
                item.variant.stock.save()
            else:
                item.variant.stock_quantity = max(getattr(item.variant, "stock_quantity", 0) - item.quantity, 0)
                item.variant.save()

        # --- Vernostné body
        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            earned_points = int(total // Decimal("10"))
            profile.loyalty_points += earned_points
            profile.save()
            messages.info(request, f"🎁 Získali ste {earned_points} vernostných bodov!")

        # --- Vyprázdniť košík
        cart.items.all().delete()
        request.session["last_order_created_for_cart"] = cart.pk

        messages.success(request, "✅ Objednávka bola úspešne vytvorená. Pokračujte na platbu.")
        return redirect("payments:payment_process", order_id=order.pk)
