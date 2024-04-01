from django.contrib import admin
from django.forms import ModelForm

from ckeditor.widgets import CKEditorWidget

from blogs.models import *  # noqa


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


@admin.register(ParentBlog)
class ParentBlogAdmin(admin.ModelAdmin):
    exclude = ['updated_at']
    list_display = ['parent_name', 'priority_number']
    list_filter = ['parent_name']


class BlockBlogInline(admin.TabularInline):
    model = BlockBlog
    extra = 1
    list_display = ['title', 'text']
    widgets = {
        'text': CKEditorWidget(),
    }


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    exclude = ['updated_at']
    list_display = ['title', 'author', 'display_categories', 'views', 'date_published', 'is_active']
    list_filter = ['title', 'author', 'date_published', 'is_active']
    inlines = [BlockBlogInline,]

    def display_categories(self, obj):
        return ', '.join(category.name for category in obj.categories.all())

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            formset.save()
