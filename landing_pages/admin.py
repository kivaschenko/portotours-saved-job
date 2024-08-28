from django.contrib import admin
from django.forms import ModelForm

from ckeditor.widgets import CKEditorWidget

from landing_pages.models import LandingPage, FAQLandingPage


class FAQLandingPageInline(admin.TabularInline):
    model = FAQLandingPage
    extra = 1
    exclude = ('updated_at',)


class LandingPageForm(ModelForm):
    class Meta:
        model = LandingPage
        exclude = ['updated_at']
        widgets = {
            'content': CKEditorWidget(),
        }


@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    form = LandingPageForm
    exclude = ['updated_at', 'card_image',]
    list_display = ['id', 'title', 'slug', 'category',
                    'show_in_navbar',
                    'menu_title',
                    'show_in_lisbon_things',
                    'show_in_out_lisbon_things',
                    'show_in_menu_our_services',
                    'priority_number', 'is_active',  'updated_at']
    list_per_page = 20
    inlines = [FAQLandingPageInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            formset.save()


@admin.register(FAQLandingPage)
class FAQLandingPageAdmin(admin.ModelAdmin):
    exclude = ['updated_at',]
    list_display = ['question', 'landing_page', 'language', 'question', 'priority_number', 'is_active', 'updated_at']
    list_filter = ['question', 'landing_page', 'language', 'priority_number', 'is_active']
