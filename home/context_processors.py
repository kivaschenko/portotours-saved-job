from destinations.models import Destination
from attractions.models import Attraction
from products.models import Experience


def navbar_context(request, lang=None, **kwargs):
    if lang is None:
        lang_code = 'EN'
    else:
        lang_code = lang.upper()
    top_destinations = Destination.active.filter(language__code=lang_code).order_by('parent_destination__priority_number')[:10]
    top_attractions = Attraction.active.filter(language__code=lang_code).order_by('parent_attraction__priority_number')[:10]
    top_experiences = Experience.active.filter(language__code=lang_code).order_by('parent_experience__priority_number')[:10]
    most_popular_experiences = Experience.active.filter(language__code=lang_code, parent_experience__show_on_home_page=True).order_by(
        '-parent_experience__priority_number')
    context = {'top_destinations': top_destinations, 'top_attractions': top_attractions, 'top_experiences': top_experiences,
               'most_popular_experiences': most_popular_experiences}
    return context
