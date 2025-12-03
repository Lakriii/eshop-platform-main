from django.views import View
from django.shortcuts import render
from .permissions import RoleRequiredMixin

class DashboardHomeView(RoleRequiredMixin, View):
    allowed_roles = ['zamestnavatel']  # full access
    def get(self, request):
        return render(request, "dashboard/index.html")

class OrdersView(RoleRequiredMixin, View):
    allowed_roles = ['zamestnavatel', 'leader', 'employee']
    def get(self, request):
        return render(request, "dashboard/orders.html")

class ProductsView(RoleRequiredMixin, View):
    allowed_roles = ['zamestnavatel', 'leader', 'employee']
    def get(self, request):
        return render(request, "dashboard/products.html")

class CustomersView(RoleRequiredMixin, View):
    allowed_roles = ['zamestnavatel', 'leader']
    def get(self, request):
        return render(request, "dashboard/customers.html")

class ChartsView(RoleRequiredMixin, View):
    allowed_roles = ['zamestnavatel', 'leader']
    def get(self, request):
        return render(request, "dashboard/charts.html")
