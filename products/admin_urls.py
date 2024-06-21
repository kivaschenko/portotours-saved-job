# admin_urls.py
from django.urls import path
from .admin_views import calendar_view, events_view

urlpatterns = [
    path('schedule/calendar/<int:calendar_id>/change/', calendar_view, name='admin-calendar'),
    path('schedule/events/<int:calendar_id>', events_view, name='admin-events'),
]
