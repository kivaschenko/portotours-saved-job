from django.contrib import admin
from django.forms import ModelForm

from ckeditor.widgets import CKEditorWidget

from reviews.models import Review


class ReviewAdminForm(ModelForm):
    class Meta:
        model = Review
        exclude = ('updated_at',)
        widgets = {
            'text': CKEditorWidget(),
        }


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    form = ReviewAdminForm
    list_display = ['id', 'profile', 'parent_experience', 'show_on_home_page', 'rating', 'short_text', 'created_at', 'updated_at']
    list_filter = ['created_at', 'parent_experience', 'profile', 'show_on_home_page']
