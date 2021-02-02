from django.core.management import BaseCommand

from communication.models import SailorKeys
from user_profile.models import FullUserSailorHistory


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Added sailor key to FullUserHistory for LineInServiceRecord
        """
        list_obj = []
        for obj in FullUserSailorHistory.objects.filter(sailor_key=None, content_type__model='lineinservicerecord'):
            line_in_service_record = obj.content_object
            if not line_in_service_record or not hasattr(line_in_service_record, 'id'):
                continue
            if getattr(line_in_service_record.service_record, 'id', None):
                service_record = line_in_service_record.service_record.id
                sailor_key_id = SailorKeys.objects.filter(service_records__overlap=[service_record]).first().id
            else:
                sailor_key_id = SailorKeys.objects.filter(
                    experience_docs__overlap=[line_in_service_record.id]).first().id
            obj.sailor_key = sailor_key_id
            list_obj.append(obj)
        FullUserSailorHistory.objects.bulk_update(list_obj, ['sailor_key'])
        FullUserSailorHistory.objects.filter(module='LineServiceRecord').update(module='LineInServiceRecord')
