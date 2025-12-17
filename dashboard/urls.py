# dashboard/urls.py
from django.urls import path
from .views import (
    DashboardHomeView, ChartsView, ChartsPdfExportView,
    OrdersView, ProductsView, CustomersView
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="home"),
    path("charts/", ChartsView.as_view(), name="charts"),
    path("charts/export/pdf/", ChartsPdfExportView.as_view(), name="charts_pdf"),
    path("orders/", OrdersView.as_view(), name="orders"),
    path("products/", ProductsView.as_view(), name="products"),
    path("customers/", CustomersView.as_view(), name="customers"),
]
