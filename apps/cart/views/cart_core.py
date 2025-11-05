from apps.cart.models import Cart

def get_or_create_cart(request):
    """Vráti existujúci košík alebo vytvorí nový."""
    cart_id = request.session.get("cart_id")
    if cart_id:
        cart, created = Cart.objects.get_or_create(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.id
    return cart
