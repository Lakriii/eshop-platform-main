from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Klasické webové rozhranie (HTML šablóny)
    path('', include('core.urls')),
    path('catalog/', include('catalog.urls')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # 2. API rozhranie pre SwiftUI
    # DÔLEŽITÉ: Ak Xcode volá "catalog/api/products", prefix musí byť "catalog/"
    path('catalog/api/', include('catalog.urls')), # Tento riadok prepojí router z catalog/urls.py
    
    # Auth API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Servovanie obrázkov (nutné pre vývoj)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)