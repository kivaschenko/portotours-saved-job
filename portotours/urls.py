from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from accounts import views as accounts_views
from destinations import views as destinations_views
from attractions import views as attractions_views
from products import views as products_views
from purchases import views as purchases_views
from blogs import views as blogs_views

# HOME & ACCOUNTS
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accounts_views.HomeView.as_view(), name='home'),
    path('accounts/signup/', accounts_views.RegistrationView.as_view(), name='signup'),
    path('login/', accounts_views.CustomLoginView.as_view(), name='login'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # path("accounts/", include("django.contrib.auth.urls")),
    # Password reset
    path('password_reset/', accounts_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', accounts_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', accounts_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', accounts_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Password change
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/customized/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/customized/password_change_done.html'), name='password_change_done'),
    # Profile
    path("accounts/profile/", accounts_views.ProfileView.as_view(), name="profile"),
    path("accounts/profile/update-address/", accounts_views.AddressUpdateView.as_view(), name="address-update"),
    path("accounts/profile/upate-shipping-address/", accounts_views.ShippingAddressUpdateView.as_view(), name="shipping-address-update"),
    path("__debug__/", include("debug_toolbar.urls")),
]

# Django ckeditor: https://github.com/django-ckeditor/django-ckeditor
urlpatterns += [path('ckeditor/', include('ckeditor_uploader.urls')), ]

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

# EXPERIENCES, Calendar, Events
urlpatterns += [
    path('experiences/<str:lang>/', products_views.ExperienceListView.as_view(), name="experience-list"),
    path('experiences/<str:lang>/<slug:slug>/', products_views.ExperienceDetailView.as_view(), name='experience-detail'),
    path('actual-experience-events/<int:parent_experience_id>/', products_views.get_actual_experience_events, name='actual-experience-events'),
    path('experience-event-data/<int:event_id>/', products_views.get_event_booking_data, name='experience-event-data'),
]

# PRODUCTS & PURCHASES
urlpatterns += [
    path('create-checkout-session/', purchases_views.checkout_view, name='checkout-session'),
    path('stripe-webhook/', purchases_views.stripe_webhook, name='stripe-webhook'),
    path('my-cart/<str:lang>/', products_views.ProductCartView.as_view(), name='my-cart'),
    path('products/<int:pk>/cancel/', products_views.CancelProductView.as_view(), name='cancel-product'),
    path('payment-form/<str:lang>/', purchases_views.BillingDetailView.as_view(), name='payment-form'),
    path('confirmation/<str:lang>/', purchases_views.ConfirmationView.as_view(), name='confirmation'),
    path('purchase/get-pdf/<int:purchase_id>/', purchases_views.generate_purchase_pdf, name='generate-pdf'),
    path('create-product/', products_views.create_group_product, name='create-product'),
    path('create-private-product/', products_views.create_private_product, name='create-private-product'),
    path('edit-product/<int:pk>/', products_views.EditProductView.as_view(), name='edit-product'),
]

# BLOGS
urlpatterns += [
    path('blogs/<str:lang>/', blogs_views.BlogListView.as_view(), name='blog-list'),
    path('blogs/<str:lang>/<slug:slug>/', blogs_views.BlogDetailView.as_view(), name='blog-detail'),
]

# Scheduler urls
urlpatterns += [
    path("", include('schedule.urls'))
]


# Add static file serving during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# Add static URL mapping for serving static files from DigitalOcean Spaces
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add static URL mapping for serving media files from DigitalOcean Spaces
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
