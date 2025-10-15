# apps/catalog/forms.py
from django import forms
from .models import Product, ProductImage
from django.forms.models import inlineformset_factory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'short_description',
            'price', 'currency', 'category', 'is_active'
        ]

# Inline formset pre obrázky
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=('image', 'alt_text', 'order'),
    extra=1,
    can_delete=True
)
