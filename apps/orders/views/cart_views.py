from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib import messages
from apps.cart.models import Cart, CartItem
from apps.catalog.models import ProductVariant

def get_or_create_cart(request):
    cart_id = request.session.get("cart_id")
    if cart_id:
        cart, _ = Cart.objects.get_or_create(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.id
    return cart


class CartDetailView(View):
    def get(self, request):
        cart = get_or_create_cart(request)
        total = sum(item.line_total() for item in cart.items.all())
        return render(request, "cart/cart_detail.html", {"cart": cart, "total": total})


class AddToCartView(View):
    def post(self, request, product_id):
        variant_id = request.POST.get("variant_id")
        quantity = int(request.POST.get("quantity", 1))
        variant = get_object_or_404(ProductVariant, id=variant_id)

        if variant.available_stock <= 0:
            messages.error(request, f"Variant {variant.sku} nie je dostupný.")
            return redirect("catalog:product_detail", slug=variant.product.slug)
        if quantity > variant.available_stock:
            messages.error(request, f"Nedostatok tovaru. Max dostupné: {variant.available_stock}.")
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
        new_qty = int(request.POST.get("quantity", 1))
        if new_qty <= 0:
            item.delete()
            messages.info(request, "🗑️ Položka bola odstránená z košíka.")
        else:
            stock_qty = item.variant.available_stock
            if new_qty > stock_qty:
                messages.error(request, f"Nedostatok skladom: {item.variant.product.name}. Max: {stock_qty}")
            else:
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
