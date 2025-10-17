from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order, OrderItem

class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        # Ak je používateľ prihlásený, zobraziť jeho objednávky
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user).order_by('-created_at')
        return Order.objects.none()
