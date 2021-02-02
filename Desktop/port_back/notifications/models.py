from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import User


class UserNotification(models.Model):
    title = models.CharField(max_length=255, default='')
    text = models.TextField(default='')
    is_hidden = models.BooleanField(default=False)
    date_send = models.DateTimeField(auto_now_add=True)
    object_id = models.IntegerField(null=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    ship_id = models.PositiveIntegerField(null=True)

    class Meta:
        ordering = ['-date_send']
