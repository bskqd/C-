from copy import deepcopy
from datetime import date

from dateutil.relativedelta import relativedelta
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import raise_errors_on_nested_writes

import back_office.tasks
import directory.serializers
import sailor.misc
import sailor.tasks
from back_office.models import DependencyItem
from directory.models import (BranchOffice, Country, Course, Decision, DoctrorInMedicalInstitution,
                              FunctionAndLevelForPosition, LimitationForMedical, Port, Position, PositionForMedical,
                              Rank, Responsibility,
                              ResponsibilityWorkBook, StatusDocument, TypeDocument,
                              Commisioner, VerificationStage)
from itcs import magic_numbers
from sailor import forModelSerializer as customSerializer, forModelSerializer as customSerializers
from sailor.AbstractSerializer import PrivateField, PrivateVerificationField, ToReprMixin
from sailor.document.models import (CertificateETI, Education, LineInServiceRecord, MedicalCertificate, ProtocolSQC,
                                    QualificationDocument, ResponsibilityServiceRecord, ServiceRecord,
                                    ProofOfWorkDiploma)
from sailor.misc import update_is_active_verification_status, create_verification_status_for_document, \
    verification_stages
from sailor.models import PhotoProfile
from sailor.serializers import ResponsibilityServiceRecordSerializer
from sailor.tasks import create_duplicate_proof_diploma, check_document_to_additional_verification, save_history
from signature.models import CommissionerSignProtocol
from signature.serializers import CommissionerSerializer
from user_profile.models import UserProfile


class LineInServiceRecordSerializer(ToReprMixin, serializers.ModelSerializer):
    responsibility = customSerializer.ResponsibilitySerializer(queryset=Responsibility.objects.all(),
                                                               allow_null=True, allow_empty=True, required=False)
    # id 5 - статус "в обработаке"
    date_write = serializers.DateField(read_only=True)
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    full_name_master = serializers.CharField(required=False, allow_null=True, default='', allow_blank=True)
    number_page_book = serializers.CharField(allow_null=True, required=False)
    created_by = PrivateField(source='_author')
    verificated_by = PrivateVerificationField(source='_verificator')
    ship_owner = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    all_responsibility = ResponsibilityServiceRecordSerializer(many=True, source='service_record_line', required=False)
    verification_status = serializers.PrimaryKeyRelatedField(queryset=VerificationStage.objects.all(),
                                                             required=False, write_only=True)

    class Meta:
        model = LineInServiceRecord
        fields = ('id', 'service_record', 'name_vessel', 'type_vessel', 'mode_of_navigation', 'type_geu', 'ship_owner',
                  'number_vessel', 'propulsion_power', 'electrical_power', 'all_responsibility', 'refrigerating_power',
                  'book_registration_practical', 'position', 'date_start', 'place_start', 'place_end', 'date_end',
                  'full_name_master', 'date_write', 'equipment_gmzlb', 'trading_area', 'ports_input', 'status_line',
                  'gross_capacity', 'levelRefrigerPlant', 'full_name_master_eng', 'photo', 'number_page_book',
                  'created_by', 'verificated_by', 'port_of_registration', 'is_repaired', 'repair_date_from',
                  'repair_date_to', 'days_repair', 'responsibility', 'verification_status')

    def update(self, instance, validated_data):
        verification_status = validated_data.pop('verification_status', None)
        if verification_status:
            sailor.misc.update_is_active_verification_status(instance, verification_status.pk)
        old_object = LineInServiceRecordSerializer(instance=instance).data
        all_function = validated_data.pop('service_record_line', None)
        all_function = sailor.misc.check_all_function(all_function)
        date_start = validated_data.get('date_start', instance.date_start)
        date_end = validated_data.get('date_end', instance.date_end)
        if all_function:
            days_repair = validated_data.get('days_repair', 0)
            repair_date_from = validated_data.get('repair_date_from')
            repair_date_to = validated_data.get('repair_date_to')
            all_function += sailor.misc.check_interval_date(all_function=all_function, date_start=date_start,
                                                            date_end=date_end,
                                                            days_repair=days_repair, repair_date_from=repair_date_from,
                                                            repair_date_to=repair_date_to)
            all_function = sailor.misc.get_is_repair(repair_date_from, repair_date_to, all_function)
            ResponsibilityServiceRecord.objects.filter(service_record_line_id=instance.id).delete()
            list_responsibility = [ResponsibilityServiceRecord(
                service_record_line_id=instance.id, responsibility=function.get('responsibility'),
                date_from=function.get('date_from'), date_to=function.get('date_to'),
                days_work=function.get('days_work'), is_repaired=function.get('is_repaired', False))
                for function in all_function]
            ResponsibilityServiceRecord.objects.bulk_create(list_responsibility)
        elif 'status_line' not in validated_data:
            ResponsibilityServiceRecord.objects.filter(service_record_line_id=instance.id).delete()
        # фронту желательно слать все поля по ремонту, если там произошли изменения, чтоб не выполнять эти проверки
        if validated_data.get('is_repaired') is False and (instance.repair_date_from or instance.days_repair):
            validated_data.update({'repair_date_from': None, 'repair_date_to': None, 'days_repair': None})
        if validated_data.get('repair_date_from') and instance.days_repair:
            validated_data.update({'days_repair': None})
        if validated_data.get('days_repair') and instance.repair_date_from:
            validated_data.update({'repair_date_from': None, 'repair_date_to': None})
        repair_date_from = validated_data.get('repair_date_from')
        repair_date_to = validated_data.get('repair_date_to')
        repair_days = validated_data.get('days_repair')
        sailor.misc.check_repair_enter_to_cruise(date_start_cruise=date_start, date_end_cruise=date_end,
                                                 repairs_days=repair_days,
                                                 repair_date_from=repair_date_from, repair_date_to=repair_date_to)

        raise_errors_on_nested_writes('update', self, validated_data)
        new_status_line = validated_data.get('status_line', None)
        if new_status_line and instance.status_line_id in (magic_numbers.VERIFICATION_STATUS,
                                                           magic_numbers.STATUS_CREATED_BY_AGENT):
            if settings.ENABLE_ADDITIONAL_VERIFICATION is True and validated_data.get(
                    'status_line').pk in magic_numbers.ALL_VALID_STATUSES:
                validated_data['status_line_id'] = magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION
                sailor.tasks.check_document_to_additional_verification.s(self.instance._meta.model_name,
                                                                         instance.pk).apply_async()
        if settings.ENABLE_REJECT_EXP_VERIFICATION is True:
            if new_status_line and new_status_line.pk == 10:
                sailor.tasks.on_reject_line_in_service.delay(instance.pk)
            if new_status_line and new_status_line.pk != 10 and instance.status_line_id == 10:
                sailor.tasks.on_approving_reject_line_in_service.delay(instance.pk)
        status_line = validated_data.get('status_line')
        if instance.status_line.pk != magic_numbers.VERIFICATION_STATUS and status_line and \
                status_line.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        user = self.context['request'].user
        user_id = user.id
        new_instance = LineInServiceRecordSerializer(instance=instance).data
        sailor.tasks.save_history.s(user_id=user_id,
                                    module='LineInServiceRecord',
                                    action_type='edit',
                                    content_obj=instance,
                                    new_obj=new_instance,
                                    old_obj=old_object,
                                    get_sailor=True).apply_async(serializer='pickle')
        return instance

    def to_representation(self, instance: LineInServiceRecord):
        response = super().to_representation(instance)
        response['type_vessel'] = directory.serializers.TypeVesselSailorSerializer(instance=instance.type_vessel).data
        response['mode_of_navigation'] = directory.serializers.ModeOfNavigationSerializer(
            instance=instance.mode_of_navigation).data
        response['type_geu'] = directory.serializers.TypeGeuSerializer(instance=instance.type_geu).data
        response['position'] = directory.serializers.PositionForExperienceSerializer(instance=instance.position).data
        response['status_line'] = directory.serializers.StatusDocumentSerializer(instance=instance.status_line).data
        if instance.status_line.pk == magic_numbers.VERIFICATION_STATUS:
            response['verification_status'] = sailor.misc.verification_stages(instance, context=self.context)
        return response


