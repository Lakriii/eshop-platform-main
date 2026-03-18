from rest_framework import serializers
from .models import Product, Category, ProductVariant, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class ProductImageSerializer(serializers.ModelSerializer):
    imagePath = serializers.ImageField(source='image')
    class Meta:
        model = ProductImage
        fields = ['id', 'imagePath', 'alt_text', 'is_main']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'price', 'attributes']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    isActive = serializers.BooleanField(source='is_active')

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'slug', 'isActive', 'category_detail', 'variants', 'images']