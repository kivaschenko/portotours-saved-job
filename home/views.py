from django.utils.translation import activate
from django.views.generic import TemplateView
from django.db.models import Prefetch
from destinations.models import ParentDestination, Destination
from attractions.models import ParentAttraction, Attraction
from products.models import ParentExperience, Experience, Language


# HOME
class HomeView(TemplateView):
    template_name = 'home.html'
    extra_context = {'current_language': 'en'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = self.kwargs.get('lang', 'en')
        activate(lang)
        context['current_language'] = lang
        experiences_top_year = Experience.active.filter(
            parent_experience__show_on_home_page=True,
            language__code=lang.upper(),
        ).order_by(
            'parent_experience__priority_number'
        )
        context['experiences_top_year'] = experiences_top_year
        return context
