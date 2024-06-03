from django.contrib.sitemaps import Sitemap
from .models import Page, AboutUsPage


class PageSitemap(Sitemap):
    # changefreq = 'monthly'
    # priority = 0.5

    def items(self):
        return Page.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class AboutUsSitemap(Sitemap):
    def items(self):
        items = AboutUsPage.objects.all()
        print(f"Items: {items}")
        return items

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        url = obj.get_absolute_url()
        print(f"Location for {obj}: {url}")
        return url
