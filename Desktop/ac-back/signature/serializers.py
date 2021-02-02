from django.contrib.auth import get_user_model
from rest_framework import serializers

from signature.models import CommissionerSignProtocol

User = get_user_model()


class CommissionerSerializer(serializers.ModelSerializer):
    user_fio_ukr = serializers.SerializerMethodField()

    def get_user_fio_ukr(self, obj):
        try:
            return f'{obj.signer.name}'
        except AttributeError:
            return None

    class Meta:
        model = CommissionerSignProtocol
        fields = ('signer', 'commissioner_type', 'user_fio_ukr')
        read_only = ('get_user_fio_ukr',)


class CommissionerSignSerializer(serializers.Serializer):
    signer = serializers.CharField()
    commissioner_type = serializers.CharField(max_length=2)


class ListCommissionerForProtocolSerializer(serializers.ModelSerializer):
    middle_name = serializers.SerializerMethodField()

    def get_middle_name(self, obj):
        return obj.userprofile.middle_name

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'middle_name')


class DocumentToSignForUserSerialzier(serializers.ModelSerializer):
    protocol_number = serializers.ReadOnlyField()
    protocol_status = serializers.ReadOnlyField()
    sailor = serializers.ReadOnlyField()
    sailor_full_name = serializers.ReadOnlyField()

    class Meta:
        model = CommissionerSignProtocol
        fields = ('id', 'signer', 'is_signatured', 'signature_type', 'protocol_number', 'protocol_status', 'sailor',
                  'sailor_full_name')
