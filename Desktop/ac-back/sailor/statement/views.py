"""
Views for all statements from/to sailor
"""
import json
from copy import deepcopy
from datetime import date
from itertools import chain

from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Max, Q
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

import back_office.tasks
import sailor.document.serializers
import sailor.misc
import sailor.permissions
import sailor.statement.permissions
import sailor.statement.serializers
from cadets.misc import check_cadet_student_ID
from certificates.models import TimeForCourse
from certificates.tasks import send_statement_to_eti
from communication.models import SailorKeys
from delivery.misc import create_delivery_nova_poshta
from directory.models import LevelQualification, Course
from itcs import magic_numbers
from mixins.core import FullSailorViewSet
from sailor import serializers
from sailor.document.models import (ServiceRecord, Education, MedicalCertificate,
                                    QualificationDocument)
from sailor.models import (Profile, SailorPassport, Rating)
from sailor.statement.models import (StatementServiceRecord, StatementAdvancedTraining, StatementMedicalCertificate,
                                     StatementSQC, StatementQualification, StatementETI,
                                     StatementSailorPassport)
from sailor.tasks import save_history
from sailor.utils import get_statement_date_meeting
from sailor.views import sailor_not_exists_error
from user_profile.models import UserProfile


class StatementServiceRecordSailorView(FullSailorViewSet):
    """
    CRUD of statement for service record
    """
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        (IsAdminUser | sailor.statement.permissions.StatementServiceRecordPermission),
    )
    queryset = StatementServiceRecord.objects.all()
    serializer_class = sailor.statement.serializers.StatementServiceRecordSerializer
    model = StatementServiceRecord
    select_related = ('status',)
    prefetch_related = (
        'delivery', 'delivery__city', 'delivery__city__area', 'delivery__street', 'delivery__street__type_street',
        'delivery__warehouse'
    )

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        type_post = serializer.initial_data['type_post']
        status_document = magic_numbers.status_statement_serv_rec_in_process
        if type_post == 'novaposhta':
            ct = ContentType.objects.get(model__iexact='NovaPoshtaDelivery')
            delivery_id = create_delivery_nova_poshta(serializer.initial_data)
            ser = serializer.save(content_type_id=ct.id, object_id=delivery_id, status_id=status_document,
                                  author=self.request.user)
        else:
            raise ValidationError('Unknown type post')
        sailor_qs.statement_service_records.append(ser.id)
        sailor_qs.save(update_fields=['statement_service_records'])
        save_history.s(user_id=self.request.user.id, sailor_key_id=sailor_id,
                       module='StatementServiceRecord', action_type='create',
                       content_obj=ser, serializer=sailor.statement.serializers.StatementServiceRecordSerializer,
                       new_obj=ser).apply_async(serializer='pickle')

    @action(detail=True, methods=['post'])
    @swagger_auto_schema(operation_summary='Use only with V2 API', request_body=no_body)
    def create_service_record(self, request, *args, **kwargs):
        """
        creating service record from statement service record
        """
        sailor_id = self.kwargs.get('sailor_pk')
        if not sailor_id:
            raise ValidationError('Use only for V2 version API')  # TODO TO delete when have only V2 api
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        statement_service_record = self.get_object()
        if statement_service_record.status_id == magic_numbers.status_statement_serv_rec_created:
            raise ValidationError('Statement was created')
        if statement_service_record.is_payed is False:
            raise ValidationError('Statement not payed')
        split_fio_ukr = request.data['auth_agent_ukr'].split(' ')
        date_start = request.data.get('date_start', date.today())
        auth_agent_ukr = split_fio_ukr[1][:1] + '. ' + split_fio_ukr[0]
        split_fio_eng = request.data['auth_agent_eng'].split(' ')
        auth_agent_eng = split_fio_eng[1][:1] + '. ' + split_fio_eng[0]
        status_id = magic_numbers.VERIFICATION_STATUS
        user = self.request.user
        branch_office = user.userprofile.branch_office
        text_issued_by = '{} {} {}, {}'.format(user.last_name, user.first_name, user.userprofile.middle_name,
                                               branch_office.name_ukr)
        service_record = ServiceRecord.objects.create(auth_agent_ukr=auth_agent_ukr,
                                                      auth_agent_eng=auth_agent_eng,
                                                      status_document_id=status_id, issued_by=text_issued_by,
                                                      branch_office=branch_office, date_issued=date_start)
        if statement_service_record.photo:
            statement_photo = json.loads(statement_service_record.photo)
            profile = Profile.objects.filter(id=sailor_qs.profile).first()
            _profile = deepcopy(profile)
            if profile.photo:
                profile_photo = json.loads(profile.photo)
                profile_photo += statement_photo
            else:
                profile_photo = statement_photo
            profile.photo = json.dumps(profile_photo)
            profile.save(update_fields=['photo'])

            save_history.s(user_id=self.request.user.id, module='Profile', action_type='edit',
                           content_obj=profile, serializer=serializers.ProfileMainInfoSerializer, new_obj=profile,
                           old_obj=_profile, sailor_key_id=sailor_id).apply_async(serializer='pickle')

        _statement_service_record = deepcopy(statement_service_record)
        statement_service_record.status_id = magic_numbers.status_statement_serv_rec_created
        statement_service_record.save(update_fields=['status_id'])
        sailor_qs.service_records.append(service_record.id)
        sailor_qs.save(update_fields=['service_records'])

        save_history.s(user_id=self.request.user.id, module='ServiceRecord', action_type='create',
                       content_obj=service_record, serializer=sailor.document.serializers.ServiceRecordSailorSerializer,
                       new_obj=service_record, sailor_key_id=sailor_id).apply_async(serializer='pickle')

        save_history.s(user_id=self.request.user.id, module='StatementServiceRecord', action_type='edit',
                       content_obj=_statement_service_record,
                       serializer=sailor.statement.serializers.StatementServiceRecordSerializer,
                       old_obj=_statement_service_record, sailor_key_id=sailor_id,
                       new_obj=statement_service_record).apply_async(serializer='pickle')

        return Response({'status': 'success', 'description': 'service record is created'})


