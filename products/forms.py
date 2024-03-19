from django import forms

from schedule.models import Calendar

from products.models import Language, ExperienceEvent


class ExperienceEventForm(forms.ModelForm):
    class Meta:
        model = ExperienceEvent
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.calendar:
            relation = self.instance.calendar.calendarrelation_set.first()
            parent_experience_obj = relation.content_object
            if parent_experience_obj.is_private:
                self.fields['max_participants'].disabled = True
                self.fields['special_price'].disabled = True
                self.fields['child_special_price'].disabled = True
            else:
                self.fields['total_price'].disabled = True


ExperienceEventFormSet = forms.inlineformset_factory(Calendar, ExperienceEvent, form=ExperienceEventForm)
