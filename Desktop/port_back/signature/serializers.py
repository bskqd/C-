import os

import requests
from django.conf import settings
from rest_framework import serializers, exceptions
from rest_framework.exceptions import PermissionDenied

import signature.utils
from core.models import User
from ship.models import IORequest
from signature.models import Signature, IORequestSign, CenterCertificationKey


class SignatureSerializer(serializers.ModelSerializer):
    file_signature_name = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'created_at', 'is_actual', 'password', 'type_signature', 'ERDPOU', 'name', 'port',
                  'blocked_user', 'agent', 'file_signature_name', 'file_signature')
        read_only_fields = ('created_at', 'is_actual', 'author')
        model = Signature
        extra_kwargs = {'blocked_user': {'allow_null': True, 'allow_empty': True, 'required': False},
                        'file_signature': {'required': False},
                        'password': {'required': False, 'allow_blank': True, 'write_only': True}}

    def create(self, validated_data):
        request = self.context.get('request')
        file_signature = validated_data.get('file_signature')
        user: User = request.user
        if user.type_user == user.AGENT_CH:
            password_signature = validated_data.pop('password')
        else:
            password_signature = validated_data.get('password')
        type_signature = validated_data.get('type_signature')
        if (not user.userprofile.cifra_person or not user.userprofile.cifra_key) \
                and type_signature != Signature.STAMP:
            status, response = signature.utils.register_in_cifra(
                request.user,
                file_signature=file_signature,
                signature_password=password_signature
            )
            if not status:
                raise exceptions.ValidationError({'status': 'Can\'t create a user in cifra',
                                                  'detail': response})
        signature_instance: Signature = super().create(validated_data=validated_data)
        created_port = signature_instance.port_id
        if user.type_user == user.HARBOR_MASTER_CH and validated_data.get('type_signature') == Signature.SIGN:
            ports_to_create = user.harbor_master.ports.exclude(pk=created_port)
            del validated_data['port']
            _ = [Signature.objects.create(**validated_data, port=port) for port in ports_to_create]
        return signature_instance

    def get_file_signature_name(self, instance: Signature):
        if instance.file_signature:
            return os.path.basename(instance.file_signature.name)
        return None


class SignatureUploadSerializer(serializers.Serializer):
    signature = serializers.FileField()


class IORequestSignSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = IORequestSign
        read_only_fields = ('created_at', 'author')

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'POST':
            user = request.user
            if user in attrs.get('signature').blocked_user.all():
                raise PermissionDenied()
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context.get('request').user
        file_signature = validated_data.get('file_signature')

        document: IORequest = validated_data.get('io_request')
        signature_instance: Signature = validated_data.get('signature')
        author_to_send = signature_instance.author
        register_file = file_signature
        if not author_to_send.userprofile.cifra_key:
            if signature_instance.type_signature == signature_instance.STAMP:
                register_signature: Signature = Signature.objects.filter(
                    is_actual=True, type_signature=Signature.SIGN, port=signature_instance.port
                ).first()
                author_to_send = register_signature.author
                io_request_for_getting_file: IORequestSign = register_signature.iorequestsign_set.first()
                register_file = io_request_for_getting_file.file_signature
            response, detail = signature.utils.register_in_cifra(user=author_to_send,
                                                                 file_signature=register_file)
            if not response:
                raise exceptions.ValidationError(detail)
            user.refresh_from_db()
        if not document.cifra_uuid:
            self.send_file_to_cifra(document, author_to_send)
        if document.signatures.count() == 2:
            raise exceptions.ValidationError('The signature was be')
        file_to_send = {'file_signature': file_signature.file.getvalue()}
        headers = {'Authorization': f'Bearer {author_to_send.userprofile.cifra_key}'}
        url = f'{settings.CIFRA_URL}api/v1/documents/{document.cifra_uuid}/counterparty/'
        data_to_send = {'base64_signature': validated_data.get('base64_signature')}
        response = requests.post(url=url, data=data_to_send, files=file_to_send, headers=headers)
        if response.status_code in [requests.status_codes.codes.ok, requests.status_codes.codes.created]:
            signature_inst = document.signatures.create(
                signature=validated_data.get('signature'),
                base64_signature=validated_data.get('base64_signature'),
            )
            signature_inst.file_signature.save(file_signature.name, file_signature)
            return signature_inst
        response_json = response.json()
        raise exceptions.ValidationError(response_json, code=response.status_code)


class CenterCertificationKeySerializer(serializers.ModelSerializer):
    issuerCNs = serializers.CharField(source='issuer_cn')
    ocspAccessPointAddress = serializers.CharField(source='ocsp_address')
    ocspAccessPointPort = serializers.IntegerField(source='ocsp_port')
    cmpAddress = serializers.CharField(source='cmp_address')
    tspAddress = serializers.CharField(source='tsp_address')
    tspAddressPort = serializers.IntegerField(source='tsp_port')
    directAccess = serializers.BooleanField(source='direct_access')
    qscdSNInCert = serializers.BooleanField(source='qscd_SN_in_cert')
    cmpCompatibility = serializers.IntegerField(source='cmp_compatibility')
    certsInKey = serializers.IntegerField(source='certs_in_key')
    name = serializers.SerializerMethodField()

    def get_name(self, instance):
        return instance.issuer_cn[0]

    class Meta:
        fields = ('id', 'issuerCNs', 'ocspAccessPointAddress', 'address', 'ocspAccessPointPort',
                  'cmpAddress', 'tspAddress', 'tspAddressPort', 'directAccess', 'qscdSNInCert',
                  'cmpCompatibility', 'certsInKey', 'name')
        model = CenterCertificationKey
