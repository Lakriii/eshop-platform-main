# apps/catalog/urls.py
from django.urls import path
from .views import ProductListView, ProductDetailView, CategoryDetailView, ProductCreateView, ProductUpdateView
from . import views

app_name = "catalog"

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),  # <-- List produktov
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
