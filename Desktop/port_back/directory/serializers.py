from rest_framework import serializers

from directory.models import (TypeVessel, Flag, StaffPosition, Port, StatusDocument, TypeDocument, Agency, Contacts,
                              Country, Sex, TowingCompany, Tow, TowingCompanyDocs, TowDocs)


class TypeVesselSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeVessel
        fields = '__all__'


class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffPosition
        fields = '__all__'


class PortSerializer(serializers.ModelSerializer):
    harbor_master = serializers.IntegerField(source='harbor_master.user_id', read_only=True)

    class Meta:
        model = Port
        fields = '__all__'


class StatusDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusDocument
        fields = '__all__'


class TypeDocumentSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField()

    class Meta:
        model = TypeDocument
        fields = '__all__'


class AgencySerializer(serializers.ModelSerializer):
    head_of_agency = serializers.IntegerField(source='agency_user.user_id', read_only=True)

    class Meta:
        model = Agency
        fields = ('id', 'short_name', 'full_name', 'address', 'post_address',
                  'IBAN', 'MFO', 'EDRPOU', 'phone', 'head_of_agency')


class TowingCompanySerializer(serializers.ModelSerializer):
    head_towing = serializers.IntegerField(source='head_towing.user_id', read_only=True)

    class Meta:
        model = TowingCompany
        fields = ('id', 'short_name', 'full_name', 'address', 'post_address', 'status'
                  'IBAN', 'MFO', 'EDRPOU', 'phone', 'head_towing')


class TowSerializer(serializers.ModelSerializer):
    tow_master = serializers.IntegerField(source='tow_master.user_id', read_only=True)

    class Meta:
        model = Tow
        fields = ('id', 'IMO', 'name', 'power', 'port', 'status', 'busy_to', 'tow_master')
        extra_kwargs = {'busy_to': {'required': False}}


class TowingCompanyDocsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TowingCompanyDocs
        fields = '__all__'


class TowDocsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TowDocs
        fields = '__all__'


class ContactsSerializer(serializers.ModelSerializer):
    contact_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Contacts
        fields = ('id', 'value', 'type_contact', 'contact_id')


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class SexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sex
        fields = '__all__'
