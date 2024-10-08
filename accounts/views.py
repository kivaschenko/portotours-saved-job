import os
import base64

from django.core.mail import EmailMultiAlternatives
from django.http import Http404
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, LoginView
from django.views.generic import UpdateView, DetailView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login

from .forms import (CustomSignupForm, AddressForm, ProfileInfoForm, CustomLoginForm)
from accounts.models import User, Profile


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


class CustomLogoutView(LoginRequiredMixin, BaseLogoutView):
    """Custom logout view."""

    def get(self, request, *args, **kwargs):
        # Perform any additional logic you need before logging out
        # For example, you might want to clear some session data
        # You can also add logging or other actions here

        # Clear the session
        request.session.flush()

        # Call the parent class's get method to perform the logout
        return super().get(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        # If you need to perform any checks before logging out, you can do it here
        # For example, you might want to check if the user has certain permissions
        # If not, you can redirect them to another page or display an error message

        # Call the parent class's dispatch method to continue with the logout process
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    form = CustomLoginForm
    template_name = 'registration/login.html'  # Specify the template name for your login page
    success_url = reverse_lazy('home')  # Redirect URL after successful login

    def form_valid(self, form):
        # Reset session on login
        self.request.session.flush()
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'profile/profile_detail.html'
    model = User

    def get_object(self, queryset=None):
        try:
            obj = Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            raise Http404(
                "No %(verbose_name)s found matching the query" % {"verbose_name": 'Profile'}
            )
        return obj


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = AddressForm
    template_name = 'profile/address_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        try:
            obj = Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            raise Http404(
                "No %(verbose_name)s found matching the query" % {"verbose_name": 'Profile'}
            )
        return obj


class ProfileInfoUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileInfoForm
    template_name = 'profile/info_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        try:
            obj = Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            raise Http404(
                "No %(verbose_name)s found matching the query" % {"verbose_name": 'Profile'}
            )
        return obj


# --------------
# PASSWORD RESET


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/customized/password_reset_form.html'
    email_template_name = 'registration/customized/password_reset_email.html'
    html_email_template_name = 'registration/customized/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    subject_template_name = 'registration/customized/password_reset_subject.txt'

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        subject = self.format_email_subject(self.render_to_string(subject_template_name, context))
        body = self.render_to_string(email_template_name, context)
        html_content = render_to_string(html_email_template_name, context)

        email = EmailMultiAlternatives(subject, body, from_email, [to_email])

        # Find the paths to the SVG images
        svg_file_paths = {
            'logo': os.path.join(settings.STATIC_ROOT, 'icons/logo_black.svg'),
            'phone_icon': os.path.join(settings.STATIC_ROOT, 'icons/phone-icon.svg'),
            'email_icon': os.path.join(settings.STATIC_ROOT, 'icons/email-icon.svg'),
            # Add more image paths as needed
        }

        # Embed SVG images as base64 encoded strings
        for name, path in svg_file_paths.items():
            with open(path, 'rb') as f:
                content = f.read()
                encoded_content = base64.b64encode(content).decode('utf-8')
                html_content = html_content.replace(f'src="{name}.svg"', f'src="data:image/svg+xml;base64,{encoded_content}"')

        email.attach_alternative(html_content, 'text/html')
        email.send()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = settings.SITE_NAME
        context['protocol'] = settings.PROTOCOL
        context['domain'] = settings.DOMAIN
        return context


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/customized/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/customized/password_reset_confirm.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/customized/password_reset_complete.html'
