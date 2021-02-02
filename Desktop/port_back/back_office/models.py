from django.db import models

import back_office.managers
from core.models import (DateTimesABC, )


class PriceIORequest(DateTimesABC):
    """
    Cost of requests for different types of ships
    """
    objects = models.Manager()
    today = back_office.managers.TodayManager()
    today_first_form = back_office.managers.TodayFirstFormManager()

    FIRST_FORM = 'First'
    # SECOND_FORM = 'Second'

    TYPE_OF_FORM_CHOICES = (
        (FIRST_FORM, FIRST_FORM),
    )

    price = models.FloatField(default=0.0)
    date_start = models.DateField()
    date_end = models.DateField(null=True, blank=True)
    type_of_form = models.CharField(choices=TYPE_OF_FORM_CHOICES, default=FIRST_FORM, max_length=30)


class DeadweightPricePeriod(DateTimesABC):
    """
    Deadweight price validity period
    """
    date_start = models.DateField()
    date_end = models.DateField(null=True, blank=True)


class DeadweightPrice(models.Model):
    """
    Cost IORequest on the deadweight of the vessel
    """
    from_deadweight = models.FloatField()
    to_deadweight = models.FloatField(null=True, blank=True)
    price = models.FloatField(default=0.0)
    price_period = models.ForeignKey(DeadweightPricePeriod, on_delete=models.CASCADE, related_name='prices')
