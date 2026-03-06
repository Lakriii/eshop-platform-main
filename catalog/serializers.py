from rest_framework import serializers
from .models import Product, Category, ProductVariant, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'alt_text']

class ProductVariantSerializer(serializers.ModelSerializer):
    stock_quantity = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'price', 'sku', 'stock_quantity', 'attributes']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'currency', 'is_active',
            'in_stock', 'category_detail', 'variants', 'images'
        ]