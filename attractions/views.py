from django.views.generic import DetailView, ListView

from attractions.models import Attraction
from products.models import Language


class AttractionListView(ListView):
    model = Attraction
    paginate_by = 1
    queryset = Attraction.active.all()
    extra_context = {}

    def get_queryset(self):
        queryset = super(AttractionListView, self).get_queryset()
        current_language = Language.objects.get(code=self.kwargs['lang'].upper())
        self.extra_context['current_language'] = current_language.code.lower()
        filtered = queryset.filter(language=current_language)
        return filtered


class AttractionDetailView(DetailView):
    model = Attraction
    extra_context = {'languages': {}}
    queryset = Attraction.active.all()

    def get_object(self, queryset=None):
        obj = super(AttractionDetailView, self).get_object(queryset=queryset)
        self.extra_context['current_language'] = obj.language.code.lower()
        # find all other languages
        brothers = obj.parent_attraction.child_attractions.all()
        # create local urls
        if len(brothers) > 0:
            for brother in brothers:
                lang = brother.language.code.lower()
                url = brother.localized_url
                self.extra_context['languages'].update({lang: url})
        return obj
