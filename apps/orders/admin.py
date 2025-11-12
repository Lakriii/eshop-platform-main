from django.contrib import admin
from .models import Order, OrderItem, PaymentRecord, Coupon

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total', 'created_at']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity', 'price']  # použijeme existujúce polia

class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'total_amount', 'status', 'created_at']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'active', 'valid_from', 'valid_to', 'max_uses_total', 'max_uses_per_user']
