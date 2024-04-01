from django.test import TestCase
from django.urls import reverse

from products.models import Language
from .models import ParentBlog, Blog, Category


class BlogModelTestCase(TestCase):
    fixtures = [
        'products/fixtures/testing/languages.json',
    ]

    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.parent_blog = ParentBlog.objects.create(parent_name='Test Parent Blog')
        self.language = Language.objects.get(code='EN')

    def test_create_blog(self):
        blog = Blog.objects.create(title='Test Blog', parent_blog=self.parent_blog, language=self.language)
        blog.categories.set([self.category])
        self.assertEqual(blog.title, 'Test Blog')
        self.assertEqual(blog.categories.count(), 1)

    def test_calculate_read_time(self):
        content = "This is a test blog content."
        read_time = Blog.calculate_read_time(content)
        # Perform assertions on read_time based on your expected value


class BlogViewTestCase(TestCase):
    fixtures = [
        'products/fixtures/testing/languages.json',
    ]

    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.parent_blog = ParentBlog.objects.create(parent_name='Test Parent Blog')
        self.language = Language.objects.get(code='EN')

    def test_blog_list_view(self):
        url = reverse('blog-list', kwargs={'lang': 'en'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Perform assertions on response content and context data

    def test_blog_detail_view(self):
        blog = Blog.objects.create(title='Test Blog', parent_blog=self.parent_blog, language=self.language)
        url = reverse('blog-detail', kwargs={'lang': 'en', 'slug': blog.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Perform assertions on response content and context data
