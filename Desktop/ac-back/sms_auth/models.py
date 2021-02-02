import random
from datetime import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as postgresfield
from django.db import models

from communication.models import SailorKeys
from directory.models import StatusDocument
from sailor.models import Profile


class SecurityCode(models.Model):
    """СМС Пароль для регистрации и авторицации в ЛК"""

    phone = models.CharField(max_length=15)
    security_code = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        if not self.security_code:
            self.security_code = random.randint(100000, 999999)
        super(SecurityCode, self).save(*args, **kwargs)


class UserStatementVerification(models.Model):
    """Верификация пользователя для регисрации в ЛК"""
    ETRANSPORT = 'e-transport'
    ESAILOR = 'e-sailor'
    MORRICHSERVICE = 'morrichservice'
    MDU = 'MDU'
    SERVICE_CHOICES = (
        (ETRANSPORT, ETRANSPORT),
        (ESAILOR, ESAILOR),
        (MORRICHSERVICE, MORRICHSERVICE),
        (MDU, MDU)
    )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    birthday = models.DateField()
    phone = models.CharField(max_length=15)
    inn = models.CharField(max_length=20)
    passport = models.CharField(max_length=50)
    email = models.EmailField()
    status_document = models.ForeignKey(StatusDocument, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    photo = postgresfield.ArrayField(models.IntegerField())
    sailor_id = models.IntegerField(null=True)
    service = models.CharField(max_length=20, default=ETRANSPORT, choices=SERVICE_CHOICES)


class PhotoDocumentForVerification(models.Model):
    """Сканы документов для верификации пользователя в ЛК"""

    photo = models.ImageField()


class HistoryNotification(models.Model):
    """История отправки СМС сообщений"""
    TYPE_NOTIFICATION_CHOICES = (
        ('Push', 'Push'),
        ('Phone', 'Phone'),
        ('Mail', 'Mail')
    )
    destination = models.CharField(max_length=355)
    message = models.CharField(max_length=600)
    status_answer = models.CharField(max_length=600)
    id_mailing = models.CharField(max_length=600, null=True, blank=True)
    distance_code = models.CharField(max_length=355, null=True, blank=True)
    date_answer = models.DateTimeField(null=True, blank=True)
    send_time = models.DateTimeField(default=datetime.now)
    type = models.CharField(max_length=50, default='Phone', choices=TYPE_NOTIFICATION_CHOICES)
    document_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('document_type', 'object_id')
