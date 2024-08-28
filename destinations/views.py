from django.views.generic import DetailView, ListView
from django.http import Http404

from destinations.models import Destination
from products.models import Language


# -----------
# Destination

class DestinationDetailView(DetailView):
    model = Destination
    template_name = 'destinations/destination_detail.html'
    extra_context = {'languages': {}}
    queryset = Destination.active.all()

    def get_object(self, queryset=None):
        obj = super(DestinationDetailView, self).get_object(queryset=queryset)
        # find all other languages
        brothers = obj.parent_destination.child_destinations.all()
        # create local urls
        if len(brothers) > 0:
            for brother in brothers:
                lang = brother.language.code.lower()
                url = brother.localized_url
                self.extra_context['languages'].update({lang: url})
        return obj

    def get_queryset(self):
        queryset = super().get_queryset().filter(language__code=self.lang.upper())
        if queryset.exists():
            return queryset
        else:
            raise Http404

    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        super().setup(request, *args, **kwargs)
        lang = self.kwargs.get('lang')
        if not Language.objects.filter(code=lang.upper()).exists():
            raise Http404
        self.lang = lang
        self.extra_context.update({'current_language': lang})


class DestinationListView(ListView):
    model = Destination
    template_name = 'destinations/destination_list.html'
    queryset = Destination.active.all()
    paginate_by = 10
    extra_context = {}

    def get_queryset(self):
        queryset = super().get_queryset().filter(language__code=self.lang.upper())
        if queryset.exists():
            return queryset
        else:
            raise Http404

    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        super().setup(request, *args, **kwargs)
        lang = self.kwargs.get('lang')
        if not Language.objects.filter(code=lang.upper()).exists():
            raise Http404
        self.lang = lang
        self.extra_context.update({'current_language': lang})
