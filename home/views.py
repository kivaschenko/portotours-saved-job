from datetime import timedelta, datetime

from django.views.generic import TemplateView, DetailView
from django.utils.translation import activate
from django.shortcuts import redirect

from destinations.models import Destination
from attractions.models import Attraction
from products.models import Experience
from reviews.models import Review

from .models import Page

from .forms import SubscriberForm, ExperienceSearchForm


class HomeView(TemplateView):
    template_name = 'home/home.html'

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
        year_ago = datetime.utcnow() - timedelta(days=365)
        context['reviews_top_year'] = Review.objects.filter(
            show_on_home_page=True, created_at__gte=year_ago
        ).order_by('-created_at')[:6]
        context['subscription_form'] = SubscriberForm()
        context['experience_form'] = ExperienceSearchForm(lang)
        return context

    def post(self, request, *args, **kwargs):
        lang = self.kwargs.get('lang', 'en')
        activate(lang)
        context = self.get_context_data(**kwargs)
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect after successful form submission
            return redirect('home', lang=lang)
        else:
            # If form is not valid, re-render the page with the form and any existing data
            context['subscription_form'] = form
            return self.render_to_response(context)


# -----
# Pages

class PageDetailView(DetailView):
    model = Page
