from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.catalog.models import ProductVariant
from .models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.payments.services import create_payment_intent


class CartView(APIView):
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key
        )
        items = [
            {'id': it.id, 'sku': it.variant.sku, 'qty': it.quantity, 'price': str(it.price)}
            for it in cart.items.select_related('variant')
        ]
        return Response({'id': cart.id, 'items': items})


class CartItemAddView(APIView):
    def post(self, request):
        variant_id = request.data.get('variant_id')
        qty = int(request.data.get('quantity', 1))
        variant = get_object_or_404(ProductVariant, pk=variant_id)

        cart, _ = Cart.objects.get_or_create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key
        )
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={'quantity': qty, 'price': variant.get_price()}
        )
        if not created:
            item.quantity += qty
            item.save()

        return Response({'ok': True})


class CheckoutView(APIView):
    @transaction.atomic
    def post(self, request):
        cart = get_object_or_404(Cart, pk=request.data.get('cart_id'))

        order = Order.objects.create(user=cart.user, status='pending_payment')

        total_cents = 0
        for it in cart.items.select_related('variant'):
            price = it.price
            OrderItem.objects.create(
                order=order,
                product_name=it.variant.product.name,
                sku=it.variant.sku,
                price=price,
                quantity=it.quantity
            )
            total_cents += int(price * 100) * it.quantity

        order.total = total_cents / 100
        order.save()

        pi = create_payment_intent(
            amount_cents=total_cents,
            currency='EUR',
            metadata={'order_id': order.id}
        )
        return Response({'client_secret': pi.client_secret})
