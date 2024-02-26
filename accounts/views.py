from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login

from .forms import CustomSignupForm
from accounts.models import User


# HOME
class HomeView(TemplateView):
    template_name = 'home.html'


# -----------------
# BUILT IN ACCOUNTS

class RegistrationView(FormView):
    template_name = 'registration/signup.html'
    form_class = CustomSignupForm
    success_url = reverse_lazy('home')
    extra_context = {}

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            user = form.save()
            self.extra_context.update({'messages': 'You have registered successfully!'})
            login(request, user)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class LogoutView(LoginRequiredMixin, TemplateView):
    pass


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'profile/profile_detail.html'
    model = User
