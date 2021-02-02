from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import directory.serializers
from communication.models import ShipKey
from core.models import (Photo, User, Agent, HeadAgency, HarborWorker, HarborMaster,
                         UserMarad, BorderGuard, PortManager, HeadTowingCompany, TowMaster)
from directory.models import Port, Contacts, Agency
from ship.models import MainInfo
from ship.serializers import MainInfoSerializer, PhotoSerializer
from signature.models import Signature


class PhotoUploaderSerializer(serializers.Serializer):
    photo = serializers.FileField()
    type_photo = serializers.CharField()
    content_type = serializers.CharField()
    document_id = serializers.IntegerField()


class PhotoPutSerializer(serializers.Serializer):
    photo = serializers.FileField()
    photo_id = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all())


class PhotoDeleteSerializer(serializers.Serializer):
    content_type = serializers.CharField()
    document_id = serializers.IntegerField()
    photo_id = serializers.IntegerField()


class ShipSerializer(serializers.Serializer):

    def to_representation(self, instance):
        try:
            filtering = {f'{instance._meta.model_name}__overlap': [instance.pk]}
            ship = ShipKey.objects.get(**filtering)
        except ShipKey.DoesNotExist:
            return MainInfoSerializer(instance=None, context=self.context).data
        try:
            main_info = MainInfo.objects.get(pk=ship.maininfo)
        except MainInfo.DoesNotExist:
            ship.delete()
            return MainInfoSerializer(instance=None, context=self.context).data
        resp = MainInfoSerializer(instance=main_info, context=self.context).data
        return resp


class UserMaradSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)

    class Meta:
        model = UserMarad
        fields = ('id', 'photo',)


class HarborMasterSerializer(serializers.ModelSerializer):
    ports = serializers.PrimaryKeyRelatedField(queryset=Port.objects.all(), required=True, many=True)
    photo = PhotoSerializer(read_only=True)

    class Meta:
        model = HarborMaster
        fields = ('id', 'photo', 'ports')


class HeadAgencySerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)

    class Meta:
        model = HeadAgency
        fields = ('id', 'photo', 'agency', 'inn', 'accept_agreement')
        extra_kwargs = {'inn': {'required': False},
                        'accept_agreement': {'required': False}}


class AgentSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)
    agency = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all(), required=False)

    class Meta:
        model = Agent
        fields = ('id', 'photo', 'agency', 'is_admin', 'inn')
        extra_kwargs = {'inn': {'required': False}}

    def get_is_admin(self, instance):
        return instance.user.has_perm('authorization.agent_admin_agency')


class HarborWorkerSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)
    port = serializers.PrimaryKeyRelatedField(queryset=Port.objects.all())

    class Meta:
        model = HarborWorker
        fields = ('id', 'photo', 'port')


class BorderGuardSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)
    port = serializers.PrimaryKeyRelatedField(queryset=Port.objects.all())

    class Meta:
        model = BorderGuard
        fields = ('id', 'photo', 'port')


class PortManagerSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)
    port = serializers.PrimaryKeyRelatedField(queryset=Port.objects.all())

    class Meta:
        model = PortManager
        fields = ('id', 'photo', 'port')


class HeadTowingCompanySerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)

    class Meta:
        model = HeadTowingCompany
        fields = ('id', 'photo', 'towing_company', 'inn')
        extra_kwargs = {'inn': {'required': False}}


class TowMasterSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(read_only=True)

    class Meta:
        model = TowMaster
        fields = ('id', 'photo', 'tow', 'inn')
        extra_kwargs = {'inn': {'required': False}}


class FullInfoUserSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name', 'type_user', 'info', 'is_changed_password')
        read_only_fields = ('is_changed_password',)

    def get_info(self, instance):
        if instance.type_user == User.MARAD_CH:
            return UserMaradSerializer(instance.user_marad, context=self.context).data
        elif instance.type_user == User.HARBOR_MASTER_CH:
            return HarborMasterSerializer(instance.harbor_master, context=self.context).data
        elif instance.type_user == User.HEAD_AGENCY_CH:
            return HeadAgencySerializer(instance.head_agency, context=self.context).data
        elif instance.type_user == User.AGENT_CH:
            return AgentSerializer(instance.agent, context=self.context).data
        elif instance.type_user == User.HARBOR_WORKER_CH:
            return HarborWorkerSerializer(instance.harbor_worker, context=self.context).data
        elif instance.type_user == User.BORDER_GUARD_CH:
            return BorderGuardSerializer(instance.border_guard, context=self.context).data
        elif instance.type_user == User.PORT_MANAGER_CH:
            return PortManagerSerializer(instance.port_manager, context=self.context).data
        elif instance.type_user == User.HEAD_TOWING_CH:
            return HeadTowingCompanySerializer(instance.head_towing, context=self.context).data
        elif instance.type_user == User.TOW_MASTER_CH:
            return TowMasterSerializer(instance.tow_master, context=self.context).data
        return None


