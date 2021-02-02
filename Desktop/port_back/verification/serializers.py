from django.core.validators import RegexValidator
from rest_framework import serializers

from directory.models import Port, StatusDocument, Flag, TypeVessel
from ship.models import IORequest

io_number_validator = RegexValidator(r'\d+\/\d{4,4}', 'io_number must be like a 15/2021.')


class PublicVerificationQuerySerializer(serializers.Serializer):
    io_number = serializers.CharField(validators=[io_number_validator], required=False)
    imo_number = serializers.CharField(min_length=7, max_length=10, required=False)
    qr_code = serializers.CharField(required=False)


class PublicVerificationSerializer(serializers.ModelSerializer):
    full_number = serializers.ReadOnlyField()
    port = serializers.SlugRelatedField(slug_field='name', queryset=Port.objects.all())
    status_document = serializers.SlugRelatedField(slug_field='name', queryset=StatusDocument.objects.all())
    captain_full_name = serializers.SerializerMethodField()

    class Meta:
        model = IORequest
        fields = ('full_number', 'datetime_issued', 'datetime_io', 'port', 'type',
                  'next_port', 'cargo', 'status_document', 'ship_name', 'next_port_country',
                  'deadweight', 'request_info', 'captain_full_name', 'remarks')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        request_info = response.pop('request_info')
        del request_info['staff']
        del request_info['main_info']['id']
        del request_info['main_info']['_photo']
        del request_info['main_info']['author']
        del request_info['main_info']['is_ban']
        del request_info['main_info']['created_at']
        del request_info['main_info']['ban_comment']
        request_info['main_info']['flag'] = Flag.objects.get(id=request_info['main_info'].pop('flag')).name
        request_info['main_info']['type_vessel'] = TypeVessel.objects.get(
            id=request_info['main_info'].pop('type_vessel')
        ).name
        response['request_info'] = request_info
        return response

    def get_captain_full_name(self, instance: IORequest):
        captain = instance.ship_staff.filter(position=1).first()
        if captain:
            return captain.full_name
        else:
            return None
