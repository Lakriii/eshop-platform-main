# catalog/views.py
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Product, Category
from .forms import ProductForm, ProductImageFormSet
from django.views.generic import ListView
from .models import Product, Category
from .filters import ProductFilter  # ← nový import


# --- MIXIN ---
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


# catalog/views.py

class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 24  # pekné 4x6 na stránku

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related("category")

        self.filter = ProductFilter(self.request.GET, queryset=queryset)
        return self.filter.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
        context["categories"] = Category.objects.filter(is_active=True, parent__isnull=False)

        # Pre pekné zobrazenie aktuálnej kategórie ak je filtrovaná
        if self.filter.form['category'].value():
            context["current_category"] = Category.objects.filter(
                id=self.filter.form['category'].value()
            ).first()

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
        product = self.get_object()
        context["variants"] = product.variants.all()
        return context


class CategoryDetailView(ListView):
    model = Product
    template_name = "catalog/category_detail.html"
    context_object_name = "products"

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs["slug"], is_active=True
        )
        return Product.objects.filter(
            category=self.category, is_active=True
        ).select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["subcategories"] = Category.objects.filter(
            parent=self.category, is_active=True
        )

        # KĽÚČOVÁ ZMENA – bezpečný reverse pre šablónu
        # Ak by z nejakého dôvodu chýbal name="product_detail" v urls.py,
        # šablóna sa už nezrúti, len sa odkaz nezobrazí.
        try:
            # Skúsime získať URL pre "dummy" slug – ak name existuje, uložíme ho
            reverse("catalog:product_detail", args=["test"])
            context["product_detail_url_name"] = "catalog:product_detail"
        except Exception:
            # Ak name neexistuje → šablóna použije fallback (# alebo nič)
            context["product_detail_url_name"] = None

        return context


# --- STAFF VIEWS ---
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
            data["images"] = ProductImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
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