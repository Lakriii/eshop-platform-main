from django.views.generic import DetailView, ListView
from django.contrib import messages
from apps.orders.models import Order

class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"


class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user).order_by("-created_at")
        return Order.objects.none()
