from django.contrib.postgres import fields
from django.db import models


class ShipKey(models.Model):
    imo_number = models.IntegerField(unique=True)
    maininfo = models.IntegerField(unique=True, primary_key=True)
    shipstaff = fields.ArrayField(base_field=models.IntegerField(), default=list)
    iorequest = fields.ArrayField(base_field=models.IntegerField(), default=list)
