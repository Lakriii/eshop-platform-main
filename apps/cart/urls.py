# apps/cart/urls.py
from django.urls import path
from .views import (
    CartDetailView, 
    AddToCartView, 
    CartItemUpdateView, 
    CartItemRemoveView, 
    CheckoutView
)

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart_detail'),
    path('add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('update/<int:item_id>/', CartItemUpdateView.as_view(), name='cart_item_update'),
    path('remove/<int:item_id>/', CartItemRemoveView.as_view(), name='cart_item_remove'),
    path('checkout/', CheckoutView.as_view(), name='cart_checkout'),
]
