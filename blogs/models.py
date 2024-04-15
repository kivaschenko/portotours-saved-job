import re

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.conf import settings

from ckeditor.fields import RichTextField

from products.models import Language


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class ParentBlog(models.Model):
    """A Parent Blog brings together all blogs with multilingual content,
    but all in one context. To save the common banner,
    card image and link between blog details page languages.
    """
    parent_name = models.CharField(max_length=60, unique=True, db_index=True)
    priority_number = models.IntegerField(null=True, blank=True, default=0, help_text="number for ordering in list on page by default")
    banner = models.FileField(upload_to='media/banners/', null=True, blank=True)
    card_image = models.FileField(upload_to='media/cards/', null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.parent_name

    class Meta:
        ordering = ('parent_name',)


class BlogActiveManager(models.Manager):
    def get_queryset(self):
        return super(BlogActiveManager, self).get_queryset().filter(is_active=True)


class Blog(models.Model):
    # Business logic part
    parent_blog = models.ForeignKey(ParentBlog, on_delete=models.SET_NULL, related_name='child_blogs', null=True, blank=True,
                                    help_text="The Parent Blog brings together all blogs with multilingual content but same context and common banner.")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='blogs', null=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    # SEO part
    slug = models.SlugField(max_length=255, unique=True, db_index=True, editable=True, blank=True,
                            help_text="max 255 characters, exactly url tail that is unique")
    page_title = models.CharField(max_length=120, help_text="seo title for header in search list, max 120 characters", null=True, blank=True)
    page_description = models.TextField(max_length=600, help_text="seo page description, max 500 characters", null=True, blank=True)
    keywords = models.TextField(max_length=500, help_text="seo keywords", null=True, blank=True)
    # content part
    title = models.CharField(max_length=160, help_text="160 characters, max")
    short_description = models.TextField(max_length=300, help_text="300 characters, max", null=True, blank=True)
    categories = models.ManyToManyField(Category)
    views = models.IntegerField(default=0)
    read_time = models.IntegerField(default=0)  # in minutes
    date_published = models.DateTimeField(auto_now_add=True)
    middle_picture = models.ImageField(upload_to='blogs/middle_pictures', null=True, blank=True)
    objects = models.Manager()
    active = BlogActiveManager()

    class Meta:
        ordering = ('-date_published',)
        unique_together = ('title', 'slug')

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<Blog(id={self.id} title={self.title}...>"

    def get_absolute_url(self):
        return reverse("blog-detail", kwargs={"slug": self.slug, "lang": self.language})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.page_title:
            self.page_title = self.title
        if not self.page_description:
            self.page_description = self.short_description
        # self.read_time = self.calculate_read_time(self.content)
        super(Blog, self).save(*args, **kwargs)

    @property
    def localized_url(self):
        return f"/blogs/{self.language.code.lower()}/{self.slug}/"

    @staticmethod
    def calculate_read_time(content):
        words = re.findall(r'\w+', content)
        num_words = len(words)

        # Average reading speed in words per minute
        words_per_minute = 200

        # Calculate estimated read time
        read_time_minutes = num_words / words_per_minute

        # Round up to the nearest minute
        read_time_minutes = round(read_time_minutes)

        return read_time_minutes


class BlockBlog(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="blocks")
    title = models.CharField(max_length=255, help_text="title of text block including within Blog, max 255 characters", null=True, blank=True)
    text = RichTextField(max_length=3000, help_text="maximum length of text block 3000 characters", null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']

    def display_text(self):
        return mark_safe(self.text)



