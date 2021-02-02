import json
from typing import List

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from pgcrypto import fields

import core.managers
from port_back.middleware import get_current_authenticated_user


class User(AbstractUser):
    BASIC = 'basic'
    TOTP = 'TOTP'
    YUBIKEY = 'YUBIKEY'
    TYPE_AUTHORIZATION_CHOICES = (
        (BASIC, BASIC),
        (TOTP, TOTP),
        (YUBIKEY, YUBIKEY)
    )

    username = None
    ADMIN_CH = 'admin'
    AGENT_CH = 'agent'
    MARAD_CH = 'user_marad'
    HEAD_AGENCY_CH = 'head_agency'
    HARBOR_MASTER_CH = 'harbor_master'
    HARBOR_WORKER_CH = 'harbor_worker'
    ACCOUNTANT_CH = 'accountant'
    BORDER_GUARD_CH = 'border_guard'
    PORT_MANAGER_CH = 'port_manager'
    HEAD_TOWING_CH = 'head_towing'
    TOW_MASTER_CH = 'tow_master'

    TYPE_USER_CHOICES = (
        (ADMIN_CH, ADMIN_CH),
        (AGENT_CH, AGENT_CH),
        (MARAD_CH, MARAD_CH),
        (HEAD_AGENCY_CH, HEAD_AGENCY_CH),
        (HARBOR_MASTER_CH, HARBOR_MASTER_CH),
        (HARBOR_WORKER_CH, HARBOR_WORKER_CH),
        (ACCOUNTANT_CH, ACCOUNTANT_CH),
        (BORDER_GUARD_CH, BORDER_GUARD_CH),
        (PORT_MANAGER_CH, PORT_MANAGER_CH),
        (HEAD_TOWING_CH, HEAD_TOWING_CH),
        (TOW_MASTER_CH, TOW_MASTER_CH)
    )

    middle_name = models.CharField(default='', blank=True, max_length=150)
    type_user = models.CharField(choices=TYPE_USER_CHOICES, default=AGENT_CH, max_length=15)
    email = models.EmailField(_('email address'), unique=True, max_length=150)
    type_authorization = models.CharField(default=BASIC, choices=TYPE_AUTHORIZATION_CHOICES, max_length=15)
    is_changed_password = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = core.managers.CustomUserManager()

    def __str__(self):
        return self.email

    @classmethod
    def get_type_authorization(cls, type_user):
        user_authorization = {
            User.MARAD_CH: User.YUBIKEY,
            User.HARBOR_MASTER_CH: User.YUBIKEY,
            User.HARBOR_WORKER_CH: User.YUBIKEY,
            User.AGENT_CH: User.TOTP,
            User.HEAD_AGENCY_CH: User.YUBIKEY,
        }
        return User.BASIC

    @property
    def userprofile(self):
        if self.type_user == self.AGENT_CH:
            return self.agent
        elif self.type_user in [self.MARAD_CH, self.ADMIN_CH]:
            return self.user_marad
        elif self.type_user == self.HEAD_AGENCY_CH:
            return self.head_agency
        elif self.type_user == self.HARBOR_MASTER_CH:
            return self.harbor_master
        elif self.type_user == self.HARBOR_WORKER_CH:
            return self.harbor_worker
        elif self.type_user == self.BORDER_GUARD_CH:
            return self.border_guard
        elif self.type_user == self.PORT_MANAGER_CH:
            return self.port_manager
        elif self.type_user == self.HEAD_TOWING_CH:
            return self.head_towing
        elif self.type_user == self.TOW_MASTER_CH:
            return self.tow_master
        else:
            return None

    @property
    def get_port(self) -> List:
        if self.type_user in [self.HARBOR_WORKER_CH, self.BORDER_GUARD_CH, self.PORT_MANAGER_CH]:
            return [getattr(self.userprofile, 'port_id', None)]
        elif self.type_user == self.HARBOR_MASTER_CH:
            return list(self.userprofile.ports.values_list('pk', flat=True))
        return []

    @property
    def get_user_full_name(self):
        if self.middle_name:
            return f'{self.last_name} {self.first_name} {self.middle_name}'
        return f'{self.last_name} {self.first_name}'

    @property
    def get_agency(self):
        return getattr(self.userprofile, 'agency', None)

    def set_default_permission(self):
        getter_default_group = {self.MARAD_CH: 1,
                                self.HARBOR_MASTER_CH: 2,
                                self.HARBOR_WORKER_CH: 3,
                                self.HEAD_AGENCY_CH: 4,
                                self.AGENT_CH: 5,
                                self.ACCOUNTANT_CH: 6,
                                self.BORDER_GUARD_CH: 7,
                                self.PORT_MANAGER_CH: 8,
                                self.HEAD_TOWING_CH: 9,
                                self.TOW_MASTER_CH: 10}
        default_group = getter_default_group.get(self.type_user)
        self.groups.add(default_group)
        return True


