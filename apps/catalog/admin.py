from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, Stock

# -------------------
# Kategorie
# -------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


# -------------------
# ProductImage inline
# -------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'order')
    ordering = ('order',)


# -------------------
# ProductVariant inline
# -------------------
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('sku', 'attributes', 'price', 'stock_quantity')


# -------------------
# Product admin
# -------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description', 'short_description')
    inlines = [ProductImageInline, ProductVariantInline]


# -------------------
# Stock admin
# -------------------
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('variant', 'quantity', 'reserved', 'available')
    search_fields = ('variant__sku', 'variant__product__name')
