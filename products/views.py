from django.db.models import Sum
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

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
            self.extra_context['customer_id'] = None
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
    extra_context = {'current_language': 'en'}

    def get_queryset(self):
        return Product.pending.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()  # Ensure queryset is evaluated every time
        print('queryset:', queryset)

        context['product_ids'] = [product.pk for product in queryset]
        context['total_price_sum'] = queryset.aggregate(total_price_sum=Sum('total_price'))['total_price_sum'] or 0
        context['old_price_sum'] = queryset.aggregate(old_price_sum=Sum('old_total_price'))['old_price_sum'] or 0
        context['discounted_price_sum'] = round(context['old_price_sum'] - context['total_price_sum'], 2)

        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context


class CancelProductView(DeleteView):
    model = Product
    template_name = 'products/cancel_form.html'
    success_url = reverse_lazy('my-cart', kwargs={'lang': 'en'})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Update certain ExperienceEvent: change booked_participants and remaining_participants!
        self.object.occurrence.event.experienceevent.update_booking_data(booked_number=-self.object.total_booked)
        self.object.occurrence.delete()
        self.object.status = 'Cancelled'
        self.object.save()
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
def create_group_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # Extract data from JSON
        adults = data.get('adults')
        children = data.get('children')
        language_code = data.get('language_code')
        customer_id = data.get('customer_id')
        session_key = data.get('session_key')
        event_id = data.get('event_id')
        parent_experience_id = data.get('parent_experience_id')

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


@csrf_exempt
@transaction.atomic
def update_group_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            adults = data.get('adults')
            children = data.get('children')
            language_code = data.get('language_code')
            event_id = data.get('event_id')
            product_id = data.get('product_id')
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # Data validation
        if None in (adults, children, language_code, event_id, product_id):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
            exp_event = ExperienceEvent.objects.get(id=event_id)
            language = Language.objects.get(code=language_code)
        except (Product.DoesNotExist, ExperienceEvent.DoesNotExist, Language.DoesNotExist):
            return JsonResponse({'error': 'Invalid product, event, or language'}, status=400)

        total_booked = adults + children

        # Update logic
        if product.occurrence.event_id != exp_event.id:
            # Update for new event
            product.occurrence.event.experienceevent.update_booking_data(booked_number=-total_booked)
            product.occurrence.delete()
            occurrence = Occurrence.objects.create(
                event=exp_event,
                title=exp_event.title,
                description=f"This occurrence has been created for the product: {product.id}.",
                start=exp_event.start,
                end=exp_event.end,
                original_start=exp_event.start,
                original_end=exp_event.end
            )
            product.occurrence = occurrence
            product.save()
            product.objects.update(
                occurrence=occurrence,
                start_datetime=exp_event.start,
                end_datetime=exp_event.end,
                adults_price=exp_event.special_price,
                child_price=exp_event.child_special_price,
                language=language
            )
            exp_event.update_booking_data(booked_number=total_booked)
        else:
            # Update for current event
            if product.adults_count != adults or product.child_count != children:
                product.adults_count = adults
                product.child_count = children
                product.occurrence.event.experienceevent.update_booking_data(booked_number=-total_booked)
                product.occurrence.event.experienceevent.update_booking_data(booked_number=total_booked)
            if product.language != language:
                product.language = language
            product.save()

        logger.info(f"Product {product.id} was updated.")
        return JsonResponse({'message': 'Product updated successfully'}, status=201)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def get_event_booking_data(request, event_id):
    actual_data_dict = {}
    event = ExperienceEvent.objects.get(id=event_id)
    actual_data_dict[event.experienceevent.id] = {
        'date': event.experienceevent.start_date,
        'time': event.experienceevent.start_time,
        'adult_price': float(event.experienceevent.special_price),
        'child_price': float(event.experienceevent.child_special_price),
        # 'total_price': float(event.experienceevent.total_price),
        'max_participants': event.experienceevent.max_participants,
        'booked_participants': event.experienceevent.booked_participants,
        'remaining_participants': event.experienceevent.remaining_participants,
        'experience_event_id': event.experienceevent.id,
    }
    print('result:', actual_data_dict)
    return JsonResponse({'result': actual_data_dict}, status=200)


