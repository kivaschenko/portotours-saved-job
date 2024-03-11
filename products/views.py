from django.db.models import Sum, F
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, FormView, DeleteView

from products.forms import FastBookingForm
from products.models import *  # noqa
from products.services import get_actual_events_for_experience

Customer = settings.AUTH_USER_MODEL


# ----------
# Experience

class ExperienceListView(ListView):
    model = Experience
    template_name = 'experiences/experience_list.html'
    extra_context = {}
    queryset = Experience.active.all()
    paginate_by = 10  # TODO: add pagination handling into template

    def get_queryset(self):
        queryset = super(ExperienceListView, self).get_queryset()
        current_language = Language.objects.get(code=self.kwargs['lang'].upper())
        self.extra_context['current_language'] = current_language.code.lower()
        filtered = queryset.filter(language=current_language)
        return filtered


class ExperienceDetailWithFormView(FormView, DetailView):
    model = Experience
    template_name = 'experiences/experience_detail.html'
    extra_context = {'languages': {}}
    queryset = Experience.active.all()
    form_class = FastBookingForm
    success_url = reverse_lazy('my-cart', kwargs={'lang': 'en'})

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
        return obj

    def form_valid(self, form):
        # add event handler here
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            data = form.cleaned_data
            # create new Product
            new_product = Product(
                customer=self.kwargs['customer'],
                session_key=self.kwargs['session_key'],
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
            kwargs.update({'session_key': self.request.session.session_key})
        else:
            kwargs['customer'] = None
            # If the user is not authenticated, get the current session
            if not self.request.session.exists(self.request.session.session_key):
                self.request.session.create()
            kwargs.update({'session_key': self.request.session.session_key})
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


class UserIsAuthentiacedOrSessionKeyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        session_key = request.session.session_key
        self.queryset = Product.objects.none()
        if session_key is None and not user.is_authenticated:
            # Redirect user to login page or any other page as you see fit
            return redirect(reverse_lazy('login'))
        elif user.is_authenticated:
            if Product.objects.filter(customer=user).exists():
                self.queryset = Product.pending.filter(customer=user)
        elif session_key:
            # Here, you can perform additional checks if needed, like checking if the session key exists in your models
            if Product.objects.filter(session_key=session_key).exists():
                self.queryset = Product.pending.filter(session_key=session_key)
        return super(UserIsAuthentiacedOrSessionKeyRequiredMixin, self).dispatch(request, *args, **kwargs)


class ProductCartView(UserIsAuthentiacedOrSessionKeyRequiredMixin, ListView):
    """View for listing all products for current user (session) only."""
    model = Product
    template_name = 'products/my_cart.html'
    queryset = Product.pending.all()
    extra_context = {'current_language': 'en'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_ids = [product.pk for product in self.queryset.all()]
        context['product_ids'] = product_ids
        context['total_price_sum'] = 0
        context['old_price_sum'] = 0
        context['discounted_price_sum'] = 0
        try:
            # Calculate the sum of total prices
            total_price_sum = self.queryset.aggregate(total_price_sum=Sum('total_price'))['total_price_sum']
            # Calculate the sum of old prices
            old_price_sum = self.queryset.aggregate(old_price_sum=Sum('old_total_price'))['old_price_sum']
            # Add the sum to the context
            context['total_price_sum'] = total_price_sum
            context['old_price_sum'] = old_price_sum
            context['discounted_price_sum'] = round(old_price_sum - total_price_sum, 2)
        except Exception as e:
            logger.error(f'Error while calculating total_price_sum: {e}')
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def post(self, request, *args, **kwargs):
        """This logic for cancellation on the fly in cart without confirm page.
            In hold mode if template button does not exist."""
        if 'cancel_product_id' in request.POST:
            product_id = request.POST.get('cancel_product_id')
            product = Product.objects.get(pk=product_id)
            product.status = 'Cancelled'
            product.save()
        else:
            logger.error(f'Cancellation. Product not found.')
        return HttpResponseRedirect(reverse_lazy('my-cart', kwargs={'lang': 'en'}))


class CancelProductView(DeleteView):
    model = Product
    template_name = 'products/cancel_form.html'
    success_url = reverse_lazy('my-cart', kwargs={'lang': 'en'})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Here you can perform any logic you want before changing the status
        self.object.status = 'Cancelled'
        self.object.save()
        # Instead of calling delete() on the object, change its status
        return HttpResponseRedirect(self.get_success_url())


@csrf_exempt
def get_actual_experience_events(request):
    if not request.method == 'POST':
        return HttpResponseBadRequest('Required post request.')
    try:
        data = json.loads(request.body.decode('utf-8'))
        parent_experience_id = int(data['parent_experience_id'])

        result = get_actual_events_for_experience(parent_experience_id)
        return JsonResponse({'result': result})
    except json.decoder.JSONDecodeError as exp:
        return HttpResponseBadRequest('Invalid JSON data')

