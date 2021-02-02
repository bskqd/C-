import json

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from communication.models import SailorKeys
from reports.serializers import StatementETISailorSerializer
from sailor.document.models import CertificateETI
from sailor.models import Profile, ContactInfo
from sailor.statement.models import StatementETI

User = get_user_model()


class StatementETISailorSerializer(serializers.RelatedField):
    """
    Information about the sailor in the report on the statements of ETI
    """

    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.filter(statement_eti__overlap=[obj]).first()
        else:
            qs = obj
        if qs is None:
            return {}
        profile = Profile.objects.get(id=qs.profile)
        phone = None
        try:
            user_by_phone = User.objects.get(id=qs.user_id)
            if user_by_phone.username.startswith('+380'):
                phone = user_by_phone.username
        except User.DoesNotExist:
            pass
        if not phone and profile.contact_info:
            contact_json = json.loads(profile.contact_info)
            contact_qs = ContactInfo.objects.filter(id__in=contact_json, type_contact_id=1)
            phone = contact_qs.first().value if contact_qs.exists() else None
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y'),
            'phone': phone
        }


class ETIOnlineStatementSerializer(serializers.ModelSerializer):
    sailor = StatementETISailorSerializer(source='id', queryset=SailorKeys.objects.all())

    class Meta:
        fields = ('id', 'number', 'date_meeting', 'course', 'status_document', 'institution', 'is_payed', 'is_continue',
                  'sailor', 'created_at')
        model = StatementETI
        read_only_fields = ('id', 'number', 'date_meeting', 'course',
                            'institution', 'is_payed', 'is_continue', 'sailor', 'created_at')


class ETIOnlineCertificateETISerializer(serializers.ModelSerializer):
    sailor = serializers.IntegerField(write_only=True)

    class Meta:
        model = CertificateETI
        fields = ('id', 'ntz', 'ntz_number', 'course_training', 'date_start', 'date_end', 'status_document', 'sailor')

    def create(self, validated_data):
        sailor = validated_data.pop('sailor')
        with transaction.atomic():
            instance = super(ETIOnlineCertificateETISerializer, self).create(validated_data=validated_data)
            sailor_instance: SailorKeys = get_object_or_404(SailorKeys, pk=sailor)
            sailor_instance.statement_eti.append(instance.pk)
            sailor_instance.save(update_fields=['statement_eti'])
            return instance
