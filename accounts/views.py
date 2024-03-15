from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.views.generic import TemplateView, UpdateView, DetailView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login

from .forms import CustomSignupForm, AddressForm, ShippingAddressForm
from accounts.models import User, Profile


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

    def get_object(self, queryset=None):
        # Get the user from the request
        return self.request.user


class AddressUpdateView(UpdateView):
    model = Profile
    form_class = AddressForm
    template_name = 'profile/address_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.profile


class ShippingAddressUpdateView(UpdateView):
    model = Profile
    form_class = ShippingAddressForm
    template_name = 'profile/shipping_address_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.profile


# --------------
# PASSWORD RESET

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
