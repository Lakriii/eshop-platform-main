from django.urls import path
from .views import PaymentProcessView, PaymentSuccessView

urlpatterns = [
    path("<int:order_id>/", PaymentProcessView.as_view(), name="payment_page"),
    path("success/<int:order_id>/", PaymentSuccessView.as_view(), name="payment_success"),
]