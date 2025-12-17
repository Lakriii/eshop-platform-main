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

from weasyprint import HTML, CSS
from django.template.loader import render_to_string

from orders.models import Order

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
# CHARTS VIEW (ZOBRAZENIE GRAFOV NA STRÁNKE)
# -----------------------------
class ChartsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/charts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_14_days = timezone.now().date() - timedelta(days=13)

        # Agregácia objednávok za posledných 14 dní
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

        # --- Vytvorenie grafov do PNG a konverzia do base64 pre HTML ---
        def create_graph_image():
            fig, ax1 = plt.subplots(figsize=(8,4))
            ax1.plot(labels, orders_data, color='#1f77b4', marker='o', label='Objednávky')
            ax1.set_xlabel("Dátum")
            ax1.set_ylabel("Počet objednávok", color='#1f77b4')
            ax1.tick_params(axis='y', labelcolor='#1f77b4')
            ax2 = ax1.twinx()
            ax2.bar(labels, revenue_data, alpha=0.3, color='#ff7f0e', label='Obrat (€)')
            ax2.set_ylabel("Obrat (€)", color='#ff7f0e')
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')

        context["chart_image"] = create_graph_image()
        return context


# -----------------------------
# PDF EXPORT - WEASYPRINT + MATPLOTLIB
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

        # --- Vytvorenie grafu ako obrázok ---
        fig, ax1 = plt.subplots(figsize=(8,4))
        ax1.plot(labels, orders_data, color='#1f77b4', marker='o', label='Objednávky')
        ax1.set_xlabel("Dátum")
        ax1.set_ylabel("Počet objednávok", color='#1f77b4')
        ax1.tick_params(axis='y', labelcolor='#1f77b4')
        ax2 = ax1.twinx()
        ax2.bar(labels, revenue_data, alpha=0.3, color='#ff7f0e', label='Obrat (€)')
        ax2.set_ylabel("Obrat (€)", color='#ff7f0e')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        # --- Vytvorenie HTML pre WeasyPrint ---
        html_string = render_to_string("dashboard/charts_pdf_template.html", {
            "chart_image": chart_base64,
            "report_title": "Fiktívny E-shop Dashboard",
            "report_date": timezone.now()
        })

        pdf_file = HTML(string=html_string).write_pdf(stylesheets=[CSS(string='body { font-family: sans-serif; }')])

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="dashboard_report.pdf"'
        return response
