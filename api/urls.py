"""from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.catalog.views import ProductViewSet
from apps.cart import views as cart_views


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')


urlpatterns = [
path('', include(router.urls)),
path('cart/', cart_views.CartView.as_view(), name='cart'),
path('cart/items/', cart_views.CartItemAddView.as_view(), name='cart-add-item'),
path('checkout/', cart_views.CheckoutView.as_view(), name='checkout'),
]"""