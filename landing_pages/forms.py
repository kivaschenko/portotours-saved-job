from django import forms


class LandingPageForm(forms.Form):
    def __init__(self, lang, destinations, *args, initial_data=None, **kwargs):
        super(LandingPageForm, self).__init__(*args, **kwargs)
        self.fields['place'] = forms.ChoiceField(choices=(('', 'Choose place'),), required=False)
        destinations = destinations.values_list('slug', 'name')
        self.fields['place'].choices += [(slug, name) for slug, name in destinations]
