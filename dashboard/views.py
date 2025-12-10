from django.views import View
from django.shortcuts import render
from .permissions import RoleRequiredMixin


class DashboardHomeView(RoleRequiredMixin, View):
    allowed_roles = ['zamestnavatel']
    template_name = "dashboard/home.html"

    def get(self, request):
        return render(request, self.template_name)


class OrdersView(RoleRequiredMixin, View):
    allowed_roles = ['zamestnavatel', 'leader', 'employee']
    template_name = "dashboard/orders.html"

    def get(self, request):
        return render(request, self.template_name)


class ProductsView(RoleRequiredMixin, View):
    allowed_roles = ['zamestnavatel', 'leader', 'employee']
    template_name = "dashboard/products.html"

    def get(self, request):
        return render(request, self.template_name)


class CustomersView(RoleRequiredMixin, View):
    allowed_roles = ['zamestnavatel', 'leader']
    template_name = "dashboard/customers.html"

    def get(self, request):
        return render(request, self.template_name)


class ChartsView(RoleRequiredMixin, View):
    allowed_roles = ['zamestnavatel', 'leader']
    template_name = "dashboard/charts.html"

    def get(self, request):
        return render(request, self.template_name)
