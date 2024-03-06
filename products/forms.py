from django import forms

from schedule.models import Calendar

from products.models import Language, ExperienceEvent


class FastBookingForm(forms.Form):
    adult = forms.ChoiceField(
        choices=(
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8)
        )
    )
    children = forms.ChoiceField(
        choices=(
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
        )
    )
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))
    language = forms.ModelChoiceField(queryset=Language.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form'}),
                                      initial=Language.objects.get(code='EN'))


class ExperienceEventForm(forms.ModelForm):
    class Meta:
        model = ExperienceEvent
        fields = '__all__'


ExperienceEventFormSet = forms.inlineformset_factory(Calendar, ExperienceEvent, form=ExperienceEventForm
                                                     )
