from django.core.management import BaseCommand
from django.db.models import F
from datetime import timedelta

from sailor.document.models import ProtocolSQC


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Добавление date_end протоколам ДКК"""
        ProtocolSQC.objects.all().update(date_end=F('date_meeting') + timedelta(days=365))
