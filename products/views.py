from django.db.models import Sum
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, DeleteView

from schedule.models import Occurrence

from products.models import *  # noqa
from products.product_services import get_actual_events_for_experience

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


class ExperienceDetailView(DetailView):
    model = Experience
    template_name = 'experiences/experience_detail.html'
    extra_context = {'languages': {}}
    queryset = Experience.active.all()
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
        return context

    def get_object(self, queryset=None):
        obj = super(ExperienceDetailView, self).get_object(queryset=queryset)
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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def setup(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.extra_context.update({'customer_id': request.user.id})
            self.extra_context.update({'session_key': request.session.session_key})
        else:
            self.extra_context['customer'] = None
            # If the user is not authenticated, get the current session
            if not request.session.exists(request.session.session_key):
                request.session.create()
            self.extra_context.update({'session_key': request.session.session_key})
        kwargs = super(ExperienceDetailView, self).setup(request, *args, **kwargs)
        return kwargs


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
        # TODO: Add update for certain ExperienceEvent: change booked_participants and remaining_participants!
        # Instead of calling delete() on the object, change its status
        return HttpResponseRedirect(self.get_success_url())


def get_actual_experience_events(request, parent_experience_id):
    try:
        result = get_actual_events_for_experience(parent_experience_id)
        print({'result': result})
        return JsonResponse({'result': result}, status=200)
    except json.decoder.JSONDecodeError as exp:
        return HttpResponseBadRequest('Invalid JSON data')


@csrf_exempt
def create_product(request):
    if request.method == 'POST':
        adults = int(request.POST.get('adults'))
        children = int(request.POST.get('children'))
        language_code = request.POST.get('language')
        customer_id = int(request.POST.get('customer_id'))
        session_key = request.POST.get('session_key')
        event_id = int(request.POST.get('event_id'))
        parent_experience_id = int(request.POST.get('parent_experience_id'))

        # Get ExperienceEvent obj
        exp_event = ExperienceEvent.objects.get(id=event_id)

        # Get language
        language = Language.objects.get(code=language_code)

        # Create a new product using the received data
        new_product = Product(
            customer_id=customer_id,
            session_key=session_key,
            parent_experience_id=parent_experience_id,
            language=language,
            start_datetime=exp_event.start,
            end_datetime=exp_event.end,
            adults_price=exp_event.special_price,
            adults_count=adults,
            child_price=exp_event.child_special_price,
            child_count=children,
        )
        new_product.save()

        # Update ExperienceEvent data
        total_booked = adults + children
        exp_event.update_booking_data(booked_number=total_booked)

        # Create Occurrence for Product
        occurrence = Occurrence(
            event=exp_event,
            title=exp_event.title,
            description=f"This occurrence has been created for the product: {new_product.id}.",
            start=exp_event.start,
            end=exp_event.end,
            original_start=exp_event.start,
            original_end=exp_event.end
        )
        occurrence.save()

        new_product.occurrence = occurrence
        new_product.save()

        # Return a JSON response indicating success
        return JsonResponse({'message': 'Product created successfully'}, status=201)

    # If the request method is not POST, return an error response
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def get_event_booking_data(request, event_id):
    actual_data_dict = {}
    event = ExperienceEvent.objects.get(id=event_id)
    actual_data_dict[event.experienceevent.id] = {
        'date': event.experienceevent.start_date,
        'time': event.experienceevent.start_time,
        'adult_price': float(event.experienceevent.special_price),
        'child_price': float(event.experienceevent.child_special_price),
        'max_participants': event.experienceevent.max_participants,
        'booked_participants': event.experienceevent.booked_participants,
        'remaining_participants': event.experienceevent.remaining_participants,
        'experience_event_id': event.experienceevent.id,
    }
    print('result:', actual_data_dict)
    return JsonResponse({'result': actual_data_dict}, status=200)


class EditProductView(DetailView):
    model = Product
    template_name = 'products/edit_booking_form.html'
    queryset = Product.objects.all()
