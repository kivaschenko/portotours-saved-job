from datetime import datetime, timedelta

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.contrib import messages
from django.shortcuts import render, redirect

import pytz
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
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
    success_url = reverse_lazy('my-cart')

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
        return obj

    def form_valid(self, form):
        # add event handler here
        messages.success(self.request, 'Your experience has been reserved for 30 minutes. If you do not pay within this time, the reserve will be canceled..')
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        # Override post method to handle POST requests
        if isinstance(request.user, AnonymousUser):
            user_id = 0
        elif isinstance(request.user, settings.AUTH_USER_MODEL):
            user_id = request.user.id
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            data = form.cleaned_data
            # create new Product
            new_product = Product(
                customer_id=self.kwargs['customer'],
                session=self.kwargs['session'],
                parent_experience=self.object.parent_experience,
                language=data['language'],
                start_datetime=data['date'],
                adults_price=self.object.parent_experience.price,
                adults_count=int(data['adult']),
                child_price=self.object.parent_experience.child_price,
                child_count=int(data['children']),
            )
            new_product.save()

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def setup(self, request, *args, **kwargs):
        """Initialize attributes shared by all view methods."""
        if hasattr(self, "get") and not hasattr(self, "head"):
            self.head = self.get
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if self.request.user.is_authenticated:
            kwargs.update({'customer': self.request.user})
        else:
            kwargs['customer'] = None
            # If the user is not authenticated, get the current session
            if not self.request.session.exists(
                    self.request.session.session_key):
                self.request.session.create()
            kwargs.update({'session': Session.objects.get(
                session_key=self.request.session.session_key)})
        return kwargs


def get_calendar_experience_events(request, parent_experience_slug):
    parent_experience = ParentExperience.objects.get(slug=parent_experience_slug)
    # start = datetime.utcnow().date()
    # end = start + timedelta(days=30)
    # occurrences = parent_experience.event.get_occurrences(start=start, end=end)
    occurrences = parent_experience.event.occurrences_after(max_occurrences=100)
    context = {'occurrences': occurrences}
    return HttpResponse(json.dumps(context), content_type='application/json')


# Products


class SessionKeyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        session_key = request.session.session_key
        if session_key is None:
            # Redirect user to login page or any other page as you see fit
            return redirect(reverse_lazy('login'))
        else:
            # Here, you can perform additional checks if needed, like checking if the session key exists in your models
            if not Product.objects.filter(session=session_key).exists():
                return redirect(reverse_lazy('login'))
            else:
                self.queryset = Product.pending.filter(session=session_key)
            return super(SessionKeyRequiredMixin, self).dispatch(request, *args, **kwargs)


class ProductCartView(SessionKeyRequiredMixin, ListView):
    """View for listing all products for current user (session) only."""
    model = Product
    template_name = 'products/my_cart.html'
    queryset = Product.pending.all()
