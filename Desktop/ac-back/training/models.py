from django.contrib.postgres import fields as postgresfield
from django.db import models


class AvailableExamsToday(models.Model):
    list_positions = postgresfield.ArrayField(models.IntegerField(), default=list)
    datetime_meeting = models.DateTimeField()
    datetime_end_meeting = models.DateTimeField()
