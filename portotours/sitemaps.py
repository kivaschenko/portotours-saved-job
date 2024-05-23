# sitemaps.py (this can be placed in one of your apps, or a common app like home)
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class ListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return [
            'destination-list',
            'attraction-list',
            'experience-list',
            'blog-list',
        ]

    def location(self, item):
        return reverse(item, kwargs={'lang': 'en'})
