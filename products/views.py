from django.shortcuts import render
from django.views.generic import TemplateView


class DestinationDetailView(TemplateView):
    template_name = 'destinations/destination_detail.html'

