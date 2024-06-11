# admin_views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from schedule.models import Occurrence
from products.models import ExperienceEvent


@staff_member_required
def calendar_view(request, event_id):
    event = get_object_or_404(ExperienceEvent, id=event_id)
    return render(request, 'admin/calendar.html', {'event': event})


@staff_member_required
def events_view(request):
    events = ExperienceEvent.objects.all()
    return render(request, 'admin/event.html', {'events': events})


@staff_member_required
def event_occurrences(request, event_id):
    event = get_object_or_404(ExperienceEvent, id=event_id)
    occurrences = Occurrence.objects.filter(event=event)
    occurrences_list = [{
        'title': occurrence.title,
        'start': occurrence.start.isoformat(),
        'end': occurrence.end.isoformat()
    } for occurrence in occurrences]
    return JsonResponse(occurrences_list, safe=False)
