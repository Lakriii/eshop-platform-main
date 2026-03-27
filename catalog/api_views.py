from rest_framework import viewsets, permissions
from .models import Product, Category
# Importujeme modely a serializers z aplikácie orders
from orders.models import Order
from orders.serializers import OrderSerializer
from .serializers import ProductSerializer, CategorySerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """API pre produkty"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API pre kategórie"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class OrderViewSet(viewsets.ModelViewSet):
    """API pre objednávky (iba pre prihlásených)"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)