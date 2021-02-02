from datetime import datetime

from django.db import models
from django.db.models import Q


class TodayManager(models.Manager):
    def get_queryset(self):
        today = datetime.now().date()
        return super(TodayManager, self).get_queryset().filter((Q(date_end__gte=today) | Q(date_end__isnull=True)) &
                                                               Q(date_start__lte=today))


class TodayFirstFormManager(TodayManager):
    def get_queryset(self):
        return super(TodayFirstFormManager, self).get_queryset().filter(type_of_form='First')


class TodaySecondFormManager(TodayManager):
    def get_queryset(self):
        return super(TodaySecondFormManager, self).get_queryset().filter(type_of_form='Second')


class ForDateManager(models.Manager):
    def date(self, date, **kwargs):
        return self.get_queryset().filter((Q(date_end__gte=date) | Q(date_end__isnull=True)) &
                                          Q(date_start__lte=date)).filter(**kwargs)
