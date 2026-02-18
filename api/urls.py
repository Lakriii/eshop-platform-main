from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router automaticky vytvorí cesty pre produkty (api/products/ a api/products/ID/)
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    # Produkty a kategórie
    path('', include(router.urls)),
    
    # Používateľské funkcie
    path('register/', views.register_user, name='register'),
    path('profile/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    
    # Objednávky a testy
    path('checkout/simulate/', views.simulate_checkout, name='simulate_checkout'),
    path('test-auth/', views.test_auth, name='test_auth'),
]