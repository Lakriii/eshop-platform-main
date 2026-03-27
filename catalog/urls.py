from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import ProductViewSet, CategoryViewSet

# Namespace pre aplikáciu
app_name = 'catalog'

router = DefaultRouter()
router.register(r'products-api', ProductViewSet, basename='product-api')
router.register(r'categories-api', CategoryViewSet, basename='category-api')

urlpatterns = [
    # Klasické Views
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # API
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='api_register'),
]