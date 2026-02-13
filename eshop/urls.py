"""
URL configuration for eshop project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# IMPORTUJEME VIEWS Z TVOJEJ API ZLOŽKY
from api import views as api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- WEBOVÉ URL (KLASICKÉ DJANGO STRÁNKY) ---
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    path('', include('core.urls')),
    path('catalog/', include('catalog.urls')),  # web katalóg
    path("cart/", include("cart.urls", namespace="cart")),
    path("orders/", include(("orders.urls", "orders"), namespace="orders")),
    path("payments/", include("payments.urls", namespace="payments")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("api/", include("api.urls")),

    # --- API URL (PRE SWIFTUI APP) ---
    # Tvoje existujúce katalógové API
    path('api/catalog/', include('catalog.api_urls', namespace='catalog_api')),

    # JWT TOKEN ENDPOINTY (Login a Refresh)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # TESTOVACÍ ENDPOINT (Pre overenie, či JWT v SwiftUI funguje)
    # Tento riadok vyrieši chybu AttributeError v pytest
    path('api/test-auth/', api_views.test_auth, name='test_auth'),
]

# Obsluha statických súborov a obrázkov (Media)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)