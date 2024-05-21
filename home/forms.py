from django import forms
from django.core.cache import cache

from destinations.models import Destination
from products.models import Experience
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
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    def __init__(self, lang, *args, initial_data=None, **kwargs):
        super(ExperienceSearchForm, self).__init__(*args, **kwargs)
        self.fields['place'] = forms.ChoiceField(choices=(('', 'Choose destination'),), required=False)
        destinations = cache.get('destinations_{}'.format(lang))
        if not destinations:
            all_active_experiences = Experience.active.all()
            destinations = (Destination.objects.filter(experience__in=all_active_experiences).
                            filter(language__code=lang.upper()).
                            distinct().values_list('slug', 'name'))
            cache.set('destinations_{}'.format(lang), destinations, timeout=3600)
        self.fields['place'].choices += [(slug, name) for slug, name in destinations]

        self.fields['date'].widget.attrs['class'] = 'datepicker'  # Add CSS class for custom styling

        # Set initial data if provided
        if initial_data is not None:
            self.initial = initial_data


