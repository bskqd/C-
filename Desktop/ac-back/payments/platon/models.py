from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as postgresfield
from django.db import models


# Create your models here.


class PlatonPayments(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    send_time = models.DateTimeField()
    order = models.CharField(default='', max_length=50)
    platon_id = models.CharField(max_length=50, default='')
    amount = models.FloatField()
    description = models.TextField(default='')
    ip_address = models.GenericIPAddressField(null=True)
    pay_time = models.DateTimeField(null=True)
    pan_mask = models.CharField(max_length=16, default='')
    status = models.CharField(max_length=15, default='')
    sum_distribution = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
