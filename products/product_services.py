import logging
from datetime import datetime, timedelta
from typing import Any, Union

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.utils import timezone
from schedule.models import Event, EventRelation, Calendar, Rule

from destinations.models import Destination
from products.models import ParentExperience, ExperienceEvent, Experience, Language

logger = logging.getLogger(__name__)


# Handling ParentExperience and Event creating

def create_event_for_parent_experience(start_datetime: Union[str, datetime], end_datetime: Union[str, datetime], title: str, parent_experience_id: int,
                                       description: str = '', creator_id: int = 1, rule_name: str = None, end_recurring_period: datetime = None,
                                       calendar_name: str = None, color_event: str = '#BF4040') -> tuple[Event, Any]:
    """Use primitive arguments to create an event, as it can be handled by a Celery task."""
    if type(start_datetime) is str:
        start = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M')
    else:
        start = start_datetime
    if type(end_datetime) is str:
        end = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M')
    else:
        end = end_datetime

    if rule_name is None:
        # set by default Daily
        rule, _ = Rule.objects.get_or_create(name="Daily")
    else:
        rule, _ = Rule.objects.get_or_create(name=rule_name)
    if calendar_name is None:
        # use by default common Experience Calendar
        calendar, _ = Calendar.objects.get_or_create(name="Experience Calendar")
    else:
        calendar, _ = Calendar.objects.get_or_create(name=calendar_name)
    if end_recurring_period is None:
        # set by default 1 month duration
        end_recurring_period = end + timedelta(days=31)
    event, _ = Event.objects.get_or_create(start=start, end=end, title=title, description=description, creator_id=creator_id, rule=rule,
                                           end_recurring_period=end_recurring_period, calendar=calendar, color_event=color_event)
    # bind new Event to ParentExperience
    relation, _ = EventRelation.objects.get_or_create(event, content_type=ContentType.objects.get_for_model('products.ParentExperience'),
                                                      object_id=parent_experience_id, distinction='owner')
    return event, relation


# New booking logic

def get_actual_events_for_experience(parent_experience_id: int) -> dict:
    result = {}
    if not ParentExperience.objects.filter(id=parent_experience_id).exists():
        return result
    parent_experience = ParentExperience.objects.get(id=parent_experience_id)
    languages_queryset = parent_experience.allowed_languages.values_list('code', flat=True)
    result['languages'] = list(languages_queryset)
    actual_events_list = []
    now = datetime.utcnow()
    try:
        calendar = Calendar.objects.get_calendars_for_object(parent_experience).first()
        actual_events = calendar.events.filter(start__gte=now, experienceevent__remaining_participants__gt=0)

        if len(actual_events) > 0:
            for event in actual_events:
                adult_price = float(0)
                child_price = float(0)
                total_price = float(0)
                if event.experienceevent.total_price is not None:
                    total_price = float(event.experienceevent.total_price)
                if event.experienceevent.special_price is not None:
                    adult_price = float(event.experienceevent.special_price)
                if event.experienceevent.child_special_price is not None:
                    child_price = float(event.experienceevent.child_special_price)
                actual_events_list.append(
                    {'date': event.experienceevent.start_date, 'time': event.experienceevent.start_time, 'adult_price': adult_price, 'child_price': child_price,
                     'max_participants': event.experienceevent.max_participants, 'booked_participants': event.experienceevent.booked_participants,
                     'remaining_participants': event.experienceevent.remaining_participants, 'experience_event_id': event.experienceevent.id,
                     'is_private': parent_experience.is_private, 'total_price': total_price, })
            result['events'] = actual_events_list
    except EventRelation.DoesNotExist:
        logger.error(f'No events found for ParentExperience id={parent_experience_id}')
    finally:
        return result


def update_experience_event_booking(exp_event_id: int, booked_number: int) -> bool:
    exp_event = ExperienceEvent.objects.get(id=exp_event_id)
    if booked_number > 0:
        if exp_event.remaining_participants < booked_number:
            logger.error(f'Booked number {booked_number} exceeds number of participants')
            return False
        else:
            exp_event.booked_participants += booked_number
            exp_event.save()
            exp_event.remaining_participants = exp_event.max_participants - exp_event.booked_participants
            exp_event.save()
    elif booked_number < 0:
        if exp_event.booked_participants < booked_number:
            logger.error(f'Booked number {booked_number} exceeds number of participants')
            return False
        else:
            exp_event.booked_participants += booked_number
            exp_event.save()
            exp_event.remaining_participants = exp_event.max_participants - exp_event.booked_participants
            exp_event.save()
    logger.info(f'Booked number {booked_number} updated')
    return True


