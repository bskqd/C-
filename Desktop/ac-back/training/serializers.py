import json

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import serializers

from communication.models import SailorKeys
from directory.models import Commisioner, Position, Decision, StatusDocument
from directory.serializers import RankSerializer
from reports.serializers import ListStatementDKKSerializer
from sailor.document.models import ProtocolSQC
from sailor.document.serializers import ProtocolDKKSerializer
from sailor.forModelSerializer import PositionSerializer
from sailor.models import ContactInfo, Profile
from sailor.statement.models import StatementSQC
from signature.models import CommissionerSignProtocol
from signature.serializers import CommissionerSignSerializer


class ListSailorSerializer(serializers.RelatedField):
    def to_representation(self, obj):
        try:
            if type(obj) is int:
                qs = self.queryset.get(id=obj)
            else:
                qs = obj
        except ObjectDoesNotExist:
            qs = SailorKeys.objects.only('protocol_dkk', 'profile', 'pk').filter(
                statement_dkk__overlap=[self.parent._instance.pk]).first()
            if not qs:
                return {
                    'id': None,
                    'full_name_ukr': '',
                    'full_name_eng': '',
                    'birth_date': '',
                    'phone': []
                }
            self.parent._instance.sailor = qs.pk
            self.parent._instance.save(update_fields=['sailor'])
        profile = Profile.objects.get(id=qs.profile)
        try:
            contact_ids = json.loads(profile.contact_info)
        except:
            contact_ids = []
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y'),
            'phone': list(
                ContactInfo.objects.filter(id__in=contact_ids, type_contact_id=1).values_list('value', flat=True))
        }


class StatementDKKTrainingSerializer(ListStatementDKKSerializer):
    sailor = ListSailorSerializer(queryset=SailorKeys.objects.all())
    rank = RankSerializer(read_only=True)
    position = PositionSerializer(source='list_positions', queryset=Position.objects.all())

    class Meta:
        model = StatementSQC
        fields = (
            'id', 'number', 'date_create', 'date_meeting', 'branch_office', 'sailor', 'status_document',
            'protocol_number',
            'number_document', 'position', 'rank', 'is_experience_required', 'is_continue', 'userexam_id',
            'is_cadet')
        read_only = ('id', 'number', 'date_create', 'branch_office', 'sailor', 'status_document', 'protocol_number',
                     'number_document', 'position', 'rank', 'is_experience_required', 'is_continue')


class DetailStatementDKKTrainingSerializer(ListStatementDKKSerializer):
    status_dkk = serializers.ReadOnlyField(source='get_status_position', read_only=True)
    sailor = ListSailorSerializer(queryset=SailorKeys.objects.all())

    class Meta:
        model = StatementSQC
        fields = ('id', 'number', 'date_create', 'branch_office', 'sailor', 'status_document', 'protocol_number',
                  'number_document', 'position', 'rank', 'is_experience_required', 'is_continue', 'userexam_id',
                  'status_dkk')
        read_only = ('id', 'number', 'date_create', 'branch_office', 'sailor', 'status_document', 'protocol_number',
                     'number_document', 'position', 'rank', 'is_experience_required', 'is_continue')


# class CommitteHeadByName(serializers.ModelSerializer):
#     class Meta:
#         fields = ('FIO_main',)
#         model = Committe


class ProtocolDKKTrainingSerializer(ProtocolDKKSerializer):
    commissioner_sign = CommissionerSignSerializer(many=True)
    decision = serializers.PrimaryKeyRelatedField(queryset=Decision.objects.all(), required=False, allow_null=True)
    status_document = serializers.PrimaryKeyRelatedField(queryset=StatusDocument.objects.all(),
                                                         required=False, allow_null=True)

    def create(self, validated_data):
        commissioner_sign = None
        if 'commissioner_sign' in validated_data:
            commissioner_sign = validated_data.pop('commissioner_sign')
        if 'sailor' in validated_data:
            validated_data['_sailor'] = validated_data.pop('sailor')
        protocol = ProtocolSQC.objects.create(**validated_data)
        if commissioner_sign:
            for commissioner in commissioner_sign:
                signer, _ = Commisioner.objects.get_or_create(name=commissioner.get('signer'))
                CommissionerSignProtocol.objects.create(
                    signer_id=signer.pk,
                    protocol_dkk=protocol,
                    commissioner_type=commissioner.get('commissioner_type', 'SC'),
                    is_signatured=True
                )
        return protocol

    def get_signing(self, obj):
        try:
            signing = CommissionerSignProtocol.objects.filter(protocol_dkk=obj)
            sign_status = signing.filter(is_signatured=True).exists()
            sign_access = signing.exists() is True and signing.filter(is_signatured=False).exists() is True
            return {'sign_status': sign_status, 'sign_access': sign_access}
        except (AttributeError, ValidationError, IndexError, KeyError):
            return {'sign_status': None, 'sign_access': None}


class RequestTokenSerializer(serializers.Serializer):
    domain = serializers.CharField()


class SearchSailorSerializer(serializers.Serializer):
    phone = serializers.CharField()
    sailor_id = serializers.CharField()
