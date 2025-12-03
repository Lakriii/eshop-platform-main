from django.urls import path
from . import views


app_name = "dashboard"


urlpatterns = [
path('', views.DashboardHomeView.as_view(), name='home'),
path('orders/', views.OrdersView.as_view(), name='orders'),
path('products/', views.ProductsView.as_view(), name='products'),
path('customers/', views.CustomersView.as_view(), name='customers'),
path('charts/', views.ChartsView.as_view(), name='charts'),
]