from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from catalog.models import Product, Category
from cart.models import Cart, CartItem
from orders.models import Order
from .serializers import ProductSerializer, CategorySerializer
from cart.serializers import CartSerializer, OrderSerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    # Dôležité: prefetch_related opravuje tvoj problém s nenčítaním dát
    queryset = Product.objects.filter(is_active=True).prefetch_related('variants', 'images', 'variants__stock')
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def add_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))
        
        item, created = CartItem.objects.get_or_create(
            cart=cart, 
            variant_id=variant_id,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        order = serializer.save(user=self.request.user, total=cart.total_price, status='pending_payment')
        
        for item in cart.items.all():
            order.items.create(
                product=item.variant.product, 
                quantity=item.quantity, 
                price=item.variant.price if item.variant.price else item.variant.product.price
            )
        cart.items.all().delete()