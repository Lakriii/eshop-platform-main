# cart/views/cart_items.py
from django.views.generic import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from catalog.models import ProductVariant
from cart.models import CartItem
from .cart_core import get_or_create_cart


# TOTO JE CHÝBAJÚCA TRIEDA – BEZ TOHTO VŠETKO PADÁ!
class AddToCartView(View):
    def post(self, request, product_id):
        cart = get_or_create_cart(request)
        variant_id = request.POST.get("variant_id")
        if not variant_id:
            messages.error(request, "Chýba variant produktu.")
            return redirect("catalog:product_detail", product_id=product_id)

        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = int(request.POST.get("quantity", 1))

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={"quantity": quantity, "price": variant.price}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, "Produkt bol pridaný do košíka.")
        return redirect("cart:cart_detail")


class CartItemUpdateView(View):
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        qty = request.POST.get("quantity", "0").strip()

        if not qty.isdigit() or int(qty) <= 0:
            item.delete()
            messages.success(request, "Položka bola odstránená.")
        else:
            item.quantity = int(qty)
            item.save()
            messages.success(request, "Množstvo bolo aktualizované.")

        return redirect("cart:cart_detail")


class CartItemRemoveView(View):
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
        messages.success(request, "Položka bola odstránená z košíka.")
        return redirect("cart:cart_detail")