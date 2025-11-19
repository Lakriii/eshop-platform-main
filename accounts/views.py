from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.forms import CustomUserCreationForm

# PROFILE
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Môžeš pridať Profile model alebo objednávky
        context["profile"] = getattr(self.request.user, "profile", None)
        return context

# REGISTER
class RegisterView(CreateView):
    template_name = "core/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"Account created for {user.username}!")
        # automatické prihlásenie
        from django.contrib.auth import login
        login(self.request, user)
        return super().form_valid(form)
