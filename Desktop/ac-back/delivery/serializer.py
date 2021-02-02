from rest_framework import serializers

from delivery.models import NovaPoshtaArea, NovaPoshtaCity, NovaPoshtaWarehouse, NovaPoshtaStreet, NovaPoshtaDelivery


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NovaPoshtaArea
        fields = ('id', 'name_ukr')


class NovaPoshtaCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = NovaPoshtaCity
        fields = ('id', 'name_ukr', 'area')


class NovaPoshtaWarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = NovaPoshtaWarehouse
        fields = ('id', 'number', 'name_ukr', 'short_address', 'city')


class NovaPoshtaStreetSerializer(serializers.ModelSerializer):
    name_ukr = serializers.ReadOnlyField(source='get_full_name_ukr')

    class Meta:
        model = NovaPoshtaStreet
        fields = ('id', 'name_ukr')
        read_only = fields


class NovaPoshtaDeliverySerializer(serializers.RelatedField):
    def to_representation(self, value):
        if type(value) is int:
            qs = self.queryset.select_related('city', 'city__area', 'street', 'street__type_street',
                                              'warehouse').get(id=value)
        else:
            qs = value
        response = {'id': qs.id, 'post_service': qs.ukr_name_post, 'is_courier': qs.is_courier,
                    'phone_number': qs.phone_number, 'area': qs.city.area.name_ukr, 'city': qs.city.name_ukr,
                    'house': qs.house, 'apartment': qs.apartment}
        if qs.is_courier:
            if qs.street:
                street = qs.street.type_street.name_ukr + ' ' + qs.street.name_ukr
            else:
                street = qs.other_street
            response.update({'street': street, 'warehouse': None, 'number_warehouse': None})
        else:
            response.update({'street': None, 'warehouse': qs.warehouse.name_ukr,
                             'number_warehouse': qs.warehouse.number})
        return response


class DeliverySerializer(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, NovaPoshtaDelivery):
            serializer = NovaPoshtaDeliverySerializer(read_only=True).to_representation(value)
        else:
            raise Exception('Unexpected type of tagged object')
        return serializer
