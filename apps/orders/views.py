from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.shortcuts import get_object_or_404, render, redirect
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
        # Ak je používateľ prihlásený, zobrazí jeho objednávky
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user).order_by('-created_at')
        return Order.objects.none()


# 🟢 Simulovaná platba
class PaymentView(View):
    template_name = "orders/payment.html"

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.status != "pending_payment":
            messages.warning(request, "Táto objednávka už bola zaplatená alebo zrušená.")
            return redirect("order_detail", pk=order.pk)

        return render(request, self.template_name, {"order": order})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.status != "pending_payment":
            messages.warning(request, "Platbu už nie je možné spracovať.")
            return redirect("order_detail", pk=order.pk)

        # Simulácia úspešnej platby
        order.status = "paid"
        order.save()

        messages.success(request, "✅ Platba bola úspešne spracovaná. Ďakujeme za objednávku!")
        return redirect("thank_you", pk=order.pk)


# 🟣 Stránka „Ďakujeme za objednávku“
class ThankYouView(TemplateView):
    template_name = "orders/thank_you.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(Order, pk=self.kwargs.get("pk"))
        context["order"] = order
        return context
