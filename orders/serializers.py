from rest_framework import serializers
from .models import Order 
# Ak potrebuješ detaily produktov v objednávke, importuj ich z catalogu:
from catalog.models import Product 

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'