class StatementAdvancedTrainingView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
    )
    queryset = StatementAdvancedTraining.objects.all()
    serializer_class = sailor.statement.serializers.StatementAdvancedTrainingSerializer
    model = StatementAdvancedTraining
    select_related = ('level_qualification', 'status_document', 'educational_institution',)

    def get_queryset(self):
        qs = super().get_queryset()
        userprofile: UserProfile = self.request.user.userprofile
        if userprofile.type_user == userprofile.SECRETARY_ATC:
            qs = qs.filter(educational_institution=userprofile.education_institution)
        return qs

    def perform_create(self, serializer):
        sailor_id = self.kwargs[self.sailor_lookup]
        try:
            sailor_qs = SailorKeys.objects.get(id=int(sailor_id))
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        statement_in_process = self.get_queryset().filter(
            status_document_id__in=[magic_numbers.status_statement_adv_training_in_process,
                                    magic_numbers.CREATED_FROM_PERSONAL_CABINET]
        )
        if statement_in_process.exists():
            raise ValidationError('Statement exists')
        level_qualification = serializer.initial_data['level_qualification']
        qualification = LevelQualification.objects.get(id=level_qualification)
        statement_date = get_statement_date_meeting(sailor_key=sailor_id,
                                                    hour_for_statement=qualification.course_time_hours)
        date_meeting = statement_date['date_meeting']
        date_end_meeting = statement_date['date_end_meeting']
        number = self.model.generate_number()
        status_document = magic_numbers.status_statement_adv_training_in_process
        ser = serializer.save(number=number, status_document_id=status_document, author=self.request.user,
                              date_meeting=date_meeting, date_end_meeting=date_end_meeting)
        sailor_qs.statement_advanced_training.append(ser.id)
        sailor_qs.save(update_fields=['statement_advanced_training'])
        back_office.tasks.added_statement_adv_training_in_dependency.s(
            statement_id=ser.id,
            date_end_meeting=date_end_meeting,
            sailor_key=sailor_id,
            qualification_id=level_qualification).apply_async()
        save_history.s(user_id=self.request.user.id,
                       module='StatementAdvancedTraining',
                       action_type='create',
                       content_obj=ser,
                       serializer=sailor.statement.serializers.StatementAdvancedTrainingSerializer,
                       new_obj=ser,
                       get_sailor=True).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        if hasattr(instance, 'education'):
            raise ValidationError('Statement related to advanced training')
        dependency_item = instance.items.first()
        if dependency_item and dependency_item.packet_item.is_payed:
            raise ValidationError('Statement can only be deleted with the packet')
        if dependency_item:
            dependency_item.delete()
        return super().perform_destroy(instance)

    @swagger_auto_schema(request_body=sailor.statement.serializers.ShortAdvancedTrainingSerializer)
    @action(methods=['post'], detail=True, url_name='create_advanced_training', url_path='create_advanced_training',
            permission_classes=[sailor.statement.permissions.AdvancedTrainingPermission])
    def create_advanced_training(self, request, *args, **kwargs):
        sailor_id = kwargs['sailor_pk']
        statement_id = kwargs['pk']
        serializer = sailor.statement.serializers.ShortAdvancedTrainingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            sailor_qs = SailorKeys.objects.get(id=int(sailor_id))
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        statement = self.queryset.get(id=statement_id)
        if hasattr(statement, 'education'):
            raise ValidationError('Statement used')
        if statement.is_payed is False or \
                statement.status_document.id != magic_numbers.status_statement_adv_training_valid:
            raise ValidationError('Statement is not valid')
        date_end_educ = statement.date_end_meeting
        expired_date = date_end_educ + relativedelta(years=5)
        education = Education.objects.create(statement_advanced_training=statement, status_document_id=2,
                                             author=self.request.user, name_nz=statement.educational_institution,
                                             qualification=statement.level_qualification, type_document_id=3,
                                             registry_number=data['registry_number'], serial=data['serial'],
                                             number_document=data['number_document'], expired_date=expired_date,
                                             date_end_educ=date_end_educ, date_issue_document=date_end_educ)
        sailor_qs.education.append(education.id)
        sailor_qs.save(update_fields=['education'])
        save_history.s(user_id=self.request.user.id, module='Education', action_type='create',
                       content_obj=education, serializer=sailor.document.serializers.EducationSerializer,
                       new_obj=education,
                       sailor_key_id=sailor_qs.pk).apply_async(serializer='pickle')
        return Response({'status': 'success', 'description': 'advanced training is created'})


