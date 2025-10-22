from django.urls import path
from .views import PaymentProcessView, PaymentSuccessView

app_name = "payments"

urlpatterns = [
    path("<int:order_id>/", PaymentProcessView.as_view(), name="payment_process"),
    path("success/<int:order_id>/", PaymentSuccessView.as_view(), name="payment_success"),
]