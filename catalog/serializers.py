from rest_framework import serializers
from .models import Product, Category, ProductVariant

class ProductVariantSerializer(serializers.ModelSerializer):
    # Ak v databáze nemáš stĺpec 'name' v tabuľke ProductVariant, 
    # tento riadok ho vytvorí dynamicky z hlavného produktu:
    name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'price', 'stock']

class ProductSerializer(serializers.ModelSerializer):
    # many=True hovorí, že jeden produkt môže mať viacero variantov (napr. S, M, L)
    variants = ProductVariantSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'is_active', 'category_name', 'variants']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']