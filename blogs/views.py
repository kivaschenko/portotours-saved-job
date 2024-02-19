from django.views.generic import DetailView, ListView

from blogs.models import Blog
from products.models import Language


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogs/blog_detail.html'
    extra_context = {'languages': {}}
    queryset = Blog.active.all()

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


class BlogListView(ListView):
    model = Blog
    template_name = 'blogs/blog_list.html'
    queryset = Blog.active.all()
    paginate_by = 10
    extra_context = {}

    def get_queryset(self):
        queryset = super(BlogListView, self).get_queryset()
        current_language = Language.objects.get(code=self.kwargs['lang'].upper())
        self.extra_context['current_language'] = current_language.code.lower()
        filtered = queryset.filter(language=current_language)
        return filtered
