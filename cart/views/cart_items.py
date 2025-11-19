from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from catalog.models import ProductVariant
from cart.models import CartItem
from .cart_core import get_or_create_cart

class AddToCartView(View):
    def post(self, request, product_id):
        variant_id = request.POST.get("variant_id")
        quantity = int(request.POST.get("quantity", 1))

        variant = get_object_or_404(ProductVariant, id=variant_id)
        available = variant.available_stock

        if available <= 0:
            messages.error(request, f"Variant {variant.sku} nie je momentálne dostupný.")
            return redirect("catalog:product_detail", slug=variant.product.slug)

        if quantity > available:
            messages.error(request, f"Nedostatok tovaru. Max dostupné: {available}.")
            return redirect("catalog:product_detail", slug=variant.product.slug)

        cart = get_or_create_cart(request)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={"quantity": quantity, "price": variant.get_price()},
        )
        if not created:
            item.quantity += quantity
            item.save()

        messages.success(request, f"{variant.product.name} ({variant.sku}) bol pridaný do košíka.")
        return redirect("cart:cart_detail")


class CartItemUpdateView(View):
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
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        messages.info(request, "🗑️ Položka bola odstránená z košíka.")
        return redirect("cart:cart_detail")
