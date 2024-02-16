from django import forms

from products.models import Language


class FastBookingForm(forms.Form):
    adult = forms.ChoiceField(choices=((1, 1), (2, 2), (3, 3)))
    children = forms.ChoiceField(choices=((1, 1), (2, 2)))
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))
    language = forms.ModelChoiceField(queryset=Language.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form'}),
                                      initial=Language.objects.get(code='EN'))
