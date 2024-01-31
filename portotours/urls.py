from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as accounts_views
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

# DESTINATIONS
urlpatterns += [
    # path('products/portugal/destinations/some-test-slug-for-current-destionation-detail-view/',
    #      products_views.DestinationDetailView.as_view(), name="destination-detail"),  # <- remove this before merge to master!
    path('products/portugal/destinations/', products_views.DestinationListView.as_view(), name="destination-list"),
    path('destinations/<str:lang>/', products_views.DestinationLanguageListView.as_view(), name='destination-list-by-language'),
    path('products/portugal/destinations/<slug:slug>/', products_views.DestinationDetailView.as_view(), name="destination-detail"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
