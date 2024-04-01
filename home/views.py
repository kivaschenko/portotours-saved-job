from django.shortcuts import render
from django.views.generic import TemplateView

from destinations.models import ParentDestination, Destination
from attractions.models import ParentAttraction, Attraction
from products.models import ParentExperience, Experience


def navbar_view(request, lang='en', **kwargs):
    lang_code = lang.upper()
    top_destinations = Destination.active.filter(language__code=lang_code).order_by('parent_destination__priority_number')[:10]
    top_attractions = Attraction.active.filter(language__code=lang_code).order_by('parent_attraction__priority_number')[:10]
    top_experiences = Experience.active.filter(language__code=lang_code).order_by('parent_experience__priority_number')[:10]
    context = {'top_destinations': top_destinations, 'top_attractions': top_attractions, 'top_experiences': top_experiences}
    return render(request, 'include/navbar.html', context)


# HOME
class HomeView(TemplateView):
    template_name = 'home.html'


# views.py

# from django.shortcuts import render
# from .models import Attraction
#
# def my_view(request):
#     english_attractions = Attraction.active.filter(language__code='EN').order_by('parent_attraction__priority_number')
#     return render(request, 'your_template.html', {'english_attractions': english_attractions})