class StatementMedicalCertificateView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
    )
    queryset = StatementMedicalCertificate.objects.all()
    serializer_class = sailor.statement.serializers.StatementMedicalCertificateSerializer
    model = StatementMedicalCertificate
    select_related = ('position', 'status_document', 'medical_institution')

    def perform_create(self, serializer):
        sailor_id = self.kwargs[self.sailor_lookup]
        try:
            sailor_qs = SailorKeys.objects.get(id=int(sailor_id))
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        position = serializer.initial_data['position']
        statement_in_process = self.get_queryset().filter(
            status_document_id__in=[magic_numbers.status_statement_medical_cert_in_process,
                                    magic_numbers.CREATED_FROM_PERSONAL_CABINET]
        )
        if statement_in_process.exists():
            raise ValidationError('Statement exists')
        date_meeting = get_statement_date_meeting(sailor_key=sailor_id)['date_meeting']
        number = self.model.generate_number()
        status_document = magic_numbers.status_statement_medical_cert_in_process
        ser = serializer.save(number=number, status_document_id=status_document, author=self.request.user,
                              date_meeting=date_meeting)
        sailor_qs.statement_medical_certificate.append(ser.id)
        sailor_qs.save(update_fields=['statement_medical_certificate'])
        back_office.tasks.added_statement_med_certificate_in_dependency.s(statement_id=ser.id,
                                                                          date_meeting=date_meeting,
                                                                          sailor_key=sailor_id,
                                                                          position=position).apply_async()
        save_history.s(user_id=self.request.user.id, module='StatementMedicalCertificate', action_type='create',
                       content_obj=ser, serializer=sailor.statement.serializers.StatementMedicalCertificateSerializer,
                       new_obj=ser,
                       get_sailor=True).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        if hasattr(instance, 'medicalcertificate'):
            raise ValidationError('Statement related to medical certificate')
        dependency_item = instance.items.first()
        if dependency_item and dependency_item.packet_item.is_payed:
            raise ValidationError('Statement can only be deleted with the packet')
        if dependency_item:
            dependency_item.delete()
        return super().perform_destroy(instance)

    @swagger_auto_schema(request_body=sailor.document.serializers.ShortMedicalSerializer)
    @action(methods=['post'], detail=True, url_name='create_certificate', url_path='create_certificate')
    def create_medical_certificate(self, request, *args, **kwargs):
        sailor_id = kwargs['sailor_pk']
        statement_id = kwargs['pk']
        serializer = sailor.document.serializers.ShortMedicalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            sailor_qs = SailorKeys.objects.get(id=int(sailor_id))
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        statement = self.queryset.get(id=statement_id)
        if hasattr(statement, 'medicalcertificate'):
            raise ValidationError('Statement used')
        if statement.is_payed is False or \
                statement.status_document.id != magic_numbers.status_statement_medical_cert_valid:
            raise ValidationError('Statement is not valid')
        date_start = statement.date_meeting
        doctor = data.get('doctor')
        if self.request.user.userprofile.type_user == self.request.user.userprofile.MEDICAL:
            doctor = self.request.user.userprofile.doctor_info
        medical_cert = MedicalCertificate.objects.create(medical_statement=statement,
                                                         status_document_id=magic_numbers.status_qual_doc_in_proccess,
                                                         author=self.request.user,
                                                         doctor=doctor,
                                                         limitation=data['limitation'],
                                                         date_start=date_start,
                                                         date_end=data['date_end'],
                                                         position=statement.position,
                                                         number=data['number'])
        sailor_qs.medical_sertificate.append(medical_cert.id)
        sailor_qs.save(update_fields=['medical_sertificate'])
        statement.status_document_id = magic_numbers.STATUS_STATEMENT_MEDICAL_CERT_CREATED
        statement.save(update_fields=['status_document_id'])
        save_history.s(user_id=self.request.user.id, module='MedicalCertificate', action_type='create',
                       content_obj=medical_cert, serializer=sailor.document.serializers.MedicalCertificateSerializer,
                       new_obj=medical_cert, sailor_key_id=sailor_id).apply_async(serializer='pickle')
        return Response({'status': 'success', 'description': 'medical certificate is created'})


