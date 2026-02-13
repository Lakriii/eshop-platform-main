from django.contrib import admin
from django.urls import path
from api import views  # Stačí jeden čistý import
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # 1. Administrácia Django
    path('admin/', admin.site.urls),

    # 2. JWT Autentifikácia (Login a Refresh)
    # Ak používaš vlastný View (napr. MyTokenObtainPairView), daj ho sem. 
    # Ak nie, nechaj TokenObtainPairView.as_view()
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 3. Používateľské funkcie (Registrácia a Profil)
    path('api/register/', views.register_user, name='register'),
    path('user-profile/', views.get_user_profile, name='user_profile'),

    # 4. Testovacia cesta pre Swift
    path('test-auth/', views.test_auth, name='test_auth'),
]