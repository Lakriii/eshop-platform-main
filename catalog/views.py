from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Product, Category
from .forms import ProductForm, ProductImageFormSet
# Predpokladám, že máš ProductFilter v filters.py, ak nie, treba ho vytvoriť alebo filter odstrániť
try:
    from .filters import ProductFilter
except ImportError:
    ProductFilter = None

from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer

User = get_user_model()

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related("category")
        if ProductFilter:
            self.filter = ProductFilter(self.request.GET, queryset=queryset)
            return self.filter.qs.distinct().order_by("id")
        return queryset.order_by("id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if ProductFilter:
            context["filter"] = self.filter
            cat_id = self.filter.form['category'].value()
            context["current_category"] = Category.objects.filter(id=cat_id).first() if cat_id else None
        
        context["categories"] = Category.objects.filter(is_active=True)
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["variants"] = self.object.variants.all()
        return context

class CategoryDetailView(ListView):
    model = Product
    template_name = "catalog/category_detail.html"
    context_object_name = "products"

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"], is_active=True)
        return Product.objects.filter(category=self.category, is_active=True).select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["subcategories"] = Category.objects.filter(parent=self.category, is_active=True)
        return context

class ProductCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:product_list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["images"] = ProductImageFormSet(self.request.POST, self.request.FILES)
        else:
            data["images"] = ProductImageFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        images = context["images"]
        self.object = form.save()
        if images.is_valid():
            images.instance = self.object
            images.save()
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:product_list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["images"] = ProductImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data["images"] = ProductImageFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        images = context["images"]
        self.object = form.save()
        if images.is_valid():
            images.instance = self.object
            images.save()
        return super().form_valid(form)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer