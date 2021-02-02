import json
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db.models import QuerySet, Value
from django.db.models.functions import Concat
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import notifications.tasks
import port_back.constants
from communication.models import ShipKey
from core.models import Photo, User
from directory.models import TypeDocument
from ship.models import MainInfo, ShipStaff, IORequest, ShipAgentNomination, ShipInPort, DraftDocument, ShipHistory
from signature.models import IORequestSign
import signature.utils


class PhotoSerializer(serializers.Serializer):
    def to_representation(self, instance):
        request = self.context['request']
        if hasattr(self.parent.Meta, 'model'):
            root_instance = self.parent.Meta.model
        elif isinstance(self.root.instance, list):
            root_instance = self.root.instance[0]
        elif isinstance(self.root.instance, QuerySet):
            root_instance = self.root.instance.first()
        else:
            root_instance = self.root.instance
        ct_name = root_instance._meta.model_name
        name_type_documents = list(TypeDocument.objects.values_list('name', flat=True))
        return [{'id': instance.pk,
                 'file': request.build_absolute_uri(instance.file.url),
                 'type_photo': instance.type_photo, 'content_type': ct_name,
                 'cifra_uuid': instance.cifra_uuid}
                for instance in Photo.objects.filter(id__in=instance).exclude(type_photo__in=name_type_documents)]


class PhotoTypeDocumentSerializer(serializers.Serializer):
    def to_representation(self, instance):
        request = self.context['request']
        if isinstance(self.root.instance, list):
            root_instance = self.root.instance[0]
        elif isinstance(self.root.instance, QuerySet):
            root_instance = self.root.instance.first()
        else:
            root_instance = self.root.instance
        ct_name = root_instance._meta.model_name
        result = {}
        type_documents = TypeDocument.objects.values('name', 'group__name')
        name_type_documents = list(type_documents.values_list('name', flat=True))
        list_name_and_group = list(type_documents)
        for p in Photo.objects.filter(id__in=instance, type_photo__in=name_type_documents):
            if p.type_photo in result.keys():
                result[p.type_photo].append({'id': p.pk,
                                             'file': request.build_absolute_uri(p.file.url),
                                             'content_type': ct_name,
                                             'group': self.get_group_type_document(p.type_photo, list_name_and_group),
                                             'cifra_uuid': p.cifra_uuid})
            else:
                result[p.type_photo] = [{'id': p.pk,
                                         'file': request.build_absolute_uri(p.file.url),
                                         'content_type': ct_name,
                                         'group': self.get_group_type_document(p.type_photo, list_name_and_group),
                                         'cifra_uuid': p.cifra_uuid}]
        return result

    @staticmethod
    def get_group_type_document(name_type_document, list_documents):
        for doc in list_documents:
            if doc['name'] == name_type_document:
                return doc['group__name']
        return None


class MainInfoSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)
    author = serializers.ReadOnlyField(source='author_full_name')

    class Meta:
        model = MainInfo
        exclude = ('_photo',)

    def validate(self, attrs):
        is_ban = attrs.get('is_ban')
        ban_comment = attrs.get('ban_comment')
        if is_ban is not None and not ban_comment:
            raise ValidationError('Comment is required to the ban')
        return super().validate(attrs)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        is_ban = validated_data.pop('is_ban', None)
        if is_ban is not None and user.type_user in [User.MARAD_CH, User.ADMIN_CH]:
            instance.is_ban = is_ban
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ShipStaffSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)
    author = serializers.ReadOnlyField(source='author_full_name')

    class Meta:
        model = ShipStaff
        exclude = ('_photo',)
        read_only_fields = ('created_at', 'modified_at')


class IORequestSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)
    full_number = serializers.ReadOnlyField()
    photo_documents = PhotoTypeDocumentSerializer(read_only=True, source='photo')
    author = serializers.ReadOnlyField(source='author_full_name')
    signature_info = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField(read_only=True)
    draft = serializers.PrimaryKeyRelatedField(queryset=DraftDocument.objects.all(),
                                               required=False, allow_null=True)
    payment_info = serializers.SerializerMethodField(read_only=True)
    signature_password = serializers.CharField(write_only=True)

    def get_signature_info(self, instance: IORequest):
        signatures: QuerySet[IORequestSign] = instance.signatures.all()
        return signatures.annotate(
            author_full_name=Concat('author__first_name', Value(' '), 'author__last_name')
        ).values('author_full_name', 'signature__name',
                 'signature__ERDPOU', 'created_at', 'signature__type_signature')

    def get_payment_info(self, instance: IORequest):
        payment_due = 'за організаційно-технічні послуги з ПДВ; '
        requisites = '''Отримувач: __________________________;
Код ЄДРПОУ ____________;
IBAN: UA______________________________;
Призначення платежу: за організаційно-технічні послуги з ПДВ'''
        amount = instance.price_form1
        if instance.is_payed:
            return None
        return {'payment_due': payment_due, 'requisites': requisites, 'amount': amount}

    class Meta:
        model = IORequest
        exclude = ('_photo', 'request_info', 'price_form1')
        read_only_fields = ('created_at', 'modified_at', 'number', 'photo_documents', 'datetime_issued')
        extra_kwargs = {'status_document': {'required': False, 'allow_null': True},
                        'number': {'required': False, 'allow_null': True},
                        'remarks': {'allow_blank': True, 'required': False}}

    def get_price(self, instance):
        return instance.price_form1

    def create(self, validated_data):
        del validated_data['signature_password']
        return super().create(validated_data=validated_data)

    def validate(self, attrs):
        status_document = attrs.get('status_document')
        valid_status_document = status_document and status_document.pk == port_back.constants.ISSUED
        if valid_status_document and not self.instance.is_payed:
            del attrs['status_document']
        # TODO Uncomment when ship's inspection act becomes mandatory
        # if valid_status_document and self.instance.type == IORequest.OUTPUT and not self.instance.inspection_act:
        #     raise ValidationError('Need load ship\'s inspection act')
        return super().validate(attrs)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        ship_key = ShipKey.objects.filter(iorequest__overlap=[instance.pk])
        if ship_key.exists():
            try:
                main_info = MainInfo.objects.get(id=ship_key.first().maininfo)
                response['is_ban'] = main_info.is_ban
                response['ban_comment'] = main_info.ban_comment
            except MainInfo.DoesNotExist:
                pass
        if instance.request_info:
            response['main_info'] = self.change_photo_info([instance.request_info['main_info']], MainInfo)[0]
            response['ship_staff'] = self.change_photo_info(instance.request_info['staff'], ShipStaff)
        return response

    def update(self, instance: IORequest, validated_data):
        ship_key = self.context['view'].kwargs['ship_pk']
        user = self.context['request'].user
        status_document = validated_data.get('status_document')
        valid_status_document = status_document and status_document.pk == port_back.constants.ISSUED
        canceled_status_document = status_document and status_document.pk == port_back.constants.CANCELED
        if valid_status_document:
            self.check_ship_ban(ship_key)
        if valid_status_document and instance.status_document.pk == port_back.constants.PROCESSED:
            self.work_with_ship_in_port(instance, ship_key)
            instance.datetime_issued = datetime.now()
            signature.utils.signature_file(instance)
        if canceled_status_document and instance.status_document.pk == port_back.constants.ISSUED:
            self.update_info_about_ship_in_port(instance, ship_key)
        if status_document and status_document != instance.status_document:
            remarks = validated_data.get('remarks')
            notifications.tasks.informing_about_change_status_iorequest.s(io_request_id=instance.pk,
                                                                          ship_key=ship_key,
                                                                          text_status=status_document.name.lower(),
                                                                          id_author_changes=user.pk,
                                                                          remarks=remarks,
                                                                          ).apply_async()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def check_ship_ban(self, ship_key):
        """
        Checks if the ship is banned
        """
        try:
            main_info = MainInfo.objects.get(id=ship_key)
        except MainInfo.DoesNotExist:
            raise ValidationError('Ship does not exists')
        if main_info.is_ban:
            raise ValidationError('Ship is banned')

    def work_with_ship_in_port(self, io_request: IORequest, ship_key):
        """
        Added or remove ship in port
        """
        agency = None
        if io_request.author.type_user == User.AGENT_CH:
            agency = io_request.author.get_agency
        if io_request.type == IORequest.INPUT:
            try:
                ShipInPort.objects.create(ship_key=ship_key,
                                          port=io_request.port,
                                          input_datetime=io_request.datetime_io,
                                          agency=agency)
            except IntegrityError:
                pass
        else:
            ShipInPort.objects.filter(ship_key=ship_key, port=io_request.port).delete()

    def update_info_about_ship_in_port(self, io_request: IORequest, ship_key):
        """
        Returns the ship to the port (if IORequest type was INPUT) or
        removes it from the port (if IORequest type was OUTPUT)
        when the status changes from Issued to Canceled
        """
        if io_request.type == IORequest.INPUT:
            ShipInPort.objects.filter(ship_key=ship_key, port=io_request.port).delete()
        else:
            ship_history = ShipHistory.objects.filter(
                ship_id=ship_key, content_type__model='shipinport'
            ).order_by('-created_at')
            if ship_history.exists():
                data = ship_history.first().serialized_data
                data_for_insert = {
                    'port_id': data['port'],
                    'agency_id': data['agency'],
                    'ship_key': data['ship_key'],
                    'input_datetime': datetime.strptime(data['input_datetime'], '%Y-%m-%dT%H:%M:%SZ'),
                }
                ShipInPort.objects.create(**data_for_insert)

    def change_photo_info(self, main_info, model):
        """
        Replaces photo_id with full information about the photo
        """
        request = self.context['request']
        for obj in main_info:
            obj_photo = json.loads(obj.pop('_photo'))
            obj['photo'] = [{
                'id': photo.pk,
                'type_photo': photo.type_photo,
                'file': request.build_absolute_uri(photo.file.url),
                'content_type': model._meta.model_name,
            } for photo in Photo.objects.filter(id__in=obj_photo)]
        return main_info


class SearchSerializer(serializers.Serializer):
    query = serializers.CharField()


class ShipAgentNominationSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)
    verifier = serializers.ReadOnlyField(source='verifier.get_user_full_name', allow_null=True)
    agency = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ShipAgentNomination
        fields = ('id', 'agency', 'verifier', 'created_at', 'modified_at', 'status_document', 'port',
                  'photo', 'date_verification', 'rejection_reason')
        read_only_fields = ('created_at', 'modified_at', 'date_verification')
        extra_kwargs = {'status_document': {'required': False, 'allow_null': True},
                        'rejection_reason': {'required': False, 'allow_null': True}}

    def get_agency(self, instance):
        agency = getattr(instance.agent, 'get_agency', None)
        return {'id': agency.pk, 'name': agency.short_name} if agency else None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        try:
            main_info = MainInfo.objects.get(id=instance.ship_key)
        except MainInfo.DoesNotExist:
            main_info = None
        response['author'] = {'id': instance.agent.pk, 'full_name': instance.agent.get_user_full_name}
        response['ship'] = MainInfoSerializer(instance=main_info, context=self.context).data
        return response

    def validate(self, data):
        rejection_reason = data.get('rejection_reason')
        status_document = data.get('status_document')
        if status_document and status_document.pk == port_back.constants.DECLINE and not rejection_reason:
            raise ValidationError('You must indicate the reason for the refusal')
        return super().validate(data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        status_document = validated_data.pop('status_document', None)
        can_change_status = status_document and user.type_user in [User.HARBOR_WORKER_CH,
                                                                   User.HARBOR_MASTER_CH,
                                                                   User.ADMIN_CH]
        valid_status = can_change_status and status_document.pk == port_back.constants.ISSUED
        invalid_status = can_change_status and status_document.pk == port_back.constants.DECLINE
        if valid_status or invalid_status:
            instance.status_document = status_document
            instance.date_verification = datetime.today()
            instance.verifier = user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ShipInPortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipInPort
        fields = ('port', 'input_datetime')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        try:
            main_info = MainInfo.objects.get(id=instance.ship_key)
            response['ship'] = MainInfoSerializer(instance=main_info, context=self.context).data
        except MainInfo.DoesNotExist:
            pass
        return response


class DraftDocumentSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(queryset=ContentType.objects.all(), slug_field='model')

    class Meta:
        model = DraftDocument
        fields = '__all__'
        read_only_fields = ('modified_at', 'author', 'created_at')
