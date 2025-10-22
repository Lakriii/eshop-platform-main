from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib import messages
from .models import Cart, CartItem
from apps.catalog.models import ProductVariant
from apps.orders.models import Order, OrderItem
from apps.orders.forms import CheckoutForm
from apps.orders.models import Order, OrderItem, Coupon


def get_or_create_cart(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            session_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
            for item in session_cart.items.all():
                existing_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    variant=item.variant,
                    defaults={'quantity': item.quantity, 'price': item.price}
                )
                if not created:
                    existing_item.quantity += item.quantity
                    existing_item.save()
            session_cart.delete()
        except Cart.DoesNotExist:
            pass
    else:
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)

    return cart


class CartDetailView(View):
    def get(self, request):
        cart = get_or_create_cart(request)
        total = sum(item.line_total() for item in cart.items.all())
        return render(request, "cart/cart_detail.html", {"cart": cart, "total": total})


class AddToCartView(View):
    def post(self, request, product_id):
        variant = ProductVariant.objects.filter(product_id=product_id).first()
        if not variant:
            messages.error(request, "Produkt nie je k dispozícii.")
            return redirect("catalog")

        cart = get_or_create_cart(request)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={"quantity": 1, "price": variant.get_price()},
        )
        if not created:
            item.quantity += 1
            item.save()
        messages.success(request, f"{variant.product.name} bol pridaný do košíka.")
        return redirect("cart_detail")


class CartItemUpdateView(View):
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        new_qty = int(request.POST.get("quantity", 1))

        if new_qty <= 0:
            item.delete()
            messages.info(request, "🗑️ Položka bola odstránená z košíka.")
        else:
            # kontrola skladu
            stock_qty = getattr(item.variant, "stock", getattr(item.variant, "stock_quantity", 0))
            if new_qty > stock_qty:
                messages.error(request, f"Nedostatok skladom: {item.variant.product.name}. Max: {stock_qty}")
                return redirect("cart_detail")

            item.quantity = new_qty
            item.save()
            messages.success(request, "🔄 Počet kusov bol aktualizovaný.")

        return redirect("cart_detail")


class CartItemRemoveView(View):
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        messages.info(request, "🗑️ Položka bola odstránená z košíka.")
        return redirect("cart_detail")

class CheckoutView(View):
    """Dokončenie objednávky + kupóny + vernostné body."""

    def get(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Váš košík je prázdny.")
            return redirect("cart_detail")

        form = CheckoutForm()
        total = sum(item.line_total() for item in cart.items.all())
        return render(request, "cart/checkout.html", {"cart": cart, "form": form, "total": total})

    def post(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Váš košík je prázdny.")
            return redirect("cart_detail")

        form = CheckoutForm(request.POST)
        if form.is_valid():
            total = sum(item.line_total() for item in cart.items.all())

            # --- Aplikovanie kupónu ---
            coupon_code = form.cleaned_data.get("coupon_code")
            discount = 0
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code, active=True)
                    discount = total * coupon.discount_percentage / 100
                    total -= discount
                    messages.success(request, f"Zľava {coupon.discount_percentage}% bola aplikovaná! (-{discount:.2f}€)")
                except Coupon.DoesNotExist:
                    messages.error(request, "Neplatný alebo neaktívny kupón.")

            # --- Kontrola skladu ---
            for item in cart.items.all():
                stock_qty = item.variant.stock.quantity if hasattr(item.variant, "stock") else item.variant.stock_quantity
                if item.quantity > stock_qty:
                    messages.error(
                        request,
                        f"Nedostatok skladom: {item.variant.product.name}. Max: {stock_qty}"
                    )
                    return redirect("cart_detail")

            # --- Vytvorenie objednávky ---
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                status='pending_payment',
                total=total,
                billing_name=form.cleaned_data['full_name'],
                billing_email=form.cleaned_data['email'],
                billing_phone=form.cleaned_data['phone'],
                billing_address=f"{form.cleaned_data['billing_street']}, "
                                f"{form.cleaned_data['billing_city']} "
                                f"{form.cleaned_data['billing_postcode']} "
                                f"{form.cleaned_data['billing_country']}",
                shipping_address=f"{form.cleaned_data['shipping_street']}, "
                                 f"{form.cleaned_data['shipping_city']} "
                                 f"{form.cleaned_data['shipping_postcode']} "
                                 f"{form.cleaned_data['shipping_country']}",
            )

            # --- Uloženie položiek + odpočet skladu ---
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product_name=item.variant.product.name,
                    sku=item.variant.sku,
                    price=item.price,
                    quantity=item.quantity
                )

                if hasattr(item.variant, "stock"):
                    item.variant.stock.quantity -= item.quantity
                    item.variant.stock.save()
                else:
                    item.variant.stock_quantity = max(item.variant.stock_quantity - item.quantity, 0)
                    item.variant.save()

            # --- Vernostné body ---
            if request.user.is_authenticated:
                profile = request.user.profile  # musíš mať model Profile
                earned_points = int(total // 10)
                profile.loyalty_points += earned_points
                profile.save()
                messages.info(request, f"Získali ste {earned_points} vernostných bodov!")

            cart.items.all().delete()
            messages.success(request, "✅ Objednávka bola vytvorená! Pokračujte k platbe.")

            # 🔧 FIX: použijeme namespace 'payments'
            return redirect("payments:payment_process", order_id=order.pk)

        total = sum(item.line_total() for item in cart.items.all())
        return render(request, "cart/checkout.html", {"cart": cart, "form": form, "total": total})