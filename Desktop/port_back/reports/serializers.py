from rest_framework import serializers

import ship.serializers
from core.serializers import ShipSerializer
from ship.models import IORequest


class IORequestReportSerializer(ship.serializers.IORequestSerializer):
    agency = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = IORequest
        fields = ('id', 'datetime_io', 'port', 'type', 'number', 'next_port', 'cargo', 'remarks', 'ship_staff',
                  'status_document', 'full_number', 'agency', 'next_port_country')
        read_only_fields = fields

    def to_representation(self, instance):
        response = super(IORequestReportSerializer, self).to_representation(instance)
        response['ship'] = ShipSerializer(instance=instance, context=self.context).data
        return response

    def get_agency(self, instance):
        return instance.agency
