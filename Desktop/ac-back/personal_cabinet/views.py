import base64
from copy import deepcopy
from datetime import datetime, timezone, date
from itertools import chain

import pyqrcode as qr
from cryptography.fernet import Fernet
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone as tz
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import generics, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from agent.models import AgentSailor
from cadets.misc import check_cadet_student_ID
from cadets.models import StudentID
from communication.models import SailorKeys
from delivery.misc import create_delivery_nova_poshta
from directory.models import Rank, BranchOffice, Position
from itcs import magic_numbers
from itcs.settings import PRICE_SERVICE_RECORD, CODE_EXPIRATION_TIME
from notifications.views import tbot
from personal_cabinet.core import SailorGetQuerySetMixin, PhotoUploadMixin
from personal_cabinet.models import PersonalDataProcessing
from personal_cabinet.serializers import (PersonalEducationSerializer, PersonalQualificationDocumentSerializer,
                                          PersonalProofOfWorkDiplomaSerializer,
                                          PersonalMedicalCertificateSerializer, PersonalSailorPassportSerializer,
                                          PersonalCitizenPassportSerializer, PersonalProtocolDKKSerializer,
                                          PersonalExperienceDocumentSerializer, PersonalSailorStatementDKKSerialize,
                                          PersonalCertificateNTZSerializer,
                                          PersonalStatementQualificationDocumentSerializer,
                                          PersonalProfileMainInfoSerializer, CheckDocumentsStatementDKKSerializer,
                                          CheckDocumentParamsSerializer, PersonalDataProcessingSerializer,
                                          ChangeMainPhoneSerializer,
                                          PersonalLineInServiceRecordSerializer, PersonalStudentsIDSerializer)
from personal_cabinet.tasks import added_phone_to_profile
from personal_cabinet.utils import add_watermark_response
from sailor.document.models import ServiceRecord, LineInServiceRecord, Education, ProtocolSQC, \
    CertificateETI, MedicalCertificate, QualificationDocument, ProofOfWorkDiploma, ResponsibilityServiceRecord
from sailor.misc import (CheckSailorForPositionDKK, check_is_continue,
                         get_is_repair, check_interval_date, check_all_function)
from sailor.models import (Profile, SailorPassport, Passport, PhotoProfile,
                           Rating)
from sailor.statement.models import StatementServiceRecord, StatementSQC, StatementQualification, \
    StatementSailorPassport
from sailor.statement.serializers import StatementServiceRecordSerializer, StatementDKKWithoutDocSer, \
    StatementQualificationDocumentSerializer, StatementSailorPassportSerializer
from sailor.tasks import save_history
from sms_auth.misc import send_message, create_sms_code
from sms_auth.models import SecurityCode
from user_profile.models import UserProfile
from user_profile.serializer import UserSerializer

sailor_not_exists_error = 'Sailor does not exists'

User = get_user_model()


