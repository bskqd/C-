from django.core.management import BaseCommand

from communication.models import SailorKeys
from sailor.document.models import Education


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Добавление date_end протоколам ДКК"""
        education_docs = Education.objects.filter(id__lt=184000, status_document_id=34)
        for document in education_docs:
            sailor_key = SailorKeys.objects.filter(education__overlap=[document.pk])
            sailor_key = sailor_key.first()
            sailor_key.education.remove(document.pk)
            document.delete()
