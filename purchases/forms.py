from itertools import chain

from django import forms

from products.models import Product


class CheckoutMultipleChoiceWidget(forms.widgets.CheckboxSelectMultiple):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'checkout-multiple-choice'

    def render(self, name, value, renderer, attrs=None, choices=()):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [f'<ul{" ".join([f"{k}={v}" for k, v in final_attrs.items()])}>']
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            output.append('<li>')
            output.append(self.render_checkbox(name, option_value, option_label, i, value))
            output.append('</li>')
        output.append('</ul>')
        return '\n'.join(output)

    def render_checkbox(self, name, value, label, idx, values):
        final_attrs = dict(self.attrs, type='checkbox', name=name, value=value)
        if str(value) in values:
            final_attrs['checked'] = 'checked'
        final_attrs['id'] = f"{name}_{idx}"
        cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in values)
        option_label = forms.label_for_checkbox(label, final_attrs['id'])
        return f'{cb.tag()} {option_label}'


class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, user_id, **kwargs):
        kwargs['queryset'] = Product.objects.filter(customer_id=user_id)
        super(CustomModelMultipleChoiceField, self).__init__(**kwargs)


class ProductCartForm(forms.Form):
    def __init__(self, user_id, *args, **kwargs):
        super(ProductCartForm, self).__init__(*args, **kwargs)
        self.fields['my_products'] = CustomModelMultipleChoiceField(
            user_id=user_id,
            queryset=Product.objects.none(),  # Initialize with an empty queryset
            widget=forms.CheckboxSelectMultiple(
                attrs={
                    'class': '',  # customize here
                }),
        )
