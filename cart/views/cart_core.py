# cart/views/cart_core.py
from cart.models import Cart

def get_or_create_cart(request):
    cart_id = request.session.get("cart_id")
    if cart_id:
        try:
            return Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            pass

    user = request.user if request.user.is_authenticated else None
    cart = Cart.objects.create(user=user)
    request.session["cart_id"] = cart.pk
    request.session.save()
    return cart

