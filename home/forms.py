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
    place = forms.ChoiceField(choices=(('', 'Choose place'),))
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, lang, *args, initial_data=None, **kwargs):
        super(ExperienceSearchForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datepicker'  # Add CSS class for custom styling

        # Customize place field choices to show distinct destinations
        destinations = Destination.objects.filter(language__code=lang.upper()).distinct().values_list('slug', 'name')
        self.fields['place'].choices += [(slug, name) for slug, name in destinations]

        # Customize available dates based on remaining_participants > 0
        if initial_data is not None:
            self.initial = initial_data
