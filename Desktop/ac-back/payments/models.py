from random import randint

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.
from directory.models import Rank


class CcyCode(models.Model):
    code_num = models.PositiveSmallIntegerField()
    code_str = models.CharField(max_length=3)
    rate = models.FloatField(default=1.0)


class Service(models.Model):
    pass


class PaymentRecord(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    send_time = models.DateTimeField()
    system_id = models.IntegerField(unique_for_year='send_time')
    amount = models.PositiveIntegerField()
    ccy_code = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=2000, blank=True, null=True)
    rrn = models.CharField(max_length=50, null=True, blank=True)
    fee = models.PositiveIntegerField(null=True)
    response_code = models.IntegerField(null=True)
    pan_mask = models.CharField(max_length=16, blank=True, null=True)
    pay_time = models.DateTimeField(null=True)
    payment_no = models.BigIntegerField(null=True)
    result = models.CharField(max_length=5, blank=True, null=True)
    result_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['system_id'])
        ]

    def save(self, retry=False, *args, **kwargs):
        try:
            if not self.system_id:
                self.system_id = randint(1, 2147483647)
            self.validate_unique()
            super().save(*args, **kwargs)
        except ValidationError:
            self.save(*args, **kwargs, retry=True)


class DescriptionForPaymentsForDKK(models.Model):
    text = models.TextField(default='')
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE)

"""
from django.utils import timezone as tz
from payments.models import *
p = PaymentsRecords(amount=23456, ccy_code=986, send_time=tz.datetime.now())
"""
