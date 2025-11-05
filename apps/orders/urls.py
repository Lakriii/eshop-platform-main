from django.urls import path
from .views import OrderDetailView, OrderListView, PaymentView, ThankYouView
from . import views

app_name = "orders"

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('payment/<int:pk>/', PaymentView.as_view(), name='payment_process'),
    path('thank-you/<int:pk>/', ThankYouView.as_view(), name='thank_you'),
    path("employee/coupons/", OrderListView.as_view(), name="employee_coupons"),
    path("coupons/", views.CouponListView.as_view(), name="coupon_list"),
    path("coupons/add/", views.CouponCreateView.as_view(), name="coupon_add"),
    path("coupons/<int:pk>/edit/", views.CouponUpdateView.as_view(), name="coupon_edit"),
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
]
