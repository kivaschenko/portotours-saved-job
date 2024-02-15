from django import forms
from django.forms.widgets import DateInput
from django.utils.safestring import mark_safe

from bootstrap_datepicker_plus.widgets import DatePickerInput

from products.models import Language


class ColoredDateInput(DateInput):
    """ColoredDateInput is a custom widget inheriting from Django's DateInput widget.
    It takes an additional parameter occurrences, which is a list of dates that have occurrences.
    The render method of the widget is overridden to include a script that initializes the Bootstrap datepicker
    and colors the dates based on the occurrences list."""

    def __init__(self, occurrences, *args, **kwargs):
        self.occurrences = occurrences
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        rendered_widget = super().render(name, value, attrs, renderer)
        script = """
            <script>
                $(document).ready(function() {{
                    const occurrences = {0};
                    $('#{1}').datepicker({{
                        beforeShowDay: function(date) {{
                            var dateString = $.datepicker.formatDate('yyyy-mm-dd', date);
                            if (occurrences.indexOf(dateString) !== -1) {{
                                return [true, 'highlighted-date', 'This date has an occurrence'];
                            }}
                            return [true, '', ''];
                        }},
                        dateFormat: 'yyyy-mm-dd'
                    }});
                }});
            </script>
        """.format(self.occurrences, attrs['id'])

        return rendered_widget + mark_safe(script)


class FastBookingForm(forms.Form):
    adult = forms.ChoiceField(choices=((1, 1), (2, 2), (3, 3)))
    children = forms.ChoiceField(choices=((1, 1), (2, 2)))
    date = forms.DateField(widget=DatePickerInput)
    language = forms.ModelChoiceField(queryset=Language.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form'}),
                                      initial=Language.objects.get(code='EN'))

    # def __init__(self, occurrences, *args, **kwargs):
    #     super(FastBookingForm, self).__init__(*args, **kwargs)
    #     self.fields['date'] = forms.DateField(
    #         widget=ColoredDateInput(occurrences=occurrences,),
    #         input_formats='yyyy-mm-dd', required=True, label='When'
    #     )