class Photo(models.Model):
    file = models.FileField(upload_to='%Y-%m-%d/')
    type_photo = models.CharField(default='', max_length=100)
    cifra_uuid = models.UUIDField(editable=True, null=True)
    is_signed = models.BooleanField(default=False)

    @property
    def get_absolute_file(self):
        return self.file.url


class PhotoFieldABC(models.Model):
    _photo = fields.CharPGPSymmetricKeyField(max_length=250, default='[]')

    @property
    def photo(self):
        if self._photo:
            return list(json.loads(self._photo))
        return self._photo

    @photo.setter
    def photo(self, value):
        self._photo = json.dumps(value)

    class Meta:
        abstract = True


class DateTimesABC(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuthorABC(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, default=get_current_authenticated_user, null=True)

    class Meta:
        abstract = True

    @property
    def author_full_name(self):
        if not self.author:
            return None
        return self.author.get_user_full_name


class UserMarad(PhotoFieldABC):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_marad')
    cifra_person = models.UUIDField(editable=True, null=True)
    cifra_key = models.CharField(max_length=512, default='', blank=True)


class HarborMaster(PhotoFieldABC):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='harbor_master')
    cifra_person = models.UUIDField(editable=True, null=True)
    cifra_key = models.CharField(max_length=512, default='', blank=True)


class HeadAgency(PhotoFieldABC):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='head_agency')
    agency = models.OneToOneField('directory.Agency', on_delete=models.CASCADE, related_name='agency_user')
    accept_agreement = models.BooleanField(default=False)
    inn = models.CharField(max_length=12, default='', blank=True)
    cifra_person = models.UUIDField(editable=True, null=True)
    cifra_key = models.CharField(max_length=512, default='', blank=True)


class Agent(PhotoFieldABC):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent')
    agency = models.ForeignKey('directory.Agency', on_delete=models.CASCADE, related_name='agents')
    inn = models.CharField(max_length=12, default='', blank=True)
    cifra_person = models.UUIDField(editable=True, null=True)
    cifra_key = models.CharField(max_length=512, default='', blank=True)


class HarborWorker(PhotoFieldABC):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='harbor_worker')
    port = models.ForeignKey('directory.Port', on_delete=models.CASCADE)


class BorderGuard(PhotoFieldABC):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='border_guard')
    port = models.ForeignKey('directory.Port', on_delete=models.CASCADE, related_name='border_guards')


class PortManager(PhotoFieldABC):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='port_manager')
    port = models.ForeignKey('directory.Port', on_delete=models.CASCADE, related_name='port_managers')


class HeadTowingCompany(PhotoFieldABC):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='head_towing')
    towing_company = models.OneToOneField('directory.TowingCompany', on_delete=models.CASCADE,
                                          related_name='head_towing')
    inn = models.CharField(max_length=12, default='', blank=True)
    cifra_person = models.UUIDField(editable=True, null=True)
    cifra_key = models.CharField(max_length=512, default='', blank=True)


class TowMaster(PhotoFieldABC):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tow_master')
    tow = models.OneToOneField('directory.Tow', on_delete=models.CASCADE, related_name='tow_master')
    inn = models.CharField(max_length=12, default='', blank=True)
    cifra_person = models.UUIDField(editable=True, null=True)
    cifra_key = models.CharField(max_length=512, default='', blank=True)


class UserHistory(DateTimesABC, AuthorABC):
    CREATE = 'Create'
    EDIT = 'Edit'
    DELETE = 'Delete'
    HISTORY_TYPE_CHOICES = (
        (CREATE, CREATE),
        (EDIT, EDIT),
        (DELETE, DELETE)
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    serialized_data = models.JSONField()
    history_type = models.CharField(choices=HISTORY_TYPE_CHOICES, max_length=20)
