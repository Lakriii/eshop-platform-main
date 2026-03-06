from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Webové rozhranie (pôvodné)
    path('', include('core.urls')),
    path('catalog/', include('catalog.urls')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # API rozhranie pre SwiftUI
    path('api/catalog/', include('catalog.api_urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Servovanie obrázkov (nutné pre Mac/DEBUG)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)