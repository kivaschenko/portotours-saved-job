from datetime import timedelta

from django.db.models import ExpressionWrapper, F, DurationField
from django.views.generic import DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

from schedule.models import EventRelation

from products.models import Experience, ParentExperience, ExperienceEvent
from reviews.models import Testimonial
from destinations.models import Destination

from .models import LandingPage


class LandingPageView(DetailView):
    model = LandingPage
    template_name = 'landing_pages/landing_page.html'
    queryset = LandingPage.active.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = self.kwargs.get('lang', 'en')
        context['current_language'] = lang
        parent_experiences = ParentExperience.objects.filter(categories=self.object.category)

        experiences = []
        for par_exp in parent_experiences:
            found_experience = par_exp.child_experiences.filter(is_active=True, language__code=lang.upper()).first()
            if found_experience:
                experiences.append(found_experience)

        if experiences:
            experiences_queryset = Experience.objects.filter(
                pk__in=[exp.pk for exp in experiences]
            )
            tour_type = self.request.GET.get('tour_type', 'all')
            if tour_type in ['private', 'group']:
                experiences_queryset = experiences_queryset.filter(
                    parent_experience__is_private=(tour_type == 'private')
                )

            sort_by = self.request.GET.get('filter_by', 'all')
            if sort_by in ['price_low', 'price_high', 'discount', 'hot_deals']:
                order_by_field = {
                    'price_low': 'parent_experience__price',
                    'price_high': '-parent_experience__price',
                    'discount': '-parent_experience__increase_percentage_old_price',
                    'hot_deals': '-parent_experience__is_hot_deals',
                }.get(sort_by)
                if order_by_field:
                    experiences_queryset = experiences_queryset.order_by(order_by_field)

            start = timezone.now()
            end = start + timezone.timedelta(days=30)

            time_of_day = self.request.GET.get('time_of_day', 'all')
            if time_of_day != 'all':
                experiences_to_remove = []
                time_filters = {
                    'morning': {'start__hour__lt': 12},
                    'afternoon': {'start__hour__gte': 12, 'start__hour__lte': 17},
                    'evening': {'start__hour__lte': 17},
                }
                for experience in experiences_queryset:
                    events = EventRelation.objects.get_events_for_object(
                        experience.parent_experience, distinction='experience event'
                    ).filter(
                        start__range=(start, end), experienceevent__remaining_participants__gte=1
                    ).filter(
                        **time_filters.get(time_of_day, {})
                    )
                    if not events.exists():
                        experiences_to_remove.append(experience)

                if experiences_to_remove:
                    experiences_queryset = experiences_queryset.exclude(pk__in=[exp.pk for exp in experiences_to_remove])

            duration = self.request.GET.get('duration', 'all')
            if duration != 'all':
                experiences_to_remove = []
                duration_filters = {
                    '0-1': {'duration__lte': timedelta(hours=1)},
                    '1-4': {'duration__gt': timedelta(hours=1), 'duration__lte': timedelta(hours=4)},
                    '4-10': {'duration__gt': timedelta(hours=4), 'duration__lte': timedelta(hours=10)},
                    '24-72': {'duration__gt': timedelta(hours=24), 'duration__lte': timedelta(hours=72)},
                }
                duration_filter = duration_filters.get(duration, {})
                for experience in experiences_queryset:
                    events = EventRelation.objects.get_events_for_object(
                        experience.parent_experience, distinction='experience event'
                    ).filter(
                        start__range=(start, end), experienceevent__remaining_participants__gte=1
                    ).annotate(
                        duration=ExpressionWrapper(F('end') - F('start'), output_field=DurationField())
                    ).filter(
                        **duration_filter
                    )
                    if not events.exists():
                        experiences_to_remove.append(experience)

                if experiences_to_remove:
                    experiences_queryset = experiences_queryset.exclude(pk__in=[exp.pk for exp in experiences_to_remove])

            if self.object.destinations.all():
                experiences_queryset = experiences_queryset.filter(destinations__in=self.object.destinations.all())
                destinations = self.object.destinations.values_list('slug', 'name')
            else:
                destination_ids_list = experiences_queryset.values_list('destinations', flat=True)
                unique_destination_ids = set(destination_ids_list)
                destinations = Destination.active.filter(id__in=unique_destination_ids).values_list('slug', 'name')
            context['destinations'] = [(slug, name) for slug, name in destinations]
            destination_slug = self.request.GET.get('destination', 'all')
            if destination_slug != 'all':
                experiences_queryset = experiences_queryset.filter(destinations__slug=destination_slug)
        else:
            experiences_queryset = Experience.objects.none()

        page = self.request.GET.get('page', 1)
        paginator = Paginator(experiences_queryset, 10)
        try:
            experiences_paginated = paginator.page(page)
        except PageNotAnInteger:
            experiences_paginated = paginator.page(1)
        except EmptyPage:
            experiences_paginated = paginator.page(paginator.num_pages)
        context['experiences'] = experiences_paginated
        context['testimonials'] = Testimonial.objects.all()[:6]
        return context
