from django.conf import settings
from django.db import models
from pgcrypto import fields

from directory.models import NZ, Faculty, EducationForm, StatusDocument
from sailor.managers import BySailorManager, BySailorQuerySet
from sailor.models import DateTimesABC


class StudentID(DateTimesABC):
    """
    Cadet's student ID
    """
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    serial = models.CharField(max_length=30, null=True, blank=True)
    number = models.CharField(max_length=50, null=True, blank=True)
    name_nz = models.ForeignKey(NZ, on_delete=models.PROTECT)
    date_start = models.DateField()
    date_end = models.DateField(null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT)
    education_form = models.ForeignKey(EducationForm, on_delete=models.PROTECT)
    group = models.CharField(max_length=250, null=True, blank=True)
    status_document = models.ForeignKey(StatusDocument, on_delete=models.PROTECT)
    educ_with_dkk = models.BooleanField(default=False)
    passed_educ_exam = models.BooleanField(default=False)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
