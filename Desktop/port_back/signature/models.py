import base64
import os
import uuid

from Cryptodome import Random
from Cryptodome.Cipher import AES
from django.db import models

# Create your models here.
from core.models import DateTimesABC, AuthorABC, User
from pgcrypto import fields

from ship.models import IORequest
from django.contrib.postgres.fields import ArrayField


def io_sign_upload_path(instance, filename):
    """
    For signature dkk
    :param instance:
    :param filename:
    :return:
    """
    random_file_name = ''.join([str(uuid.uuid4().hex)]) + '.p7s'
    path_to_folder = os.path.dirname(instance.io_request.pdf_file.name)
    return os.path.join(path_to_folder, random_file_name)


def signature_upload_path(instance, filename):
    return f'signature/{instance.author.username}/{filename}'


class Signature(DateTimesABC, AuthorABC):
    SIGN = 'sign'
    STAMP = 'stamp'
    TYPE_SIGNATURE_CHOICES = (
        (SIGN, SIGN),
        (STAMP, STAMP)
    )
    file_signature = models.FileField(upload_to=signature_upload_path)
    is_actual = models.BooleanField(default=True)
    password = fields.CharPGPSymmetricKeyField(max_length=255, default='')
    blocked_user = models.ManyToManyField(User, related_name='blocked_in_signature')
    type_signature = models.CharField(max_length=10, default=SIGN, choices=TYPE_SIGNATURE_CHOICES)
    ERDPOU = models.CharField(max_length=12, default='')
    name = models.CharField(max_length=255, default='')
    watermark = models.FileField(upload_to=signature_upload_path, null=True, blank=True)
    port = models.ForeignKey('directory.Port', on_delete=models.CASCADE, null=True, blank=True)
    agent = models.ForeignKey('core.User', on_delete=models.CASCADE, null=True, blank=True, related_name='signatures')

    class Meta:
        ordering = ['is_actual', '-created_at', '-modified_at']

    @property
    def encrypt_password(self):
        from signature.utils import PKCS7Encoder
        master_key = 'Jix#WLPY8It!jHX2P$!DP%ld'.encode()
        encoder = PKCS7Encoder()
        raw = encoder.encode(self.password)
        iv = Random.new().read(16)
        cipher = AES.new(master_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode('utf-8')))

    @property
    def key_owner_uuid(self):
        return self.author.userprofile.cifra_person


class IORequestSign(DateTimesABC, AuthorABC):
    signature = models.ForeignKey(Signature, on_delete=models.SET_NULL, null=True)
    io_request = models.ForeignKey(IORequest, on_delete=models.CASCADE, db_index=True, related_name='signatures')
    base64_signature = models.TextField(blank=True, default='')
    file_signature = models.FileField(upload_to=io_sign_upload_path)


class CenterCertificationKey(models.Model):
    issuer_cn = ArrayField(base_field=models.CharField(max_length=300), )
    address = models.CharField(max_length=300, default='')
    ocsp_address = models.CharField(max_length=300, default='')
    ocsp_port = models.IntegerField(null=True)
    cmp_address = models.CharField(max_length=300, default='')
    tsp_address = models.CharField(max_length=300, default='')
    tsp_port = models.IntegerField(null=True)
    direct_access = models.BooleanField(default=None, null=True)
    qscd_SN_in_cert = models.BooleanField(default=None, null=True)
    cmp_compatibility = models.IntegerField(null=True)
    certs_in_key = models.BooleanField(null=True)
