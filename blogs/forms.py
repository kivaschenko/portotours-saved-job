from django import forms
from .models import Category


class BlogFilterForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="All")
