import logging
from django.conf import settings
from django.core.cache import cache
from django.urls import resolve, reverse, Resolver404
from django.http import Http404

from destinations.models import Destination
from attractions.models import Attraction
from products.models import Experience, Product
from landing_pages.models import LandingPage


logger = logging.getLogger(__name__)


def navbar_context(request, lang=None, **kwargs):
    session_key = request.session.session_key
    cart_not_empty = Product.pending.filter(session_key=session_key).order_by('created_at').exists()
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
        cached_data.update({'number_of_products': number_of_products, 'cart_not_empty': cart_not_empty})
        return cached_data
    top_destinations = Destination.active.filter(language__code=lang_code).order_by('-parent_destination__priority_number')[:10]
    top_attractions = Attraction.active.filter(language__code=lang_code).order_by('-parent_attraction__priority_number')[:10]
    top_experiences = Experience.active.filter(language__code=lang_code).order_by('-parent_experience__priority_number')[:10]
    most_popular_experiences = Experience.active.filter(language__code=lang_code, parent_experience__show_on_home_page=True).order_by(
        '-parent_experience__priority_number')
    landing_pages = LandingPage.active.filter(language__code=lang_code).filter(show_in_navbar=True).order_by('-priority_number')
    context = {
        'top_destinations': top_destinations,
        'top_attractions': top_attractions,
        'top_experiences': top_experiences,
        'most_popular_experiences': most_popular_experiences,
        'number_of_products': number_of_products,
        'landing_pages': landing_pages,
        'cart_not_empty': cart_not_empty,
    }
    cache.set(cache_key, context, timeout=settings.NAVBAR_CONTEXT_CACHE_TIMEOUT)
    print('context:\n\t', context)
    return context


def canonical_url(request):
    try:
        match = resolve(request.path_info)
        canonical_path = reverse(match.view_name, args=match.args, kwargs=match.kwargs)
        url = request.build_absolute_uri(canonical_path)
        # Ensure the URL uses HTTPS
        url = url.replace('http://', 'https://')
        return {'canonical_url': url}
    except Resolver404:
        logger.error(f"URL could not be resolved: {request.path_info}")
        # raise Http404('Page not found')
        return {'canonical_url': ''}

