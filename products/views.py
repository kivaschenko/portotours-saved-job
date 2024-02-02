from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView

from products.models import Destination, Language


# -----------
# Destination

class DestinationDetailView(TemplateView):
    template_name = 'destinations/destination_detail.html'  # remove after testing!


class DestinationListView(ListView):
    model = Destination
    template_name = 'destinations/destination_list.html'
    paginate_by = 10


class DestinationDetailView(DetailView):
    model = Destination
<<<<<<< HEAD
    template_name = 'destinations/destination_detail.html'  # rename to 'destination_detail.html'
=======
    template_name = 'destinations/destination.html'  # rename to 'destination_detail.html'
    extra_context = {'languages': {}}
    queryset = Destination.active.all()

    def get_object(self, queryset=None):
        obj = super(DestinationDetailView, self).get_object(queryset=queryset)
        self.extra_context['current_language'] = obj.language.code.lower()
        # find all other languages
        brothers = obj.parent_destination.child_destinations.all()
        # create local urls
        if len(brothers) > 0:
            for brother in brothers:
                lang = brother.language.code.lower()
                url = brother.localized_url
                self.extra_context['languages'].update({lang: url})
        # find FAQ Destination for current language
        current_faqs = obj.parent_destination.faq_destinations.filter(language=obj.language).all()
        if current_faqs:
            self.extra_context.update({'current_faqs': current_faqs})
        else:
            self.extra_context['current_faqs'] = []
        return obj
>>>>>>> 6976ed1d295ead41541c620aff50d1c781453185


class DestinationLanguageListView(ListView):
    model = Destination
    template_name = 'destinations/destination_list.html'
    queryset = Destination.active.all()
    paginate_by = 10
    extra_context = {}

    def get_queryset(self):
        queryset = super(DestinationLanguageListView, self).get_queryset()
        current_language = Language.objects.get(code=self.kwargs["lang"].upper())
        self.extra_context["current_language"] = current_language.code.lower()
        filtered = queryset.filter(language=current_language)
        return filtered
