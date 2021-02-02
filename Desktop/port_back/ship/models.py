from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Max
from django.utils import timezone

from core.models import (User, PhotoFieldABC, DateTimesABC, AuthorABC)
from port_back.middleware import get_current_authenticated_user


def io_request_upload_path(instance, filename):
    return f'io_request/{instance.number}-{instance.created_at.year}/{filename}'


def upload_draft_path(instance, filename):
    return f'draft/{instance.pk}/{filename}'


class MainInfo(PhotoFieldABC, DateTimesABC, AuthorABC):
    name = models.CharField(max_length=255, default='')
    imo_number = models.IntegerField(unique=True)
    type_vessel = models.ForeignKey('directory.TypeVessel', on_delete=models.PROTECT)
    gross_tonnage = models.FloatField(default=0)
    flag = models.ForeignKey('directory.Flag', on_delete=models.PROTECT)
    is_ban = models.BooleanField(default=False)
    ban_comment = models.TextField(default='', blank=True)


class ShipStaff(PhotoFieldABC, DateTimesABC, AuthorABC):
    date_start = models.DateField()
    date_end = models.DateField(null=True)
    full_name = models.CharField(max_length=500, default='')
    position = models.ForeignKey('directory.StaffPosition', on_delete=models.PROTECT)
    nationality = models.ForeignKey('directory.Country', on_delete=models.PROTECT, related_name='staff_nationality')
    date_birth = models.DateField()
    country_birth = models.ForeignKey('directory.Country', on_delete=models.PROTECT, related_name='staff_births')
    sex = models.ForeignKey('directory.Sex', on_delete=models.PROTECT)
    serial_passport = models.CharField(max_length=40, default='', blank=True)
    expiration = models.DateField()


class IORequest(PhotoFieldABC, DateTimesABC, AuthorABC):
    INPUT = 'input'
    OUTPUT = 'output'

    TYPE_CHOICES = (
        (INPUT, INPUT),
        (OUTPUT, OUTPUT)
    )

    datetime_issued = models.DateTimeField(null=True, blank=True)
    datetime_io = models.DateTimeField(null=True)
    port = models.ForeignKey('directory.Port', on_delete=models.PROTECT)
    tow = models.ForeignKey('directory.Tow', null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=OUTPUT)
    number = models.IntegerField()
    next_port = models.CharField(max_length=255, default='')
    cargo = models.CharField(max_length=255, default='')
    remarks = models.TextField(default='')
    ship_staff = models.ManyToManyField(ShipStaff, related_name='ships')
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    pdf_file = models.FileField(null=True, upload_to=io_request_upload_path)
    zip_archive = models.FileField(null=True, upload_to=io_request_upload_path)
    pdf_with_watermark = models.FileField(null=True, upload_to=io_request_upload_path)
    request_info = models.JSONField(null=True, blank=True)
    ship_name = models.CharField(max_length=255, default='', blank=True)
    is_payed = models.BooleanField(default=False)
    price_form1 = models.FloatField(default=0.0)
    next_port_country = models.ForeignKey('directory.Flag', on_delete=models.PROTECT, null=True, blank=True)
    deadweight = models.FloatField(default=0.0, blank=True)
    inspection_act = models.FileField(null=True, upload_to=io_request_upload_path)
    cifra_uuid = models.UUIDField(editable=True, null=True)

    class Meta:
        ordering = ['-created_at', '-modified_at']
        permissions = (
            ('change_status_iorequest', 'Change status input/output requests'),
        )

    @property
    def full_number(self):
        return f'{self.number}/{self.created_at.year}'

    @property
    def document_number(self):
        return f'{self.number}-{self.created_at.year}'

    @classmethod
    def generate_number(cls):
        number = cls.objects.aggregate(number=Max('number'))['number'] or 0
        number += 1
        return number

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.number:
            self.number = self.generate_number()
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class ShipHistory(models.Model):
    CREATE = 'Create'
    EDIT = 'Edit'
    DELETE = 'Delete'
    HISTORY_TYPE_CHOICES = (
        (CREATE, CREATE),
        (EDIT, EDIT),
        (DELETE, DELETE)
    )

    created_at = models.DateTimeField(default=timezone.now)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    serialized_data = models.JSONField()
    ship_id = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    history_type = models.CharField(choices=HISTORY_TYPE_CHOICES, max_length=20)


class ShipAgentNomination(PhotoFieldABC, DateTimesABC):
    """
    Agent nomination for provision of interests of the ship in port
    """
    ship_key = models.PositiveIntegerField()
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    agent = models.ForeignKey(User, on_delete=models.PROTECT, default=get_current_authenticated_user)
    port = models.ForeignKey('directory.Port', on_delete=models.PROTECT)
    date_verification = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(default='', blank=True)
    verifier = models.ForeignKey(User, on_delete=models.PROTECT, related_name='verifiers', null=True, blank=True)

    class Meta:
        ordering = ('-created_at', '-modified_at')
        permissions = (
            ('change_status_shipagentnomination', 'Change status agent nomination'),
        )


class ShipInPort(models.Model):
    """
    Ships in ports
    """
    ship_key = models.PositiveIntegerField()
    port = models.ForeignKey('directory.Port', on_delete=models.PROTECT)
    agency = models.ForeignKey('directory.Agency', on_delete=models.PROTECT, null=True)
    input_datetime = models.DateTimeField()

    class Meta:
        unique_together = ('ship_key', 'port')


class DraftDocument(DateTimesABC, AuthorABC):
    document_json = models.JSONField()
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-modified_at', '-created_at']


class DraftFileStorage(FileSystemStorage):

    # This method is actually defined in Storage

    def get_available_name(self, name, max_length=None):
        if max_length and len(name) > max_length:
            raise Exception("name's length is greater than max_length")
        return name

    def _save(self, name, content):
        if self.exists(name):
            # if the file exists, do not call the superclasses _save method
            return name
        # if the file is new, DO call it
        return super()._save(name, content)


class PhotoInDraftDocument(DateTimesABC, AuthorABC):
    photo = models.FileField(storage=DraftFileStorage())
    draft = models.ForeignKey(DraftDocument, on_delete=models.CASCADE, related_name='photos')
