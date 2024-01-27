from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from accounts.models import User


class CustomSignupForm(UserCreationForm):
    pass
    # email = forms.EmailField(widget=forms.widgets.EmailInput())

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)
