from django.shortcuts import render
from django.views.generic import TemplateView


# HOME
class HomeView(TemplateView):
    template_name = 'home.html'
