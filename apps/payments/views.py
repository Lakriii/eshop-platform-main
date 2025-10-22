from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from apps.orders.models import Order

class PaymentProcessView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        return render(request, "payments/payment_process.html", {"order": order})

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        order.status = "paid"
        order.save()
        messages.success(request, "✅ Platba bola úspešná. Ďakujeme za vašu objednávku!")
        return redirect("payments:payment_success", order_id=order.pk)


class PaymentSuccessView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        return render(request, "payments/payment_success.html", {"order": order})
