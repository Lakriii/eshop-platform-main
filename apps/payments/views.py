from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from apps.orders.models import Order, PaymentRecord

class PaymentProcessView(View):
    """Simulácia platby"""
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        if order.status != "pending_payment":
            messages.warning(request, "Túto objednávku už nie je možné zaplatiť.")
            return redirect("orders:order_detail", pk=order.pk)
        return render(request, "payments/payment_page.html", {"order": order})

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        if order.status != "pending_payment":
            messages.warning(request, "Platba už nie je možná.")
            return redirect("orders:order_detail", pk=order.pk)

        # simulácia platby
        order.status = "paid"
        order.save()

        PaymentRecord.objects.create(
            order=order,
            amount=order.total,
            payment_method="simulated",
            status="completed"
        )

        messages.success(request, "Platba úspešná. Ďakujeme!")
        return redirect("payments:payment_success", order_id=order.pk)


class PaymentSuccessView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        return render(request, "payments/payment_success.html", {"order": order})
