from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem, Coupon
from .forms import CheckoutForm
from apps.cart.models import Cart, CartItem
from apps.catalog.models import ProductVariant
from apps.accounts.models import Profile
from django.contrib.auth.decorators import login_required

# 🔹 Pomocná funkcia na získanie alebo vytvorenie košíka
def get_or_create_cart(request):
    cart_id = request.session.get("cart_id")
    if cart_id:
        cart, created = Cart.objects.get_or_create(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.id
    return cart

# 🛒 Zobrazenie košíka
class CartDetailView(View):
    def get(self, request):
        cart = get_or_create_cart(request)
        total = sum(item.line_total() for item in cart.items.all())
        return render(request, "cart/cart_detail.html", {"cart": cart, "total": total})

# ➕ Pridanie produktu do košíka
class AddToCartView(View):
    def post(self, request, product_id):
        variant_id = request.POST.get("variant_id")
        quantity = int(request.POST.get("quantity", 1))
        variant = get_object_or_404(ProductVariant, id=variant_id)
        available = variant.available_stock

        if available <= 0:
            messages.error(request, f"Variant {variant.sku} nie je dostupný.")
            return redirect("catalog:product_detail", slug=variant.product.slug)
        if quantity > available:
            messages.error(request, f"Nedostatok tovaru. Max dostupné: {available}.")
            return redirect("catalog:product_detail", slug=variant.product.slug)

        cart = get_or_create_cart(request)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={"quantity": quantity, "price": variant.get_price()},
        )
        if not created:
            item.quantity += quantity
            item.save()

        messages.success(request, f"{variant.product.name} ({variant.sku}) bol pridaný do košíka.")
        return redirect("cart:cart_detail")

# 🔄 Aktualizácia počtu kusov
class CartItemUpdateView(View):
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        try:
            new_qty = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            new_qty = item.quantity

        if new_qty <= 0:
            item.delete()
            messages.info(request, "🗑️ Položka bola odstránená z košíka.")
        else:
            stock_qty = getattr(getattr(item.variant, "stock", None), "quantity", getattr(item.variant, "stock_quantity", 0))
            if new_qty > stock_qty:
                messages.error(request, f"Nedostatok skladom: {item.variant.product.name}. Max: {stock_qty}")
                return redirect("cart:cart_detail")
            item.quantity = new_qty
            item.save()
            messages.success(request, "🔄 Počet kusov bol aktualizovaný.")
        return redirect("cart:cart_detail")

# 🗑️ Odstránenie položky
class CartItemRemoveView(View):
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        messages.info(request, "🗑️ Položka bola odstránená z košíka.")
        return redirect("cart:cart_detail")

# 💳 Checkout + kupóny + body
class CheckoutView(View):
    template_name = "cart/checkout.html"

    def get(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Váš košík je prázdny.")
            return redirect("cart:cart_detail")

        form = CheckoutForm(user=request.user)
        total = sum(item.line_total() for item in cart.items.all())
        return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

    @transaction.atomic
    def post(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, "Váš košík je prázdny.")
            return redirect("cart:cart_detail")

        form = CheckoutForm(request.POST, user=request.user)
        total = sum(item.line_total() for item in cart.items.all())

        if not form.is_valid():
            messages.error(request, "Prosím vyplňte všetky povinné polia.")
            return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

        # ✅ Aplikovanie kupónu
        coupon_code = form.cleaned_data.get("coupon_code", "").strip()
        discount_amount = Decimal("0.00")
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
                discount_amount = (total * Decimal(coupon.discount_percentage) / 100).quantize(Decimal("0.01"))
                total -= discount_amount
                coupon.active = False
                coupon.save()
                messages.success(request, f"🎟️ Kupón zľava {coupon.discount_percentage}% (-{discount_amount} €) aplikovaná.")
            except Coupon.DoesNotExist:
                messages.error(request, "Neplatný alebo neaktívny kupón.")
                return render(request, self.template_name, {"cart": cart, "form": form, "total": total})

        # ✅ Kontrola skladu
        for item in cart.items.select_related("variant__stock"):
            stock_qty = getattr(getattr(item.variant, "stock", None), "quantity", getattr(item.variant, "stock_quantity", 0))
            if item.quantity > stock_qty:
                messages.error(request, f"Nedostatok skladom: {item.variant.product.name}. Max: {stock_qty}")
                return redirect("cart:cart_detail")

        # ✅ Vytvorenie objednávky
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            status="pending_payment",
            total=total,
            billing_name=form.cleaned_data['full_name'],
            billing_email=form.cleaned_data['email'],
            billing_phone=form.cleaned_data['phone'],
            billing_address=f"{form.cleaned_data['billing_street']}, {form.cleaned_data['billing_city']} {form.cleaned_data['billing_postcode']} {form.cleaned_data['billing_country']}",
            shipping_address=f"{form.cleaned_data['shipping_street']}, {form.cleaned_data['shipping_city']} {form.cleaned_data['shipping_postcode']} {form.cleaned_data['shipping_country']}",
        )

        # ✅ Uloženie položiek objednávky a odpočet skladu
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_name=item.variant.product.name,
                sku=item.variant.sku,
                price=item.price,
                quantity=item.quantity
            )
            if hasattr(item.variant, "stock") and item.variant.stock:
                item.variant.stock.quantity = max(item.variant.stock.quantity - item.quantity, 0)
                item.variant.stock.save()
            else:
                item.variant.stock_quantity = max(getattr(item.variant, "stock_quantity", 0) - item.quantity, 0)
                item.variant.save()

        # ✅ Vernostné body
        if request.user.is_authenticated:
            profile, created = Profile.objects.get_or_create(user=request.user)
            earned_points = int(total // Decimal("10"))
            profile.loyalty_points += earned_points
            profile.save()
            messages.info(request, f"💎 Získali ste {earned_points} vernostných bodov!")

            if form.cleaned_data.get("use_loyalty_points"):
                available_points = profile.loyalty_points
                points_discount_pct = min(available_points // 100 * 10, 50)  # max 50%
                points_discount_amount = (total * points_discount_pct / 100).quantize(Decimal("0.01"))
                total -= points_discount_amount
                profile.loyalty_points -= (points_discount_pct // 10) * 100
                profile.save()
                messages.success(request, f"💰 Použité vernostné body! Zľava {points_discount_pct}% (-{points_discount_amount} €).")

        # ✅ Vyprázdniť košík
        cart.items.all().delete()
        request.session["last_order_created_for_cart"] = cart.pk

        messages.success(request, "✅ Objednávka bola úspešne vytvorená. Pokračujte na platbu.")
        return redirect("payments:payment_process", order_id=order.pk)


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


@login_required
def employee_coupons_view(request):
    # kontrola role – zamestnanec, nie admin
    if not request.user.is_staff or request.user.is_superuser:
        messages.error(request, "Nemáte oprávnenie pre túto stránku.")
        return redirect("home")  # presmerovanie pre bežného používateľa

    if request.method == "POST":
        form = CouponCreateForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.created_by = request.user
            coupon.save()
            messages.success(request, f"Kupón {coupon.code} vytvorený!")
            return redirect("employee_coupons")
    else:
        form = CouponCreateForm()

    coupons = Coupon.objects.all().order_by("-id")
    return render(request, "coupons/employee_coupons.html", {"form": form, "coupons": coupons})
