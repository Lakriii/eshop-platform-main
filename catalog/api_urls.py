from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ProductViewSet, CategoryViewSet, CartViewSet, OrderViewSet

app_name = 'catalog_api'

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')
router.register('cart', CartViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]