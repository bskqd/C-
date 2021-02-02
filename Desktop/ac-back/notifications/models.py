from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from sailor.models import DateTimesABC


class DevicesData(models.Model):
    """
    Sailors' mobile device data for personal cabinet
    """
    IOS = 'iOS'
    ANDROID = 'android'
    TYPE_PLATFORMS = (
        (IOS, IOS),
        (ANDROID, ANDROID)
    )
    platform = models.CharField(max_length=25, choices=TYPE_PLATFORMS)
    device = models.CharField(max_length=255, null=True, blank=True)
    id_device = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_disable = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    endpoint_arn = models.CharField(max_length=255, null=True, blank=True)


class HistoryPushData(DateTimesABC):
    """
    History of data sent to the user via Push notifications
    """
    push_data = models.JSONField()
    user_device = models.ForeignKey(DevicesData, on_delete=models.PROTECT)


class UserNotification(models.Model):
    title = models.CharField(max_length=255, default='')
    text = models.TextField(default='')
    is_hidden = models.BooleanField(default=False)
    date_send = models.DateTimeField(auto_now_add=True)
    object_id = models.IntegerField(null=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    obj = GenericForeignKey()
    sailor_id = models.IntegerField(null=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
