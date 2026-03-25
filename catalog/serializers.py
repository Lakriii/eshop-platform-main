from rest_framework import serializers
from .models import Product, Category, ProductVariant, ProductImage
from django.contrib.auth import get_user_model

User = get_user_model()

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

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        # create_user zostáva rovnaké, len model (User) je teraz ten správny
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user