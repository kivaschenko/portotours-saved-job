from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from accounts.models import User, Profile


class CustomSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address_city', 'address_country', 'address_line1', 'address_line2', 'address_postal_code', 'address_state']


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['shipping_address_city', 'shipping_address_country', 'shipping_address_line1', 'shipping_address_line2', 'shipping_address_postal_code',
                  'shipping_address_state', 'shipping_phone', 'shipping_name']


class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))