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
        self.extra_context['current_language'] = current_language.code.lower()
        filtered = queryset.filter(language=current_language)
        return filtered


class ExperienceDetailView(DetailView):
    model = Experience
    template_name = 'experiences/experience_detail.html'
    extra_content = {'languages': {}}
    queryset = Experience.active.all()

    def get_object(self, queryset=None):
        obj = super(ExperienceDetailView, self).get_object(queryset=queryset)
        self.extra_context['current_language'] = obj.language.code.lower()
        # find all other languages
        brothers = obj.parent_experiences.child_experinces.all()
        # create local urls
        if len(brothers) > 0:
            for brother in brothers:
                lang = brother.language.code.lower()
                url = brother.localized_url
                self.extra_context['languages'].update({lang: url})
        # TODO: add UserReview list about this Experience
        return obj