class StatementSQCView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        sailor.statement.permissions.ApplicationSQCPermission,
    )
    queryset = StatementSQC.objects.all()
    serializer_class = sailor.statement.serializers.StatementDKKSerializer
    small_serializer_class = sailor.statement.serializers.StatementDKKWithoutDocSer
    model = StatementSQC
    select_related = ('rank', 'type_document', 'status_document', 'branch_office',)

    def get_permissions(self):
        if self.action == 'related_docs':
            return [IsAdminUser(), ]
        return super().get_permissions()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return StatementSQC.objects.none()
        sailor_id = self.kwargs.get('sailor_pk')
        if self.request.version == 'v1':
            sailor_id = self.kwargs['pk']
        try:
            keys = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        queryset = StatementSQC.by_sailor.select_related().prefetch_related().filter_by_sailor(sailor_key=keys)
        up = self.request.user.userprofile
        if self.request.user.is_superuser is False:
            queryset = queryset.exclude(status_document_id__in=[magic_numbers.status_state_qual_dkk_canceled,
                                                                magic_numbers.STATUS_REMOVED_DOCUMENT, ])
        if up.type_user in [up.VERIFIER, up.SECRETARY_SQC, up.MARAD]:
            queryset = queryset.exclude(status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT,
                                                                magic_numbers.status_statement_canceled])
        queryset.update(sailor=sailor_id)

        return queryset.order_by('-id')

    @staticmethod
    def get_qualification_positions(keys):
        positions = list(QualificationDocument.objects.filter(
            id__in=keys.qualification_documents, status_document_id=19).values_list('list_positions', flat=True))
        positions = list(chain.from_iterable(positions))
        exclude_ids = [98, 99, 145, 141, 142, 143, 144, 127]
        return list(set(positions) - set(exclude_ids))

    def check_have_experience(self, keys, rank_id, list_positions, is_continue):
        checking_exp = sailor.misc.CheckSailorExperience(sailor=keys.pk, list_position=list_positions)
        if is_continue is False:
            experience = checking_exp.check_experience_many_pos()
            if experience:
                return any(exp['value'] for exp in experience)
            else:
                return False
        else:
            check_exp = sailor.misc.check_continue_for_experience(
                list_positions=list_positions, rank_id=rank_id,
                ids_positions_in_qual_doc=self.get_qualification_positions(keys))
            if check_exp['is_check_exp']:
                experience = checking_exp.check_experience_many_pos()
                if experience:
                    return any(exp['value'] for exp in experience)
                else:
                    return False
            return True

    def perform_create(self, serializer):
        user = self.request.user
        sailor_id = serializer.initial_data['sailor']
        rank = serializer.validated_data.get('rank')
        rank_id = rank.pk
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        number = self.model.generate_number()
        list_positions = serializer.initial_data['list_positions']
        is_continue = sailor.misc.check_is_continue(sailor_qs=sailor_qs, rank_id=rank.pk, list_positions=list_positions)
        branch_office = user.userprofile.branch_office
        checking = sailor.misc.CheckSailorForPositionDKK(sailor=sailor_id, is_continue=is_continue,
                                                         list_position=list_positions)
        documents = checking.get_docs_with_status()
        have_all_docs = documents['have_all_doc']
        all_docs = documents.get('all_docs', [])
        is_cadet = False

        have_all_exp = self.check_have_experience(keys=sailor_qs, rank_id=rank_id, list_positions=list_positions,
                                                  is_continue=is_continue)
        if sailor_qs.students_id and bool(is_continue) is False and have_all_docs is False:
            is_cadet = check_cadet_student_ID(students_id=sailor_qs.students_id, rank_id=rank_id)
        if is_cadet and documents['not_have_educ_doc']:
            status_document = magic_numbers.status_state_qual_dkk_in_process
        elif user.userprofile.type_user == user.userprofile.AGENT:
            status_document = magic_numbers.STATUS_CREATED_BY_AGENT
        elif have_all_docs is False and have_all_exp is False:
            status_document = magic_numbers.status_state_qual_dkk_absense
        else:
            status_document = magic_numbers.status_state_qual_dkk_in_process
        ser = serializer.save(number=number, sailor=sailor_id, status_document_id=status_document,
                              is_continue=is_continue, author=user, branch_office=branch_office, is_cadet=is_cadet)
        if have_all_docs is True:
            ser.related_docs = all_docs
        if sailor_qs.statement_dkk:
            sailor_qs.statement_dkk.append(ser.id)
            sailor_qs.save(update_fields=['statement_dkk'])
        else:
            sailor_qs.statement_dkk = [ser.id]
            sailor_qs.save(update_fields=['statement_dkk'])
        if not sailor_qs.agent_id:
            Rating.objects.create(sailor_key=sailor_id, rating=4)
        save_history.s(user_id=self.request.user.id, module='StatementDKK', action_type='create',
                       content_obj=ser, serializer=sailor.statement.serializers.StatementDKKSerializer, new_obj=ser,
                       sailor_key_id=sailor_id).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        if hasattr(instance, 'protocolsqc'):
            raise ValidationError('Statement related to protocol dkk')
        dependency_item = instance.items.first()
        if dependency_item and dependency_item.packet_item.is_payed:
            raise ValidationError('Statement can only be deleted with the packet')
        if dependency_item:
            dependency_item.delete()
        return super().perform_destroy(instance)

    @action(detail=False, methods=['get'])
    def success(self, request, sailor_pk):
        queryset = self.get_queryset()
        if not queryset:
            return Response([])
        try:
            queryset = queryset.filter(protocolsqc__isnull=True).filter(
                Q(status_document_id=magic_numbers.status_state_qual_dkk_approv) |
                Q(status_document_id=magic_numbers.status_cadets_state_dkk_allowed)
            ).order_by('-id')
            return Response(self.small_serializer_class(queryset, many=True).data)
        except (TypeError, AttributeError):
            return Response([])

    @action(detail=True, methods=['patch', 'post'], )
    @swagger_auto_schema(request_body=sailor.statement.serializers.RelatedDocsStatementSQC)
    def related_docs(self, *args, **kwargs):
        instance: StatementSQC = self.get_object()
        serializer = sailor.statement.serializers.RelatedDocsStatementSQC(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ct: ContentType = data.get('content_type')
        old_document = data.get('old_document')
        new_document = data.get('new_document')
        model = ct.model_class()
        if not instance.related_docs.exists() or not hasattr(instance, 'protocolsqc'):
            raise ValidationError('First create protocol sqc')
        if self.request.method == 'POST':
            instance.related_docs.create(gm2m_ct=ct, gm2m_pk=new_document, gm2m_src_id=instance.pk)
            instance.protocolsqc.related_docs.create(
                gm2m_ct=ct,
                gm2m_pk=new_document,
                gm2m_src_id=instance.protocolsqc.pk
            )
            protocol = instance.protocolsqc
            if hasattr(protocol, 'statementqualification'):
                statement_qualification = protocol.statementqualification
                statement_qualification.related_docs.create(
                    gm2m_ct=ct,
                    gm2m_pk=new_document,
                    gm2m_src_id=protocol.statementqualification.pk
                )
                for qualification in statement_qualification.qualificationdocument_set.all():
                    qualification.related_docs.create(
                        gm2m_ct=ct,
                        gm2m_pk=new_document,
                        gm2m_src_id=qualification.pk
                    )
        elif self.request.method == 'PATCH':
            old_document_instance = model.objects.get(pk=old_document)
            new_document_instance = model.objects.get(pk=new_document)
            instance.related_docs.remove(old_document_instance)
            instance.protocolsqc.related_docs.remove(old_document_instance)
            instance.related_docs.add(new_document_instance)
            instance.protocolsqc.related_docs.add(new_document_instance)
            protocol = instance.protocolsqc
            if hasattr(protocol, 'statementqualification'):
                statement_qualification = protocol.statementqualification
                statement_qualification.related_docs.remove(old_document_instance)
                statement_qualification.related_docs.add(new_document_instance)
                for qualification in statement_qualification.qualificationdocument_set.all():
                    qualification.related_docs.remove(old_document_instance)
                    qualification.related_docs.add(new_document_instance)
        cache.delete(f'exists_{instance.sailor}_{instance.list_positions}_'
                     f'{instance.is_continue}_{instance.number}')
        return Response(self.serializer_class(instance=instance).data)


class StatementQualificationView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        sailor.statement.permissions.QualificationApplicationPermission,
    )
    queryset = StatementQualification.objects.all()
    serializer_class = sailor.statement.serializers.StatementQualificationDocumentSerializer
    model = StatementQualification
    select_related = ('rank', 'type_document', 'status_document', 'protocol_dkk', 'port')

    def perform_create(self, serializer):
        user = self.request.user
        sailor_id = self.kwargs.get('sailor_pk')
        protocol_sqc = serializer.validated_data.get('protocol_dkk')
        if protocol_sqc:
            rank = protocol_sqc.statement_dkk.rank
            list_positions = protocol_sqc.statement_dkk.list_positions
        else:
            list_positions = serializer.initial_data.get('list_positions')
            rank = serializer.validated_data.get('rank')
        if rank.is_dkk and not protocol_sqc:
            raise ValidationError('Protocol dkk is null')
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        is_continue = sailor.misc.check_is_continue(sailor_qs=sailor_qs, rank_id=rank.pk, list_positions=list_positions)
        type_document = serializer.validated_data.get('type_document')
        type_document = type_document if type_document else rank.type_document
        checking = sailor.misc.CheckSailorForPositionDKK(sailor=sailor_id, is_continue=is_continue,
                                                         list_position=list_positions)
        documents = checking.get_docs_with_status()
        have_all_docs = documents['have_all_doc']
        all_docs = documents.get('all_docs', [])
        status_document = (magic_numbers.status_state_qual_dkk_absense if not have_all_docs else
                           magic_numbers.status_state_qual_dkk_in_process)
        ser = serializer.save(
            status_document_id=status_document,
            list_positions=list_positions,
            is_continue=is_continue,
            type_document=type_document,
            rank=rank,
            author=user,
        )
        if have_all_docs:
            ser.related_docs = all_docs
        sailor_qs.statement_qualification.append(ser.id)
        sailor_qs.save(update_fields=['statement_qualification'])
        save_history.s(user_id=user.id, module='StatementQualification', action_type='create',
                       content_obj=ser,
                       serializer=sailor.statement.serializers.StatementQualificationDocumentSerializer, new_obj=ser,
                       sailor_key_id=sailor_id).apply_async(serializer='pickle')

    def destroy(self, request, *args, **kwargs):
        instance: StatementQualification = self.get_object()
        if instance.qualificationdocument_set.exists():
            raise ValidationError('Statement related to qualification document')
        key = SailorKeys.objects.filter(statement_qualification__overlap=[instance.id]).first()
        if not key:
            raise ValidationError(sailor_not_exists_error)
        _instance = deepcopy(instance)
        if instance.status_document_id != magic_numbers.STATUS_REMOVED_DOCUMENT:
            instance.status_document_id = magic_numbers.STATUS_REMOVED_DOCUMENT
            instance.save(update_fields=['status_document_id'])
            history_args = {'action_type': 'edit', 'new_obj': instance}
        else:
            id_instance = instance.id
            instance.delete()
            key.statement_qualification.remove(id_instance)
            key.save(update_fields=['statement_qualification'])
            history_args = {'action_type': 'delete'}
        save_history.s(user_id=self.request.user.id,
                       module='StatementQualification',
                       content_obj=_instance,
                       serializer=sailor.statement.serializers.StatementQualificationDocumentSerializer,
                       old_obj=_instance,
                       sailor_key_id=key.id,
                       **history_args,
                       ).apply_async(serializer='pickle')
        if getattr(instance, 'pk', None):
            return Response(self.serializer_class(instance).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_name='success')
    def success(self, request, sailor_pk):
        queryset = self.get_queryset()
        queryset = queryset.filter(
            Q(status_document_id=magic_numbers.status_state_qual_dkk_approv) & Q(
                Q(qualificationdocument__isnull=True, proofofworkdiploma__isnull=True) |
                Q(
                    Q(Q(qualificationdocument__status_document_id__in=[17]) | Q(qualificationdocument__isnull=True)) &
                    Q(Q(proofofworkdiploma__status_document_id__in=[17]) | Q(proofofworkdiploma__isnull=True))
                )
            )).order_by('-id')
        return Response(self.serializer_class(queryset, many=True).data)


