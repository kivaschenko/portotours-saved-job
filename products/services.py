import logging
from datetime import datetime, timedelta
from typing import Optional, Any, Union

from django.contrib.contenttypes.models import ContentType
from schedule.models import Event, EventRelation, Calendar, Rule

from products.models import ParentExperience

logger = logging.getLogger(__name__)


# Handling ParentExperience and Event creating

def create_event_for_parent_experience(start_datetime: Union[str, datetime], end_datetime: Union[str, datetime],
                                       title: str, parent_experience_id: int,
                                       description: str = '', creator_id: int = 1,
                                       rule_name: str = None, end_recurring_period: datetime = None,
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
    event, _ = Event.objects.get_or_create(start=start, end=end, title=title, description=description,
                                           creator_id=creator_id,
                                           rule=rule, end_recurring_period=end_recurring_period,
                                           calendar=calendar, color_event=color_event)
    # bind new Event to ParentExperience
    relation, _ = EventRelation.objects.get_or_create(
        event,
        content_type=ContentType.objects.get_for_model('products.ParentExperience'),
        object_id=parent_experience_id,
        distinction='owner'
    )
    return event, relation


# New booking logic

def get_actual_events_for_experience(parent_experience_id: int) -> dict:
    actual_events_dict = {}
    now = datetime.utcnow()
    try:
        parent_experience = ParentExperience.objects.get(id=parent_experience_id)
        calendar = Calendar.objects.get_calendars_for_object(parent_experience).first()
        actual_events = calendar.events.filter(start__gte=now)

        if len(actual_events) > 0:
            for event in actual_events:
                actual_events_dict[event.experienceevent.start_date] = {
                    'time': event.experienceevent.start_time,
                    'adult_price': str(event.experienceevent.special_price),
                    'child_price': str(event.experienceevent.child_special_price),
                    'remaining_participants': event.experienceevent.remaining_participants,
                }
    except EventRelation.DoesNotExist:
        logger.error(f'No events found for ParentExperience id={parent_experience_id}')
    return actual_events_dict
    