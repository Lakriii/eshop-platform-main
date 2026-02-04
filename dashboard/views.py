# dashboard/views.py
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from datetime import timedelta
import matplotlib.pyplot as plt
import io
import base64
import os

from django.conf import settings
from django.template.loader import render_to_string

from orders.models import Order

# Playwright
from playwright.sync_api import sync_playwright


# -----------------------------
# DASHBOARD HOME / PREHĽAD
# -----------------------------
class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        context["total_orders"] = Order.objects.count()
        context["new_orders_today"] = Order.objects.filter(created_at__date=today).count()
        context["total_revenue"] = Order.objects.aggregate(total=Sum('total'))['total'] or 0
        context["total_customers"] = Order.objects.values('user').distinct().count()

        return context


# -----------------------------
# ORDERS / PRODUCTS / CUSTOMERS
# -----------------------------
class OrdersView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/orders.html"


class ProductsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/products.html"


class CustomersView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/customers.html"


# -----------------------------
# CHARTS VIEW (HTML graf)
# -----------------------------
class ChartsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/charts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_14_days = timezone.now().date() - timedelta(days=13)

        orders = (
            Order.objects
            .filter(created_at__date__gte=last_14_days)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'), revenue=Sum('total'))
            .order_by('day')
        )

        labels = [o["day"].strftime("%d.%m.") for o in orders]
        orders_data = [o["count"] for o in orders]
        revenue_data = [float(o["revenue"] or 0) for o in orders]

        # --- Vytvorenie grafu na stránku ---
        def create_graph_image():
            fig, ax1 = plt.subplots(figsize=(8, 4))
            ax1.plot(labels, orders_data, marker='o', label='Objednávky')
            ax2 = ax1.twinx()
            ax2.bar(labels, revenue_data, alpha=0.3, label='Obrat (€)')
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')

        context["chart_image"] = create_graph_image()
        return context


# -----------------------------
# PDF EXPORT (Playwright)
# -----------------------------
class ChartsPdfExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        last_14_days = timezone.now().date() - timedelta(days=13)

        orders = (
            Order.objects
            .filter(created_at__date__gte=last_14_days)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'), revenue=Sum('total'))
            .order_by('day')
        )

        labels = [o["day"].strftime("%d.%m.") for o in orders]
        orders_data = [o["count"] for o in orders]
        revenue_data = [float(o["revenue"] or 0) for o in orders]

        # -------------------------------
        # 1) ULOŽIŤ GRAF DO STATIC
        # -------------------------------
        fig, ax1 = plt.subplots(figsize=(8, 4))
        ax1.plot(labels, orders_data, marker='o', label='Objednávky')
        ax2 = ax1.twinx()
        ax2.bar(labels, revenue_data, alpha=0.3, label='Obrat (€)')
        
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)

        chart_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        html = render_to_string("dashboard/pdf_report.html", {
            "chart_base64": chart_base64,
            "report_title": "Fiktívny E-shop Dashboard",
            "report_date": timezone.now(),
        })


        # -------------------------------
        # 3) GENEROVANIE PDF CEZ PLAYWRIGHT
        # -------------------------------
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html)
            pdf_data = page.pdf(format="A4", print_background=True)
            browser.close()

        # -------------------------------
        # 4) ODPOSLANIE PDF
        # -------------------------------
        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="dashboard_report.pdf"'
        return response
