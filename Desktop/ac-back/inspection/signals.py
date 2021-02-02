import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from inspection.tasks import sync_document, delete_document
from sailor.document.models import ServiceRecord, ProtocolSQC, QualificationDocument, ProofOfWorkDiploma
from sailor.models import (SailorPassport, Profile)
from sailor.statement.models import StatementSQC, StatementQualification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=StatementSQC)
@receiver(post_save, sender=ProtocolSQC)
@receiver(post_save, sender=StatementQualification)
@receiver(post_save, sender=QualificationDocument)
@receiver(post_save, sender=SailorPassport)
@receiver(post_save, sender=ServiceRecord)
@receiver(post_save, sender=ProofOfWorkDiploma)
@receiver(post_save, sender=Profile)
def sync_on_update_doc(sender, instance, created, **kwargs):
    sync_document.apply_async((instance, ), countdown=5)


@receiver(post_delete, sender=StatementSQC)
@receiver(post_delete, sender=ProtocolSQC)
@receiver(post_delete, sender=StatementQualification)
@receiver(post_delete, sender=QualificationDocument)
@receiver(post_delete, sender=SailorPassport)
@receiver(post_delete, sender=ServiceRecord)
@receiver(post_delete, sender=ProofOfWorkDiploma)
def delete_statement_dkk(sender, instance, **kwargs):
    delete_document.delay(instance)
