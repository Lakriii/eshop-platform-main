# apps/cart/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib import messages
from .models import Cart, CartItem
from apps.catalog.models import ProductVariant
from apps.orders.models import Order, OrderItem
from apps.orders.forms import CheckoutForm


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
            if new_qty > item.variant.stock_quantity:
                messages.error(request, f"Nedostatok skladom: {item.variant.product.name}. Max: {item.variant.stock_quantity}")
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
    """Umožní dokončiť objednávku pre prihlásených aj anonymných používateľov."""

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
            # Skontrolujeme sklad
            for item in cart.items.all():
                if item.quantity > item.variant.stock_quantity:
                    messages.error(
                        request,
                        f"Nedostatok skladom: {item.variant.product.name}. Max: {item.variant.stock_quantity}"
                    )
                    return redirect("cart_detail")

            # Vytvorenie objednávky
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                status='pending_payment',
                total=sum(item.line_total() for item in cart.items.all()),
                billing_name=form.cleaned_data['full_name'],
                billing_email=form.cleaned_data['email'],
                billing_phone=form.cleaned_data['phone'],
                billing_address=form.cleaned_data['billing_address'],
                shipping_address=form.cleaned_data['shipping_address'],
            )

            # Uložíme položky a zníženie skladu
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product_name=item.variant.product.name,
                    sku=item.variant.sku,
                    price=item.price,
                    quantity=item.quantity
                )
                item.variant.stock_quantity -= item.quantity
                item.variant.save()

            cart.items.all().delete()

            messages.success(request, "Objednávka vytvorená! Pokračujte k platbe.")
            return redirect("order_detail", pk=order.pk)
        else:
            total = sum(item.line_total() for item in cart.items.all())
            return render(request, "cart/checkout.html", {"cart": cart, "form": form, "total": total})
