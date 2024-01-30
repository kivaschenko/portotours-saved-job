from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView

from products.models import Destination


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
