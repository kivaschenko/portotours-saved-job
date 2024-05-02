from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'rating',
            'full_name',
            'title',
            'short_text'
        ]
        labels = {
            'rating': 'Rating',
            'full_name': 'Full Name',
            'title': 'Review Title',
            'short_text': 'Your Review',
        }
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review title'}),
            'short_text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your review here'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the existing choices from the model
        rating_choices = self.fields['rating'].choices
        # Filter out the empty choice (usually the first one)
        self.fields['rating'].choices = [choice for choice in rating_choices if choice[0] != '']



