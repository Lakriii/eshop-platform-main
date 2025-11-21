# cart/urls.py
from django.urls import path
from .views.cart_detail import CartDetailView
from .views.cart_items import AddToCartView, CartItemUpdateView, CartItemRemoveView
from .views.checkout import CheckoutView

app_name = "cart"

urlpatterns = [
    path("", CartDetailView.as_view(), name="cart_detail"),
    path("add/<int:product_id>/", AddToCartView.as_view(), name="add_to_cart"),
    path("update/<int:item_id>/", CartItemUpdateView.as_view(), name="cart_item_update"),   # ← toto musí byť!
    path("remove/<int:item_id>/", CartItemRemoveView.as_view(), name="cart_item_remove"),   # ← toto musí byť!
    path("checkout/", CheckoutView.as_view(), name="checkout"),
]

