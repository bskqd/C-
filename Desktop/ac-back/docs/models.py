import binascii
import os

from django.conf import settings
from django.db import models


# Create your models here.
from sailor.models import AuthorDocumentABC


class DocsForStatementServiceRecord(models.Model):
    token = models.CharField(max_length=40)
    service_record = models.ForeignKey('document.ServiceRecord', on_delete=models.CASCADE)
    num_blank = models.IntegerField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()
        return super().save(*args, **kwargs)


class DocsForServiceRecord(models.Model):
    token = models.CharField(max_length=40)
    service_record = models.ForeignKey('document.ServiceRecord', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()
        return super().save(*args, **kwargs)


class DocsForStatementDKK(models.Model):
    token = models.CharField(max_length=40)
    statement = models.ForeignKey('statement.StatementSQC', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()
        return super().save(*args, **kwargs)


class DocsForProtocolDKK(models.Model):
    token = models.CharField(max_length=40)
    protocol = models.ForeignKey('document.ProtocolSQC', on_delete=models.CASCADE)  # TODO RESTORE

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()
        return super().save(*args, **kwargs)


class DocsForStatementQualification(models.Model):
    token = models.CharField(max_length=40)
    statement = models.ForeignKey('statement.StatementQualification', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()
        return super().save(*args, **kwargs)


class TemplateDocForQualification(models.Model):
    rank = models.ForeignKey('directory.Rank', on_delete=models.PROTECT)
    file = models.FileField()
    is_proof_diploma = models.BooleanField(default=False)


class DocsForQualificationDocuments(models.Model):
    token = models.CharField(max_length=40)
    qualification = models.ForeignKey('document.QualificationDocument', on_delete=models.CASCADE)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()
        return super().save(*args, **kwargs)


class DocsForProofOfDiplomaDocuments(models.Model):
    token = models.CharField(max_length=40)
    proof = models.ForeignKey('document.ProofOfWorkDiploma', on_delete=models.CASCADE)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()
        return super().save(*args, **kwargs)