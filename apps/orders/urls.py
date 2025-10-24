from django.urls import path
from .views import OrderDetailView, OrderListView, PaymentView, ThankYouView

app_name = "orders"

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('payment/<int:pk>/', PaymentView.as_view(), name='payment_process'),
    path('thank-you/<int:pk>/', ThankYouView.as_view(), name='thank_you'),
]