class StatementETIView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
    )
    queryset = StatementETI.objects.all()
    serializer_class = sailor.statement.serializers.StatementETISerializer
    model = StatementETI
    select_related = ('course', 'status_document', 'institution',)

    def get_queryset(self):
        user = self.request.user
        userprofile = user.userprofile
        queryset = super().get_queryset()
        if userprofile.type_user == UserProfile.ETI_EMPLOYEE:
            queryset = queryset.filter(institution=userprofile.eti_institution)
        return queryset

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=int(sailor_id))
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        course_id = serializer.initial_data['course']
        course = Course.objects.get(id=course_id)
        is_continue = self.get_queryset().filter(course=course, status_document_id__in=[2, 19, 7]).exists()
        default_time = 8 * 10
        try:
            time = TimeForCourse.objects.get(is_continue=is_continue, course=course).full_time
        except TimeForCourse.DoesNotExist:
            try:
                time = TimeForCourse.objects.get(is_continue=False, course=course).full_time
            except TimeForCourse.DoesNotExist:
                time = default_time
        statement_date = get_statement_date_meeting(sailor_key=sailor_id, hour_for_statement=time, working_day=12)
        date_meeting = statement_date['date_meeting']
        date_end_meeting = statement_date['date_end_meeting']
        number = self.model.generate_number()
        status_document = magic_numbers.status_statement_eti_in_process
        ser = serializer.save(number=number, status_document_id=status_document, author=self.request.user,
                              date_meeting=date_meeting, date_end_meeting=date_end_meeting)
        if sailor_qs.statement_eti:
            sailor_qs.statement_eti.append(ser.id)
            sailor_qs.save(update_fields=['statement_eti'])
        else:
            sailor_qs.statement_eti = [ser.id]
            sailor_qs.save(update_fields=['statement_eti'])
        back_office.tasks.added_statement_eti_in_dependency.s(statement_id=ser.id,
                                                              date_end_meeting=date_end_meeting,
                                                              sailor_key=sailor_id,
                                                              course_id=course_id).apply_async()
        # certificates.tasks.send_statement_to_eti.s(statement_id=ser.pk).apply_async(countdown=10)
        save_history.s(user_id=self.request.user.id, module='StatementETI', action_type='create',
                       content_obj=ser, serializer=sailor.statement.serializers.StatementETISerializer, new_obj=ser,
                       get_sailor=True).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        dependency_item = instance.items.first()
        if dependency_item and dependency_item.packet_item.is_payed:
            raise ValidationError('Statement can only be deleted with the packet')
        if dependency_item:
            dependency_item.delete()
        return super().perform_destroy(instance)

    def get_permissions(self):
        if self.action == 'send_to_eti':
            return [IsAdminUser(), ]
        return super().get_permissions()

    @action(methods=['post'], detail=True)
    @swagger_auto_schema(request_body=no_body)
    def send_to_eti(self, request, *args, **kwargs):
        instance = self.get_object()
        send_statement_to_eti.s(instance.pk, True).apply_async()
        return Response({'status': 'success'})


