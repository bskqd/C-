import personal_cabinet.serializers
from itcs import magic_numbers


class PersonalServiceRecordSailorSerializer(personal_cabinet.serializers.BasePersonalServiceRecordSailorSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        lines = instance.lines.exclude(status_line_id__in=(magic_numbers.STATUS_REMOVED_DOCUMENT,
                                                           magic_numbers.STATUS_CREATED_BY_AGENT,
                                                           magic_numbers.CREATED_FROM_MORRICHSERVICE))
        response['lines'] = personal_cabinet.serializers.PersonalLineInServiceRecordSerializer(lines,
                                                                                               context=self.context,
                                                                                               many=True).data
        return response
