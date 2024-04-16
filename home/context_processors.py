from django.conf import settings
from django.core.cache import cache

from destinations.models import Destination
from attractions.models import Attraction
from products.models import Experience, Product


def navbar_context(request, lang=None, **kwargs):
    session_key = request.session.session_key
    user = request.user
    if lang is None:
        lang_code = 'EN'
    else:
        lang_code = lang.upper()
    cache_key = f'navbar_context_{lang_code}'
    number_of_products = 0
    if user.is_authenticated:
        if Product.pending.filter(customer=user).exists():
            number_of_products = Product.pending.filter(customer=user).count()
    elif session_key:
        if Product.pending.filter(session_key=session_key).exists():
            number_of_products = Product.pending.filter(session_key=session_key).count()
    cached_data = cache.get(cache_key)
    if cached_data:
        cached_data.update({'number_of_products': number_of_products})
        return cached_data
    top_destinations = Destination.active.filter(language__code=lang_code).order_by('parent_destination__priority_number')[:10]
    top_attractions = Attraction.active.filter(language__code=lang_code).order_by('parent_attraction__priority_number')[:10]
    top_experiences = Experience.active.filter(language__code=lang_code).order_by('parent_experience__priority_number')[:10]
    most_popular_experiences = Experience.active.filter(language__code=lang_code, parent_experience__show_on_home_page=True).order_by(
        '-parent_experience__priority_number')
    context = {
        'top_destinations': top_destinations,
        'top_attractions': top_attractions,
        'top_experiences': top_experiences,
        'most_popular_experiences': most_popular_experiences,
        'number_of_products': number_of_products,
    }
    cache.set(cache_key, context, timeout=settings.NAVBAR_CONTEXT_CACHE_TIMEOUT)
    return context
