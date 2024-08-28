from django.contrib import admin
from django.forms import ModelForm
from django.db import models
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from products.models import Experience
from blogs.models import Category, ParentBlog, Blog, BlockBlog


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
    formfield_overrides = {
        models.TextField: {'widget': CKEditorUploadingWidget()},
    }


class BlogAdminForm(ModelForm):
    class Meta:
        model = Blog
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BlogAdminForm, self).__init__(*args, **kwargs)
        self.fields['experience_recommendations'].queryset = Experience.active.all()


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm
    exclude = ['updated_at']
    list_display = ['title', 'author', 'display_categories', 'views', 'date_published', 'is_active']
    list_filter = ['title', 'author', 'date_published', 'is_active']
    search_fields = ['title', 'author', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    inlines = [BlockBlogInline,]

    def display_categories(self, obj):
        return ', '.join(category.name for category in obj.categories.all())

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            formset.save()