class ServiceRecordSailorSerializer(serializers.ModelSerializer):
    sailor = serializers.IntegerField(write_only=True)
    new_record = serializers.BooleanField(write_only=True)
    name_book = serializers.ReadOnlyField(source='get_name_book')
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    blank_strict_report = serializers.IntegerField(required=False, allow_null=True)
    created_by = PrivateField(source='_author')
    verificated_by = PrivateVerificationField(source='_verificator')
    status = serializers.PrimaryKeyRelatedField(queryset=StatusDocument.objects.all(), required=False,
                                                source='status_document')
    verification_status = serializers.PrimaryKeyRelatedField(queryset=VerificationStage.objects.all(),
                                                             required=False, write_only=True)

    class Meta:
        model = ServiceRecord
        fields = ('id', 'sailor', 'number', 'issued_by', 'photo', 'auth_agent_ukr',
                  'auth_agent_eng', 'branch_office', 'date_issued', 'status',
                  'new_record', 'name_book', 'photo', 'blank_strict_report', 'created_by', 'verificated_by',
                  'waibill_number', 'verification_status')
        extra_kwargs = {'status': {'required': False},
                        'number': {'required': False, 'allow_null': True}}

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        new_record = validated_data['new_record']
        if new_record:
            validated_data['branch_office'] = self.context.get('request').user.userprofile.branch_office
        validated_data['status_document_id'] = 14 if new_record else user.userprofile.verification_status_by_user
        if not validated_data.get('date_issued'):
            validated_data['date_issued'] = date.today()
        validated_data['issued_by'] = f'{user.last_name} {user.first_name} ' \
                                      f'{user.userprofile.middle_name}, ' \
                                      f'{user.userprofile.branch_office.name_ukr}'
        del validated_data['sailor']
        del validated_data['new_record']
        qs = ServiceRecord.objects.create(**validated_data)
        return qs

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        verification_status = validated_data.pop('verification_status', None)
        if verification_status:
            sailor.misc.update_is_active_verification_status(instance, verification_status.pk)
        old_instance = deepcopy(instance)
        if 'status_document' in validated_data and instance.status_document_id in [magic_numbers.VERIFICATION_STATUS,
                                                                                   magic_numbers.STATUS_CREATED_BY_AGENT]:
            if settings.ENABLE_ADDITIONAL_VERIFICATION is True and validated_data.get(
                    'status_document').pk in magic_numbers.ALL_VALID_STATUSES:
                validated_data['status_document_id'] = magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION
                sailor.tasks.check_document_to_additional_verification.s(self.instance._meta.model_name,
                                                                         instance.pk).apply_async()
        status_document = validated_data.get('status_document')
        if instance.status_document.pk != magic_numbers.VERIFICATION_STATUS and status_document and \
                status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        user = self.context['request'].user
        user_id = user.id
        new_instance = deepcopy(instance)
        sailor.tasks.save_history.s(user_id=user_id, module='ServiceRecord', action_type='edit',
                                    content_obj=instance, serializer=ServiceRecordSailorSerializer,
                                    new_obj=new_instance,
                                    old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance

    def to_representation(self, instance: ServiceRecord):
        response = super().to_representation(instance=instance)
        response['branch_office'] = directory.serializers.BranchOfficeSerializer(instance=instance.branch_office).data
        response['status'] = directory.serializers.StatusDocumentSerializer(instance=instance.status_document).data
        if instance.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            response['verification_status'] = sailor.misc.verification_stages(instance, context=self.context)
        return response


class ExperienceDocumentSerializer(LineInServiceRecordSerializer):
    sailor = serializers.IntegerField(write_only=True)
    responsibility_work_book = customSerializer.ResponsibilityWorkBookSerializer(
        queryset=ResponsibilityWorkBook.objects.all(), allow_null=True, allow_empty=True, required=False)

    class Meta:
        model = LineInServiceRecord
        fields = ('id', 'sailor', 'name_vessel', 'type_vessel', 'mode_of_navigation', 'type_geu', 'ship_owner',
                  'number_vessel', 'propulsion_power', 'electrical_power', 'all_responsibility', 'refrigerating_power',
                  'book_registration_practical', 'position', 'date_start', 'place_start', 'place_end', 'date_end',
                  'full_name_master', 'date_write', 'equipment_gmzlb', 'trading_area', 'ports_input', 'status_line',
                  'gross_capacity', 'levelRefrigerPlant', 'full_name_master_eng', 'photo', 'created_by',
                  'verificated_by', 'port_of_registration', 'record_type', 'responsibility_work_book', 'place_work',
                  'days_work', 'is_repaired', 'repair_date_from', 'repair_date_to', 'days_repair', 'responsibility',
                  'verification_status')

    def create(self, validated_data):
        if type(validated_data['status_line']) is int:
            validated_data['status_line_id'] = validated_data.pop('status_line')
        if 'sailor' in validated_data:
            del validated_data['sailor']
        return LineInServiceRecord.objects.create(**validated_data)

    def check_update_repair(self, instance, validated_data):
        if validated_data.get('is_repaired') is False and (instance.repair_date_from or instance.days_repair):
            validated_data.update({'repair_date_from': None, 'repair_date_to': None, 'days_repair': None})
        if validated_data.get('repair_date_from') and instance.days_repair:
            validated_data.update({'days_repair': None})
        if validated_data.get('days_repair') and instance.repair_date_from:
            validated_data.update({'repair_date_from': None, 'repair_date_to': None})
        return validated_data

    def update(self, instance, validated_data):
        verification_status = validated_data.pop('verification_status', None)
        if verification_status:
            sailor.misc.update_is_active_verification_status(instance, verification_status.pk)
        old_object = ExperienceDocumentSerializer(instance).data
        all_function = validated_data.pop('service_record_line', None)
        all_function = sailor.misc.check_all_function(all_function)
        date_start = validated_data.get('date_start', instance.date_start)
        date_end = validated_data.get('date_end', instance.date_end)
        if all_function:
            days_repair = validated_data.get('days_repair', 0)
            repair_date_from = validated_data.get('repair_date_from')
            repair_date_to = validated_data.get('repair_date_to')
            all_function += sailor.misc.check_interval_date(all_function=all_function, date_start=date_start,
                                                            date_end=date_end,
                                                            days_repair=days_repair, repair_date_from=repair_date_from,
                                                            repair_date_to=repair_date_to)
            all_function = sailor.misc.get_is_repair(repair_date_from, repair_date_to, all_function)
            ResponsibilityServiceRecord.objects.filter(service_record_line_id=instance.id).delete()
            list_responsibility = [ResponsibilityServiceRecord(
                service_record_line_id=instance.id, responsibility=function.get('responsibility'),
                date_from=function.get('date_from'), date_to=function.get('date_to'),
                days_work=function.get('days_work'), is_repaired=function.get('is_repaired', False))
                for function in all_function]
            ResponsibilityServiceRecord.objects.bulk_create(list_responsibility)
        elif 'status_line' not in validated_data:
            ResponsibilityServiceRecord.objects.filter(service_record_line_id=instance.id).delete()
        # фронту желательно слать все поля по ремонту, если там произошли изменения, чтоб не выполнять эти проверки
        validated_data = self.check_update_repair(instance, validated_data)
        repair_date_from = validated_data.get('repair_date_from')
        repair_date_to = validated_data.get('repair_date_to')
        repair_days = validated_data.get('days_repair')
        sailor.misc.check_repair_enter_to_cruise(date_start_cruise=date_start, date_end_cruise=date_end,
                                                 repairs_days=repair_days,
                                                 repair_date_from=repair_date_from, repair_date_to=repair_date_to)

        raise_errors_on_nested_writes('update', self, validated_data)
        new_status_line = validated_data.get('status_line', None)
        if 'status_line' in validated_data and instance.status_line_id in (magic_numbers.VERIFICATION_STATUS,
                                                                           magic_numbers.STATUS_CREATED_BY_AGENT):
            if settings.ENABLE_ADDITIONAL_VERIFICATION is True and validated_data.get(
                    'status_line').pk in magic_numbers.ALL_VALID_STATUSES:
                validated_data['status_line_id'] = magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION
                sailor.tasks.check_document_to_additional_verification.s(self.instance._meta.model_name,
                                                                         instance.pk).apply_async()
        if settings.ENABLE_REJECT_EXP_VERIFICATION is True:
            if new_status_line and validated_data.get('status_line').pk == 10:
                sailor.tasks.on_reject_line_in_service.delay(instance.pk)
            if new_status_line and new_status_line.pk != 10 and instance.status_line_id == 10:
                sailor.tasks.on_approving_reject_line_in_service.delay(instance.pk)
        status_line = validated_data.get('status_line')
        if instance.status_line.pk != magic_numbers.VERIFICATION_STATUS and status_line and \
                status_line.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        user = self.context['request'].user
        user_id = user.id
        new_instance = ExperienceDocumentSerializer(instance=instance).data
        sailor.tasks.save_history.s(user_id=user_id, module='ExperienceDoc', action_type='edit',
                                    content_obj=instance, new_obj=new_instance,
                                    old_obj=old_object, get_sailor=True).apply_async(serializer='pickle')
        return instance


class EducationSerializer(ToReprMixin, serializers.ModelSerializer):
    sailor = serializers.IntegerField(write_only=True)
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    created_by = PrivateField(source='_author')
    verificated_by = PrivateVerificationField(source='_verificator')
    experied_date = serializers.DateField(source='expired_date', allow_null=True, required=False)
    verification_status = serializers.PrimaryKeyRelatedField(queryset=VerificationStage.objects.all(),
                                                             required=False, write_only=True)

    class Meta:
        model = Education
        fields = (
            'id', 'sailor', 'type_document', 'number_document', 'extent', 'name_nz', 'qualification', 'speciality',
            'date_end_educ', 'experied_date', 'date_issue_document', 'special_notes', 'photo', 'status_document',
            'specialization', 'serial', 'registry_number', 'created_by', 'verificated_by', 'is_duplicate',
            'verification_status')
        extra_kwargs = {'extent': {'required': False, 'allow_null': True},
                        'name_nz': {'required': False, 'allow_null': True},
                        'qualification': {'required': False, 'allow_null': True},
                        'speciality': {'required': False, 'allow_null': True},
                        'specialization': {'required': False, 'allow_null': True},
                        'status_document': {'required': False, 'allow_null': True},
                        }

    def create(self, validated_data):
        del validated_data['sailor']
        return Education.objects.create(**validated_data)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        verification_status = validated_data.pop('verification_status', None)
        if verification_status:
            sailor.misc.update_is_active_verification_status(instance, verification_status.pk)
        old_instance = deepcopy(instance)
        if 'status_document' in validated_data and instance.status_document_id in \
                [magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT]:
            if settings.ENABLE_ADDITIONAL_VERIFICATION is True and validated_data.get(
                    'status_document').pk in magic_numbers.ALL_VALID_STATUSES:
                validated_data['status_document_id'] = magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION
                sailor.tasks.check_document_to_additional_verification.s(self.instance._meta.model_name,
                                                                         instance.pk).apply_async()
            elif validated_data.get('status_document').pk in magic_numbers.ALL_VALID_STATUSES:
                back_office.tasks.update_education_in_packet.delay(instance.pk, None, True)
        if instance.type_document_id == 3:
            validated_data['expired_date'] = validated_data.get('date_issue_document', instance.date_issue_document) \
                                             + relativedelta(years=5)
        status_document = validated_data.get('status_document')
        if instance.status_document.pk != magic_numbers.VERIFICATION_STATUS and status_document and \
                status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        sailor.tasks.save_history.s(user_id=user_id, module='Education', action_type='edit',
                                    content_obj=instance, serializer=EducationSerializer, new_obj=new_instance,
                                    old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance

    def to_representation(self, instance: Education):
        response = super(EducationSerializer, self).to_representation(instance=instance)
        response['extent'] = directory.serializers.ExtentSerializer(instance=instance.extent).data
        response['type_document'] = directory.serializers.TypeDocumentNZSerializer(instance=instance.type_document).data
        response['name_nz'] = directory.serializers.NZNameSerializer(instance=instance.name_nz).data
        response['qualification'] = directory.serializers.LevelQualitifcationSerializer(
            instance=instance.qualification).data
        response['speciality'] = directory.serializers.SpecialitySerializer(instance=instance.speciality).data
        response['specialization'] = directory.serializers.SpecializationSerializer(
            instance=instance.specialization).data
        response['status_document'] = directory.serializers.StatusDocumentSerializer(
            instance=instance.status_document).data
        if instance.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            response['verification_status'] = sailor.misc.verification_stages(instance, context=self.context)
        return response


class CertificateNTZBaseSerializer(ToReprMixin, serializers.ModelSerializer):
    sailor = serializers.IntegerField(write_only=True)
    course_traning = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source='course_training')
    status_document = customSerializer.StatusDocumentSerializer(
        queryset=StatusDocument.objects.filter(for_service='ServiceRecord'))
    date_start = serializers.DateField(format='%Y-%m-%d')
    date_end = serializers.DateField(format='%Y-%m-%d')
    created_by = PrivateField(source='_author')
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    date_create = serializers.DateTimeField(source='created_at', read_only=True)

    def to_representation(self, instance: CertificateETI):
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        userprofile = user.userprofile if user and hasattr(user, 'userprofile') else None
        response = super(CertificateNTZBaseSerializer, self).to_representation(instance=instance)
        response['ntz'] = directory.serializers.SmallETISerializer(instance=instance.ntz).data
        response['course_traning'] = directory.serializers.CourseForNTZSerializer(
            instance=instance.course_training).data
        response['status_document'] = directory.serializers.StatusDocumentSerializer(
            instance=instance.status_document).data
        if (user and user.is_superuser) or (userprofile and userprofile.type_user == UserProfile.BACK_OFFICE):
            response['is_only_dpd'] = instance.is_only_dpd
        return response


class CertificateNTZSerializer(CertificateNTZBaseSerializer):
    class Meta:
        model = CertificateETI
        read_only_fields = ['date_create']
        fields = ('id', 'sailor', 'ntz', 'ntz_number', 'course_traning', 'date_create', 'date_start', 'date_end',
                  'status_document', 'created_by', 'photo', 'is_only_dpd', 'statement')
        extra_kwargs = {'is_only_dpd': {'write_only': True}}

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        userprofile = user.userprofile if user and hasattr(user, 'userprofile') else None
        if not ((user and user.is_superuser) or (userprofile and userprofile.type_user == UserProfile.BACK_OFFICE)):
            attrs.pop('is_only_dpd', None)
        return super().validate(attrs)

    def create(self, validated_data):
        del validated_data['sailor']
        return CertificateETI.objects.create(**validated_data)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        sailor.tasks.save_history.s(user_id=user_id, module='CertificateNTZ', action_type='edit',
                                    content_obj=instance, serializer=CertificateNTZSerializer, new_obj=new_instance,
                                    old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance


class ProtocolDKKSerializer(serializers.ModelSerializer):
    branch_create = customSerializer.BranchOfficeSerializer(queryset=BranchOffice.objects.all(), required=False)
    sailor = serializers.IntegerField(write_only=True, source='_sailor')
    status_document = customSerializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all(), required=False)
    number_document = serializers.ReadOnlyField(source='get_number')
    number = serializers.IntegerField(source='number_document', required=False, allow_null=True)
    position = serializers.ReadOnlyField(source='get_position')
    rank = serializers.ReadOnlyField(source='get_rank')
    decision = customSerializer.DecisionSerializer(queryset=Decision.objects.all())
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    created_by = PrivateField(source='_author')
    signing = serializers.SerializerMethodField()
    commissioner_sign = CommissionerSerializer(many=True)
    downloadable_with_sign = serializers.ReadOnlyField()

    class Meta:
        model = ProtocolSQC
        fields = ('id', 'statement_dkk', 'date_meeting', 'branch_create', 'sailor', 'photo',
                  'status_document', 'number_document', 'position', 'rank', 'decision',
                  'created_by', 'number', 'date_end', 'is_printeble', 'signing', 'commissioner_sign',
                  'downloadable_with_sign')
        read_only = ('branch_create', 'is_printeble', 'number', 'photo', 'branch_create')

    def get_signing(self, obj):
        try:
            signing = CommissionerSignProtocol.objects.filter(signer__user=self.context['request'].user,
                                                              protocol_dkk=obj)
            sign_status = signing.filter(is_signatured=True).exists()
            sign_access = signing.exists() is True and signing.filter(is_signatured=False).exists() is True
            return {'sign_status': sign_status, 'sign_access': sign_access}
        except (AttributeError, ValidationError, IndexError, KeyError):
            return {'sign_status': None, 'sign_access': None}

    def create(self, validated_data):
        commissioner_sign = validated_data.pop('commissioner_sign', None)
        validated_data['_sailor'] = validated_data.pop('sailor', None)
        protocol = ProtocolSQC.objects.create(**validated_data)
        secretary, _ = Commisioner.objects.get_or_create(user=self.context['request'].user,
                                                         defaults={'is_disable': True})
        commissioner_bulk = [
            CommissionerSignProtocol(
                signer=commissioner.get('signer'),
                protocol_dkk=protocol,
                commissioner_type=commissioner.get('commissioner_type', 'SC'),
            ) for commissioner in commissioner_sign]
        commissioner_bulk.append(CommissionerSignProtocol(signer=secretary,
                                                          protocol_dkk=protocol, commissioner_type='SC'))
        CommissionerSignProtocol.objects.bulk_create(commissioner_bulk)
        return protocol

    def update(self, instance, validated_data):
        user = self.context['request'].user
        userprofile = user.userprofile if hasattr(user, 'userprofile') else None
        commissioner_sign = validated_data.pop('commissioner_sign', None)
        raise_errors_on_nested_writes('update', self, validated_data)
        old_instance = deepcopy(instance)
        if commissioner_sign and userprofile and userprofile.type_user == UserProfile.BACK_OFFICE:
            self.update_commissioners(instance, commissioner_sign)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        sailor.tasks.save_history.s(user_id=user_id, module='ProtocolSQC', action_type='edit',
                                    content_obj=instance, serializer=ProtocolDKKSerializer, new_obj=new_instance,
                                    old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance

    def update_commissioners(self, instance, commissioner_sign):
        instance.commissioner_sign.all().delete()
        commissioner_bulk = [
            CommissionerSignProtocol(
                signer=commissioner.get('signer'),
                protocol_dkk=instance,
                commissioner_type=commissioner.get('commissioner_type', 'SC'),
            ) for commissioner in commissioner_sign]
        CommissionerSignProtocol.objects.bulk_create(commissioner_bulk)


class ProtocolDKKWithPositionSerializer(serializers.ModelSerializer):
    position = serializers.ReadOnlyField(source='get_position')
    number_document = serializers.ReadOnlyField(source='get_number')
    rank = serializers.ReadOnlyField(source='get_rank')
    created_by = PrivateField(source='_author')
    is_continue = serializers.BooleanField(source='statement_dkk.is_continue')

    class Meta:
        model = ProtocolSQC
        fields = ('id', 'position', 'number_document', 'rank', 'created_by', 'created_by', 'is_continue')


class MedicalCertificateSerializer(serializers.ModelSerializer):
    sailor = serializers.IntegerField(write_only=True)
    position = customSerializer.PositionForMedicalSerializer(queryset=PositionForMedical.objects.all())
    limitation = customSerializer.LimitationForMedicalSerializer(queryset=LimitationForMedical.objects.all())
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    doctor = customSerializer.DoctorSerializer(queryset=DoctrorInMedicalInstitution.objects.all(), required=False,
                                               allow_null=True)
    status_document = customSerializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all())
    created_by = PrivateField(source='_author')
    verificated_by = PrivateVerificationField(source='_verificator')
    verification_status = serializers.PrimaryKeyRelatedField(queryset=VerificationStage.objects.all(),
                                                             required=False, write_only=True)

    class Meta:
        model = MedicalCertificate
        fields = ('id', 'number', 'sailor', 'position', 'limitation', 'date_end', 'date_start', 'photo', 'doctor',
                  'status_document', 'created_by', 'verificated_by', 'verification_status')

    def create(self, validated_data):
        del validated_data['sailor']
        return MedicalCertificate.objects.create(**validated_data)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        verification_status = validated_data.pop('verification_status', None)
        if verification_status:
            sailor.misc.update_is_active_verification_status(instance, verification_status.pk)
        old_instance = deepcopy(instance)
        user = self.context['request'].user
        groups_user = user.userprofile.groups_id
        check_is_change_verification = (
                'status_document' in validated_data and
                instance.status_document_id in [
                    magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT
                ] and validated_data['status_document'] not in [
                    magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT])
        if (check_is_change_verification is True and (37 in groups_user and not user.is_superuser) and
                instance.author and 37 not in instance.author.userprofile.groups_id):
            return instance
        status_document = validated_data.get('status_document')
        if check_is_change_verification is True:
            if settings.ENABLE_ADDITIONAL_VERIFICATION is True and validated_data.get(
                    'status_document').pk in magic_numbers.ALL_VALID_STATUSES:
                validated_data['status_document_id'] = magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION
                sailor.tasks.check_document_to_additional_verification.s(self.instance._meta.model_name,
                                                                         instance.pk).apply_async()
        if status_document and status_document.pk in magic_numbers.ALL_VALID_STATUSES:
            back_office.tasks.update_medical_in_packet.delay(instance.pk, None, True)
        if instance.status_document.pk != magic_numbers.VERIFICATION_STATUS and status_document and \
                status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user_id = user.id
        sailor.tasks.save_history.s(user_id=user_id, module='MedicalCertificate', action_type='edit',
                                    content_obj=instance, serializer=MedicalCertificateSerializer, new_obj=new_instance,
                                    old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            response['verification_status'] = sailor.misc.verification_stages(instance, context=self.context)
        return response


class ShortMedicalSerializer(serializers.Serializer):
    """
    Serializer for translating a medical statement into a medical certificate
    """
    doctor = serializers.PrimaryKeyRelatedField(queryset=DoctrorInMedicalInstitution.objects.all(),
                                                allow_null=True, required=False)
    limitation = serializers.PrimaryKeyRelatedField(queryset=LimitationForMedical.objects.all())
    number = serializers.IntegerField()
    date_end = serializers.DateField()


class QualificationDocumentSerializer(serializers.ModelSerializer):
    country = customSerializer.CountrySeriallizer(queryset=Country.objects.all(), allow_null=True)
    sailor = serializers.IntegerField(write_only=True)
    rank = customSerializer.RankSerializer(queryset=Rank.objects.all(), required=False, allow_null=True)
    type_document = customSerializer.TypeDocumentSerializer(queryset=TypeDocument.objects.all())
    status_document = customSerializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all(),
                                                                allow_null=True, required=False)
    photo = customSerializer.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    new_document = serializers.BooleanField(required=False)
    number = serializers.ReadOnlyField(source='get_number')
    port = customSerializer.PortSerailizer(queryset=Port.objects.all(), allow_null=True, required=False)
    number_document = serializers.IntegerField(required=False, allow_null=True)
    function_limitation = customSerializer.FunctionAndLimitationSerializer(
        queryset=FunctionAndLevelForPosition.objects.all(), allow_null=True, required=False)
    list_positions = customSerializer.PositionSerializer(queryset=Position.objects.all(), required=False,
                                                         allow_null=True)
    date_start = serializers.DateField(required=False, allow_null=True)
    strict_blank = serializers.CharField(allow_null=True, required=False)
    created_by = PrivateField(source='_author')
    verificated_by = PrivateVerificationField(source='_verificator')
    other_number = serializers.CharField(allow_null=True, required=False)
    verification_status = serializers.PrimaryKeyRelatedField(queryset=VerificationStage.objects.all(),
                                                             required=False, write_only=True)

    class Meta:
        model = QualificationDocument
        fields = ('id', 'sailor', 'country', 'number_document', 'rank', 'date_start', 'date_end',
                  'type_document', 'photo', 'status_document', 'new_document', 'statement', 'number', 'port',
                  'other_port', 'function_limitation', 'list_positions', 'strict_blank', 'created_by', 'verificated_by',
                  'other_number', 'verification_status')

    def create(self, validated_data):
        del validated_data['sailor']
        return QualificationDocument.objects.create(**validated_data)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        verification_status = validated_data.pop('verification_status', None)
        if verification_status:
            sailor.misc.update_is_active_verification_status(instance, verification_status.pk)
        old_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        if 'status_document' in validated_data and instance.status_document_id in \
                [magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT]:
            if settings.ENABLE_ADDITIONAL_VERIFICATION is True and validated_data.get(
                    'status_document').pk in magic_numbers.ALL_VALID_STATUSES:
                validated_data['status_document_id'] = magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION
                sailor.tasks.check_document_to_additional_verification.s(self.instance._meta.model_name,
                                                                         instance.pk).apply_async()
        elif ('status_document' in validated_data and
              instance.status_document_id == magic_numbers.status_qual_doc_in_proccess and
              validated_data.get('status_document').pk in magic_numbers.ALL_VALID_STATUSES):
            back_office.tasks.update_qualification_in_packet.delay(instance.pk, None, True)
        status_document = validated_data.get('status_document')
        if instance.status_document.pk != magic_numbers.VERIFICATION_STATUS and status_document and \
                status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if old_instance.status_document_id not in [18, 20] and instance.status_document_id in [18, 20]:
            sailor.tasks.create_duplicate_qual_doc.s(instance, user_id).apply_async(serializer='pickle')
        instance: QualificationDocument
        if instance.status_document_id not in [19, 21, 7, 18] and instance.items.filter(
                item_status=DependencyItem.WAS_BOUGHT
        ).exists():
            for dependency in instance.items.filter(item_status=DependencyItem.WAS_BOUGHT):
                dependency.item = instance.statement
                dependency.item_status = DependencyItem.TO_BUY
                dependency.save()
        new_instance = deepcopy(instance)
        sailor.tasks.save_history.s(user_id=user_id, module='QualificationDocument', action_type='edit',
                                    content_obj=instance, serializer=QualificationDocumentSerializer,
                                    new_obj=new_instance,
                                    old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            response['verification_status'] = sailor.misc.verification_stages(instance, context=self.context)
        return response


class ProofOfWorkDiplomaSerializer(serializers.ModelSerializer):
    city = serializers.ReadOnlyField(source='get_city')
    status_document = customSerializers.StatusDocumentSerializer(
        queryset=StatusDocument.objects.filter(for_service='QualificationDoc'))
    list_positions = serializers.ReadOnlyField(source='get_position')
    rank = serializers.ReadOnlyField(source='get_rank')
    photo = customSerializers.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    type_document = serializers.ReadOnlyField(source='get_type_document')
    number_document = serializers.ReadOnlyField(source='get_number')
    port = customSerializers.PortSerailizer(queryset=Port.objects.all(), allow_null=True, required=False)
    function_limitation = customSerializers.FunctionAndLimitationSerializer(
        queryset=FunctionAndLevelForPosition.objects.all(), allow_null=True, required=False)
    strict_blank = serializers.CharField(allow_null=True, required=False)
    date_start = serializers.DateField(allow_null=True, required=False)
    created_by = PrivateField(source='_author')
    verificated_by = PrivateVerificationField(source='_verificator')
    date_end = serializers.DateField(allow_null=True, required=False)
    verification_status = serializers.PrimaryKeyRelatedField(queryset=VerificationStage.objects.all(),
                                                             required=False, write_only=True)

    class Meta:
        model = ProofOfWorkDiploma
        fields = ('id', 'city', 'diploma', 'number_document', 'date_start', 'date_end', 'status_document',
                  'list_positions', 'rank', 'type_document', 'port', 'statement', 'other_port', 'function_limitation',
                  'strict_blank', 'photo', 'created_by', 'verificated_by', 'verification_status')

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        verification_status = validated_data.pop('verification_status', None)
        if verification_status:
            update_is_active_verification_status(instance, verification_status.pk)
        old_instance = deepcopy(instance)
        user = self.context['request'].user
        user_id = user.id
        if old_instance.status_document_id not in [18, 20] and instance.status_document_id in [18, 20]:
            create_duplicate_proof_diploma.s(instance, user_id).apply_async(serializer='pickle')
        if ('status_document' in validated_data and
                instance.status_document_id in [magic_numbers.VERIFICATION_STATUS,
                                                magic_numbers.STATUS_CREATED_BY_AGENT]):
            if settings.ENABLE_ADDITIONAL_VERIFICATION is True and validated_data.get(
                    'status_document').pk in magic_numbers.ALL_VALID_STATUSES:
                validated_data['status_document_id'] = magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION
                check_document_to_additional_verification.s(self.instance._meta.model_name, instance.pk).apply_async()
        elif ('status_document' in validated_data and
              instance.status_document_id == magic_numbers.status_qual_doc_in_proccess and
              validated_data.get('status_document').pk in magic_numbers.ALL_VALID_STATUSES):
            back_office.tasks.update_proof_in_packet.delay(instance.pk, None, True)
        status_document = validated_data.get('status_document')
        if instance.status_document.pk != magic_numbers.VERIFICATION_STATUS and status_document and \
                status_document.pk == magic_numbers.VERIFICATION_STATUS:
            create_verification_status_for_document(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        if instance.status_document_id not in [19, 21, 7, 18] and instance.items.filter(
                item_status=DependencyItem.WAS_BOUGHT
        ).exists():
            for dependency in instance.items.filter(item_status=DependencyItem.WAS_BOUGHT):
                dependency.item = instance.statement
                dependency.item_status = DependencyItem.TO_BUY
                dependency.save()
        user = self.context['request'].user
        user_id = user.id
        save_history.s(user_id=user_id, module='ProofOfDiploma', action_type='edit',
                       content_obj=instance, serializer=ProofOfWorkDiplomaSerializer, new_obj=new_instance,
                       old_obj=old_instance, get_sailor=True).apply_async(serializer='pickle')
        return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            response['verification_status'] = verification_stages(instance, context=self.context)
        return response
