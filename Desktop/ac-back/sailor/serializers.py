from copy import deepcopy
from datetime import date

from django.conf import settings
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

import directory.serializers
from back_office.models import PacketItem
from back_office.tasks import update_sailor_passport_in_packet
from communication.models import SailorKeys
from directory.models import (Country, Port, Position, Rank, Responsibility,
                              StatusDocument, Sex, VerificationStage)
from itcs import magic_numbers
from sailor import forModelSerializer as customSerializers
from sailor.AbstractSerializer import PrivateField, PrivateVerificationField, ToReprMixin
from sailor.misc import (CheckSailorForPositionDKK, CheckSailorExperience, update_is_active_verification_status,
                         create_verification_status_for_document, verification_stages)
from sailor.models import (ContactInfo, FullAddress, Passport, PhotoProfile, Profile, SailorPassport, DemandPositionDKK,
                           OldName, Rating, DocumentInVerification, CommentForVerificationDocument)
# main info Start
from sailor.tasks import (save_history, check_document_to_additional_verification)
from user_profile.models import FullUserSailorHistory
from .document.models import ResponsibilityServiceRecord, ServiceRecord
from .statement.models import StatementSailorPassport
from .tasks import delete_old_phone


class ProfileMainInfoSerializer(ToReprMixin, serializers.ModelSerializer):
    passport = serializers.DictField(source='get_passport')
    contact_info = customSerializers.ContactSerializator(queryset=ContactInfo.objects.all(), required=False,
                                                         allow_null=True)
    position = serializers.ReadOnlyField(source='get_position_from_qual')
    rank = serializers.ReadOnlyField(source='get_rank_from_qual')
    photo = customSerializers.PhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)
    sex = customSerializers.SexSerializator(queryset=Sex.objects.all())
    date_birth = serializers.DateField(format='%Y-%m-%d')
    created_by = PrivateField(source='_author')
    is_dkk = serializers.ReadOnlyField(source='sailor_is_dkk')
    exists_account = serializers.ReadOnlyField(source='exists_account_personal_cabinet')
    full_old_name = serializers.ReadOnlyField(source='get_old_full_name')
    middle_name_ukr = serializers.CharField(allow_blank=True, required=False)
    middle_name_eng = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    can_verify = serializers.SerializerMethodField()
    has_agent = serializers.ReadOnlyField()
    financial_phone = serializers.ReadOnlyField(source='get_financial_phone')
    is_cadet = serializers.ReadOnlyField()

    class Meta:
        fields = ('id', 'first_name_ukr', 'first_name_eng', 'last_name_ukr', 'last_name_eng', 'middle_name_ukr',
                  'middle_name_eng', 'sex', 'contact_info', 'position', 'rank',
                  'date_birth', 'photo', 'passport', 'created_by', 'is_dkk', 'exists_account', 'full_old_name',
                  'can_verify', 'has_agent', 'financial_phone', 'is_cadet')
        model = Profile

    def update(self, instance, validated_data):
        old_main_info = ProfileMainInfoSerializer(instance).data
        validated_data['contact_info'] = list(validated_data['contact_info'].values_list('id', flat=True))
        if 'get_passport' in validated_data:
            passport_dict = validated_data.pop('get_passport')
            key = SailorKeys.objects.get(id=passport_dict['user_id'])
            try:
                passport = Passport.objects.filter(id__in=key.citizen_passport).first()
                for _key in passport_dict:
                    setattr(passport, _key, passport_dict[_key])
                    passport.save()
            except (TypeError, AttributeError, IndexError, Passport.DoesNotExist):
                del passport_dict['user_id']
                passport = Passport.objects.create(**passport_dict)
                key.citizen_passport = [passport.id]
                key.save(update_fields=['citizen_passport'])
            except IntegrityError:
                raise ValidationError('The sailor with such passport data is exist')
        old_instance = deepcopy(instance)
        info = model_meta.get_field_info(instance)
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
        instance.save()
        key = self.context['request'].parser_context['kwargs']['pk']
        user = self.context['request'].user
        user_id = user.id
        new_instance = deepcopy(instance)
        delete_old_phone.s(old_instance=old_instance, new_instance=new_instance).apply_async(serializer='pickle')
        new_main_info = ProfileMainInfoSerializer(instance=instance).data
        save_history.s(user_id=user_id, sailor_key_id=key, module='Profile', action_type='edit',
                       content_obj=instance, new_obj=new_main_info,
                       old_obj=old_main_info).apply_async(serializer='pickle')
        return instance

    def create(self, validated_data):
        list_passport = None
        passport_dict = None
        if 'get_passport' in validated_data:
            passport_dict = validated_data['get_passport']
            del validated_data['get_passport']
        qs, created = Profile.objects.get_or_create(**validated_data)
        if not created:
            try:
                key = SailorKeys.objects.get(profile=qs.id)
                if key.citizen_passport is None and passport_dict:
                    passport = Passport.objects.create(**passport_dict).id
                    key.citizen_passport = [passport]
                    key.save(update_fields=['citizen_passport'])
                qs.id = key.id
                return qs
            except SailorKeys.DoesNotExist:
                pass
        if passport_dict:
            passport = Passport.objects.create(**passport_dict).id
            list_passport = [passport]
        key = SailorKeys.objects.create(profile=qs.id, citizen_passport=list_passport)
        user = self.context['request'].user
        user_id = user.id
        save_history.s(user_id=user_id, sailor_key_id=key.id, module='Profile', action_type='create',
                       content_obj=qs, serializer=ProfileMainInfoSerializer, new_obj=qs). \
            apply_async(serializer='pickle')
        qs.id = key.id
        return qs

    def get_can_verify(self, instance):
        try:
            user = self.context['request'].user
            return instance.can_verify(user.pk)
        except Exception:
            return False

    # def destroy(self):


