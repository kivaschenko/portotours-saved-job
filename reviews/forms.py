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
        # Turn off empty choice for rating field
        self.fields['rating'].empty_label = None


