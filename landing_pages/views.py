from django.views.generic import DetailView
from reportlab.pdfbase.pdfdoc import Destination

from products.models import Experience, ParentExperience
from reviews.models import Testimonial
from destinations.models import Destination

from .models import LandingPage


class LandingPageView(DetailView):
    model = LandingPage
    template_name = 'landing_pages/landing_page.html'
    queryset = LandingPage.active.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = 'en'
        if self.kwargs.get('lang'):
            lang = self.kwargs.get('lang')
        # activate(lang)
        context['current_language'] = lang
        parent_experiences = ParentExperience.objects.filter(categories=self.object.category)
        experiences = []
        for par_exp in parent_experiences:
            found_experience = par_exp.child_experiences.filter(is_active=True, language__code=lang.upper()).first()
            if found_experience:
                experiences.append(found_experience)
        if experiences:
            experiences_queryset = Experience.objects.filter(pk__in=[exp.pk for exp in experiences])
            if self.object.destinations.all():
                experiences_queryset = experiences_queryset.filter(destinations__in=self.object.destinations.all())
                destinations = self.object.destinations.values_list('slug', 'name')
            else:
                destination_ids_list = experiences_queryset.values_list('destinations', flat=True)
                unique_destination_ids = set(destination_ids_list)
                destinations = Destination.active.filter(id__in=unique_destination_ids).values_list('slug', 'name')
        else:
            experiences_queryset = Experience.objects.none()
        context['experiences'] = experiences_queryset
        context['destinations'] = [(slug, name) for slug, name in destinations]
        context['testimonials'] = Testimonial.objects.all()[:6]
        return context


