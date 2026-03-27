from django.contrib import admin
from .models import Category, Product, ProductVariant, ProductImage, Stock

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class StockInline(admin.StackedInline):
    model = Stock
    can_delete = False

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_active']
    list_filter = ['is_active', 'category']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    # OPRAVA: stock_quantity nahradené metódou get_stock
    list_display = ['product', 'sku', 'price', 'get_stock']
    inlines = [StockInline]

    @admin.display(description='Skladom')
    def get_stock(self, obj):
        return obj.stock.quantity if hasattr(obj, 'stock') else 0

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['variant', 'quantity', 'reserved', 'available']