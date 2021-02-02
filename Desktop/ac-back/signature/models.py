import os
import uuid

from django.conf import settings
from django.contrib.postgres import fields as postgresfield
from django.db import models

# Create your models here.


def get_upload_path(instance, filename):
    """
    For signature dkk
    :param instance:
    :param filename:
    :return:
    """
    random_file_name = ''.join([str(uuid.uuid4().hex)]) + '.p7s'
    path_to_folder = os.path.dirname(instance.protocol_dkk.document_file_docx.name)
    return os.path.join(path_to_folder, random_file_name)


class CommissionerSignProtocol(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True)
    # TODO Delete user model when we are sure that signer is working well
    signer = models.ForeignKey('directory.Commisioner', on_delete=models.SET_NULL, null=True,
                               related_name='signed_items')
    protocol_dkk = models.ForeignKey('document.ProtocolSQC', on_delete=models.CASCADE,
                                     related_name='commissioner_sign')
    signature_base64 = models.TextField(null=True, blank=True)
    signature_file = models.FileField(upload_to=get_upload_path, null=True, blank=True)
    is_signatured = models.BooleanField(default=False)
    TYPE_COMMISSIONER_CHOIES = [
        ('SC', 'Секретар'),
        ('HD', 'Голова'),
        ('CH', 'Член комісії')
    ]
    TYPE_SIGNATURE_CHOICES = [
        ('signature', 'Signature'),
        ('stamp', 'Stamp')
    ]
    commissioner_type = models.CharField(max_length=2, choices=TYPE_COMMISSIONER_CHOIES, default='SC')
    signature_type = models.CharField(max_length=15, choices=TYPE_SIGNATURE_CHOICES, default='signature')

    @property
    def protocol_number(self):
        return self.protocol_dkk.get_number

    @property
    def protocol_status(self):
        status = self.protocol_dkk.status_document
        return {'id': status.pk, 'name_ukr': status.name_ukr, 'name_eng': status.name_eng}

    @property
    def sailor(self):
        return self.protocol_dkk.sailor

    @property
    def sailor_full_name(self):
        return self.protocol_dkk.sailor_full_name


class VchasnoLogging(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()
    signature_for_protocol = models.ForeignKey(CommissionerSignProtocol, on_delete=models.DO_NOTHING, null=True,
                                               blank=True)
    params = models.JSONField()
    response = models.JSONField()
