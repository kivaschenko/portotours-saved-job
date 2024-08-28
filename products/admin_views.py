# admin_views.py
from django.core.serializers import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from products.models import ExperienceEvent, Calendar


@staff_member_required
def calendar_view(request, calendar_id):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    print(calendar)
    return render(request, 'admin/schedule/calendar/change_form.html', {'original': calendar})
