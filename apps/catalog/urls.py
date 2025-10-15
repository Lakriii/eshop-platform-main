from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    CategoryDetailView,
    ProductCreateView,
    ProductUpdateView
)

urlpatterns = [
    path('', ProductListView.as_view(), name='catalog'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
]