class ShortMainInfoSerializer(ProfileMainInfoSerializer):
    class Meta:
        model = Profile
        fields = ('first_name_ukr', 'first_name_eng', 'last_name_ukr', 'last_name_eng', 'middle_name_ukr',
                  'middle_name_eng', 'passport', 'contact_info', 'date_birth')


class ResponsibilityServiceRecordSerializer(serializers.ModelSerializer):
    responsibility = customSerializers.ResponsibilityForServiceRecordSerializer(queryset=Responsibility.objects.all(),
                                                                                allow_null=True, allow_empty=True)

    class Meta:
        model = ResponsibilityServiceRecord
        fields = ['id', 'date_from', 'date_to', 'days_work', 'responsibility', 'is_repaired']
        read_only_fields = ['is_repaired']

    def to_internal_value(self, data):
        if not data.get('days_work'):
            data['days_work'] = None
        if not data.get('date_from') or not data.get('date_to'):
            data['date_from'] = None
            data['date_to'] = None
        return super().to_internal_value(data)


class PhotoProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoProfile
        fields = '__all__'


class SailorPassportSerializer(serializers.ModelSerializer):
    sailor = serializers.IntegerField(write_only=True)
    country = customSerializers.CountrySeriallizer(queryset=Country.objects.all())
    port = customSerializers.PortSerailizer(queryset=Port.objects.all(), allow_null=True, required=False)
    status_document = customSerializers.StatusDocumentSerializer(queryset=StatusDocument.objects.filter(
        for_service='ServiceRecord'), required=False, allow_null=True)
    photo = customSerializers.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    created_by = PrivateField(source='_author')
    verificated_by = PrivateVerificationField(source='_verificator')
    verification_status = serializers.PrimaryKeyRelatedField(queryset=VerificationStage.objects.all(),
                                                             required=False, write_only=True)

    class Meta:
        model = SailorPassport
        fields = ('id', 'sailor', 'country', 'number_document', 'date_start', 'date_end', 'port', 'captain',
                  'photo', 'status_document', 'other_port', 'created_by', 'verificated_by', 'date_renewal',
                  'verification_status', 'is_new_document')
        read_only_fields = ('is_new_document',)

    def create(self, validated_data):
        del validated_data['sailor']
        return SailorPassport.objects.create(**validated_data)

    def update(self, instance, validated_data):
        verification_status = validated_data.pop('verification_status', None)
        if verification_status:
            update_is_active_verification_status(instance, verification_status.pk)
        today = date.today()
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        if 'status_document' in validated_data and instance.status_document_id in [
            magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT
        ]:
            if settings.ENABLE_ADDITIONAL_VERIFICATION is True and validated_data.get(
                    'status_document').pk in magic_numbers.ALL_VALID_STATUSES:
                validated_data['status_document_id'] = magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION
                check_document_to_additional_verification.s(self.instance._meta.model_name, instance.pk).apply_async()
            elif validated_data.get('status_document').pk in magic_numbers.ALL_VALID_STATUSES:
                update_sailor_passport_in_packet.delay(instance.pk, None, True)
        date_renewal = validated_data.get('date_renewal')
        if instance.status_document_id == magic_numbers.status_qual_doc_expired and \
                date_renewal and date_renewal > today:
            validated_data['status_document_id'] = magic_numbers.status_service_record_valid
        status_document = validated_data.get('status_document')
        if instance.status_document.pk != magic_numbers.VERIFICATION_STATUS and status_document and \
                status_document.pk == magic_numbers.VERIFICATION_STATUS:
            create_verification_status_for_document(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        save_history.s(user_id=user_id, module='SailorPassport', action_type='edit',
                       content_obj=instance, serializer=SailorPassportSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            response['verification_status'] = verification_stages(instance, context=self.context)
        return response


class DemandPositionDKKSerializer(serializers.ModelSerializer):
    list_positions = customSerializers.PositionSerializer(queryset=Position.objects.all())
    rank = customSerializers.RankSerializer(queryset=Rank.objects.all())
    demand_dkk = serializers.ReadOnlyField(source='get_demand_position', read_only=True)
    status_document = customSerializers.StatusDocumentSerializer(queryset=StatusDocument.objects.all(), required=False)
    sailor = serializers.IntegerField(write_only=True)
    date_create = serializers.DateTimeField(source='created_at', read_only=True)
    date_modified = serializers.DateTimeField(source='modified_at', read_only=True)

    class Meta:
        model = DemandPositionDKK
        fields = (
            'id', 'sailor', 'list_positions', 'rank', 'date_create', 'date_modified', 'demand_dkk', 'status_document')

    def create(self, validated_data):
        del validated_data['sailor']
        return DemandPositionDKK.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        sailor_id = self.initial_data['sailor']
        status_document = magic_numbers.status_demand_pos_all_enough
        instance.related_docs.clear()
        instance.dependency_docs.clear()
        checking = CheckSailorForPositionDKK(sailor=sailor_id, is_continue=instance.is_continue,
                                             list_position=instance.list_positions, demand_position=True)
        documents = checking.get_docs_with_status()
        is_experience = instance.is_experience
        if is_experience is False:
            checking_exp = CheckSailorExperience(sailor=sailor_id, list_position=instance.list_positions)
            experince = checking_exp.check_experience_many_pos()
            if experince:
                is_experience = any(exp['value'] for exp in experince)
                instance.is_experience = is_experience
        if documents['not_exists_docs'] and is_experience is False:
            status_document = magic_numbers.status_demand_pos_all_not_enough
        elif documents['not_exists_docs']:
            status_document = magic_numbers.status_demand_pos_not_documents
        elif is_experience is False:
            status_document = magic_numbers.status_demand_pos_not_experience
        instance.related_docs = documents.get('all_docs', [])
        instance.dependency_docs.set(documents.get('not_exists_docs', []))
        instance.status_document_id = status_document
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        save_history.s(user_id=user_id, module='DemandPositionDKK', action_type='edit',
                       content_obj=instance, serializer=DemandPositionDKKSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance


class CitizenPassportSerializer(ToReprMixin, serializers.ModelSerializer):
    country = customSerializers.CountrySeriallizer(queryset=Country.objects.all())
    city_registration = customSerializers.FullAddressSerializer(queryset=FullAddress.objects.all(), allow_null=True,
                                                                required=False)
    resident = customSerializers.FullAddressSerializer(queryset=FullAddress.objects.all(), allow_null=True,
                                                       required=False)
    photo = customSerializers.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    date = serializers.DateField(format='%Y-%m-%d')
    country_birth = customSerializers.CountrySeriallizer(queryset=Country.objects.all(), allow_null=True,
                                                         allow_empty=True, required=False)
    sailor = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    created_by = PrivateField(source='_author')
    inn = serializers.CharField(default='', required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Passport
        fields = ('id', 'serial', 'date', 'issued_by', 'country', 'photo', 'city_registration', 'resident', 'inn',
                  'country_birth', 'sailor', 'created_by')

    def create(self, validated_data):
        if 'sailor' in validated_data:
            del validated_data['sailor']
        if Passport.objects.filter(serial=validated_data['serial'], inn=validated_data['inn']).exists():
            return Passport.objects.filter(serial=validated_data['serial'], inn=validated_data['inn']).first()
        return Passport.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'sailor' in validated_data:
            del validated_data['sailor']
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        save_history.s(user_id=user_id, module='CitizenPassport', action_type='edit',
                       content_obj=instance, serializer=CitizenPassportSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoProfile
        fields = '__all__'


class FullUserSailorHistorySerializer(serializers.ModelSerializer):
    datetime = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    content_type = serializers.SerializerMethodField()
    sailor = serializers.IntegerField(source='sailor_key')

    class Meta:
        model = FullUserSailorHistory
        fields = ('full_user_name', 'sailor_key', 'datetime', 'module', 'old_obj_json', 'new_obj_json', 'content_type',
                  'sailor')
        read_only = fields
        read_only_fields = fields

    def get_content_type(self, instance):
        if instance.content_type:
            return instance.content_type.model
        return None


class OldNameSerializer(serializers.ModelSerializer):
    date_create = serializers.DateTimeField(read_only=True, source='created_at')
    photo = customSerializers.PhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)
    sailor = serializers.IntegerField(write_only=True)
    last_name_ukr = serializers.CharField(source='new_last_name_ukr', required=False)
    last_name_eng = serializers.CharField(source='new_last_name_eng', required=False)
    first_name_ukr = serializers.CharField(source='new_first_name_ukr', required=False)
    first_name_eng = serializers.CharField(source='new_first_name_eng', required=False)
    middle_name_ukr = serializers.CharField(source='new_middle_name_ukr', required=False)
    middle_name_eng = serializers.CharField(source='new_middle_name_eng', required=False)

    class Meta:
        model = OldName
        fields = ('id', 'change_date', 'photo', 'date_create', 'sailor', 'old_last_name_ukr',
                  'old_last_name_eng', 'old_first_name_ukr', 'old_first_name_eng', 'old_middle_name_ukr',
                  'old_middle_name_eng', 'last_name_ukr', 'last_name_eng', 'first_name_ukr', 'first_name_eng',
                  'middle_name_ukr', 'middle_name_eng')
        read_only_fields = ('old_last_name_ukr', 'old_last_name_eng', 'old_first_name_ukr', 'old_first_name_eng',
                            'old_middle_name_ukr', 'old_middle_name_eng')

    def create(self, validated_data):
        del validated_data['sailor']
        return OldName.objects.create(**validated_data)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        profile = instance.profile
        sailor_instance = SailorKeys.objects.filter(profile=profile.id).first()
        if not sailor_instance:
            raise ValidationError('Sailor does not exists')
        change_date = validated_data.pop('change_date', None)
        all_change_name = OldName.objects.filter(profile_id=profile.id).order_by('-change_date')
        if instance.id != all_change_name.first().id:
            raise ValidationError('only last record can be edited')
        if change_date:
            date_less = all_change_name.exclude(id=instance.id).filter(change_date__lte=instance.change_date)
            if change_date < instance.change_date and \
                    date_less.exists() and date_less.first().change_date >= change_date:
                raise ValidationError('less date exists')
            instance.change_date = change_date
        _instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        if validated_data:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            new_name_for_profile = {
                'first_name_ukr': validated_data.get('new_first_name_ukr') or profile.first_name_ukr,
                'first_name_eng': validated_data.get('new_first_name_eng') or profile.first_name_eng,
                'last_name_ukr': validated_data.get('new_last_name_ukr') or profile.last_name_ukr,
                'last_name_eng': validated_data.get('new_last_name_eng') or profile.last_name_eng,
                'middle_name_ukr': validated_data.get('new_middle_name_ukr') or profile.middle_name_ukr,
                'middle_name_eng': validated_data.get('new_middle_name_eng') or profile.middle_name_eng
            }
            for attr, value in new_name_for_profile.items():
                setattr(profile, attr, value)
            profile.save()
        instance.save()
        save_history.s(user_id=user_id, module='SailorOldName', action_type='edit',
                       content_obj=_instance, serializer=OldNameSerializer, new_obj=instance,
                       old_obj=_instance, sailor_key_id=sailor_instance.pk).apply_async(serializer='pickle')
        return instance


class RatingSerializer(serializers.ModelSerializer):
    statement = serializers.PrimaryKeyRelatedField(queryset=PacketItem.objects.all(), write_only=True,
                                                   required=False, allow_null=True)

    class Meta:
        model = Rating
        fields = ('rating', 'statement')


class DeletePhotoSerializer(serializers.Serializer):
    type_document = serializers.CharField()
    id_document = serializers.IntegerField()


class CheckContinueSerializer(serializers.Serializer):
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all(), many=True)


class CommentForVerificationSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='_author')
    document_id = serializers.PrimaryKeyRelatedField(queryset=DocumentInVerification.objects.all(), write_only=True)

    class Meta:
        model = CommentForVerificationDocument
        fields = ('id', 'comment', 'author', 'document_id')

    def to_representation(self, instance):
        # TODO check on line in service record (Why the context is empty?)
        if not self.context:
            return None
        user = self.context['request'].user
        response = super().to_representation(instance)
        if not hasattr(user, 'userprofile'):
            response.pop('author', None)
            response['date'] = instance.created_at
        return response


class VerificationStageForDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentInVerification
        fields = '__all__'

    def to_representation(self, instance):
        response = {'document_id': instance.pk}
        response.update(directory.serializers.VerificationStageSerializer(instance.verification_status).data)
        response['is_active'] = instance.is_active
        if instance.comments.exists():
            response['commments'] = CommentForVerificationSerializer(instance.comments.all(),
                                                                     many=True,
                                                                     context=self.context).data
        else:
            response['commments'] = []
        return response


class MergeSailorSerializer(serializers.Serializer):
    old_sailor = serializers.PrimaryKeyRelatedField(queryset=SailorKeys.objects.all())


class CreateNewServiceRecordSerializer(serializers.ModelSerializer):
    statement = serializers.PrimaryKeyRelatedField(
        queryset=StatementSailorPassport.objects.filter(
            status_document_id=StatementSailorPassport.StatusDocument.APPROVED,
            sailor_passport__isnull=True),
        write_only=True)
    passport = serializers.PrimaryKeyRelatedField(queryset=SailorPassport.objects.all(), required=False,
                                                  allow_null=True)

    class Meta:
        fields = ('id', 'statement', 'number_document', 'passport')
        model = SailorPassport

    def create(self, validated_data):
        view = self.context.get('view')
        statement: StatementSailorPassport = validated_data.pop('statement', None)
        if not view:
            raise ValidationError('Can\'t create with this request')
        with transaction.atomic():
            instance = super(CreateNewServiceRecordSerializer, self).create(validated_data=validated_data)
            sailor_instance: SailorKeys = get_object_or_404(SailorKeys, pk=view.kwargs.get('sailor_pk'))
            print(sailor_instance)
            sailor_instance.sailor_passport.append(instance.pk)
            sailor_instance.save(update_fields=['sailor_passport'])
            if statement:
                statement.sailor_passport = instance
                statement.save(update_fields=['sailor_passport'])
        return instance

    def update(self, instance, validated_data):
        statement = validated_data.pop('statement', None)
        instance = super(CreateNewServiceRecordSerializer, self).update(instance=instance,
                                                                        validated_data=validated_data)
        if statement:
            statement.sailor_passport = instance
            statement.save(update_fields=['sailor_passport'])
        return instance
