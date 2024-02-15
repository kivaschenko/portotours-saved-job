from datetime import datetime, timedelta
from django.shortcuts import render
from .forms import DateSelectionForm


import pytz
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from pytz import UTC

from django.views.generic import DetailView, ListView, FormView

from products.forms import FastBookingForm
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


class ExperienceDetailWithFormView(DetailView, FormView):
    model = Experience
    template_name = 'experiences/experience_detail.html'
    extra_context = {'languages': {}}
    queryset = Experience.active.all()
    form_class = FastBookingForm
    success_url = reverse_lazy('home')

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #
    #     # Retrieve or generate the occurrences list here
    #     obj = self.get_object()
    #     # TODO: add this param max_occurrences to settings.py
    #     occurrences_generator = obj.parent_experience.event.occurrences_after(max_occurrences=100)
    #     occurrences = [occ.start.strftime('%Y-%m-%d') for occ in occurrences_generator]
    #     # Pass the occurrences list to the form's initialization
    #     kwargs['occurrences'] = occurrences
    #     return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.extra_context['current_language'] = self.object.language.code.lower()
        # find all other languages
        brothers = self.object.parent_experience.child_experiences.all()
        # create local urls
        if len(brothers) > 0:
            for brother in brothers:
                lang = brother.language.code.lower()
                url = brother.localized_url
                self.extra_context['languages'].update({lang: url})
        # TODO: add UserReview list about this Experience
        occurrences_generator = self.object.parent_experience.event.occurrences_after(max_occurrences=100)
        occurrences = [occ.start.strftime('%Y-%m-%d') for occ in occurrences_generator]
        self.extra_context['occurrences'] = occurrences
        print('extra_content:', self.extra_context)
        context.setdefault("view", self)
        if self.extra_context is not None:
            context.update(self.extra_context)
        if "form" not in context:
            context["form"] = self.get_form()
        return context

    def get_object(self, queryset=None):
        obj = super(ExperienceDetailWithFormView, self).get_object(queryset=queryset)
        self.extra_context['current_language'] = obj.language.code.lower()
        # find all other languages
        brothers = obj.parent_experience.child_experiences.all()
        # create local urls
        if len(brothers) > 0:
            for brother in brothers:
                lang = brother.language.code.lower()
                url = brother.localized_url
                self.extra_context['languages'].update({lang: url})
        # TODO: add UserReview list about this Experience
        occurrences_generator = obj.parent_experience.event.occurrences_after(max_occurrences=100)
        occurrences = [occ.start.strftime('%Y-%m-%d') for occ in occurrences_generator]
        self.extra_context['occurrences'] = mark_safe(occurrences)
        print('extra_content:', self.extra_context)
        return obj

    def form_valid(self, form):
        # Handle form submission
        # For example, save the form data
        form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        # Override post method to handle POST requests
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


def get_calendar_experience_events(request, parent_experience_slug):
    parent_experience = ParentExperience.objects.get(slug=parent_experience_slug)
    # start = datetime.utcnow().date()
    # end = start + timedelta(days=30)
    # occurrences = parent_experience.event.get_occurrences(start=start, end=end)
    occurrences = parent_experience.event.occurrences_after(max_occurrences=100)
    context = {'occurrences': occurrences}
    return HttpResponse(json.dumps(context), content_type='application/json')
