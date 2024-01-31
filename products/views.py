from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView

from products.models import Destination, Language


# -----------
# Destination

class DestinationDetailView(TemplateView):
    template_name = 'destinations/destination_detail.html'  # remove after testing!


class DestinationListView(ListView):
    model = Destination
    template_name = 'destinations/destination_list.html'
    paginate_by = 10


class DestinationDetailView(DetailView):
    model = Destination
    template_name = 'destinations/destination.html'  # rename to 'destination_detail.html'


class DestinationLanguageListView(ListView):
    model = Destination
    template_name = 'destinations/destination_list.html'
    queryset = Destination.active.all()
    paginate_by = 10

    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        if hasattr(self, "get") and not hasattr(self, "head"):
            self.head = self.get
        self.request = request
        self.args = args
        self.kwargs = kwargs
        print(self.kwargs)

    def get_queryset(self):
        queryset = super(DestinationLanguageListView, self).get_queryset()
        current_language = Language.objects.get(code=self.kwargs["lang"].upper())
        filtered = queryset.filter(language=current_language)
        print(filtered, '<- filtered')
        return filtered
