import django_filters
from django import forms
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Názov obsahuje',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hľadať podľa názvu...'})
    )

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(is_active=True),
        label='Kategória',
        method='filter_by_category',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Cena od',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'})
    )

    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Cena do',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '9999.99'})
    )

    in_stock = django_filters.BooleanFilter(
        method='filter_in_stock',
        label='Len skladom',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        initial=True,
        widget=forms.HiddenInput()  # vždy len aktívne produkty
    )

    class Meta:
        model = Product
        fields = []

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(variants__stock_quantity__gt=0).distinct()
        return queryset

    def filter_by_category(self, queryset, name, value):
        if value:
            # Hľadaj všetky podkategórie cez parent_id
            sub_ids = Category.objects.filter(parent=value, is_active=True).values_list('id', flat=True)
            return queryset.filter(category__in=[value.id] + list(sub_ids))
        return queryset

