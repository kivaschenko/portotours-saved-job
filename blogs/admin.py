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


class BlogAdminForm(ModelForm):
    class Meta:
        model = Blog
        fields = '__all__'
        widgets = {
            'content': CKEditorWidget(),
        }


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm
    exclude = ['updated_at']
    list_display = ['title', 'author', 'display_categories', 'views', 'date_published', 'is_active']
    list_filter = ['title', 'author', 'date_published', 'is_active']

    def display_categories(self, obj):
        return ', '.join(category.name for category in obj.categories.all())
