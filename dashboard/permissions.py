# dashboard/permissions.py
from django.shortcuts import render
from django.contrib.auth.mixins import AccessMixin

class RoleRequiredMixin(AccessMixin):
    allowed_roles = []  # napriklad ['zamestnavatel', 'leader']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)
        return self.handle_no_permission()

    def handle_no_permission(self):
        return render(self.request, "dashboard/login_error.html")
