from django.contrib import admin
from django.urls import path
from api import views as api_views  # Dôležitý import s aliasom
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Login (Získanie tokenu)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Registrácia
    path('api/register/', api_views.register_user, name='register'),

    # Profil
    path('api/user-profile/', api_views.get_user_profile, name='user_profile'),

    # Testovacia cesta
    path('api/test-auth/', api_views.test_auth, name='test_auth'),
]