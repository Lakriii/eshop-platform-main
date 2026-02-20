from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CustomAuthToken
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.register_user, name='register'),
    path('login/', CustomAuthToken.as_view(), name='api_login'),
    path('profile/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    path('checkout/simulate/', views.simulate_checkout, name='simulate_checkout'),
    path('test-auth/', views.test_auth, name='test_auth'),
]