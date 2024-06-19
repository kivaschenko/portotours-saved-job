from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from accounts import views as accounts_views
from attractions import views as attractions_views
from attractions.sitemaps import AttractionSitemap
from blogs import views as blogs_views
from blogs.sitemaps import BlogSitemap
from destinations import views as destinations_views
from destinations.sitemaps import DestinationSitemap
from home import views as home_views
from home.sitemaps import PageSitemap, AboutUsSitemap
from landing_pages import views as landing_pages_views
from landing_pages.sitemaps import LandingPageSitemap
from products import views as products_views
from products.sitemaps import ExperienceSitemap
from purchases import views as purchases_views
from reviews import views as reviews_views
from .sitemaps import ListSitemap

sitemaps = {
    'attractions': AttractionSitemap,
    'destinations': DestinationSitemap,
    'blogs': BlogSitemap,
    'experiences': ExperienceSitemap,
    'pages': PageSitemap,
    'company': AboutUsSitemap,
    'landing_pages': LandingPageSitemap,
    'lists': ListSitemap,
}

# 404, 500 ERRORS
handler404 = 'products.views.custom_page_not_found_view'
handler500 = 'products.views.custom_error_view'
handler403 = 'products.views.custom_permission_denied_view'
handler400 = 'products.views.custom_bad_request_view'

# Booking, payment endpoints
urlpatterns = [
    # API for JS Real Booking is happening
    # Check what exactly url out is using in JS files for booking:
    # static/js/first_booking.js
    # static/js/first_booking_private.js
    # static/js/update_private_product.js
    # static/js/update_product.js
    path('create-product/', products_views.create_group_product, name='create-product'),
    path('update-product/', products_views.update_group_product, name='update-product'),
    path('create-private-product/', products_views.create_private_product, name='create-private-product'),
    path('update-private-product/', products_views.update_private_product, name='update-private-product'),
    # Create & Update Products without real booking
    path('create-group-product-without-booking/', products_views.create_group_product_without_booking, name='create-group-product-without-booking'),
    path('update-group-product-without-booking/', products_views.update_group_product_without_booking, name='update-group-product-without-booking'),
    path('create-private-product-without-booking/', products_views.create_private_product_without_booking, name='create-private-product-without-booking'),
    path('update-private-product-without-booking/', products_views.update_private_product_without_booking, name='update-private-product-without-booking'),
]

# PRODUCTS & PURCHASES
urlpatterns += [
    path('checkout/', purchases_views.checkout_payment_intent_view, name='checkout-payment-intent'),
    path('my-cart/<str:lang>/', products_views.ProductCartView.as_view(), name='my-cart'),
    path('en/products/<int:pk>/cancel/', products_views.CancelProductView.as_view(), name='cancel-product'),
    path('en/products/delete/<int:pk>/', products_views.DeleteProductView.as_view(), name='delete-product'),
    path('payment-form/<str:lang>/', purchases_views.BillingDetailView.as_view(), name='payment-form'),
    path('confirmation/<str:lang>/', purchases_views.ConfirmationView.as_view(), name='confirmation'),
    path('en/edit-product/<int:pk>/', products_views.EditProductView.as_view(), name='edit-product'),
    path('en/generate-pdf/<int:product_id>/', products_views.generate_pdf, name='generate-pdf'),
    # Stripe web-hook
    path('stripe-webhook/', purchases_views.stripe_webhook, name='stripe-webhook'),
    # QR codes
    path('check-experience/<str:product_number>/', products_views.check_experience, name='check-experience'),
]

# HOME & ADMIN
urlpatterns += [
    path('grappelli/', include('grappelli.urls')),  # grappelli URLS
    path('odt-admin/', admin.site.urls),
    # path('', RedirectView.as_view(url=reverse_lazy('home', kwargs={'lang': 'en'})), name='redirect_home'),
    # path('<str:lang>/', home_views.HomeView.as_view(), name='home'),
    path('', home_views.HomeView.as_view(), name='home'),
    path('en/pages/<slug:slug>/', home_views.PageDetailView.as_view(), name='page_detail'),
    path('<str:lang>/company/<slug:slug>/', home_views.AboutUsDetailView.as_view(), name='about-us'),
    # for development and noindex
    # path('test-page-noindex/', home_views.TestPageView.as_view(), name='test-page-noindex'),
]

# ACCOUNTS & PROFILES
urlpatterns += [
    path('accounts/signup/', accounts_views.RegistrationView.as_view(), name='signup'),
    path("accounts/login/", accounts_views.CustomLoginView.as_view(), name='login'),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    # path("accounts/", include("django.contrib.auth.urls")),
    # Password reset
    path('password_reset/', accounts_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', accounts_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', accounts_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', accounts_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Password change
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/customized/password_change_form.html'),
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/customized/password_change_done.html'),
         name='password_change_done'),
    # Profile
    path("accounts/profile/", accounts_views.ProfileView.as_view(), name="profile"),
    path("accounts/profile/update-address/", accounts_views.AddressUpdateView.as_view(), name="address-update"),
    path("accounts/profile/update-info/", accounts_views.ProfileInfoUpdateView.as_view(), name="profile-info-update"),
]

# Django ckeditor: https://github.com/django-ckeditor/django-ckeditor
urlpatterns += [path('ckeditor/', include('ckeditor_uploader.urls')), ]

# DESTINATIONS
urlpatterns += [
    path('<str:lang>/destinations/', destinations_views.DestinationListView.as_view(), name='destination-list'),
    path('<str:lang>/destinations/<slug:slug>/', destinations_views.DestinationDetailView.as_view(), name="destination-detail"),
]

# ATTRACTIONS
urlpatterns += [
    path('<str:lang>/attractions/', attractions_views.AttractionListView.as_view(), name="attraction-list"),
    path('<str:lang>/attractions/<slug:slug>/', attractions_views.AttractionDetailView.as_view(), name="attraction-detail"),
]

# EXPERIENCES, Calendar, Events
urlpatterns += [
    path('<str:lang>/experiences/', products_views.ExperienceListView.as_view(), name="experience-list"),
    path('<str:lang>/experiences/<slug:slug>/', products_views.ExperienceDetailView.as_view(), name='experience-detail'),
    # API for JS
    path('actual-experience-events/<int:parent_experience_id>/', products_views.get_actual_experience_events, name='actual-experience-events'),
    path('experience-event-data/<int:event_id>/', products_views.get_event_booking_data, name='experience-event-data'),
    path('private-experience-event-data/<int:event_id>/', products_views.get_private_event_booking_data, name='private-experience-event-data'),
    path('actual-experience-events-with-discount/<int:parent_experience_id>/', products_views.get_actual_experience_events_with_discount,
         name='actual-experience-events-with-discount'),
]

# BLOGS
urlpatterns += [
    path('<str:lang>/blog/', blogs_views.BlogListView.as_view(), name='blog-list'),
    path('<str:lang>/blog/<slug:slug>/', blogs_views.BlogDetailView.as_view(), name='blog-detail'),
]

# REVIEWS
urlpatterns += [
    path('reviews/<int:experience_id>/', reviews_views.review_list, name='review-list'),
    # path('reviews/', reviews_views.ReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', reviews_views.ReviewDetailView.as_view(), name='review-details'),
]

# LANDING PAGES
urlpatterns += [path('<str:lang>/tour-type/<slug:slug>/', landing_pages_views.LandingPageView.as_view(), name='landing-page'), ]

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

# Sitemap
urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', home_views.robots_txt),
]
