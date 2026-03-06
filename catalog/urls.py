from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ProductViewSet, CategoryViewSet # Uisti sa, že api_views existuje

from .views import (
    ProductListView,
    ProductDetailView,
    CategoryDetailView,
    ProductCreateView,
    ProductUpdateView,
)

app_name = "catalog"

# API Router - toto zabezpečí /api/products/
router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = [
    # 1. API endpointy
    path('api/', include(router.urls)),

    # 2. Klasické Webové zobrazenia (HTML)
    path('', ProductListView.as_view(), name='product_list'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
]