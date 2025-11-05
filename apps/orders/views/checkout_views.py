from decimal import Decimal
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.db import transaction
from apps.orders.models import Order, OrderItem, Coupon
from apps.cart.models import Cart
from apps.orders.forms import CheckoutForm
from apps.accounts.models import Profile
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

        form = CheckoutForm(request.POST, user=request.user)
        total = sum(item.line_total() for item in cart.items.all())

        if not form.is_valid():
            messages.error(request, "Prosím vyplňte všetky povinné polia.")
            return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

        coupon_code = form.cleaned_data.get("coupon_code", "").strip()
        discount_amount = Decimal("0.00")
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
                if not coupon.is_valid(request.user):
                    raise Coupon.DoesNotExist
                discount_amount = (total * Decimal(coupon.discount_percentage) / Decimal("100")).quantize(Decimal("0.01"))
                total -= discount_amount
                coupon.used_by.add(request.user)
                messages.success(request, f"🎟️ Zľava {coupon.discount_percentage}% (-{discount_amount} €) aplikovaná.")
            except Coupon.DoesNotExist:
                messages.error(request, "Neplatný alebo neaktívny kupón.")
                return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            status="pending_payment",
            total=total,
            billing_name=form.cleaned_data['full_name'],
            billing_email=form.cleaned_data['email'],
            billing_phone=form.cleaned_data['phone'],
            billing_address=f"{form.cleaned_data['billing_street']}, {form.cleaned_data['billing_city']} {form.cleaned_data['billing_postcode']} {form.cleaned_data['billing_country']}",
            shipping_address=f"{form.cleaned_data['shipping_street']}, {form.cleaned_data['shipping_city']} {form.cleaned_data['shipping_postcode']} {form.cleaned_data['shipping_country']}",
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_name=item.variant.product.name,
                sku=item.variant.sku,
                price=item.price,
                quantity=item.quantity
            )
            if hasattr(item.variant, "stock") and item.variant.stock:
                item.variant.stock.quantity -= item.quantity
                item.variant.stock.save()

        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            profile.loyalty_points += int(total // Decimal("10"))
            profile.save()

        cart.items.all().delete()
        messages.success(request, "✅ Objednávka bola vytvorená! Pokračujte k platbe.")
        return redirect("payments:payment_process", order_id=order.pk)
