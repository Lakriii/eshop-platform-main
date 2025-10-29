from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib import messages
from .models import Cart, CartItem
from apps.catalog.models import ProductVariant
from apps.orders.models import Order, OrderItem, Coupon
from apps.orders.forms import CheckoutForm
from django.db import transaction


def get_or_create_cart(request):
    """Získa alebo vytvorí košík pre session alebo prihláseného užívateľa."""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Zlúčenie session košíka s používateľským
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
    """Zobrazenie košíka."""
    def get(self, request):
        cart = get_or_create_cart(request)
        total = sum(item.line_total() for item in cart.items.all())
        return render(request, "cart/cart_detail.html", {"cart": cart, "total": total})


class AddToCartView(View):
    """Pridanie produktu do košíka."""
    def post(self, request, product_id):
        variant = ProductVariant.objects.filter(product_id=product_id).first()
        if not variant:
            messages.error(request, "Produkt nie je k dispozícii.")
            return redirect("catalog:product_list")

        # ✅ Kontrola, či je produkt skladom
        stock_qty = getattr(getattr(variant, "stock", None), "quantity", getattr(variant, "stock_quantity", 0))
        if stock_qty <= 0:
            messages.error(request, f"❌ Produkt '{variant.product.name}' je vypredaný.")
            return redirect("catalog:product_list")

        cart = get_or_create_cart(request)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={"quantity": 1, "price": variant.get_price()},
        )

        if not created:
            if item.quantity + 1 > stock_qty:
                messages.warning(request, f"⚠️ Nedostatok na sklade. Max: {stock_qty} ks.")
            else:
                item.quantity += 1
                item.save()
                messages.success(request, f"{variant.product.name} bol pridaný do košíka.")
        else:
            messages.success(request, f"{variant.product.name} bol pridaný do košíka.")

        return redirect("cart:cart_detail")


class CartItemUpdateView(View):
    """Aktualizácia počtu kusov v košíku."""
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)

        try:
            new_qty = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            new_qty = item.quantity

        if new_qty <= 0:
            item.delete()
            messages.info(request, "🗑️ Položka bola odstránená z košíka.")
        else:
            stock_qty = getattr(getattr(item.variant, "stock", None), "quantity", getattr(item.variant, "stock_quantity", 0))
            if new_qty > stock_qty:
                messages.error(request, f"Nedostatok skladom: {item.variant.product.name}. Max: {stock_qty}")
                return redirect("cart:cart_detail")

            item.quantity = new_qty
            item.save()
            messages.success(request, "🔄 Počet kusov bol aktualizovaný.")

        return redirect("cart:cart_detail")


class CartItemRemoveView(View):
    """Odstránenie položky z košíka."""
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        messages.info(request, "🗑️ Položka bola odstránená z košíka.")
        return redirect("cart:cart_detail")


class CheckoutView(View):
    """Dokončenie objednávky + kupóny + vernostné body."""
    def get(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Váš košík je prázdny.")
            return redirect("cart:cart_detail")

        form = CheckoutForm()
        total = sum(item.line_total() for item in cart.items.all())
        return render(request, "cart/checkout.html", {"cart": cart, "form": form, "total": total})

    @transaction.atomic
    def post(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Váš košík je prázdny.")
            return redirect("cart:cart_detail")

        form = CheckoutForm(request.POST)
        total = sum(item.line_total() for item in cart.items.all())

        if not form.is_valid():
            messages.error(request, "Prosím vyplňte všetky povinné polia.")
            return render(request, "cart/checkout.html", {"cart": cart, "form": form, "total": total})

        # ✅ Kupón
        coupon_code = form.cleaned_data.get("coupon_code", "").strip()
        discount = Decimal("0.00")
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
                pct = Decimal(coupon.discount_percentage) / Decimal("100")
                discount = (total * pct).quantize(Decimal("0.01"))
                total = (total - discount).quantize(Decimal("0.01"))
                messages.success(request, f"Zľava {coupon.discount_percentage}% aplikovaná (-{discount} €).")
                coupon.active = False
                coupon.save()
            except Coupon.DoesNotExist:
                messages.error(request, "Neplatný alebo neaktívny kupón.")
                return render(request, "cart/checkout.html", {"cart": cart, "form": form, "total": total})

        # ✅ Kontrola skladu pred objednávkou
        for item in cart.items.select_related("variant__stock"):
            stock_qty = getattr(getattr(item.variant, "stock", None), "quantity", getattr(item.variant, "stock_quantity", 0))
            if item.quantity > stock_qty:
                messages.error(request, f"Nedostatok skladom: {item.variant.product.name}. Max: {stock_qty}")
                return redirect("cart:cart_detail")

        # ✅ Vytvorenie objednávky
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            status='pending_payment',
            total=total,
            billing_name=form.cleaned_data['full_name'],
            billing_email=form.cleaned_data['email'],
            billing_phone=form.cleaned_data['phone'],
            billing_address=f"{form.cleaned_data['billing_street']}, {form.cleaned_data['billing_city']} {form.cleaned_data['billing_postcode']} {form.cleaned_data['billing_country']}",
            shipping_address=f"{form.cleaned_data['shipping_street']}, {form.cleaned_data['shipping_city']} {form.cleaned_data['shipping_postcode']} {form.cleaned_data['shipping_country']}",
        )

        # ✅ Uloženie položiek a odpočet skladu
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

        # ✅ Vernostné body
        if request.user.is_authenticated and hasattr(request.user, "profile"):
            earned_points = int(total // Decimal("10"))
            request.user.profile.loyalty_points += earned_points
            request.user.profile.save()
            messages.info(request, f"🎁 Získali ste {earned_points} vernostných bodov!")

        # ✅ Vyprázdniť košík
        cart.items.all().delete()
        request.session["last_order_created_for_cart"] = cart.pk

        messages.success(request, "✅ Objednávka bola úspešne vytvorená. Pokračujte na platbu.")
        return redirect("payments:payment_process", order_id=order.pk)
