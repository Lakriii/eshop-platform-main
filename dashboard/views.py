# dashboard/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from orders.models import Order


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"


class OrdersView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/orders.html"


class ProductsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/products.html"


class CustomersView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/customers.html"


class ChartsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/charts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orders_by_day = (
            Order.objects
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(
                orders_count=Count("id"),
                total_revenue=Sum("total")
            )
            .order_by("day")
        )

        # pre graf 1 – počet objednávok
        context["labels"] = [o["day"].strftime("%d.%m.%Y") for o in orders_by_day]
        context["orders_data"] = [o["orders_count"] for o in orders_by_day]

        # pre graf 2 – tržby
        context["revenue_data"] = [
            float(o["total_revenue"] or 0) for o in orders_by_day
        ]

        return context