# def search_experience_by_place_start_lang(place: str, start_date: str, current_language: str) -> list:
#     destination = Destination.active.filter(slug=place).first()
#     if not destination:
#         return Experience.objects.none()
#
#     experiences = Experience.active.filter(destinations=destination, language__code=current_language)
#     if not experiences.exists():
#         return Experience.objects.none()
#
#     start = timezone.datetime.strptime(start_date, "%Y-%m-%d") - timezone.timedelta(days=2)
#     end = start + timezone.timedelta(days=30)
#
#     filtered_experiences = []
#     for experience in experiences:
#         events = EventRelation.objects.get_events_for_object(
#             experience.parent_experience, distinction='experience event').filter(
#             start__range=(start, end), experienceevent__remaining_participants__gte=1)
#         if events.exists():
#             filtered_experiences.append(experience)
#
#     return filtered_experiences


def search_experience_by_place_start_lang(place: str, start_date: str, current_language: str) -> QuerySet:
    # Fetch the Language instance based on the provided language code
    language_instance = Language.objects.filter(code=current_language).first()
    if not language_instance:
        return Experience.objects.none()

    experiences = Experience.active.filter(language=language_instance).distinct().order_by('-parent_experience__priority_number')
    if not experiences.exists():
        return Experience.objects.none()
    experiences_to_remove = []
    if place:
        destination = Destination.active.filter(slug=place).first()
        if not destination:
            return Experience.objects.none()
        else:
            experiences = experiences.filter(destinations=destination)
    if start_date:
        # Convert the start date to a timezone-aware datetime object
        start = timezone.make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
        start = start - timezone.timedelta(days=2)
        if start < timezone.now():
            start = timezone.now()
        end = start + timezone.timedelta(days=60)
        for experience in experiences:
            events = EventRelation.objects.get_events_for_object(
                experience.parent_experience, distinction='experience event'
            ).filter(
                start__range=(start, end), experienceevent__remaining_participants__gte=1
            )
            if not events.exists():
                experiences_to_remove.append(experience)
    if experiences_to_remove:
        experiences = experiences.exclude(pk__in=[exp.pk for exp in experiences_to_remove])

    return experiences


def prepare_google_items_for_cart(products_queryset: QuerySet) -> list[dict]:
    items = []
    if products_queryset.exists():
        for product in products_queryset:
            experience = product.parent_experience.child_experiences.first()
            item = experience.ecommerce_items
            item.update({
                'currency': "EUR",
                'price': float(product.total_price),
                'quantity': product.total_booked,
                'item_variant': product.language.code.upper(),
            })
            items.append(item)
    return items


# Second purchase discount logic
def get_actual_events_for_experience_with_second_purchase_discount(parent_experience_id: int) -> dict:
    result = {}
    if not ParentExperience.objects.filter(id=parent_experience_id).exists():
        return result
    parent_experience = ParentExperience.objects.get(id=parent_experience_id)
    languages_queryset = parent_experience.allowed_languages.values_list('code', flat=True)
    result['languages'] = list(languages_queryset)
    actual_events_list = []
    now = datetime.utcnow()
    try:
        calendar = Calendar.objects.get_calendars_for_object(parent_experience).first()
        actual_events = calendar.events.filter(start__gte=now, experienceevent__remaining_participants__gt=0)

        if len(actual_events) > 0:
            for event in actual_events:
                adult_price = float(0)
                child_price = float(0)
                total_price = float(0)
                if event.experienceevent.total_price is not None:
                    total_price = float(event.experienceevent.total_price - parent_experience.second_purchase_discount)
                if event.experienceevent.special_price is not None:
                    adult_price = float(event.experienceevent.special_price - parent_experience.second_purchase_discount)
                if event.experienceevent.child_special_price is not None:
                    child_price = float(event.experienceevent.child_special_price)
                actual_events_list.append(
                    {'date': event.experienceevent.start_date, 'time': event.experienceevent.start_time, 'adult_price': adult_price, 'child_price': child_price,
                     'max_participants': event.experienceevent.max_participants, 'booked_participants': event.experienceevent.booked_participants,
                     'remaining_participants': event.experienceevent.remaining_participants, 'experience_event_id': event.experienceevent.id,
                     'is_private': parent_experience.is_private, 'total_price': total_price, })
            result['events'] = actual_events_list
    except EventRelation.DoesNotExist:
        logger.error(f'No events found for ParentExperience id={parent_experience_id}')
    finally:
        return result


