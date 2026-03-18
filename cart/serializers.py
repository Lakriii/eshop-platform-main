from rest_framework import serializers
from .models import Cart, CartItem
# Order nepatrí do cart.models! Ak ho tu potrebuješ, importuj ho z orders:
from orders.models import Order 

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']