from datetime import datetime

from django.conf import settings
from django.db import models


# Create your models here.


class AuthorizationLog(models.Model):
    auth_response = models.JSONField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True)
    status_response = models.IntegerField(null=True, blank=True)
    descr = models.TextField(default='', null=True, blank=True)
    datetime = models.DateTimeField(default=datetime.now)
    inn = models.CharField(max_length=50, default='', null=True, blank=True)
    phone = models.CharField(max_length=50, default='', null=True, blank=True)
    first_name = models.CharField(max_length=100, default='', null=True, blank=True)
    last_name = models.CharField(max_length=100, default='', null=True, blank=True)
    middle_name = models.CharField(max_length=100, default='', null=True, blank=True)
    line_exit = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'