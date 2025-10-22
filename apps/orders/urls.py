from django.urls import path
from .views import OrderDetailView, OrderListView

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path("order/<int:pk>/payment/", OrderDetailView.as_view(), name="order_payment"),
    path("order/<int:pk>/thank-you/", OrderDetailView.as_view(), name="order_thank_you"),
]
