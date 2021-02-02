from django.conf import settings
from django.contrib.postgres import fields as postgresfield
from django.db import models
# Create your models here.
from pgcrypto import fields

from directory.models import StatusDocument, City
from sailor.models import DateTimesABC


class AgentSailor(DateTimesABC):
    sailor_key = models.IntegerField()
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sailors')
    is_disable = models.BooleanField(default=False)
    date_end_proxy = models.DateField(null=True)

    class Meta:
        unique_together = (('sailor_key', 'agent'), )


class StatementAgentSailor(DateTimesABC):
    """
    Заявление моряка к агенту
    """
    sailor_key = fields.IntegerPGPSymmetricKeyField()
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent')
    status_document = models.ForeignKey(StatusDocument, on_delete=models.PROTECT)
    photo = postgresfield.ArrayField(default=list, base_field=models.IntegerField())
    date_end_proxy = models.DateField(blank=True, null=True)


class AgentGroup(models.Model):
    """
    Группы агентов
    """
    name_ukr = models.CharField(max_length=255)
    is_disable = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name_ukr}'


class StatementAgent(DateTimesABC):
    """
    Заявление на агента
    """
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=150, blank=True)
    status_document = models.ForeignKey(StatusDocument, on_delete=models.PROTECT)
    contact_info = postgresfield.ArrayField(models.IntegerField(), default=list)
    photo = postgresfield.ArrayField(default=list, base_field=models.IntegerField())
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    group = models.ForeignKey(AgentGroup, on_delete=models.PROTECT, null=True)
    tax_number = models.CharField(max_length=15, blank=True, default='')
    serial_passport = models.CharField(max_length=15, blank=True, default='')


class CodeToStatementAgentSailor(DateTimesABC):
    """
    Security code to create statement Agent-Sailor
    """
    security_code = models.IntegerField(unique=True)
    phone = models.CharField(max_length=15)
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sailor_key = models.IntegerField()
