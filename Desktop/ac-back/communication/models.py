from django.contrib.postgres import fields as postgresfield
from django.db import models

# Create your models here.
from .managers import ByDocumentManager


class SailorKeys(models.Model):
    objects = models.Manager()
    by_document = ByDocumentManager()

    profile = models.BigIntegerField()
    citizen_passport = postgresfield.ArrayField(models.IntegerField(), default=list)
    inn = models.IntegerField(null=True, blank=True)
    qualification_documents = postgresfield.ArrayField(models.IntegerField(), default=list)
    service_records = postgresfield.ArrayField(models.IntegerField(), default=list)
    experience_docs = postgresfield.ArrayField(models.IntegerField(), default=list)
    # 'value':id cert or service_record, 'id_book':}
    education = postgresfield.ArrayField(models.IntegerField(), default=list)
    sertificate_ntz = postgresfield.ArrayField(models.IntegerField(), default=list)
    medical_sertificate = postgresfield.ArrayField(models.IntegerField(), default=list)
    sailor_passport = postgresfield.ArrayField(models.IntegerField(), default=list)
    statement_dkk = postgresfield.ArrayField(models.IntegerField(), default=list)
    protocol_dkk = postgresfield.ArrayField(models.IntegerField(), default=list)
    statement_qualification = postgresfield.ArrayField(models.IntegerField(), default=list)
    user_id = models.IntegerField(null=True, blank=True)
    demand_position = postgresfield.ArrayField(models.IntegerField(), default=list)
    statement_service_records = postgresfield.ArrayField(models.IntegerField(), default=list)
    students_id = postgresfield.ArrayField(models.IntegerField(), default=list)
    agent_id = models.IntegerField(null=True, blank=True)
    statement_eti = postgresfield.ArrayField(models.IntegerField(), default=list)
    packet_item = postgresfield.ArrayField(models.IntegerField(), default=list)
    statement_sailor_passport = postgresfield.ArrayField(models.IntegerField(), default=list)
    statement_medical_certificate = postgresfield.ArrayField(models.IntegerField(), default=list)
    statement_advanced_training = postgresfield.ArrayField(models.IntegerField(), default=list)

    class Meta:
        app_label = 'communication'

#
# class SailorKeysRefactor(models.Model):
#
#     profile = models.BigIntegerField()
#     profile_changed_to = models.BigIntegerField()
#
#     qualification_documents = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     service_records = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     experience_docs = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     # 'value':id cert or service_record, 'id_book':}
#     education = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     sertificate_ntz = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     medical_sertificate = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     sailor_passport = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     statement_dkk = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     protocol_dkk = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     statement_qualification = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     status = models.PositiveSmallIntegerField(choices=((1, 'Success'), (2, 'Error')), null=True, default=0)
#     status_description = models.PositiveSmallIntegerField(
#         choices=(
#             (0, 'Not faund'),
#             (1, 'Mapped'),
#             (3, 'Server Error')
#         )
#     )
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         app_label = 'communication'


# class Tmp(models.Model):
#     sailors = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
#     qual = models.IntegerField(null=True, blank=True)
#
# class Tmp1(models.Model):
#     id_diploma = models.IntegerField()