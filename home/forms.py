from django import forms

from products.models import Experience, ExperienceEvent
from destinations.models import Destination  # Assuming you have a Destination model
from .models import Subscriber


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        labels = {'email': ''}
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email Address'})
        }


class ExperienceSearchForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, lang, *args, initial_data=None, **kwargs):
        super(ExperienceSearchForm, self).__init__(*args, **kwargs)
        self.fields['place'] = forms.ChoiceField(choices=(('', 'Choose place'),))

        destinations = Destination.objects.filter(language__code=lang.upper()).distinct().values_list('slug', 'name')
        self.fields['place'].choices += [(slug, name) for slug, name in destinations]

        self.fields['date'].widget.attrs['class'] = 'datepicker'  # Add CSS class for custom styling

        # Set initial data if provided
        if initial_data is not None:
            self.initial = initial_data


