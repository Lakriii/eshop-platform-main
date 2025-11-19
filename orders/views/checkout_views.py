from decimal import Decimal
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.db import transaction
from orders.models import Order, OrderItem, Coupon
from cart.models import Cart
from orders.forms import CheckoutForm
from accounts.models import Profile
from .cart_views import get_or_create_cart

class CheckoutView(View):
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

    # Celková suma košíka
    total = sum(item.line_total() for item in cart.items.all())
    
    # Inicializácia formulára s user a cart_total
    form = CheckoutForm(request.POST, user=request.user)
    
    if not form.is_valid():
        messages.error(request, "Prosím vyplňte všetky povinné polia.")
        return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

    discount_amount = Decimal("0.00")
    coupon = None

    # Spracovanie kupónu
    coupon_code = form.cleaned_data.get("coupon_code", "").strip()
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
            success, usage_or_reason = coupon.use_by(request.user)
            if not success:
                messages.error(request, f"Neplatný kupón: {usage_or_reason}")
                return render(request, self.template_name, {"cart": cart, "form": form, "total": total})
            # vypočítanie zľavy z kupónu
            discount_amount = (total * Decimal(coupon.discount_percentage) / Decimal("100")).quantize(Decimal("0.01"))
            total -= discount_amount
            messages.success(request, f"🎟️ Zľava {coupon.discount_percentage}% (-{discount_amount} €) aplikovaná.")
        except Coupon.DoesNotExist:
            messages.error(request, "Neplatný alebo neaktívny kupón.")
            return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

    # Spracovanie vernostných bodov
    loyalty_discount_amount = Decimal("0.00")
    if form.cleaned_data.get("use_loyalty_points") and request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        points_to_use = profile.loyalty_points
        # 1 bod = 0.1%, max 20%
        pct_discount = min(points_to_use * 0.1, 20)
        loyalty_discount_amount = (total * Decimal(pct_discount) / Decimal("100")).quantize(Decimal("0.01"))
        total -= loyalty_discount_amount
        # Odpočítanie bodov
        profile.loyalty_points -= int(points_to_use)
        profile.save()

    # Vytvorenie objednávky
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        status="pending_payment",
        total=total,
        billing_name=form.cleaned_data['full_name'],
        billing_email=form.cleaned_data['email'],
        billing_phone=form.cleaned_data['phone'],
        billing_address=f"{form.cleaned_data['billing_street']}, {form.cleaned_data['billing_city']} {form.cleaned_data['billing_postcode']} {form.cleaned_data['billing_country']}",
        shipping_address=f"{form.cleaned_data['shipping_street']}, {form.cleaned_data['shipping_city']} {form.cleaned_data['shipping_postcode']} {form.cleaned_data['shipping_country']}",
        coupon=coupon,
        used_loyalty_points=int(points_to_use) if request.user.is_authenticated else 0,
    )

    # Vytvorenie položiek objednávky
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.variant.product,
            quantity=item.quantity,
            price=item.price,
        )
        # Aktualizácia skladu
        if hasattr(item.variant, "stock") and item.variant.stock:
            item.variant.stock.quantity -= item.quantity
            item.variant.stock.save()

    # Pridanie nových vernostných bodov za objednávku
    if request.user.is_authenticated:
        profile.loyalty_points += int(total // Decimal("10"))
        profile.save()

    # Vyprázdnenie košíka
    cart.items.all().delete()
    messages.success(request, "✅ Objednávka bola vytvorená! Pokračujte k platbe.")
    return redirect("payments:payment_process", order_id=order.pk)
