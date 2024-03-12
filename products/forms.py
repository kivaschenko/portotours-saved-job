from django import forms

from schedule.models import Calendar

from products.models import Language, ExperienceEvent




class ExperienceEventForm(forms.ModelForm):
    class Meta:
        model = ExperienceEvent
        fields = '__all__'


ExperienceEventFormSet = forms.inlineformset_factory(Calendar, ExperienceEvent, form=ExperienceEventForm)
