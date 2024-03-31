from math import ceil
from django.views.generic import DetailView, ListView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from blogs.models import Blog, Category
from products.models import Language


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogs/blog_detail.html'
    extra_context = {'languages': {}}
    queryset = Blog.active.all()

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.views += 1
        self.object.save(update_fields=['views'])

        # Calculate midpoint
        blocks_count = len(self.object.blocks.all())
        self.midpoint = ceil(blocks_count / 2)

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(BlogDetailView, self).get_object(queryset=queryset)
        self.extra_context['current_language'] = obj.language.code.lower()
        # find all other languages
        brothers = obj.parent_blog.child_blogs.all()
        # create local urls
        if len(brothers) > 0:
            for brother in brothers:
                lang = brother.language.code.lower()
                url = brother.localized_url
                self.extra_context['languages'].update({lang: url})
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['midpoint'] = self.midpoint
        return context




class BlogListView(ListView):
    model = Blog
    template_name = 'blogs/blog_list.html'
    queryset = Blog.active.all()
    paginate_by = 10
    extra_context = {}

    def get_queryset(self):
        queryset = super(BlogListView, self).get_queryset()
        categories = Category.objects.all()
        self.extra_context['categories'] = categories
        current_language = Language.objects.get(code=self.kwargs['lang'].upper())
        self.extra_context['current_language'] = current_language.code.lower()
        queryset = queryset.filter(language=current_language)
        # filter by category by click button
        category_id = self.request.GET.get('category_id')
        if category_id:
            category = Category.objects.get(pk=category_id)
            queryset = queryset.filter(categories=category)

        return queryset
    # TODO: Complete filtering by Category
    # def get(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     context = self.get_context_data(object_list=queryset)
    #     html = render_to_string(self.template_name, context, request=request)
    #     return JsonResponse({'html': html})

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    _("Empty list and “%(class_name)s.allow_empty” is False.")
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()
        return self.render_to_response(context)