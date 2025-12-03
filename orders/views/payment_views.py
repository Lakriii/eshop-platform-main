from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from orders.models import Order


class PaymentView(View):
    template_name = "orders/payment.html"

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.status != "pending_payment":
            messages.warning(request, "Táto objednávka už bola zaplatená alebo zrušená.")
            return redirect("orders:order_detail", pk=order.pk)
        return render(request, self.template_name, {"order": order})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.status != "pending_payment":
            messages.warning(request, "Platbu už nie je možné spracovať.")
            return redirect("orders:order_detail", pk=order.pk)

        order.status = "paid"
        order.save()
        messages.success(request, "Platba bola úspešná. Ďakujeme za objednávku!")
        return redirect("orders:thank_you", pk=order.pk)


class ThankYouView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/thank_you.html"
    context_object_name = "order"

    def get_object(self):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        if order.user != self.request.user and not self.request.user.is_staff:
            messages.error(self.request, "Nemáte oprávnenie zobraziť túto stránku.")
            return redirect("orders:order_list")
        return order