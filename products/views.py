from datetime import datetime, timedelta

from django.http import JsonResponse, HttpResponse
from pytz import UTC

from django.views.generic import DetailView, ListView

from products.models import *  # noqa


# ----------
# Experience

class ExperienceListView(ListView):
    model = Experience
    template_name = 'experiences/experience_list.html'
    extra_content = {}
    queryset = Experience.active.all()
    paginate_by = 10  # TODO: add pagination handling into template

    def get_queryset(self):
        queryset = super(ExperienceListView, self).get_queryset()
        current_language = Language.objects.get(code=self.kwargs['lang'].upper())
        self.extra_content['current_language'] = current_language.code.lower()
        filtered = queryset.filter(language=current_language)
        return filtered


class ExperienceDetailView(DetailView):
    model = Experience
    template_name = 'experiences/experience_detail.html'
    extra_content = {'languages': {}}
    queryset = Experience.active.all()

    def get_object(self, queryset=None):
        obj = super(ExperienceDetailView, self).get_object(queryset=queryset)
        self.extra_content['current_language'] = obj.language.code.lower()
        # find all other languages
        brothers = obj.parent_experience.child_experiences.all()
        # create local urls
        if len(brothers) > 0:
            for brother in brothers:
                lang = brother.language.code.lower()
                url = brother.localized_url
                self.extra_content['languages'].update({lang: url})
        # TODO: add UserReview list about this Experience
        return obj


def get_calendar_experience_events(request, parent_experience_slug):
    parent_experience = ParentExperience.objects.get(slug=parent_experience_slug)
    # start = datetime.utcnow().date()
    # end = start + timedelta(days=30)
    # occurrences = parent_experience.event.get_occurrences(start=start, end=end)
    occurrences = parent_experience.event.occurrences_after(max_occurrences=100)
    context = {'occurrences': occurrences}
    return HttpResponse(json.dumps(context), content_type='application/json')
