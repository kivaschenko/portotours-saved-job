from django.http import JsonResponse
from django.http import HttpResponse
from django.views.generic import TemplateView, DetailView
from django.utils.translation import activate

from destinations.models import Destination
from attractions.models import Attraction
from products.models import Experience
from reviews.models import Testimonial

from .models import Page, AboutUsPage

from .forms import SubscriberForm, ExperienceSearchForm


class HomeView(TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = 'en'
        if self.kwargs.get('lang'):
            lang = self.kwargs.get('lang', 'en')
        # activate(lang)
        context['current_language'] = lang
        context['destinations_top_year'] = Destination.active.filter(
            parent_destination__show_on_home_page=True,
            language__code=lang.upper(),
        ).order_by('-parent_destination__priority_number')[:6]
        context['attractions_top_year'] = Attraction.active.filter(
            parent_attraction__show_on_home_page=True,
            language__code=lang.upper(),
        ).order_by('-parent_attraction__priority_number')[:6]
        context['experiences_top_year'] = Experience.active.filter(
            parent_experience__show_on_home_page=True,
            language__code=lang.upper(),
        ).order_by('-parent_experience__priority_number')[:6]
        context['testimonials'] = Testimonial.objects.all()[:6]
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
            # Return JSON response indicating success
            return JsonResponse({'success': True})
        else:
            # If form is not valid, return JSON response with errors
            return JsonResponse({'success': False, 'errors': form.errors})


# -----
# Pages

class PageDetailView(DetailView):
    model = Page


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /odt-admin/",
        "Disallow: /en/accounts/",
        # "Allow: /",
        "",
        "Sitemap: https://onedaytours.pt/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# About Us

class AboutUsDetailView(DetailView):
    model = AboutUsPage
