from rest_framework import serializers
from .models import Product, Category, ProductVariant

# -------------------------
# Product Variant Serializer
# -------------------------
class ProductVariantSerializer(serializers.ModelSerializer):
    # Dynamicky získame názov hlavného produktu
    name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'price', 'stock_quantity']

# -------------------------
# Product Serializer
# -------------------------
class ProductSerializer(serializers.ModelSerializer):
    # Jeden produkt môže mať viacero variantov
    variants = ProductVariantSerializer(many=True, read_only=True)
    # Zobrazíme názov kategórie namiesto celého objektu
    category_name = serializers.CharField(source='category.name', read_only=True)
    # Pre filter podľa kategórie bude užitočné mať ID aj nested objekt
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'currency', 'is_active',
            'in_stock', 'category_name', 'category', 'variants'
        ]

    def get_category(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name
            }
        return None

# -------------------------
# Category Serializer
# -------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']