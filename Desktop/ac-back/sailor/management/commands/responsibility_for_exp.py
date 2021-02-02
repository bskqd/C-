from django.core.management import BaseCommand
from copy import deepcopy

from sailor.document.models import LineInServiceRecord, ResponsibilityServiceRecord
from directory.models import Responsibility


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Добавление обязанностей из старых записей ПКМ в таблицу responsibilityservicerecord"""
        have_responsibility = set(ResponsibilityServiceRecord.objects.values_list('service_record_line', flat=True))
        line = LineInServiceRecord.objects.filter(responsibility__isnull=False).exclude(id__in=have_responsibility)
        responsibility_ids = list(Responsibility.objects.all().values_list('id', flat=True))
        all_responsibility = []
        for exp in line:
            for _id in exp.responsibility:
                if _id not in responsibility_ids:
                    continue
                all_responsibility.append(ResponsibilityServiceRecord(date_from=exp.date_start, date_to=exp.date_end,
                                                                      service_record_line_id=exp.id,
                                                                      responsibility_id=_id))
        ResponsibilityServiceRecord.objects.bulk_create(all_responsibility, ignore_conflicts=True)
