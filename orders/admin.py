from django.contrib import admin
from .models import Order, OrderItem, Coupon, CouponUsage, PaymentRecord

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Pole 'product' je teraz v poriadku vďaka related_name v modeli
    readonly_fields = ('price',) 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('billing_name', 'billing_email', 'id')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'active', 'valid_from', 'valid_to')
    list_filter = ('active', 'valid_from', 'valid_to')
    search_fields = ('code',)

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'used_at')
    list_filter = ('used_at',)
    readonly_fields = ('used_at',)

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('order', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)