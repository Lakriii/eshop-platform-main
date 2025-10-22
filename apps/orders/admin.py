from django.contrib import admin
from .models import Order, OrderItem, PaymentRecord, Coupon

# Inline pre položky objednávky
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'sku', 'price', 'quantity', 'line_total')
    
    def line_total(self, obj):
        return obj.line_total()
    line_total.short_description = "Celkom"

# Inline pre platby
class PaymentRecordInline(admin.TabularInline):
    model = PaymentRecord
    extra = 0
    readonly_fields = ('amount', 'payment_method', 'status', 'created_at')

# Hlavný admin pre objednávky
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'billing_name', 'billing_email')
    inlines = [OrderItemInline, PaymentRecordInline]

# Admin pre kupóny
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'active')
    list_filter = ('active',)
    search_fields = ('code',)