def get_private_event_booking_data(request, event_id):
    actual_data_dict = {}
    event = ExperienceEvent.objects.get(id=event_id)
    actual_data_dict[event.experienceevent.id] = {
        'date': event.experienceevent.start_date,
        'time': event.experienceevent.start_time,
        'total_price': float(event.experienceevent.total_price),
        'max_participants': event.experienceevent.max_participants,
        'booked_participants': event.experienceevent.booked_participants,
        'remaining_participants': event.experienceevent.remaining_participants,
        'experience_event_id': event.experienceevent.id,
    }
    print('result:', actual_data_dict)
    return JsonResponse({'result': actual_data_dict}, status=200)


class EditProductView(DetailView):
    model = Product
    template_name = 'products/update_product.html'
    queryset = Product.objects.all()
    extra_context = {}

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def setup(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.extra_context.update({'customer_id': request.user.id})
            self.extra_context.update({'session_key': request.session.session_key})
        else:
            self.extra_context['customer_id'] = None
            # If the user is not authenticated, get the current session
            if not request.session.exists(request.session.session_key):
                request.session.create()
            self.extra_context.update({'session_key': request.session.session_key})
        kwargs = super(EditProductView, self).setup(request, *args, **kwargs)
        return kwargs


@csrf_exempt
def create_private_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # Extract data from JSON
        adults = data.get('adults')
        children = data.get('children')
        language_code = data.get('language_code')
        customer_id = data.get('customer_id')
        session_key = data.get('session_key')
        event_id = data.get('event_id')
        parent_experience_id = data.get('parent_experience_id')

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
            total_price=exp_event.total_price,
            adults_count=adults,
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


@csrf_exempt
def update_private_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # Extract data from JSON
        adults = data.get('adults')
        children = data.get('children')
        language_code = data.get('language_code')
        event_id = data.get('event_id')
        product_id = data.get('product_id')

        total_booked = adults + children

        # Get Product
        product = Product.objects.get(id=product_id)

        # Get ExperienceEvent obj
        exp_event = ExperienceEvent.objects.get(id=event_id)

        # Get language
        language = Language.objects.get(code=language_code)

        # Check if the same event is used for the product
        if product.occurrence.event_id != exp_event.id:
            # cancellation the booking for old event
            product.occurrence.event.experienceevent.update_booking_data(booked_number=-total_booked)
            # create booking for new event
            product.start_date = exp_event.start
            product.end_date = exp_event.end
            product.total_price = exp_event.total_price
            if product.language != language:
                product.language = language
            product.save()

            # Update ExperienceEvent data for new event
            exp_event.update_booking_data(booked_number=total_booked)

            # Update Occurrence for Product
            occurrence = product.occurrence
            occurrence.event = exp_event.event_ptr,
            occurrence.title = exp_event.title,
            occurrence.description = f"This occurrence has been created for the product: {product.id}.",
            occurrence.start = exp_event.start,
            occurrence.end = exp_event.end,
            occurrence.original_start = exp_event.start,
            occurrence.original_end = exp_event.end
            occurrence.save()

            product.occurrence = occurrence
            product.save()
        else:
            # update data for current product event
            if product.adults_count != adults or product.child_count != children:
                product.adults_count = adults
                product.child_count = children
                # cancellation the booking
                product.occurrence.event.experienceevent.update_booking_data(booked_number=-total_booked)
                # rebooking with new data
                product.occurrence.event.experienceevent.update_booking_data(booked_number=total_booked)
            if product.language != language:
                product.language = language
            product.save()
            # update
        logger.info(f"Product {product.id} was updated.")

        # Return a JSON response indicating success
        return JsonResponse({'message': 'Product updated successfully'}, status=201)

    # If the request method is not POST, return an error response
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


# 404, 500 ERRORS HANDLERS

def custom_page_not_found_view(request, exception):
    return render(request, "errors/404.html", {})


def custom_error_view(request, exception=None):
    return render(request, "errors/500.html", {})


def custom_permission_denied_view(request, exception=None):
    return render(request, "errors/403.html", {})


def custom_bad_request_view(request, exception=None):
    return render(request, "errors/400.html", {})
