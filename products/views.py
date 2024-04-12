from django.db.models import Sum
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, DeleteView
from django.db import transaction

from weasyprint import HTML

from products.models import *  # noqa
from products.product_services import get_actual_events_for_experience, update_experience_event_booking, search_experience_by_place_start_lang
from home.forms import ExperienceSearchForm

Customer = settings.AUTH_USER_MODEL


# ----------
# Experience

class ExperienceListView(ListView):
    model = Experience
    template_name = 'experiences/experience_list.html'
    extra_context = {}
    queryset = Experience.active.all()
    paginate_by = 10

    def get_queryset(self):
        current_language = Language.objects.get(code=self.kwargs['lang'].upper())
        self.extra_context['current_language'] = current_language.code.lower()
        place = self.request.GET.get('place')
        date = self.request.GET.get('date')
        queryset = search_experience_by_place_start_lang(place, date, current_language.code)
        if queryset is not None:
            tour_type = self.request.GET.get('tour_type', 'all')
            if tour_type == 'private':
                queryset = queryset.filter(parent_experience__is_private=True)
            elif tour_type == 'group':
                queryset = queryset.filter(parent_experience__is_private=False)
            sort_by = self.request.GET.get('filter_by', 'all')
            if sort_by == 'price_low':
                queryset = queryset.order_by('parent_experience__price')
            elif sort_by == 'price_high':
                queryset = queryset.order_by('-parent_experience__price')
            elif sort_by == 'discount':
                queryset = queryset.order_by('-parent_experience__increase_percentage_old_price')
            elif sort_by == 'hot_deals':
                queryset = queryset.order_by('-parent_experience__is_hot_deals')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        place = self.request.GET.get('place')
        date = self.request.GET.get('date')
        if place is None and date is None:
            initial_data = None
        else:
            initial_data = {'place': place, 'date': date}
        form = ExperienceSearchForm(lang=self.kwargs['lang'].upper(), initial_data=initial_data)
        context['experience_form'] = form
        return context

    def get(self, request, *args, **kwargs):
        place = self.request.GET.get('place')
        date = self.request.GET.get('date')
        if place == '' and date == '':
            # Reset action, redirect to the same view without query parameters
            lang_code = self.kwargs['lang'].lower()
            return HttpResponseRedirect(reverse('experience-list', kwargs={'lang': lang_code}))
        return super().get(request, *args, **kwargs)


class ExperienceDetailView(DetailView):
    model = Experience
    template_name = 'experiences/experience_details.html'
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

class UserIsAuthenticatedOrSessionKeyRequiredMixin:
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
        return super(UserIsAuthenticatedOrSessionKeyRequiredMixin, self).dispatch(request, *args, **kwargs)


class ProductCartView(UserIsAuthenticatedOrSessionKeyRequiredMixin, ListView):
    """View for listing all products for current user (session) only."""
    model = Product
    template_name = 'products/my_cart.html'
    extra_context = {'current_language': 'en'}

    def get_queryset(self):
        return Product.pending.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()  # Ensure queryset is evaluated every time
        print('Cart queryset:', queryset)

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
        booked_number = - self.object.total_booked
        exp_event_id = self.object.occurrence.event_id
        update_result = update_experience_event_booking(exp_event_id, booked_number)
        if not update_result:
            return HttpResponseBadRequest('Not allowed booking number.')
        self.object.status = 'Cancelled'
        self.object.save()
        self.object.occurrence.delete()
        # Instead of calling delete() on the object, change its status
        return HttpResponseRedirect(self.get_success_url())


def get_actual_experience_events(request, parent_experience_id):
    try:
        result = get_actual_events_for_experience(parent_experience_id)
        return JsonResponse({'result': result}, status=200)
    except json.decoder.JSONDecodeError as exp:
        return HttpResponseBadRequest('Invalid JSON data')