class UserSerializer(serializers.ModelSerializer):
    user_marad = UserMaradSerializer(required=False, allow_null=True)
    harbor_master = HarborMasterSerializer(required=False, allow_null=True)
    head_agency = HeadAgencySerializer(required=False, allow_null=True)
    agent = AgentSerializer(required=False, allow_null=True)
    harbor_worker = HarborWorkerSerializer(required=False, allow_null=True)
    border_guard = BorderGuardSerializer(required=False, allow_null=True)
    port_manager = PortManagerSerializer(required=False, allow_null=True)
    head_towing = HeadTowingCompanySerializer(required=False, allow_null=True)
    tow_master = TowMasterSerializer(required=False, allow_null=True)
    contacts = directory.serializers.ContactsSerializer(required=False, allow_null=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name', 'type_user', 'email', 'password', 'user_marad',
                  'harbor_master', 'head_agency', 'agent', 'harbor_worker', 'border_guard', 'port_manager',
                  'head_towing', 'tow_master', 'contacts', 'date_joined', 'is_active')
        extra_kwargs = {'password': {'write_only': True, 'required': False}}
        read_only_fields = ('date_joined',)

    def validate(self, data):
        author = self.context['request'].user
        all_type_users = ('user_marad', 'harbor_master', 'head_agency', 'agent', 'harbor_worker',
                          'border_guard', 'port_manager', 'head_towing', 'tow_master')
        type_user = data.get('type_user')
        if type_user and type_user in all_type_users and not (set(all_type_users) & set(data.keys())):
            raise serializers.ValidationError('User must include type user')
        agent = data.get('agent')
        if type_user and type_user == User.AGENT_CH and author.type_user != User.HEAD_AGENCY_CH and \
                not agent and not agent.get('agency'):
            raise ValidationError('Agency must be specified')
        return super().validate(data)

    def create(self, validated_data):
        author = self.context['request'].user
        user_marad = validated_data.pop('user_marad', None)
        harbor_master = validated_data.pop('harbor_master', None)
        head_agency = validated_data.pop('head_agency', None)
        harbor_worker = validated_data.pop('harbor_worker', None)
        border_guard = validated_data.pop('border_guard', None)
        port_manager = validated_data.pop('port_manager', None)
        head_towing = validated_data.pop('head_towing', None)
        tow_master = validated_data.pop('tow_master', None)
        agent = validated_data.pop('agent', None)
        try:
            User.objects.filter(harbor_master__ports=harbor_master['ports'], is_active=True).update(is_active=False)
        except (TypeError, AttributeError):
            pass
        type_user = validated_data.get('type_user')
        contacts = validated_data.pop('contacts', [])
        user = User.objects.create_user(type_authorization=User.get_type_authorization(type_user), **validated_data)
        if user.type_user == User.MARAD_CH and user_marad is not None:
            UserMarad.objects.create(user=user, **user_marad)
        elif user.type_user == User.HEAD_AGENCY_CH and head_agency is not None:
            HeadAgency.objects.create(user=user, **head_agency)
        elif user.type_user == User.HARBOR_MASTER_CH and harbor_master is not None:
            ports = harbor_master.pop('ports')
            harbor_master_instance = HarborMaster.objects.create(user=user, **harbor_master)
            Port.objects.filter(id__in=[p.pk for p in ports]).update(harbor_master=harbor_master_instance)
            Signature.objects.filter(
                type_signature=Signature.SIGN,
                is_actual=True,
                port__in=ports).update(is_actual=False)
        elif user.type_user == User.HARBOR_WORKER_CH and harbor_worker is not None:
            HarborWorker.objects.create(user=user, **harbor_worker)
        elif user.type_user == User.BORDER_GUARD_CH and border_guard is not None:
            BorderGuard.objects.create(user=user, **border_guard)
        elif user.type_user == User.PORT_MANAGER_CH and port_manager is not None:
            PortManager.objects.create(user=user, **port_manager)
        elif user.type_user == User.HEAD_TOWING_CH and head_towing is not None:
            PortManager.objects.create(user=user, **head_towing)
        elif user.type_user == User.TOW_MASTER_CH and tow_master is not None:
            TowMaster.objects.create(user=user, **tow_master)
        elif user.type_user == User.AGENT_CH and agent is not None:
            if author.type_user == User.HEAD_AGENCY_CH:
                agent['agency'] = author.head_agency.agency
            Agent.objects.create(user=user, **agent)
        Contacts.objects.bulk_create([Contacts(user=user, **contact) for contact in contacts])
        user.set_default_permission()
        return user

    def update(self, instance: User, validated_data):
        data_for_relation_user = None
        relation_user = None
        contacts = validated_data.pop('contacts', [])
        if instance.type_user == User.MARAD_CH:
            relation_user = instance.user_marad
            data_for_relation_user = validated_data.pop('user_marad', None)
        elif instance.type_user == User.HEAD_AGENCY_CH:
            relation_user = instance.head_agency
            data_for_relation_user = validated_data.pop('head_agency', None)
        elif instance.type_user == User.HARBOR_MASTER_CH:
            relation_user = instance.harbor_master
            data_for_relation_user = validated_data.pop('harbor_master', None)
            data_for_relation_user.pop('ports', None)
        elif instance.type_user == User.HARBOR_WORKER_CH:
            relation_user = instance.harbor_worker
            data_for_relation_user = validated_data.pop('harbor_worker', None)
        elif instance.type_user == User.BORDER_GUARD_CH:
            relation_user = instance.border_guard
            data_for_relation_user = validated_data.pop('border_guard', None)
        elif instance.type_user == User.PORT_MANAGER_CH:
            relation_user = instance.port_manager
            data_for_relation_user = validated_data.pop('port_manager', None)
        elif instance.type_user == User.HEAD_TOWING_CH:
            relation_user = instance.head_towing
            data_for_relation_user = validated_data.pop('head_towing', None)
        elif instance.type_user == User.TOW_MASTER_CH:
            relation_user = instance.tow_master
            data_for_relation_user = validated_data.pop('tow_master', None)
        elif instance.type_user == User.AGENT_CH:
            relation_user = instance.agent
            data_for_relation_user = validated_data.pop('agent', None)
            if data_for_relation_user:
                data_for_relation_user.pop('agency', None)
        if data_for_relation_user and relation_user:
            for attr, value in data_for_relation_user.items():
                setattr(relation_user, attr, value)
            relation_user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if contacts:
            self.update_contacts_user(instance, contacts)
        return instance

    @staticmethod
    def update_contacts_user(user: User, contacts: list):
        for contact in contacts:
            contact_id = contact.pop('contact_id', None)
            Contacts.objects.update_or_create(id=contact_id, user=user, defaults=contact)


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=20)
    old_password = serializers.CharField(max_length=20)

    def validate(self, attrs):
        if attrs['new_password'] == attrs['old_password']:
            raise ValidationError('The new password must not be the same as the old one')
        return super().validate(attrs)
