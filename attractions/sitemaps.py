from django.contrib.sitemaps import Sitemap
from .models import Attraction


class AttractionSitemap(Sitemap):
    # changefreq = 'monthly'
    # priority = 0.6

    def items(self):
        return Attraction.active.all()

    def lastmod(self, obj):
        return obj.updated_at
