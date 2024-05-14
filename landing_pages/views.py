from django.views.generic import DetailView
from products.models import Experience, ParentExperience
from reviews.models import Testimonial

from .models import LandingPage
from .forms import LandingPageForm


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
        print(experiences, '<- experiences')
        destinations = self.object.destinations.all()
        context['experience_form'] = LandingPageForm(lang, destinations)
        if experiences:
            experiences_queryset = Experience.objects.filter(pk__in=[exp.pk for exp in experiences])
            if self.object.destinations:
                experiences_queryset = experiences_queryset.filter(destinations__in=self.object.destinations.all())
        else:
            experiences_queryset = Experience.objects.none()
        context['experiences'] = experiences_queryset
        context['testimonials'] = Testimonial.objects.all()[:6]
        return context


