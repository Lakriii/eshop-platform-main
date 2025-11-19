from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from orders.models import Coupon


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "Nemáte oprávnenie na prístup k tejto sekcii.")
        return redirect("home")


class CouponListView(StaffRequiredMixin, ListView):
    model = Coupon
    template_name = "orders/coupon_list.html"
    context_object_name = "coupons"


class CouponCreateView(StaffRequiredMixin, CreateView):
    model = Coupon
    fields = ["code", "discount_percentage", "active", "valid_from", "valid_to", "max_uses_total", "max_uses_per_user"]
    template_name = "orders/coupon_form.html"
    success_url = reverse_lazy("orders:coupon_list")

    def form_valid(self, form):
        messages.success(self.request, f"Kupón {form.instance.code} bol pridaný.")
        return super().form_valid(form)


class CouponUpdateView(StaffRequiredMixin, UpdateView):
    model = Coupon
    fields = ["code", "discount_percentage", "active", "valid_from", "valid_to", "max_uses_total", "max_uses_per_user"]
    template_name = "orders/coupon_form.html"
    success_url = reverse_lazy("orders:coupon_list")

    def form_valid(self, form):
        messages.success(self.request, f"Kupón {form.instance.code} bol upravený.")
        return super().form_valid(form)


@login_required
def apply_coupon(request):
    code = request.POST.get("coupon_code") or request.POST.get("code")
    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        messages.error(request, "❌ Neplatný kupón.")
        return redirect("cart:cart_detail")

    if not coupon.is_valid(request.user):
        messages.error(request, "⏰ Kupón vypršal, je neaktívny alebo už bol použitý.")
        return redirect("cart:cart_detail")

    coupon.used_by.add(request.user)
    request.session["coupon_id"] = coupon.id
    messages.success(request, f"🎉 Kupón '{coupon.code}' bol úspešne uplatnený!")
    return redirect("cart:cart_detail")
