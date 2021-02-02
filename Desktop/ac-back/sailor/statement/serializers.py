from copy import deepcopy
from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import raise_errors_on_nested_writes

import certificates.tasks
from back_office.tasks import update_sailor_passport_in_packet
from communication.models import SailorKeys
from delivery.serializer import DeliverySerializer
from directory.models import StatusDocument, LevelQualification, Rank, Position, Port, TypeDocument
from directory.serializers import (LevelQualitifcationSerializer, NZSerializer, StatusDocumentSerializer,
                                   PositionForMedicalSerializer, MedicalInstitutionSerializer, SmallETISerializer,
                                   CourseForNTZSerializer,
                                   PortSerializer, PortCaptainSerializer)
from itcs import magic_numbers
from sailor import forModelSerializer as customSerializer
from sailor.AbstractSerializer import PrivateField, PrivateVerificationField
from sailor.document.models import ProtocolSQC
from sailor.misc import update_date_meeting_statement_dpd
from sailor.models import PhotoProfile, SailorPassport, Profile
from sailor.serializers import SailorPassportSerializer
from sailor.statement.models import (StatementServiceRecord, StatementAdvancedTraining, StatementMedicalCertificate,
                                     StatementSQC, StatementQualification, StatementETI,
                                     StatementSailorPassport)
from sailor.statement.tasks import disable_old_sailor_passport
from sailor.tasks import save_history


class StatementServiceRecordListSerializer(serializers.RelatedField):
    def to_representation(self, obj):
        try:
            if type(obj) is int:
                qs = self.queryset.get(id=obj)
            else:
                qs = obj
        except ObjectDoesNotExist:
            try:
                qs = SailorKeys.objects.only('protocol_dkk', 'profile', 'pk').filter(
                    statement_service_records__overlap=[self.parent._instance.pk]).first()
                if not qs:
                    raise AttributeError
            except AttributeError:
                return {
                    'id': None,
                    'full_name_ukr': '',
                    'full_name_eng': '',
                    'birth_date': ''
                }
        profile = Profile.objects.get(id=qs.profile)
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y')
        }

    def to_internal_value(self, data):
        return data


