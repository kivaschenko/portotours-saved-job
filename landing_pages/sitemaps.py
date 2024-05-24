from django.contrib.sitemaps import Sitemap
from .models import LandingPage


class LandingPageSitemap(Sitemap):
    # changefreq = 'monthly'
    # priority = 0.5

    def items(self):
        return LandingPage.active.all()

    def lastmod(self, obj):
        return obj.updated_at