# @transaction.atomic
def create_group_product(request):
    print(request.POST)
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
        update_result = update_experience_event_booking(exp_event.id, booked_number=total_booked)
        if not update_result:
            return HttpResponseBadRequest('Not allowed booking number.')

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

        if None in (adults, children, language_code, event_id, product_id):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
            exp_event = ExperienceEvent.objects.get(id=event_id)
            language = Language.objects.get(code=language_code)
        except (Product.DoesNotExist, ExperienceEvent.DoesNotExist, Language.DoesNotExist):
            return JsonResponse({'error': 'Invalid product, event, or language'}, status=400)

        total_booked = adults + children

        if product.occurrence.event_id != exp_event.id:
            update_result = update_experience_event_booking(product.occurrence.event_id, booked_number=-total_booked)
            if not update_result:
                return HttpResponseBadRequest('Not allowed booking number.')
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
            product.start_datetime = exp_event.start
            product.end_datetime = exp_event.end
            product.adults_count = adults
            product.child_count = children
            product.adults_price = exp_event.special_price
            product.child_price = exp_event.child_special_price
            product.language = language
            product.save()
            update_result = update_experience_event_booking(exp_event.id, booked_number=total_booked)
            if not update_result:
                return HttpResponseBadRequest('Not allowed booking number.')
        else:
            if product.adults_count != adults or product.child_count != children:
                product.adults_count = adults
                product.child_count = children
            if product.language != language:
                product.language = language
                update_result = update_experience_event_booking(product.occurrence.event_id, booked_number=-total_booked)
                if not update_result:
                    return HttpResponseBadRequest('Not allowed booking number.')
                update_result = update_experience_event_booking(product.occurrence.event_id, booked_number=total_booked)
                if not update_result:
                    return HttpResponseBadRequest('Not allowed booking number.')
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
        'max_participants': event.experienceevent.max_participants,
        'booked_participants': event.experienceevent.booked_participants,
        'remaining_participants': event.experienceevent.remaining_participants,
        'experience_event_id': event.experienceevent.id,
    }
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


@transaction.atomic
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
        update_result = update_experience_event_booking(exp_event.id, booked_number=total_booked)
        if not update_result:
            return HttpResponseBadRequest('Not allowed booking number.')

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


@transaction.atomic
def update_private_product(request):
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

        if None in (adults, children, language_code, event_id, product_id):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
            exp_event = ExperienceEvent.objects.get(id=event_id)
            language = Language.objects.get(code=language_code)
        except (Product.DoesNotExist, ExperienceEvent.DoesNotExist, Language.DoesNotExist):
            return JsonResponse({'error': 'Invalid product, event, or language'}, status=400)

        total_booked = adults + children

        if product.occurrence.event_id != exp_event.id:
            update_result = update_experience_event_booking(product.occurrence.event_id, booked_number=-total_booked)
            if not update_result:
                return HttpResponseBadRequest('Not allowed booking number.')
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
            product.start_datetime = exp_event.start
            product.end_datetime = exp_event.end
            product.adults_count = adults
            product.child_count = children
            product.total_price = exp_event.total_price
            product.language = language
            product.save()
            update_result = update_experience_event_booking(exp_event.id, booked_number=total_booked)
            if not update_result:
                return HttpResponseBadRequest('Not allowed booking number.')
        else:
            if product.adults_count != adults or product.child_count != children:
                product.adults_count = adults
                product.child_count = children
            if product.language != language:
                product.language = language
                update_result = update_experience_event_booking(product.occurrence.event_id, booked_number=-total_booked)
                if not update_result:
                    return HttpResponseBadRequest('Not allowed booking number.')
                update_result = update_experience_event_booking(product.occurrence.event_id, booked_number=total_booked)
                if not update_result:
                    return HttpResponseBadRequest('Not allowed booking number.')
            product.save()
        logger.info(f"Product {product.id} was updated.")
        return JsonResponse({'message': 'Product updated successfully'}, status=201)

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


# PDF Generator

def generate_pdf(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    experience = product.parent_experience.child_experiences.filter(language_id=product.language_id).first()
    context = {'product': product, 'experience': experience}
    html_template = render_to_string('products/product_pdf.html', context)
    pdf_file = HTML(string=html_template).write_pdf()

    filename = f'Booked_{product_id}.pdf'
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def create_product(request):
    print('request.POST', request.POST)
    if request.method == 'POST':
        data = json.loads(request.body)

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
