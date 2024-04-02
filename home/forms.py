from django import forms
from .models import Subscriber

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        labels = {'email': ''}
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email Address'})
        }
