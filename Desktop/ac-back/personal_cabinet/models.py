from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class PersonalDataProcessing(models.Model):
    sailor = models.IntegerField()
    date_create = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)


class HistoryUserInPersonalCabinet(models.Model):
    TYPE_ACTION_CHOICES = (
        ('login', 'login'),
        ('create', 'create'),
        ('edit', 'edit')
    )
    sailor = models.IntegerField()
    date_create = models.DateTimeField(auto_now_add=True)
    longitude = models.FloatField()
    latitude = models.FloatField()
    action = models.CharField(max_length=50, default='login', choices=TYPE_ACTION_CHOICES)
    document_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('document_type', 'object_id')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class CurrentAppVersion(models.Model):
    """
    Версия мобильного приложения
    """
    version = models.CharField(max_length=50)
    date_create = models.DateTimeField(auto_now_add=True)
