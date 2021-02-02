from copy import deepcopy

from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

import sailor.document.serializers
import sailor.tasks
from itcs import magic_numbers
from sailor.document.models import LineInServiceRecord, ServiceRecord
from user_profile.models import FullUserSailorHistory


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Updating the statuses of dependent records of remote service record
        """
        content_type = ContentType.objects.get_for_model(model=ServiceRecord)
        for service_record in ServiceRecord.objects.filter(status_document_id=magic_numbers.STATUS_REMOVED_DOCUMENT):
            user_id = None
            sailor_key = None
            for history in FullUserSailorHistory.objects.filter(content_type=content_type,
                                                                object_id=service_record.id,
                                                                action_type='edit',
                                                                old_obj_json__isnull=False,
                                                                new_obj_json__isnull=False):
                old_status = history.old_obj_json.get('status') or history.old_obj_json.get('status_document')
                new_status = history.new_obj_json.get('status') or history.new_obj_json.get('status_document')
                sailor_key = history.sailor_key
                if new_status and new_status['id'] == 86 and old_status and old_status['id'] != 86:
                    user_id = history.user.pk
                    break
            for line in service_record.lines.all():
                line: LineInServiceRecord
                if line.status_line_id == magic_numbers.STATUS_REMOVED_DOCUMENT:
                    continue
                old_line = deepcopy(line)
                line.status_line_id = magic_numbers.STATUS_REMOVED_DOCUMENT
                line.save(update_fields=['status_line'])
                if not user_id:
                    user_id = 13
                sailor.tasks.save_history.s(user_id=user_id,
                                            sailor_key_id=sailor_key,
                                            module='LineInServiceRecord',
                                            content_obj=line,
                                            serializer=sailor.document.serializers.LineInServiceRecordSerializer,
                                            old_obj=old_line,
                                            new_obj=line,
                                            action_type='edit'
                                            ).apply_async(serializer='pickle')
