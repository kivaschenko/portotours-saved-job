# admin_urls.py
from django.urls import path
from .admin_views import calendar_view, events_view, event_occurrences

urlpatterns = [
    path('calendar/<int:event_id>/', calendar_view, name='admin-calendar'),
    path('events/', events_view, name='admin-events'),
    path('event_occurrences/<int:event_id>/', event_occurrences, name='event-occurrences'),
]
