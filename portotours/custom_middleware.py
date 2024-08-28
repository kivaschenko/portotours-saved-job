import logging

from django.core.exceptions import DisallowedHost
from django.http import HttpResponseBadRequest, HttpRequest

logger = logging.getLogger(__name__)


class ExcludeAdminFromAnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)

        if not request.path.startswith('/odt-admin/'):
            # Include your Google Analytics tracking code here
            response.content += b'''<!-- Google tag (gtag.js) -->
            <script async src="https://www.googletagmanager.com/gtag/js?id=G-9X9P4D6080"></script>
            <script>
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());

                gtag('config', 'G-9X9P4D6080');
            </script>'''
        return response


class IgnoreDisallowedHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except DisallowedHost as e:
            logger.warning(f"DisallowedHost exception: {e}")
            return HttpResponseBadRequest("Bad Request (Invalid Host)")
        return response