class MainSailorInfoView(ListAPIView):
    """
    Main info about sailor
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalProfileMainInfoSerializer

    def get_queryset(self):
        try:
            sailor = SailorKeys.objects.get(user_id=self.request.user.id)
            self.serializer_class.sailor_key_val = sailor.pk
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        except SailorKeys.MultipleObjectsReturned:
            sailor = SailorKeys.objects.filter(user_id=self.request.user.pk).first()
        if sailor.profile:
            return Profile.objects.filter(id=sailor.profile)
        else:
            return []


class BasePersonalQualificationDocumentView(PhotoUploadMixin, mixins.ListModelMixin,
                                            mixins.CreateModelMixin, GenericViewSet):
    """
    Sailor's qualification documents (diplomas, specialist certificates)
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalQualificationDocumentSerializer
    model = QualificationDocument

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def perform_create(self, serializer):
        sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        status_document = self.get_create_status_document()
        list_positions = serializer.initial_data['list_positions']
        rank_id = Position.objects.get(id=list_positions[0]).rank_id
        ser = serializer.save(status_document_id=status_document,
                              sailor=sailor_qs.pk,
                              rank_id=rank_id)
        sailor_qs.qualification_documents.append(ser.id)
        sailor_qs.save(update_fields=['qualification_documents'])
        save_history.s(user_id=self.request.user.id,
                       module='QualificationDocument',
                       action_type='create',
                       content_obj=ser,
                       serializer=PersonalQualificationDocumentSerializer,
                       new_obj=ser,
                       sailor_key_id=sailor_qs.pk,
                       ).apply_async(serializer='pickle')

    @action(detail=False, methods=['get'], url_name='diploma_for_proof',
            url_path='diploma_for_proof')
    def get_diploma_for_proof(self, request):
        """
        Returns a list of qualification documents for proof work diplomas
        """
        queryset = self.get_queryset()
        try:
            queryset = queryset.filter(Q(type_document_id__in=[1, 49]) &
                                       (Q(status_document_id=magic_numbers.status_qual_doc_valid) |
                                        Q(status_document_id=magic_numbers.VERIFICATION_STATUS))
                                       ).order_by('-id')
            return Response(self.serializer_class(queryset, many=True).data)
        except (TypeError, AttributeError):
            return Response([])

    @action(detail=False, methods=['get'], url_name='diplomas_for_apply')
    def get_diplomas_for_apply(self, request, *args, **kwargs):
        """
        Returns a list of qualification documents with different statuses
        """
        try:
            sailor_key = SailorKeys.objects.get(user_id=self.request.user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        queryset = self.model.by_sailor.filter_by_sailor(sailor_key)
        try:
            queryset = queryset.filter(status_document_id__in=(magic_numbers.status_qual_doc_valid,
                                                               magic_numbers.VERIFICATION_STATUS,
                                                               magic_numbers.STATUS_CREATED_BY_AGENT)
                                       ).order_by('-id')
            return Response(self.serializer_class(queryset, many=True).data)
        except TypeError:
            return Response([])


class BasePersonalProofOfWorkDiplomaView(PhotoUploadMixin, mixins.ListModelMixin,
                                         mixins.CreateModelMixin, GenericViewSet):
    """
    Sailor's qualification documents (proof of work diploma)
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalProofOfWorkDiplomaSerializer

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_PERSONAL_CABINET,
            magic_numbers.CREATED_FROM_MORRICHSERVICE
        )

    def get_queryset(self):
        try:
            sailor = SailorKeys.objects.get(user_id=self.request.user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        diplomas = list(QualificationDocument.objects.filter(id__in=sailor.qualification_documents,
                                                             type_document_id=49).values_list('id', flat=True))
        return ProofOfWorkDiploma.objects.filter(diploma__in=diplomas).exclude(
            status_document_id__in=self.get_exclude_status_document()).order_by('-id')

    def perform_create(self, serializer):
        sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        status_document = self.get_create_status_document()
        ser = serializer.save(status_document_id=status_document)
        save_history.s(user_id=self.request.user.id,
                       module='ProofOfDiploma',
                       action_type='create',
                       content_obj=ser,
                       serializer=PersonalProofOfWorkDiplomaSerializer,
                       new_obj=ser,
                       sailor_key_id=sailor_qs.pk,
                       ).apply_async(serializer='pickle')


class BasePersonalServiceRecordsView(PhotoUploadMixin, mixins.ListModelMixin,
                                     mixins.CreateModelMixin, GenericViewSet):
    """
    Sailor's service records
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = None
    model = ServiceRecord

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def perform_create(self, serializer):
        sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        status_document = self.get_create_status_document()
        try:
            split_fio_ukr = serializer.initial_data['auth_agent_ukr'].split(' ')
            auth_agent_ukr = split_fio_ukr[1][:1] + '. ' + split_fio_ukr[0]
            split_fio_eng = serializer.initial_data['auth_agent_eng'].split(' ')
            auth_agent_eng = split_fio_eng[1][:1] + '. ' + split_fio_eng[0]
        except IndexError:
            auth_agent_ukr = serializer.validated_data.get('auth_agent_ukr')
            auth_agent_eng = serializer.validated_data.get('auth_agent_eng')
        branch_office: BranchOffice = serializer.validated_data.get('branch_office')
        issued_by = serializer.validated_data.get('issued_by') + f', {branch_office.name_ukr}'
        ser = serializer.save(status_document_id=status_document,
                              auth_agent_ukr=auth_agent_ukr,
                              auth_agent_eng=auth_agent_eng,
                              issued_by=issued_by)
        sailor_qs.service_records.append(ser.id)
        sailor_qs.save(update_fields=['service_records'])
        save_history.s(user_id=self.request.user.id,
                       module='ServiceRecord',
                       action_type='create',
                       content_obj=ser,
                       serializer=self.serializer_class,
                       new_obj=ser,
                       sailor_key_id=sailor_qs.pk,
                       ).apply_async(serializer='pickle')


class BasePersonalEducationView(PhotoUploadMixin, mixins.ListModelMixin,
                                mixins.CreateModelMixin, GenericViewSet):
    """
    Educational documents
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalEducationSerializer
    model = Education

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def perform_create(self, serializer):
        sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        status_document = self.get_create_status_document()
        ser = serializer.save(status_document_id=status_document, sailor=sailor_qs.pk)
        sailor_qs.education.append(ser.id)
        sailor_qs.save(update_fields=['education'])
        save_history.s(user_id=self.request.user.id,
                       module='Education',
                       action_type='create',
                       content_obj=ser,
                       serializer=PersonalEducationSerializer,
                       new_obj=ser,
                       sailor_key_id=sailor_qs.pk,
                       ).apply_async(serializer='pickle')


class BasePersonalNTZCertificatesView(PhotoUploadMixin, mixins.ListModelMixin,
                                      mixins.CreateModelMixin, GenericViewSet):
    """
    Sailor's ETI certificates
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalCertificateNTZSerializer
    model = CertificateETI

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(ntz_number=-1)

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def perform_create(self, serializer):
        sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        status_document = self.get_create_status_document()
        ser = serializer.save(status_document_id=status_document, sailor=sailor_qs.pk)
        sailor_qs.sertificate_ntz.append(ser.id)
        sailor_qs.save(update_fields=['sertificate_ntz'])
        save_history.s(user_id=self.request.user.id,
                       module='CertificateNTZ',
                       action_type='create',
                       content_obj=ser,
                       serializer=PersonalCertificateNTZSerializer,
                       new_obj=ser,
                       sailor_key_id=sailor_qs.pk,
                       ).apply_async(serializer='pickle')


class BasePersonalMedicalCertificatesView(PhotoUploadMixin, mixins.ListModelMixin,
                                          mixins.CreateModelMixin, GenericViewSet):
    """
    Sailor's medical certificates
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalMedicalCertificateSerializer
    model = MedicalCertificate

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def perform_create(self, serializer):
        sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        status_document = self.get_create_status_document()
        ser = serializer.save(status_document_id=status_document, sailor=sailor_qs.pk)
        sailor_qs.medical_sertificate.append(ser.id)
        sailor_qs.save(update_fields=['medical_sertificate'])
        save_history.s(user_id=self.request.user.id,
                       module='MedicalCertificate',
                       action_type='create',
                       content_obj=ser,
                       serializer=PersonalMedicalCertificateSerializer,
                       new_obj=ser,
                       sailor_key_id=sailor_qs.pk,
                       ).apply_async(serializer='pickle')


class BasePersonalSailorPassportView(PhotoUploadMixin, mixins.ListModelMixin,
                                     mixins.CreateModelMixin, GenericViewSet):
    """
    Sailor's passports
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalSailorPassportSerializer
    model = SailorPassport

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def perform_create(self, serializer):
        sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        status_document = self.get_create_status_document()
        ser = serializer.save(status_document_id=status_document, sailor=sailor_qs.pk, is_new_document=False)
        sailor_qs.sailor_passport.append(ser.id)
        sailor_qs.save(update_fields=['sailor_passport'])
        save_history.s(user_id=self.request.user.id,
                       module='SailorPassport',
                       action_type='create',
                       content_obj=ser,
                       serializer=PersonalSailorPassportSerializer,
                       new_obj=ser,
                       sailor_key_id=sailor_qs.pk,
                       ).apply_async(serializer='pickle')


class BasePersonalCitizenPassport(mixins.ListModelMixin, GenericViewSet, SailorGetQuerySetMixin):
    """
    Sailor's citizen passports
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalCitizenPassportSerializer
    model = Passport


class BasePersonalProtocolDKK(mixins.ListModelMixin, GenericViewSet):
    """
    Sailor's protocols SQC
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalProtocolDKKSerializer
    model = ProtocolSQC

    @action(detail=True, methods=['get'], permission_classes=(IsAuthenticated,))
    def for_statement_qual(self, request):
        """
        Returns a list of protocols sqc for statements for qualification documents
        """
        try:
            keys = SailorKeys.objects.get(user_id=self.request.user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        if keys.protocol_dkk:
            quals_docs = QualificationDocument.objects.filter(id__in=keys.qualification_documents)
            proofs_docs = ProofOfWorkDiploma.objects.filter(diploma__in=quals_docs)
            protocol_ids = keys.protocol_dkk
            exclude_list = []
            protocols = ProtocolSQC.objects.filter(
                Q(id__in=protocol_ids) & Q(statementqualification__isnull=True) & Q(status_document_id=29)
                & Q(decision_id=magic_numbers.decision_allow)).order_by('-id')
            for protocol in protocols:
                qual_doc = quals_docs.filter(rank_id=protocol.statement_dkk.rank_id,
                                             list_positions__contains=protocol.statement_dkk.list_positions,
                                             date_start__gte=protocol.date_meeting)
                proof_doc = proofs_docs.filter(diploma__rank_id=protocol.statement_dkk.rank_id,
                                               diploma__list_positions__contains=protocol.statement_dkk.list_positions,
                                               date_start__gte=protocol.date_meeting)
                if proof_doc.exists() or qual_doc.exists():
                    exclude_list.append(protocol.pk)
            protocols = protocols.exclude(id__in=exclude_list)
            return Response(self.serializer_class(protocols, many=True).data)
        else:
            return Response([])


class BasePersonalExperienceDoc(PhotoUploadMixin, mixins.ListModelMixin,
                                mixins.CreateModelMixin, GenericViewSet):
    """
    Sailor's experience documents (certificates)
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalExperienceDocumentSerializer
    model = LineInServiceRecord

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_PERSONAL_CABINET,
            magic_numbers.CREATED_FROM_MORRICHSERVICE
        )

    def get_queryset(self):
        try:
            sailor = SailorKeys.objects.get(user_id=self.request.user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        return LineInServiceRecord.objects.filter(id__in=sailor.experience_docs).exclude(
            status_line_id__in=self.get_exclude_status_document()).order_by('-id')

    def perform_create(self, serializer):
        sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        status_line = self.get_create_status_document()
        if (serializer.initial_data.get('date_start') or serializer.initial_data.get('date_end')) and \
                serializer.initial_data.get('days_work'):
            raise ValidationError('Must be only interval or days')
        all_function = serializer.validated_data.pop('service_record_line', None)
        all_function = check_all_function(all_function)
        date_start = serializer.validated_data.get('date_start')
        date_end = serializer.validated_data.get('date_end')
        if serializer.validated_data.get('is_repaired'):
            days_repair = serializer.validated_data.get('days_repair', 0)
            repair_date_from = serializer.validated_data.get('repair_date_from')
            repair_date_to = serializer.validated_data.get('repair_date_to')
        else:
            days_repair = 0
            repair_date_from = None
            repair_date_to = None
        if (repair_date_from and repair_date_to and (
                not (date_start <= repair_date_from <= date_end) or not (date_start <= repair_date_to <= date_end))):
            # период ремонта не входит в рейс
            raise ValidationError('wrong date intervals')
        if serializer.validated_data[
            'record_type'] != 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо':
            # промежутки времени, которые моряк работал, не выполняя никаких обязанностей
            date_intervals = check_interval_date(all_function=all_function, date_start=date_start, date_end=date_end,
                                                 days_repair=days_repair, repair_date_from=repair_date_from,
                                                 repair_date_to=repair_date_to)
            if all_function:
                all_function += date_intervals
        ser = serializer.save(date_write=date.today(), status_line_id=status_line)
        if all_function:
            self.create_responsibility(repair_date_from, repair_date_to, all_function, ser.id)
        sailor_qs.experience_docs.append(ser.id)
        sailor_qs.save(update_fields=['experience_docs'])
        save_history.s(user_id=self.request.user.id,
                       module='ExperienceDoc',
                       action_type='create',
                       content_obj=ser,
                       serializer=PersonalExperienceDocumentSerializer,
                       new_obj=ser,
                       sailor_key_id=sailor_qs.pk,
                       ).apply_async(serializer='pickle')

    @staticmethod
    def create_responsibility(repair_date_from=None, repair_date_to=None, all_function=None, service_line_id=None):
        all_function = get_is_repair(repair_date_from, repair_date_to, all_function)
        list_responsibility = [ResponsibilityServiceRecord(
            service_record_line_id=service_line_id, responsibility=function.get('responsibility'),
            date_from=function.get('date_from'), date_to=function.get('date_to'),
            days_work=function.get('days_work'), is_repaired=function.get('is_repaired', False))
            for function in all_function]
        ResponsibilityServiceRecord.objects.bulk_create(list_responsibility)


class BasePersonalStatementDKK(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                               GenericViewSet):
    # permission_classes = (IsDkkStatementOwnerOrAdmin,)
    permission_classes = (IsAuthenticated,)
    queryset = StatementSQC.objects.all()
    serializer_class = PersonalSailorStatementDKKSerialize
    model = StatementSQC

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    # def get_permissions(self):
    #     if self.action in ['sailor_statements_sqc', 'success_sailor_statements_sqc']:
    #         return [permission() for permission in (IsAuthenticated,)]
    #     return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        try:
            sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        sailor_statement_id = sailor_qs.statement_dkk or []
        user_statement = StatementSQC.objects.filter(
            id__in=sailor_statement_id).exclude(status_document_id__in=(magic_numbers.status_state_qual_dkk_approv,
                                                                        magic_numbers.status_state_qual_dkk_rejected,
                                                                        magic_numbers.status_state_qual_dkk_student,
                                                                        magic_numbers.status_state_qual_dkk_canceled,
                                                                        magic_numbers.STATUS_REMOVED_DOCUMENT))
        user_statement_ranks = list(user_statement.values_list('rank_id', flat=True))
        user_statement_positions = list(
            chain.from_iterable(list(user_statement.values_list('list_positions', flat=True))))
        rank = Rank.objects.get(id=serializer.initial_data['rank'])
        list_positions = serializer.initial_data['list_positions']
        if rank.pk in user_statement_ranks and set(list_positions).issubset(
                set(user_statement_positions)):
            raise ValidationError('Statement with this rank/positions exists')
        number = serializer.initial_data.get('number')
        if number is None:
            number = StatementSQC.generate_number()
        is_continue = check_is_continue(sailor_qs=sailor_qs, rank_id=rank.pk, list_positions=list_positions)
        branch_office_id = 2
        status_document = self.get_create_status_document()
        is_cadet = False
        if sailor_qs.students_id and bool(is_continue) is False:
            is_cadet = check_cadet_student_ID(students_id=sailor_qs.students_id, rank_id=rank.pk)
        ser = serializer.save(number=number,
                              sailor=sailor_qs.id,
                              status_document_id=status_document,
                              is_continue=is_continue,
                              branch_office_id=branch_office_id,
                              is_cadet=is_cadet)
        sailor_qs.statement_dkk.append(ser.id)
        if not sailor_qs.agent_id:
            Rating.objects.create(sailor_key=sailor_qs.pk, rating=4)
        sailor_qs.save(update_fields=['statement_dkk'])
        save_history.s(user_id=self.request.user.id,
                       module='StatementDKK',
                       action_type='create',
                       content_obj=ser,
                       serializer=StatementDKKWithoutDocSer,
                       new_obj=ser,
                       sailor_key_id=sailor_qs.pk,
                       ).apply_async(serializer='pickle')

    @swagger_auto_schema(request_body=no_body)
    @action(methods=['patch'], detail=True, url_name='cancel_document')
    def cancel_document(self, request, *args, **kwargs):
        instance = self.get_object()
        old_instance = deepcopy(instance)
        if instance.status_document_id in (magic_numbers.status_state_qual_dkk_in_process,
                                           magic_numbers.status_state_qual_dkk_absense,
                                           magic_numbers.CREATED_FROM_PERSONAL_CABINET,
                                           magic_numbers.CREATED_FROM_MORRICHSERVICE):
            instance.status_document_id = magic_numbers.status_state_qual_dkk_canceled
            instance.save(update_fields=['status_document_id'])
            save_history.s(user_id=self.request.user.pk,
                           module='StatementDKK',
                           action_type='edit',
                           content_obj=instance,
                           serializer=StatementDKKWithoutDocSer,
                           new_obj=instance,
                           old_obj=old_instance,
                           get_sailor=True,
                           ).apply_async(serializer='pickle')
            return Response(self.serializer_class(instance).data)
        else:
            raise ValidationError('Cant cancel document in this status')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            if hasattr(self, 'detail_serializer_class'):
                return self.detail_serializer_class
        return super(BasePersonalStatementDKK, self).get_serializer_class()

    @action(detail=True, methods=['get'], url_name='sailor_statements_sqc')
    def sailor_statements_sqc(self, request, *args, **kwargs):
        """
        returns a list of statement sqc excluding canceled
        """
        queryset = self.get_queryset()
        try:
            sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        queryset = queryset.order_by('-id')
        queryset.update(sailor=sailor_qs.pk)
        if not queryset:
            queryset = []
        return Response(self.serializer_class(queryset, many=True).data)

    @action(detail=True, methods=['get'], url_name='success_sailor_statements_sqc')
    def success_sailor_statements_sqc(self, request, *args, **kwargs):
        """
        return a list of approved non-protocol_sqc statements
        """
        queryset = self.get_queryset()
        try:
            # if self.request.user.has_perm('sailor.get_full_statement_dkk'):
            queryset = queryset.filter(status_document_id=24, protocolsqc__isnull=True).order_by('-id')
            return Response(self.serializer_class(queryset, many=True).data)
        except TypeError:
            return Response([])


class BasePersonalStatementQualification(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                                         GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = StatementQualification.objects.all()
    serializer_class = PersonalStatementQualificationDocumentSerializer
    model = StatementQualification

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_PERSONAL_CABINET,
            magic_numbers.CREATED_FROM_MORRICHSERVICE
        )

    def perform_create(self, serializer):
        try:
            protocol_dkk_id = serializer.initial_data['protocol_dkk']
            protocol_dkk = ProtocolSQC.objects.get(id=protocol_dkk_id)
            rank = protocol_dkk.statement_dkk.rank
            list_positions = protocol_dkk.statement_dkk.list_positions
            list_positions_qs = Position.objects.filter(id__in=list_positions)
            if StatementQualification.objects.filter(protocol_dkk=protocol_dkk).exists():
                raise ValidationError('Qualification document with this statement exists')
        except (KeyError, ProtocolSQC.DoesNotExist):
            if serializer.initial_data.get('list_positions'):
                list_positions_qs = Position.objects.filter(id__in=serializer.initial_data.get('list_positions', []))
                list_positions = list(list_positions_qs.values_list('id', flat=True))
                rank = list_positions_qs.first().rank
            else:
                rank = Rank.objects.get(type_document_id=serializer.initial_data['type_document'])
                list_positions_qs = Position.objects.filter(rank_id=rank.id)
                list_positions = list(list_positions_qs.values_list('id', flat=True))
        if rank.is_dkk is True and serializer.initial_data.get('protocol_dkk') is None:
            raise ValidationError('Protocol dkk is null')
        try:
            sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        agent_sailor = AgentSailor.objects.filter(
            sailor_key=sailor_qs.pk
        ).exclude(
            agent__userprofile__type_user=UserProfile.MARAD
        )
        if agent_sailor.exists():
            positions_text = '\n-'.join(list(list_positions_qs.values_list('name_ukr', flat=True)))
            agent = agent_sailor.first().agent
            text_message = f'''Моряк {sailor_qs.pk} пытается подать заявку на ДПВ в кабинете моряка
Звание:
{rank.name_ukr}
Должности:
{positions_text}
ФИО агента:
[{agent.pk}]{agent.get_full_name()} 
'''

            tbot.send_message('-486413060', text_message)
            raise ValidationError('Can\'t create statement for qualification document')  # TODO Del when its need to do
        number = StatementQualification.generate_number()
        is_continue = check_is_continue(sailor_qs=sailor_qs, rank_id=rank.pk, list_positions=list_positions)
        if rank.type_document_id == 49 and (
                'type_document' in serializer.initial_data and serializer.initial_data['type_document']):
            type_document = serializer.initial_data['type_document']
        else:
            type_document = rank.type_document_id
        checking = CheckSailorForPositionDKK(sailor=sailor_qs.pk, is_continue=is_continue,
                                             list_position=list_positions)
        documents = checking.get_docs_with_status()
        have_all_docs = documents['have_all_doc']
        status_document = self.get_create_status_document()
        if have_all_docs and status_document == magic_numbers.CREATED_FROM_PERSONAL_CABINET:
            status_document = magic_numbers.status_state_qual_dkk_in_process
        ser = serializer.save(number=number,
                              status_document_id=status_document,
                              list_positions=list_positions,
                              is_continue=is_continue,
                              type_document_id=type_document,
                              rank=rank,
                              sailor=sailor_qs.id,
                              author_id=None)
        sailor_qs.statement_qualification.append(ser.id)
        sailor_qs.save(update_fields=['statement_qualification'])
        save_history.s(user_id=self.request.user.id,
                       module='StatementQualification',
                       action_type='create',
                       content_obj=ser,
                       serializer=StatementQualificationDocumentSerializer,
                       new_obj=ser,
                       sailor_key_id=sailor_qs.id,
                       ).apply_async(serializer='pickle')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            if hasattr(self, 'detail_serializer_class'):
                return self.detail_serializer_class
        return super(BasePersonalStatementQualification, self).get_serializer_class()

    @action(detail=False, methods=['get'])
    def sailor_statements_qual_doc(self, request, *args, **kwargs):
        """
        return a list of statements qualification documents
        """
        queryset = self.get_queryset()
        try:
            return Response(self.serializer_class(queryset.order_by('-id'), many=True).data)
        except TypeError:
            return Response([])

    @action(detail=False, methods=['get'], )
    def success_statements_qual_doc(self, request, *args, **kwargs):
        """
        return a list of approved statements non-qualification documents
        """
        queryset = self.get_queryset()
        try:
            # 24- статус "схвалено"
            queryset = queryset.filter(qualifcationdocument__isnull=True, status_document_id=24).order_by('-id')
            return Response(self.serializer_class(queryset, many=True).data)
        except TypeError:
            return Response([])

    @swagger_auto_schema(request_body=no_body)
    @action(methods=['patch'], detail=True, url_name='cancel_document')
    def cancel_document(self, request, *args, **kwargs):
        instance = self.get_object()
        old_instance = deepcopy(instance)
        if not instance.is_payed and instance.status_document_id in (magic_numbers.status_state_qual_dkk_in_process,
                                                                     magic_numbers.status_state_qual_dkk_absense,
                                                                     magic_numbers.CREATED_FROM_PERSONAL_CABINET,
                                                                     magic_numbers.CREATED_FROM_MORRICHSERVICE):
            instance.status_document_id = magic_numbers.status_state_qual_dkk_canceled
            instance.save(update_fields=['status_document_id'])
            save_history.s(user_id=self.request.user.pk,
                           module='StatementQualification',
                           action_type='edit',
                           content_obj=instance,
                           serializer=StatementQualificationDocumentSerializer,
                           new_obj=instance,
                           old_obj=old_instance,
                           get_sailor=True,
                           ).apply_async(serializer='pickle')
            return Response(self.serializer_class(instance).data)
        else:
            raise ValidationError('Cant cancel document in this status')


class GenerateMarkedImage(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        photo = get_object_or_404(PhotoProfile, photo=kwargs.get('name'))
        return add_watermark_response(photo.photo.name)


class GenerateQr(APIView):
    permission_classes = (IsAuthenticated,)

    def __greate_qr(self, obj):
        creation_date = tz.now().date()
        sailor_data = 'id={}&date={}'.format(
            str(obj.id),
            creation_date.isoformat()  # '2020-02-23'
        )
        key = base64.b64decode(settings.CRYPTO_KEY)
        fernet_alg = Fernet(key)
        # TODO: add URI!!!!
        sailor_data_enc = fernet_alg.encrypt(sailor_data.encode()).decode()
        qrc = qr.create('{}{}'.format(settings.QR_CHECKER_URL, sailor_data_enc))
        return qrc.png_as_base64_str(scale=10, module_color=(61, 76, 99, 255))
        # stream = BytesIO()
        # qrc.svg(stream, scale=8)
        # encoded_string = base64.b64encode(stream.getvalue()).decode('utf-8')
        # return encoded_string

    def get(self, request, *args, **kwargs):
        user = request.user.id
        sailor_qs = SailorKeys.objects.filter(user_id=user)
        if not sailor_qs.exists():
            raise ValidationError(sailor_not_exists_error)
        sailor_qs = sailor_qs.first()
        return Response({'qr': 'data:image/png;base64,{}'.format(self.__greate_qr(sailor_qs))})


class BaseCountDocsSailor(APIView):
    permission_classes = (IsAuthenticated,)
    """
    Count all docs for sailor
    """

    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_PERSONAL_CABINET,
            magic_numbers.CREATED_FROM_MORRICHSERVICE,
            magic_numbers.status_statement_canceled,
            magic_numbers.status_state_qual_dkk_canceled
        )

    def get(self, request):
        sailor = self.request.user.id
        try:
            keys = SailorKeys.objects.get(user_id=sailor)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        keys.save(force_update=True)
        response = {
            'passports': self.count_passports(keys),
            'education': self.count_education(keys),
            'education_student': self.count_cadet_education(keys),
            'ntz': self.count_ntz(keys),
            'dpo_documents': self.count_qualification_documents(keys),
            'service_record': self.count_service_record(keys),
            'eperience_doc': self.count_experience(keys),
            'sqc': self.count_documents_sqc(keys),
            'medical_sertificate': self.count_medical_documents(keys),
        }
        return Response(response)

    def count_passports(self, sailor_qs):
        sailor_passport_count = SailorPassport.objects.filter(id__in=sailor_qs.sailor_passport).exclude(
            status_document_id__in=self.get_exclude_status_document()
        ).count()
        return {'passport_sailor': sailor_passport_count, 'passport': 1, 'sum': sailor_passport_count + 1}

    def count_education(self, sailor_qs):
        document_about_education_count = Education.objects.filter(id__in=sailor_qs.education).exclude(
            status_document_id__in=self.get_exclude_status_document()
        ).count()
        return document_about_education_count

    def count_cadet_education(self, sailor_qs):
        document_about_education_count = StudentID.objects.filter(id__in=sailor_qs.students_id).exclude(
            status_document_id__in=self.get_exclude_status_document()
        ).count()
        return document_about_education_count

    def count_ntz(self, sailor_qs):
        certificate_eti_count = CertificateETI.objects.filter(id__in=sailor_qs.sertificate_ntz).exclude(
            Q(status_document_id__in=self.get_exclude_status_document()) | Q(ntz_number=-1)
        ).count()
        return certificate_eti_count

    def count_qualification_documents(self, sailor_qs):
        qualification_document = QualificationDocument.objects.filter(
            id__in=sailor_qs.qualification_documents
        ).exclude(status_document_id__in=self.get_exclude_status_document())
        qualification_document_qs = qualification_document.filter(type_document_id__in=[3, 49])
        proof_of_diplomas = ProofOfWorkDiploma.objects.filter(
            diploma__in=qualification_document_qs
        ).exclude(status_document_id__in=self.get_exclude_status_document()).count()
        qualification_document = qualification_document.count() + proof_of_diplomas
        statement_qualification = StatementQualification.objects.filter(
            id__in=sailor_qs.statement_qualification
        ).exclude(status_document_id__in=self.get_exclude_status_document()).count()
        return {'qual_doc': qualification_document, 'statement_qual_doc': statement_qualification}

    def count_service_record(self, sailor_qs):
        all_service_record = ServiceRecord.objects.filter(id__in=sailor_qs.service_records).exclude(
            status_document_id__in=self.get_exclude_status_document())
        line_in_service_record_count = LineInServiceRecord.objects.filter(
            service_record__in=all_service_record
        ).exclude(
            status_line_id__in=self.get_exclude_status_document()).count()
        statement_serv_rec_count = StatementServiceRecord.objects.filter(
            id__in=sailor_qs.statement_service_records
        ).exclude(status_id__in=self.get_exclude_status_document()).count()
        return {'num': all_service_record.count(), 'line_in_service_record': line_in_service_record_count,
                'statement_service_records': statement_serv_rec_count}

    def count_experience(self, sailor_qs):
        experience_doc_count = LineInServiceRecord.objects.filter(id__in=sailor_qs.experience_docs).exclude(
            status_line_id__in=self.get_exclude_status_document()).count()
        return experience_doc_count

    def count_documents_sqc(self, sailor_qs):
        statement_dkk_count = StatementSQC.objects.filter(id__in=sailor_qs.statement_dkk).exclude(
            status_document_id__in=self.get_exclude_status_document()).count()
        protocol_dkk_count = ProtocolSQC.objects.filter(id__in=sailor_qs.protocol_dkk).exclude(
            status_document_id__in=self.get_exclude_status_document()).count()
        return {'statement_sqc': statement_dkk_count, 'protocol_sqc': protocol_dkk_count,
                'sum': statement_dkk_count + protocol_dkk_count}

    def count_medical_documents(self, sailor_qs):
        medical_sertificate = MedicalCertificate.objects.filter(id__in=sailor_qs.medical_sertificate).exclude(
            status_document_id__in=self.get_exclude_status_document()).count()
        return medical_sertificate


class CheckDocumentsStatementDKKView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CheckDocumentParamsSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        try:
            sailor_qs = SailorKeys.objects.get(user_id=user.pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        rank_id = request.data.get('rank')
        list_positions = request.data.get('list_positions')
        if sailor_qs.qualification_documents is None:
            sailor_qs.qualification_documents = []
        is_continue = check_is_continue(sailor_qs, rank_id, list_positions)
        checking = CheckSailorForPositionDKK(sailor=sailor_qs.pk, is_continue=is_continue,
                                             list_position=list_positions, demand_position=True)
        documents = checking.get_docs_with_status()
        have_all_docs = False
        not_exists_document = documents.get('not_exists_docs', [])
        if not not_exists_document:
            have_all_docs = True
        serializer = CheckDocumentsStatementDKKSerializer(not_exists_document, many=True)
        exists_document = documents.get('exists_doc', [])
        return Response({'have_all_docs': have_all_docs, 'not_exists_docs': serializer.data,
                         'exists_docs': exists_document})


class BaseStatementServiceRecordSailor(mixins.CreateModelMixin,
                                       mixins.ListModelMixin, GenericViewSet):
    """
    Creating/receiving statements for service record book from personal cabinet
    """
    permission_classes = (IsAuthenticated,)
    queryset = StatementServiceRecord.objects.all()
    serializer_class = StatementServiceRecordSerializer
    model = StatementServiceRecord

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def perform_create(self, serializer):
        try:
            sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        if sailor_qs.statement_service_records and \
                StatementServiceRecord.objects.filter(
                    id__in=sailor_qs.statement_service_records,
                    is_payed=False).exclude(
                    status_id__in=[magic_numbers.status_statement_serv_rec_rejected]).exclude(status_id__in=(
                        magic_numbers.STATUS_REMOVED_DOCUMENT,
                        magic_numbers.STATUS_CREATED_BY_AGENT,
                        magic_numbers.CREATED_FROM_PERSONAL_CABINET,
                        magic_numbers.CREATED_FROM_MORRICHSERVICE,
                        magic_numbers.status_statement_canceled,
                        magic_numbers.status_state_qual_dkk_canceled
                )).exists():
            raise ValidationError('Statement exists')
        type_delivery = serializer.initial_data['type_delivery']
        status = self.get_create_status_document()
        if type_delivery == 'novaposhta':
            ct = ContentType.objects.get(model__iexact='NovaPoshtaDelivery')
            delivery_id = create_delivery_nova_poshta(serializer.initial_data)
            ser = serializer.save(content_type_id=ct.id, object_id=delivery_id, status_id=status, sailor=sailor_qs.pk)
        else:
            raise ValidationError('Unknown type delivery')
        if sailor_qs.statement_service_records:
            sailor_qs.statement_service_records.append(ser.id)
            sailor_qs.save(update_fields=['statement_service_records'])
        else:
            sailor_qs.statement_service_records = [ser.id]
            sailor_qs.save(update_fields=['statement_service_records'])
        save_history.s(user_id=self.request.user.id,
                       sailor_key_id=sailor_qs.pk,
                       module='StatementServiceRecord',
                       action_type='create',
                       content_obj=ser,
                       serializer=StatementServiceRecordSerializer,
                       new_obj=ser,
                       ).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        key = SailorKeys.objects.filter(statement_service_records__overlap=[instance.id]).first()
        if not key:
            raise ValidationError(sailor_not_exists_error)
        key.statement_service_records.remove(instance.id)
        key.save(update_fields=['statement_service_records'])
        _instance = deepcopy(instance)
        instance.delete()
        save_history.s(user_id=self.request.user.id,
                       module='StatementServiceRecord',
                       action_type='delete',
                       content_obj=_instance,
                       serializer=StatementServiceRecordSerializer,
                       old_obj=_instance,
                       sailor_key_id=key.id,
                       ).apply_async(serializer='pickle')

    @swagger_auto_schema(request_body=no_body)
    @action(methods=['patch'], detail=True, url_name='cancel_document')
    def cancel_document(self, request, *args, **kwargs):
        instance = self.get_object()
        old_instance = deepcopy(instance)
        if not instance.is_payed and instance.status_id in [magic_numbers.status_statement_serv_rec_in_process,
                                                            magic_numbers.CREATED_FROM_PERSONAL_CABINET,
                                                            magic_numbers.CREATED_FROM_MORRICHSERVICE]:
            instance.status_id = magic_numbers.status_state_qual_dkk_canceled
            instance.save(update_fields=['status_id'])
            save_history.s(user_id=self.request.user.pk,
                           module='StatementServiceRecord',
                           action_type='edit',
                           content_obj=instance,
                           serializer=StatementServiceRecordSerializer,
                           new_obj=instance,
                           old_obj=old_instance,
                           get_sailor=True,
                           ).apply_async(serializer='pickle')
            return Response(self.serializer_class(instance).data)
        else:
            raise ValidationError('Cant cancel document in this status')


class NoPayedStatement(APIView):
    """
    Unpaid statements from SQC and SR
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        sailor = self.request.user.id
        try:
            keys = SailorKeys.objects.get(user_id=sailor)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        total_cost_statement_sr = 0
        statement_dkk = []
        statement_service_record = []
        statement_qual = []
        if keys.statement_service_records:
            statement_sr = StatementServiceRecord.objects.filter(
                id__in=keys.statement_service_records, is_payed=False
            ).exclude(status_id__in=(magic_numbers.STATUS_REMOVED_DOCUMENT,))
            total_cost_statement_sr = float(statement_sr.count() * PRICE_SERVICE_RECORD)
            statement_service_record = [{'id': statement.id,
                                         'summ': float(PRICE_SERVICE_RECORD)} for statement in statement_sr]
        total_cost_statement_dkk = 0
        if keys.statement_dkk:
            filter_statement = StatementSQC.objects.filter(
                id__in=keys.statement_dkk, is_payed=False,
                status_document_id=magic_numbers.status_state_qual_dkk_in_process)
            total_cost_statement_dkk = sum(list(filter_statement.values_list('rank__price', flat=True)))
            statement_dkk = [{'id': statement.id, 'number': statement.get_number, 'summ': statement.rank.price,
                              'date_create': statement.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                             for statement in filter_statement]
        total_cost_statement_qual = 0
        if keys.statement_qualification:
            filter_statement = StatementQualification.objects.filter(
                id__in=keys.statement_qualification, is_payed=False,
                status_document_id__in=[magic_numbers.status_state_qual_dkk_in_process,
                                        magic_numbers.status_state_qual_dkk_absense,
                                        magic_numbers.CREATED_FROM_PERSONAL_CABINET])
            total_cost_statement_qual = sum(list(filter_statement.values_list('type_document__price', flat=True)))
            statement_qual = [
                {'id': statement.id, 'number': statement.get_number, 'summ': statement.type_document.price}
                for statement in filter_statement]

        return Response({'total_statement_dkk': float(total_cost_statement_dkk), 'statement_dkk': statement_dkk,
                         'total_statement_service_record': total_cost_statement_sr,
                         'statement_service_record': statement_service_record,
                         'total_statement_qual_doc': total_cost_statement_qual, 'statement_qual_doc': statement_qual})


class BaseStudentIDPerSailor(PhotoUploadMixin, mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    """
    Cadet's student ID
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalStudentsIDSerializer
    model = StudentID

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def perform_create(self, serializer):
        sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        status_document = self.get_create_status_document()
        ser = serializer.save(status_document_id=status_document, sailor=sailor_qs.pk)
        sailor_qs.students_id.append(ser.id)
        sailor_qs.save(update_fields=['students_id'])
        save_history.s(user_id=self.request.user.id,
                       module='StudentID',
                       action_type='create',
                       content_obj=ser,
                       new_obj=ser,
                       serializer=PersonalStudentsIDSerializer,
                       sailor_key_id=sailor_qs.pk,
                       ).apply_async(serializer='pickle')


class BaseDataProcessingView(generics.RetrieveAPIView, generics.CreateAPIView, GenericViewSet):
    queryset = PersonalDataProcessing.objects.all()
    serializer_class = PersonalDataProcessingSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            sailor_key = SailorKeys.objects.get(user_id=self.request.user.pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        return PersonalDataProcessing.objects.get(sailor=sailor_key.pk)

    def perform_create(self, serializer):
        try:
            sailor_key = SailorKeys.objects.get(user_id=self.request.user.pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        serializer.save(sailor=sailor_key.pk)


class ChangeMainPhoneView(APIView):
    """
    The sailor's financial phone number, which is used to enter the PC through the mobile application
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ChangeMainPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.data['phone_number']
        security_code = serializer.data['security_code']
        user = self.request.user
        if user.username.startswith('+'):
            raise ValidationError({'description': 'Username is valid', 'status': 'error'})
        if phone_number.startswith('+') is False:
            phone_number = '+' + phone_number
        phone_check = User.objects.filter(username=phone_number)
        if phone_check.exists():
            raise ValidationError({'description': 'User exists', 'status': 'error'})
        try:
            sailor_qs = SailorKeys.objects.get(user_id=user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError({'description': sailor_not_exists_error, 'status': 'error'})
        try:
            current_user = User.objects.get(id=sailor_qs.user_id)
        except User.DoesNotExist:
            raise ValidationError({'description': 'User does not exists', 'status': 'error'})
        if security_code:
            try:
                sailor_enter = SecurityCode.objects.get(phone=phone_number)
                time_end_security_code = datetime.now(timezone.utc) - relativedelta(minutes=CODE_EXPIRATION_TIME)
                if sailor_enter.created_at < time_end_security_code:
                    sailor_enter.delete()
                    raise ValidationError({'description': 'Code is invalid', 'status': 'error'})
                if sailor_enter.security_code == security_code:
                    sailor_enter.delete()
                    old_current_user = deepcopy(current_user)
                    current_user.username = phone_number
                    current_user.save(update_fields=['username'])
                    added_phone_to_profile.s(profile_id=sailor_qs.profile, phone_number=phone_number,
                                             sailor_id=sailor_qs.pk, user_id=user.id).apply_async()
                    save_history.s(user_id=user.id, module='User', action_type='edit', content_obj=current_user,
                                   serializer=UserSerializer, new_obj=current_user, sailor_key_id=sailor_qs.pk,
                                   old_obj=old_current_user).apply_async(serializer='pickle')
                    return Response({'description': 'Username changed', 'status': 'success'})
                else:
                    raise ValidationError({'description': 'Code is invalid', 'status': 'error'})
            except SecurityCode.DoesNotExist:
                raise ValidationError({'description': 'Code is invalid', 'status': 'error'})
        else:
            new_security_code = create_sms_code(phone_number=phone_number)
            text = f'{new_security_code} - код для підтвердження збереження номера'
            send_message(phone_number, text)
            return Response({'status': 'Message send'})


class BaseStatementSailorPassport(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    Creating/receiving statements for sailor passport from personal cabinet
    """
    permission_classes = (IsAuthenticated,)
    queryset = StatementSailorPassport.objects.all()
    serializer_class = StatementSailorPassportSerializer

    def get_create_status_document(self):
        return magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def perform_create(self, serializer):
        try:
            sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        if self.get_queryset().filter(status_document_id__in=(magic_numbers.status_statement_sailor_passport_in_process,
                                                              magic_numbers.CREATED_FROM_PERSONAL_CABINET,
                                                              magic_numbers.CREATED_FROM_MORRICHSERVICE)).exists():
            raise ValidationError('Statement exists')
        number = StatementSailorPassport.generate_number()
        status_document = self.get_create_status_document()
        is_continue = False
        sailor_passport_id = None
        if sailor_qs.sailor_passport:
            sailor_passport = SailorPassport.objects.filter(id__in=sailor_qs.sailor_passport,
                                                            status_document_id=magic_numbers.status_service_record_valid,
                                                            date_renewal__isnull=True)
            if sailor_passport.exists():
                is_continue = True
                sailor_passport_id = sailor_passport.first().id
        ser = serializer.save(number=number,
                              status_document_id=status_document,
                              is_continue=is_continue,
                              sailor_passport_id=sailor_passport_id,
                              sailor=sailor_qs.pk)
        sailor_qs.statement_sailor_passport.append(ser.id)
        sailor_qs.save(update_fields=['statement_sailor_passport'])
        save_history.s(user_id=self.request.user.id,
                       module='StatementSailorPassport',
                       action_type='create',
                       content_obj=ser,
                       serializer=StatementSailorPassportSerializer,
                       new_obj=ser,
                       get_sailor=True,
                       ).apply_async(serializer='pickle')


class LineInServiceRecordsView(PhotoUploadMixin,
                               mixins.CreateModelMixin, GenericViewSet):
    """
    Adding line in service record book
    """
    permission_classes = (IsAuthenticated,)
    queryset = LineInServiceRecord.objects.all()
    serializer_class = PersonalLineInServiceRecordSerializer

    def perform_create(self, serializer):
        sailor_qs = SailorKeys.objects.get(user_id=self.request.user.id)
        status_line = magic_numbers.CREATED_FROM_PERSONAL_CABINET
        allow_write = [magic_numbers.status_service_record_valid, magic_numbers.VERIFICATION_STATUS,
                       magic_numbers.CREATED_FROM_PERSONAL_CABINET]
        if serializer.validated_data['service_record'].status_document_id not in allow_write:
            raise ValidationError('Status service record is not valid')
        all_function = serializer.validated_data.pop('service_record_line', None)
        all_function = check_all_function(all_function)
        date_start = serializer.validated_data['date_start']
        date_end = serializer.validated_data['date_end']
        if serializer.validated_data.get('is_repaired'):
            days_repair = serializer.validated_data.get('days_repair', 0)
            repair_date_from = serializer.validated_data.get('repair_date_from')
            repair_date_to = serializer.validated_data.get('repair_date_to')
        else:
            days_repair = 0
            repair_date_from = None
            repair_date_to = None
        if (repair_date_from and repair_date_to and (
                not (date_start <= repair_date_from <= date_end) or not (date_start <= repair_date_to <= date_end))):
            # период ремонта не входит в рейс
            raise ValidationError('wrong date intervals')
        date_intervals = check_interval_date(all_function=all_function, date_start=date_start, date_end=date_end,
                                             days_repair=days_repair,
                                             repair_date_from=serializer.validated_data.get('repair_date_from'),
                                             repair_date_to=serializer.validated_data.get('repair_date_to'))
        if all_function:
            all_function += date_intervals
        ser = serializer.save(date_write=date.today(), status_line_id=status_line)
        if all_function:
            all_function = get_is_repair(repair_date_from, repair_date_to, all_function)
            list_responsibility = [ResponsibilityServiceRecord(
                service_record_line_id=ser.id, responsibility=function.get('responsibility'),
                date_from=function.get('date_from'), date_to=function.get('date_to'),
                days_work=function.get('days_work'), is_repaired=function.get('is_repaired', False))
                for function in all_function]
            ResponsibilityServiceRecord.objects.bulk_create(list_responsibility)
        save_history.s(user_id=self.request.user.id,
                       module='LineInServiceRecord',
                       action_type='create',
                       content_obj=ser,
                       serializer=PersonalLineInServiceRecordSerializer,
                       sailor_key_id=sailor_qs.pk,
                       new_obj=ser,
                       ).apply_async(serializer='pickle')


class PowerOfAttorney(APIView):
    permission_class = (IsAuthenticated,)

    def get(self, request):
        return Response(render_to_string('personal_cabinet/power_of_attorney.html'))
