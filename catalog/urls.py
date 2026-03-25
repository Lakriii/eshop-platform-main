from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

# Importujeme tvoje existujúce views + RegisterView
from .views import (
    ProductListView,
    ProductDetailView,
    CategoryDetailView,
    ProductCreateView,
    ProductUpdateView,
    RegisterView,  # <--- TENTO IMPORT MUSÍŠ PRIDAŤ
)
from .api_views import ProductViewSet, CategoryViewSet

app_name = "catalog"

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = [
    # 1. API endpointy
    path('api/', include(router.urls)),
    
    # --- PRIDANÉ ENDPOINTY PRE MOBILNÚ APP ---
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # -----------------------------------------

    # 2. Klasické Webové zobrazenia (HTML)
    path('', ProductListView.as_view(), name='product_list'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
]