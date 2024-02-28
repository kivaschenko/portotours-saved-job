from django.views.generic import DetailView, ListView

from destinations.models import Destination
from products.models import Language


# -----------
# Destination

class DestinationDetailView(DetailView):
    model = Destination
    template_name = 'destinations/destination_detail.html'
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
        return obj


class DestinationListView(ListView):
    model = Destination
    template_name = 'destinations/destination_list.html'
    queryset = Destination.active.all()
    paginate_by = 10  # TODO: check pagination in template and front-end handlers
    extra_context = {}

    def get_queryset(self):
        queryset = super(DestinationListView, self).get_queryset()
        current_language = Language.objects.get(code=self.kwargs["lang"].upper())
        self.extra_context["current_language"] = current_language.code.lower()
        filtered = queryset.filter(language=current_language)
        return filtered
