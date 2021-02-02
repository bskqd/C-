from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


# import sys
# if sys.argv[1:2] != ['migrate']:
class User(AbstractUser):
    class TypeUserChoices(models.TextChoices):
        SECRETARY_SQC = ('secretary_sqc', 'ITCS secretary')
        COMMISSIONER = ('commissioner', 'Commissioner SQC')
        VERIFIER = ('verifier', 'Verifier')
        AGENT = ('agent', 'Agent')
        SAILOR = ('sailor', 'Sailor')
        MEDICAL = ('medical', 'Medical')
        SECRETARY_EDUCATION = ('secretary_education', 'Secretary of education institution')
        HEAD_AGENT = ('head_agent', 'Head of agents')
        SECRETARY_SERVICE = ('secretary_service', 'Service center secretary')
        REGISTRY = ('registry', 'Registry')
        DPD = ('dpd', 'DPD')
        BACK_OFFICE = ('back_office', 'Back office')
        MARAD = ('marad', 'Morrichservice')
        ETI_EMPLOYEE = ('eti_employee', 'ETI employee')
        SECRETARY_ATC = ('secretary_atc', 'Secretary of ATC')
    type_user = models.CharField(max_length=50, default=TypeUserChoices.SAILOR, choices=TypeUserChoices.choices)

    class Meta:
        db_table = 'auth_user'
