# forms.py
from django import forms
from .models import TagAttraction


class TagAttractionFilterForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(queryset=TagAttraction.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
