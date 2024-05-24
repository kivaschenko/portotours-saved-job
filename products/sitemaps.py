from django.contrib.sitemaps import Sitemap
from .models import Experience, Product


class ProductSitemap(Sitemap):
    # changefreq = 'always'
    # priority = 0.7

    def items(self):
        return Product.active.all()

    def lastmod(self, obj):
        return obj.updated_at


class ExperienceSitemap(Sitemap):
    # changefreq = 'daily'
    # priority = 0.8

    def items(self):
        return Experience.active.all()

    def lastmod(self, obj):
        return obj.updated_at