class StatementServiceRecordSerializer(serializers.ModelSerializer):
    status_document = customSerializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all(), required=False,
                                                                source='status')
    sailor = StatementServiceRecordListSerializer(required=False, queryset=SailorKeys.objects.all())
    delivery = DeliverySerializer(read_only=True)
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    date_created = serializers.DateTimeField(source='created_at', read_only=True)
    date_modified = serializers.DateTimeField(source='modified_at', read_only=True)

    class Meta:
        model = StatementServiceRecord
        fields = (
            'id', 'status_document', 'sailor', 'is_payed', 'date_created', 'date_modified',
            'delivery', 'photo')

    def update(self, instance, validated_data):
        # raise_errors_on_nested_writes('update', self, validated_data)
        status = validated_data.get('status', False)
        if instance.is_payed is False and status and status.id == magic_numbers.status_statement_serv_rec_created:
            del validated_data['status']
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        save_history.s(user_id=user_id, module='StatementServiceRecord', action_type='edit',
                       content_obj=instance, serializer=StatementServiceRecordSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance


class StatementAdvancedTrainingSerializer(serializers.ModelSerializer):
    date_end_meeting = serializers.ReadOnlyField()
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)
    date_create = serializers.DateTimeField(source='created_at', read_only=True)
    date_modified = serializers.DateTimeField(source='modified_at', read_only=True)

    class Meta:
        model = StatementAdvancedTraining
        fields = ('id', 'number', 'is_payed', 'date_create', 'date_modified', 'photo', 'status_document',
                  'level_qualification', 'educational_institution', 'date_meeting', 'date_end_meeting')
        read_only_fields = ('number', 'date_meeting', 'date_end_meeting')
        extra_kwargs = {'status_document': {'required': False}}

    def get_fields(self):
        fields = super(StatementAdvancedTrainingSerializer, self).get_fields()
        fields['level_qualification'].queryset = LevelQualification.objects.filter(type_NZ_id=2)
        return fields

    def to_representation(self, instance):
        response = super(StatementAdvancedTrainingSerializer, self).to_representation(instance)
        response['level_qualification'] = LevelQualitifcationSerializer(instance.level_qualification).data
        response['educational_institution'] = NZSerializer(instance.educational_institution).data
        response['status_document'] = StatusDocumentSerializer(instance.status_document).data
        return response

    def validate_status_document(self, obj):
        if (obj.id == magic_numbers.status_statement_adv_training_valid) and \
                (self.initial_data.get('is_payed', False) is False and self.instance.is_payed is False):
            raise ValidationError('Statement is not paid')
        return super(StatementAdvancedTrainingSerializer, self).validate(attrs=obj)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        user_id = self.context['request'].user.id
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        save_history.s(user_id=user_id, module='StatementAdvancedTraining', action_type='edit',
                       content_obj=instance, serializer=StatementAdvancedTrainingSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance


class ShortAdvancedTrainingSerializer(serializers.Serializer):
    """
    Serializer for translating a statement advanced training into a advanced training document
    """
    number_document = serializers.CharField(max_length=30)
    serial = serializers.CharField(max_length=50)
    registry_number = serializers.CharField(max_length=50)
    special_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class StatementMedicalCertificateSerializer(serializers.ModelSerializer):
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)
    date_create = serializers.DateTimeField(source='created_at', read_only=True)
    date_modified = serializers.DateTimeField(source='modified_at', read_only=True)

    class Meta:
        model = StatementMedicalCertificate
        fields = ('id', 'number', 'is_payed', 'date_create', 'date_modified', 'photo', 'position', 'status_document',
                  'medical_institution', 'date_meeting')
        read_only_fields = ('number', 'date_meeting')
        extra_kwargs = {'status_document': {'required': False}}

    def to_representation(self, instance):
        response = super(StatementMedicalCertificateSerializer, self).to_representation(instance)
        response['position'] = PositionForMedicalSerializer(instance.position).data
        response['medical_institution'] = MedicalInstitutionSerializer(instance.medical_institution).data
        response['status_document'] = StatusDocumentSerializer(instance.status_document).data
        return response

    def validate_status_document(self, obj):
        if (obj.id == magic_numbers.status_statement_medical_cert_valid) and \
                (self.initial_data.get('is_payed', False) is False and self.instance.is_payed is False):
            raise ValidationError('Statement is not paid')
        return super(StatementMedicalCertificateSerializer, self).validate(attrs=obj)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        user_id = self.context['request'].user.id
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        save_history.s(user_id=user_id, module='StatementMedicalCertificate', action_type='edit',
                       content_obj=instance, serializer=StatementMedicalCertificateSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance


class StatementDKKSerializer(serializers.ModelSerializer):
    sailor = serializers.IntegerField(write_only=True)
    status_dkk = serializers.ReadOnlyField(source='get_status_position', read_only=True)
    number = serializers.ReadOnlyField(source='get_number', read_only=True)
    status_document = customSerializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all(),
                                                                required=False, allow_null=True, allow_empty=True)
    rank = customSerializer.RankSerializer(queryset=Rank.objects.all(), required=False)
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)
    list_positions = customSerializer.PositionSerializer(queryset=Position.objects.all(), required=False,
                                                         allow_null=True)
    date_create = serializers.DateTimeField(read_only=True, source='created_at')
    created_by = PrivateField(source='_author')
    approved_by = PrivateVerificationField(source='_verificator')
    has_related_docs = serializers.SerializerMethodField()
    disabled_dated = serializers.ReadOnlyField()
    is_agent_create = serializers.SerializerMethodField()

    class Meta:
        model = StatementSQC
        fields = ('id', 'sailor', 'is_payed', 'photo', 'status_dkk',
                  'number', 'status_document', 'rank', 'list_positions', 'date_create', 'created_by',
                  'approved_by', 'is_cadet', 'is_continue', 'has_related_docs', 'date_meeting',
                  'disabled_dated', 'is_etransport_pay', 'is_agent_create')
        read_only_fields = ('is_etransport_pay',)

    def get_is_agent_create(self, obj):
        return obj.items.exists()

    def get_has_related_docs(self, instance):
        return instance.related_docs.exists()

    def validate(self, attrs):
        status_document = attrs.get('status_document')
        if status_document and self.instance:
            status_position = self.instance.get_status_position
            # TODO выключил проверку опыта. Нужно будет включить
            if (status_position['have_all_docs'] is not True and
                    self.instance.is_cadet is False and
                    not status_document.pk == magic_numbers.status_state_qual_dkk_rejected):
                del attrs['status_document']
            if status_position['have_all_docs'] and self.instance.status_document_id == 74 and status_document.pk != 74:
                status_document = StatusDocument.objects.get(id=magic_numbers.status_state_qual_dkk_in_process)
                attrs['status_document'] = status_document
        return super(StatementDKKSerializer, self).validate(attrs=attrs)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        status_document = validated_data.get('status_document')
        if status_document and status_document.pk != magic_numbers.status_state_qual_dkk_rejected \
                and ((not validated_data.get('is_payed', False) and
                      status_document.pk == magic_numbers.status_state_qual_dkk_approv) or (
                             user.has_perm('statement.writeApplicationSQCStatus') is False and
                             not user.has_perm('statement.writeApplicationSQCPreVerificationStatus'))
        ):
            del validated_data['status_document']
        if status_document and status_document.pk != magic_numbers.status_state_qual_dkk_rejected and \
                user.has_perm('statement.writeApplicationSQCStatusRejected') and \
                not user.has_perm('statement.writeApplicationSQCStatus'):
            del validated_data['status_document']
        date_meeting = validated_data.get('date_meeting')
        if date_meeting and instance.items.exists():
            packet = instance.items.first().packet_item
            update_date_meeting_statement_dpd(date_meeting, packet, instance.sailor, user.id)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user_id = user.id
        save_history.s(user_id=user_id, module='StatementDKK', action_type='edit',
                       content_obj=instance, serializer=StatementDKKSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance


class StatementDKKWithoutDocSer(serializers.ModelSerializer):
    """
    Для сохранения истории. Без проверки документов
    """
    sailor = serializers.IntegerField(write_only=True)
    number = serializers.ReadOnlyField(source='get_number', read_only=True)
    status_document = customSerializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all(),
                                                                required=False, allow_null=True, allow_empty=True)
    rank = customSerializer.RankSerializer(queryset=Rank.objects.all(), required=False)
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)
    list_positions = customSerializer.PositionSerializer(queryset=Position.objects.all(), required=False,
                                                         allow_null=True)
    date_create = serializers.DateTimeField(read_only=True, source='created_at')
    created_by = PrivateField(source='_author')
    approved_by = PrivateVerificationField(source='_verificator')

    class Meta:
        model = StatementSQC
        fields = ('id', 'sailor', 'is_payed', 'photo',
                  'number', 'status_document', 'rank', 'list_positions', 'rank', 'date_create', 'created_by',
                  'approved_by')

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        save_history.s(user_id=user_id, module='StatementDKK', action_type='edit',
                       content_obj=instance, serializer=StatementDKKSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance


class StatementQualificationDocumentSerializer(serializers.ModelSerializer):
    sailor = serializers.IntegerField(write_only=True)
    status_dkk = serializers.ReadOnlyField(source='get_status_position', read_only=True)
    number = serializers.ReadOnlyField(source='get_number', read_only=True)
    status_document = serializers.PrimaryKeyRelatedField(queryset=StatusDocument.objects.all(),
                                                         required=False, allow_null=True, allow_empty=True)
    port = customSerializer.PortSerailizer(queryset=Port.objects.all())
    type_document = customSerializer.TypeDocumentSerializer(queryset=TypeDocument.objects.all(), required=False,
                                                            allow_null=True)
    protocol_dkk = customSerializer.ProtocolDKKSerializer(queryset=ProtocolSQC.objects.all(), required=False,
                                                          allow_null=True)
    rank = customSerializer.RankSerializer(queryset=Rank.objects.all(), required=False, allow_null=True)
    list_positions = customSerializer.PositionSerializer(queryset=Position.objects.all(), required=False,
                                                         allow_null=True)
    created_by = PrivateField(source='_author')
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)

    class Meta:
        model = StatementQualification
        fields = ('id', 'sailor', 'photo', 'status_dkk', 'number', 'status_document', 'protocol_dkk',
                  'port', 'type_document', 'rank', 'list_positions', 'created_by', 'is_payed', 'is_continue',
                  'date_meeting')
        read_only_fields = ('date_meeting',)

    def validate(self, attrs):
        status_document = attrs.get('status_document')
        if status_document and self.instance:
            status_position = self.instance.get_status_position
            if status_document.pk == magic_numbers.status_state_qual_dkk_approv and \
                    not status_position['have_all_docs']:
                del attrs['status_document']

        if self.context['request']._request.method == 'POST':
            protocol_dkk = attrs.get('protocol_dkk')
            if protocol_dkk and StatementQualification.objects. \
                    filter(protocol_dkk_id=protocol_dkk).exists():
                raise ValidationError('Qualification document with this statement exists')
        return super(StatementQualificationDocumentSerializer, self).validate(attrs=attrs)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        if ((validated_data.get('is_payed', False) is False and instance.is_payed is False) and
                validated_data.get('status_document') and
                validated_data['status_document'].id == magic_numbers.status_state_qual_dkk_approv):
            del validated_data['status_document']
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        save_history.s(user_id=user_id, module='StatementQualification', action_type='edit',
                       content_obj=instance, serializer=StatementQualificationDocumentSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['status_document'] = StatusDocumentSerializer(instance=instance.status_document).data
        return response


class StatementETISerializer(serializers.ModelSerializer):
    sailor = serializers.IntegerField(write_only=True)
    requisites = serializers.ReadOnlyField()
    date_create = serializers.DateTimeField(source='created_at', read_only=True)
    date_modified = serializers.DateTimeField(source='modified_at', read_only=True)

    class Meta:
        model = StatementETI
        fields = ('id', 'number', 'date_create', 'date_modified', 'date_meeting', 'course', 'status_document',
                  'institution', 'sailor', 'is_payed', 'date_end_meeting', 'requisites')
        read_only_fields = ('number', 'date_meeting', 'date_end_meeting')
        extra_kwargs = {'status_document': {'required': False}}

    def to_representation(self, instance):
        response = super(StatementETISerializer, self).to_representation(instance)
        response['institution'] = SmallETISerializer(instance.institution).data
        response['course'] = CourseForNTZSerializer(instance.course).data
        response['status_document'] = StatusDocumentSerializer(instance.status_document).data
        return response

    def create(self, validated_data):
        del validated_data['sailor']
        return StatementETI.objects.create(**validated_data)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        save_history.s(user_id=user_id, module='StatementETI', action_type='edit',
                       content_obj=instance, serializer=StatementETISerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        change_to_valid = (old_instance.status_document_id != magic_numbers.status_statement_eti_valid and
                           instance.status_document_id == magic_numbers.status_statement_eti_valid)
        change_to_pay = (old_instance.is_payed != instance.is_payed and instance.is_payed)
        if change_to_valid:
            certificates.tasks.send_statement_to_eti.s(statement_id=instance.pk).apply_async(countdown=10)
        if change_to_pay:
            certificates.tasks.add_month_sum.s(instance.pk).apply_async()
        return instance


class StatementSailorPassportSerializer(serializers.ModelSerializer):
    sailor = serializers.IntegerField(write_only=True, required=False)
    number_document = serializers.CharField(write_only=True, required=False)
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)
    date_meeting = serializers.DateField(format='%d.%m.%Y', read_only=True)
    fast_obtaining = serializers.BooleanField(read_only=True)
    type_receipt = serializers.IntegerField()
    date_create = serializers.DateTimeField(source='created_at', read_only=True)
    date_modified = serializers.DateTimeField(source='modified_at', read_only=True)

    class Meta:
        model = StatementSailorPassport
        fields = ('id', 'number', 'date_create', 'date_modified', 'port', 'status_document', 'sailor',
                  'is_payed', 'is_continue', 'sailor_passport', 'photo', 'number_document', 'date_meeting',
                  'fast_obtaining', 'is_payed_blank', 'type_receipt')
        read_only_fields = ('number', 'is_continue', 'sailor_passport')
        extra_kwargs = {'status_document': {'required': False}}

    def to_representation(self, instance):
        response = super(StatementSailorPassportSerializer, self).to_representation(instance)
        response['port'] = PortSerializer(instance.port).data
        response['status_document'] = StatusDocumentSerializer(instance.status_document).data
        response['captain'] = PortCaptainSerializer(instance.port.fiocapitanofport_set.first()).data
        return response

    def create(self, validated_data):
        del validated_data['sailor']
        return StatementSailorPassport.objects.create(**validated_data)

    def validate_status_document(self, obj):
        if (obj.id == magic_numbers.status_statement_sailor_passport_valid) and \
                (self.initial_data.get('is_payed', False) is False and self.instance.is_payed is False):
            raise ValidationError('statement is not paid')
        return super(StatementSailorPassportSerializer, self).validate(attrs=obj)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        user_id = self.context['request'].user.id
        # if validated_data.get('status_document') and \
        #         validated_data['status_document'].id == magic_numbers.status_statement_sailor_passport_valid:
        #     if instance.is_continue:
        #         self._update_sailor_passport(instance)
        #     else:
        #         self._create_sailor_passport(instance, validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        save_history.s(user_id=user_id, module='StatementSailorPassport', action_type='edit',
                       content_obj=instance, serializer=StatementSailorPassportSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance

    def _update_sailor_passport(self, instance):
        sailor_passport = SailorPassport.objects.get(id=instance.sailor_passport.id)
        if sailor_passport.date_renewal:
            raise ValidationError('Sailor passport cannot be renewed')
        old_sailor_passport = deepcopy(sailor_passport)
        date_renewal = sailor_passport.date_end + relativedelta(years=5)
        sailor_passport.date_renewal = date_renewal
        sailor_passport.save(update_fields=['date_renewal'])
        update_sailor_passport_in_packet.s(sailor_passport_id=sailor_passport.pk,
                                           sailor_id=None,
                                           search_sailor=True).apply_async()
        user_id = self.context['request'].user.id
        save_history.s(user_id=user_id, module='SailorPassport', action_type='edit', content_obj=sailor_passport,
                       serializer=SailorPassportSerializer, new_obj=sailor_passport, old_obj=old_sailor_passport,
                       get_sailor=True).apply_async(serializer='pickle')

    def _create_sailor_passport(self, instance: StatementSailorPassport, validated_data):
        if instance.sailor_passport:
            raise ValidationError('Sailor passport was be created')
        sailor_qs = SailorKeys.by_document.id(instance=instance)
        if not sailor_qs:
            raise ValidationError('Sailor does not exists')
        number_document = validated_data.get('number_document')
        if not number_document:
            raise ValidationError('Number document not specified')
        date_start = date.today()
        date_end = date_start + relativedelta(years=5)
        sailor_passport = SailorPassport.objects.create(
            country_id=2, date_start=date_start, date_end=date_end, port_id=instance.port.id,
            status_document_id=magic_numbers.status_qual_doc_valid, photo=instance.photo,
            captain=instance.port.fiocapitanofport_set.first().name_ukr, number_document=number_document)
        sailor_qs.sailor_passport.append(sailor_passport.id)
        instance.sailor_passport_id = sailor_passport.id
        sailor_qs.save(update_fields=['sailor_passport'])
        disable_old_sailor_passport.s(sailor_id=sailor_qs.pk, exclude_id=sailor_passport.pk).apply_async()
        update_sailor_passport_in_packet.s(sailor_passport_id=sailor_passport.pk,
                                           sailor_id=sailor_qs.pk).apply_async()
        user_id = self.context['request'].user.id
        save_history.s(user_id=user_id, module='SailorPassport', action_type='create', content_obj=sailor_passport,
                       serializer=SailorPassportSerializer, new_obj=sailor_passport, get_sailor=True
                       ).apply_async(serializer='pickle')


class ShortStatementQualificationDocumentSerializer(StatementQualificationDocumentSerializer):
    sailor = serializers.IntegerField(read_only=True)

    class Meta:
        model = StatementQualification
        fields = ('id', 'sailor', 'number', 'status_document', 'protocol_dkk', 'port', 'type_document', 'rank',
                  'list_positions', 'is_payed', 'date_meeting')


class RelatedDocsStatementSQC(serializers.Serializer):
    old_document = serializers.IntegerField(required=False)
    new_document = serializers.IntegerField()
    content_type = serializers.SlugRelatedField(slug_field='model', queryset=ContentType.objects.all())
