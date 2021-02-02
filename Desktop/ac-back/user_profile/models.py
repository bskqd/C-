from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as postgresfield
from django.db import models

from directory.models import BranchOffice, City, DoctrorInMedicalInstitution, NTZ, NZ
from itcs import magic_numbers


class MainGroups(models.Model):
    name = models.CharField(max_length=150, unique=True)
    group = models.ManyToManyField(
        Group,
        blank=True,
    )

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    SECRETARY_SQC = 'secretary_sqc'
    COMMISSIONER = 'commissioner'
    VERIFIER = 'verifier'
    AGENT = 'agent'
    SAILOR = 'sailor'
    MEDICAL = 'medical'
    SECRETARY_EDUCATION = 'secretary_education'
    HEAD_AGENT = 'head_agent'
    SECRETARY_SERVICE = 'secretary_service'
    REGISTRY = 'registry'
    DPD = 'dpd'
    BACK_OFFICE = 'back_office'
    MARAD = 'marad'
    ETI_EMPLOYEE = 'eti_employee'
    SECRETARY_ATC = 'secretary_atc'

    TYPE_USER_CHOICES = (
        (SECRETARY_SQC, SECRETARY_SQC),
        (VERIFIER, VERIFIER),
        (COMMISSIONER, COMMISSIONER),
        (AGENT, AGENT),
        (SAILOR, SAILOR),
        (MEDICAL, MEDICAL),
        (SECRETARY_EDUCATION, SECRETARY_EDUCATION),
        (HEAD_AGENT, HEAD_AGENT),
        (SECRETARY_SERVICE, SECRETARY_SERVICE),
        (REGISTRY, REGISTRY),
        (DPD, DPD),
        (BACK_OFFICE, BACK_OFFICE),
        (MARAD, MARAD),
        (ETI_EMPLOYEE, ETI_EMPLOYEE),
        (SECRETARY_ATC, SECRETARY_ATC),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    branch_office = models.ForeignKey(BranchOffice, on_delete=models.PROTECT, null=True, blank=True)
    middle_name = models.CharField(max_length=150, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
    additional_data = models.TextField(blank=True, null=True)
    LANGUAGE_CHOICES = (
        ('EN', 'en'),
        ('UA', 'ua'),
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='UA')
    type_user = models.CharField(max_length=50, default=SECRETARY_SQC, choices=TYPE_USER_CHOICES)
    main_group = models.ManyToManyField(MainGroups, blank=True)
    is_commissioner = models.BooleanField(default=False)
    vchasno_token = models.CharField(max_length=200, default='', blank=True)
    yubikey_authorization = models.BooleanField(default=False)
    photo = models.FileField(null=True, blank=True)
    contact_info = postgresfield.ArrayField(models.IntegerField(), default=list, blank=True)
    agent_group = models.ManyToManyField('agent.AgentGroup', blank=True)
    doctor_info = models.OneToOneField(DoctrorInMedicalInstitution, on_delete=models.SET_NULL, null=True,
                                       blank=True)
    eti_institution = models.ForeignKey(NTZ, on_delete=models.PROTECT, null=True, blank=True)
    education_institution = models.ForeignKey(NZ, on_delete=models.PROTECT, null=True, blank=True)
    is_trained = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.type_user}'

    @property
    def groups_id(self):
        return self.main_group.all().values_list('pk', flat=True)

    @property
    def full_name_ukr(self):
        return f'{self.user.first_name} {self.middle_name} {self.user.last_name}'

    @property
    def short_photo_url(self):
        return self.photo.name

    @property
    def verification_status_by_user(self):
        status_by_type_user = {self.SECRETARY_EDUCATION: magic_numbers.VERIFICATION_STATUS,
                               self.AGENT: magic_numbers.STATUS_CREATED_BY_AGENT,
                               self.MARAD: magic_numbers.VERIFICATION_STATUS,
                               self.HEAD_AGENT: magic_numbers.STATUS_CREATED_BY_AGENT,
                               self.SECRETARY_SQC: magic_numbers.VERIFICATION_STATUS,
                               self.SECRETARY_SERVICE: magic_numbers.STATUS_CREATED_BY_AGENT,
                               self.VERIFIER: magic_numbers.VERIFICATION_STATUS,
                               self.REGISTRY: magic_numbers.VERIFICATION_STATUS,
                               self.MEDICAL: magic_numbers.VERIFICATION_STATUS,
                               self.DPD: magic_numbers.VERIFICATION_STATUS,
                               self.BACK_OFFICE: magic_numbers.STATUS_CREATED_BY_AGENT}
        return status_by_type_user[self.type_user]


class UserSailorHistory(models.Model):
    """
    История какой юзер на какого моряка заходил.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sailor_key = models.IntegerField()
    date_open = models.DateTimeField()


class FullUserSailorHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sailor_key = models.IntegerField(null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    module = models.CharField(max_length=250)
    action_type = models.CharField(max_length=250)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField(null=True, blank=True)
    old_obj_json = models.JSONField(null=True, blank=True)
    new_obj_json = models.JSONField(null=True, blank=True)

    def full_user_name(self):
        return f'{self.user.last_name} {self.user.first_name}'


class Version(models.Model):
    date = models.DateField(default=datetime.today)
    version = models.PositiveIntegerField()
    v_frontend = models.PositiveIntegerField()
    v_backend = models.PositiveIntegerField()

    @property
    def get_full_version(self):
        return '{}/{}/{}/{}'.format(self.date.strftime('%d%m%Y'), self.version, str(self.v_frontend).zfill(3),
                                    str(self.v_backend).zfill(3))


class BranchOfficeRestrictionForPermission(models.Model):
    perm = models.ForeignKey(Permission, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    branch_office = models.ManyToManyField(BranchOffice)

    def __str__(self):
        return '{};{}'.format(self.user.username, self.perm.codename)


class ToChangePassword(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_create = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
    is_changed = models.BooleanField(default=False)
