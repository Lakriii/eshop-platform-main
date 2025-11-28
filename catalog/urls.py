# apps/catalog/urls.py
from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    CategoryDetailView,
    ProductCreateView,
    ProductUpdateView,
)

app_name = "catalog"

urlpatterns = [
    # 1. Zoznam produktov
    path('', ProductListView.as_view(), name='product_list'),

    # 2. STAFF: Create a Edit – MUSIA BYŤ PRED detailom!
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),

    # 3. Detail produktu – až teraz (lebo <slug:slug> je "greedy")
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),

    # 4. Kategórie
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
]