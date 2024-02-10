from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as accounts_views
from destinations import views as destinations_views
from attractions import views as attractions_views
from products import views as products_views

# HOME & ACCOUNTS
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accounts_views.HomeView.as_view(), name='home'),
    path('accounts/signup/', accounts_views.RegistrationView.as_view(), name='signup'),
    path("accounts/", include("django.contrib.auth.urls")),
    # built-in path's:
    # accounts/login/ [name='login']
    # accounts/logout/ [name='logout']
    # accounts/password_change/ [name='password_change']
    # accounts/password_change/done/ [name='password_change_done']
    # accounts/password_reset/ [name='password_reset']
    # accounts/password_reset/done/ [name='password_reset_done']
    # accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
    # accounts/reset/done/ [name='password_reset_complete']
]

# Django ckeditor: https://github.com/django-ckeditor/django-ckeditor
urlpatterns += [path('ckeditor/', include('ckeditor_uploader.urls')),]

# DESTINATIONS
urlpatterns += [
    path('destinations/<str:lang>/', destinations_views.DestinationListView.as_view(), name='destination-list'),
    path('destinations/<str:lang>/<slug:slug>/', destinations_views.DestinationDetailView.as_view(), name="destination-detail"),
]

# ATTRACTIONS
urlpatterns += [
    path('attractions/<str:lang>/', attractions_views.AttractionListView.as_view(), name="attraction-list"),
    path('attractions/<str:lang>/<slug:slug>/', attractions_views.AttractionDetailView.as_view(), name="attraction-detail"),
]

# EXPERIENCES
urlpatterns += [
    path('experiences/<str:lang>/', products_views.ExperienceListView.as_view(), name="experience-list"),
    path('experiences/<str:lang>/<slug:slug>/', products_views.ExperienceDetailView.as_view(), name='experience-detail'),
]

# Add static URL mapping for serving static files from DigitalOcean Spaces
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files during development.
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
