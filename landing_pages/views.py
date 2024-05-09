from datetime import timedelta, datetime

from django.http import JsonResponse
from django.views.generic import DetailView
from django.utils.translation import activate

from destinations.models import Destination
from attractions.models import Attraction
from products.models import Experience
from reviews.models import Testimonial

from .models import LandingPage

from home.forms import SubscriberForm, ExperienceSearchForm


class LandingPageView(DetailView):
    model = LandingPage
    template_name = 'landing_pages/parent_landing.html'
    queryset = LandingPage.active.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = 'en'
        if self.kwargs.get('lang'):
            lang = self.kwargs.get('lang')
        # activate(lang)
        context['current_language'] = lang
        context['experiences'] = Experience.active.filter(
            parent_experience__category=self.object.category,
            language__code=lang.upper(),
        ).all()
        if self.object.destination:
            self.template_name = 'landing_pages/child_landing.html'
            context['experiences'] = context['experiences'].filter(destination=self.object.destination)
        context['testimonials'] = Testimonial.objects.all()[:6]
        context['subscription_form'] = SubscriberForm()
        context['experience_form'] = ExperienceSearchForm(lang)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            # Return JSON response indicating success
            return JsonResponse({'success': True})
        else:
            # If form is not valid, return JSON response with errors
            return JsonResponse({'success': False, 'errors': form.errors})

# Create your views here.
