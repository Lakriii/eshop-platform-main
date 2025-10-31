from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Order, OrderItem
from .forms import CheckoutForm
from apps.cart.models import Cart


# 🛒 Checkout s vernostnými bodmi
def checkout_view(request):
    cart = Cart(request)
    discount = 0

    if request.method == "POST":
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            # Získanie zľavy podľa bodov
            discount_percentage = form.get_loyalty_discount()
            total = cart.get_total()
            discount_amount = total * (discount_percentage / 100)
            total_after_discount = total - discount_amount

            # Tu môžeš vytvoriť Order a OrderItem z košíka
            # napr. order = Order.objects.create(user=request.user, total=total_after_discount, ...)
            
            messages.success(request, f"Zľava za body: {discount_percentage:.1f}% ({discount_amount:.2f} €)")
            return redirect("payment")  # alebo dokonči objednávku
    else:
        form = CheckoutForm(user=request.user)

    total = cart.get_total()
    if request.user.is_authenticated:
        form.user = request.user
        discount_percentage = form.get_loyalty_discount()
        discount_amount = total * (discount_percentage / 100)
        total_after_discount = total - discount_amount
    else:
        discount_percentage = 0
        discount_amount = 0
        total_after_discount = total

    return render(request, "orders/checkout.html", {
        "form": form,
        "cart": cart,
        "discount": round(discount_amount, 2),
        "total": round(total_after_discount, 2)
    })


# 📄 Detail objednávky
class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"


# 📝 Zoznam objednávok
class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
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
