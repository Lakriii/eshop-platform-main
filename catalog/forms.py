from django import forms
from .models import Product, ProductImage
from django.forms.models import inlineformset_factory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 
            'price', 'category', 'is_active'
        ]
        # Odstránené: short_description, currency (neexistujú v modely)

# Inline formset pre obrázky
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=('image', 'is_main'), # Upravené podľa modelu
    extra=1,
    can_delete=True
)