from django.views.generic import TemplateView
from django.utils.translation import activate
from destinations.models import Destination
from attractions.models import Attraction
from products.models import Experience


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = self.kwargs.get('lang', 'en')
        activate(lang)
        context['current_language'] = lang
        context['destinations_top_year'] = Destination.active.filter(
            parent_destination__show_on_home_page=True,
            language__code=lang.upper(),
        ).order_by('parent_destination__priority_number')[:6]
        context['attractions_top_year'] = Attraction.active.filter(
            parent_attraction__show_on_home_page=True,
            language__code=lang.upper(),
        ).order_by('parent_attraction__priority_number')[:6]
        context['experiences_top_year'] = Experience.active.filter(
            parent_experience__show_on_home_page=True,
            language__code=lang.upper(),
        ).order_by('parent_experience__priority_number')[:6]
        return context
