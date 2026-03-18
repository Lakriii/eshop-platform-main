from cart.models import Cart

def get_or_create_cart(request):
    """
    Pomocná funkcia na získanie alebo vytvorenie košíka zo session.
    """
    cart_id = request.session.get("cart_id")
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create()
            request.session["cart_id"] = cart.id
    else:
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.id
    return cart