# admin_views.py
from django.core.serializers import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from products.models import ExperienceEvent, Calendar


@staff_member_required
def calendar_view(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    return render(request, 'admin/schedule/calendar/change_form.html', {'original': calendar})


# @staff_member_required
# @csrf_exempt
def events_view(request, calendar_id):
    try:
        calendar = Calendar.objects.get(pk=calendar_id)
        events = calendar.events.all()
        print('events:', events)
        events_list = [{
            'title': event.title,
            'start': event.start.isoformat(),
            'end': event.end.isoformat()
        } for event in events]
        return JsonResponse({'result': events_list}, status=200)
    except json.decoder.JSONDecodeError as exp:
        return HttpResponseBadRequest(f'Invalid JSON data: {exp}')