class StatementSailorPassportView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
    )
    queryset = StatementSailorPassport.objects.all()
    serializer_class = sailor.statement.serializers.StatementSailorPassportSerializer
    model = StatementSailorPassport

    def perform_create(self, serializer):

        type_receipt_is_continue = {1: False, 2: False, 3: True, 4: True}
        sailor_id = serializer.initial_data['sailor']
        type_receipt = serializer.validated_data['type_receipt']
        fast_obtaining = True if type_receipt == 2 else False
        try:
            sailor_qs = SailorKeys.objects.get(id=int(sailor_id))
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        if self.request.user.userprofile.type_user == self.request.user.userprofile.DPD and sailor_qs.agent_id:
            raise ValidationError('Sailor has a seaman')
        statement_in_process = self.queryset.filter(
            id__in=sailor_qs.statement_sailor_passport,
            status_document_id__in=[magic_numbers.status_statement_sailor_passport_in_process,
                                    magic_numbers.CREATED_FROM_PERSONAL_CABINET]
        )
        if statement_in_process.exists():
            raise ValidationError('Statement exists')
        number = self.model.generate_number()
        status_document = magic_numbers.status_statement_sailor_passport_in_process
        is_continue = type_receipt_is_continue.get(type_receipt)
        sailor_passport_id = None
        if is_continue:
            sailor_passport = SailorPassport.objects.filter(
                id__in=sailor_qs.sailor_passport,
                status_document_id__in=[SailorPassport.StatusDocument.VALID, SailorPassport.StatusDocument.EXPIRED],
                date_renewal__isnull=True)
            if not sailor_passport.exists():
                raise ValidationError('No sailor passport to renew')
        date_meeting = get_statement_date_meeting(sailor_key=sailor_id)['date_meeting']
        ser = serializer.save(number=number, status_document_id=status_document, is_continue=is_continue,
                              author=self.request.user,
                              date_meeting=date_meeting, fast_obtaining=fast_obtaining)
        sailor_qs.statement_sailor_passport.append(ser.id)
        sailor_qs.save(update_fields=['statement_sailor_passport'])
        back_office.tasks.added_statement_sailor_passport_in_dependency.s(statement_id=ser.id,
                                                                          date_meeting=date_meeting,
                                                                          sailor_key=sailor_id,
                                                                          is_continue=is_continue).apply_async()
        save_history.s(user_id=self.request.user.id, module='StatementSailorPassport', action_type='create',
                       content_obj=ser, serializer=sailor.statement.serializers.StatementSailorPassportSerializer,
                       new_obj=ser,
                       get_sailor=True).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        dependency_item = instance.items.first()
        if dependency_item and dependency_item.packet_item.is_payed:
            raise ValidationError('Statement can only be deleted with the packet')
        if dependency_item:
            dependency_item.delete()
        return super().perform_destroy(instance)

    @action(methods=['get'], detail=False)
    def success(self, request, sailor_pk):
        queryset = self.get_queryset().filter(status_document_id=StatementSailorPassport.StatusDocument.APPROVED,
                                              sailor_passport__isnull=True)
        return Response(self.serializer_class(instance=queryset, many=True).data)
