from django.conf import settings
from django.db import models

from taggit.managers import TaggableManager

# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to='./news//%Y/%m/%d/')
    full_text = models.TextField()
    short_text = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    tags = TaggableManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    source_url = models.URLField(null=True)

    def __str__(self):
        return '{} (Created: {}) '.format(self.title, self.created_at)
