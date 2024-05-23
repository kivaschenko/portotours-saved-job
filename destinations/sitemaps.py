from django.contrib.sitemaps import Sitemap
from .models import Destination


class DestinationSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Destination.active.all()

    def lastmod(self, obj):
        return obj.updated_at
