from copy import deepcopy
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q, QuerySet
from django.http import Http404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import sailor.document
import sailor.document.permissions
import sailor.document.serializers
import sailor.misc
import sailor.permissions
import sailor.tasks
from back_office.models import DependencyItem
from back_office.tasks import update_eti_in_packet, update_protocol_in_packet
from communication.models import SailorKeys
from directory.models import Port, Position
from itcs import magic_numbers
from mixins.core import FullSailorViewSet, ObjectFromQuerySetMixin
from sailor.document.models import (CertificateETI, Education, LineInServiceRecord, MedicalCertificate,
                                    ProofOfWorkDiploma, ProtocolSQC, QualificationDocument,
                                    ResponsibilityServiceRecord, ServiceRecord)
from sailor.models import Rating
from sailor.statement.models import StatementSQC, StatementQualification, StatementETI
from sailor.views import sailor_not_exists_error
from user_profile.models import UserProfile


class ServiceRecordSailorView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        (sailor.document.permissions.ServiceRecordSailorPermission |
         sailor.permissions.PostVerificationChangeStatusPermission),
    )
    queryset = ServiceRecord.objects.all()
    serializer_class = sailor.document.serializers.ServiceRecordSailorSerializer
    model = ServiceRecord
    select_related = ('status_document', 'branch_office', 'author')
    prefetch_related = ('verification_status',)

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except (SailorKeys.DoesNotExist, ValueError):
            raise Http404
        split_fio_ukr = serializer.initial_data['auth_agent_ukr'].split(' ')
        auth_agent_ukr = split_fio_ukr[1][:1] + '. ' + split_fio_ukr[0]
        split_fio_eng = serializer.initial_data['auth_agent_eng'].split(' ')
        auth_agent_eng = split_fio_eng[1][:1] + '. ' + split_fio_eng[0]
        ser = serializer.save(auth_agent_ukr=auth_agent_ukr, auth_agent_eng=auth_agent_eng,
                              author=self.request.user)
        if ser.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(ser)
        sailor_qs.service_records.append(ser.id)
        sailor_qs.save(update_fields=['service_records'])
        sailor.tasks.save_history.s(user_id=self.request.user.id, sailor_key_id=sailor_id,
                                    module='ServiceRecord', action_type='create',
                                    content_obj=ser,
                                    serializer=sailor.document.serializers.ServiceRecordSailorSerializer,
                                    new_obj=ser).apply_async(serializer='pickle')

    def get_queryset(self):
        qs = super().get_queryset()
        userprofile = self.request.user.userprofile
        if userprofile.type_user in [userprofile.DPD]:
            return qs.filter(status_document_id__in=[magic_numbers.status_qual_doc_valid,
                                                     magic_numbers.VERIFICATION_STATUS])
        if userprofile.type_user in [userprofile.VERIFIER, userprofile.SECRETARY_SQC, userprofile.DPD,
                                     userprofile.MEDICAL, userprofile.MARAD]:
            qs = qs.exclude(status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT])
        return qs

    def destroy(self, request, *args, **kwargs):
        instance: ServiceRecord = self.get_object()
        _instance = deepcopy(instance)
        user = self.request.user
        if instance.status_document_id != magic_numbers.STATUS_REMOVED_DOCUMENT:
            instance.status_document_id = magic_numbers.STATUS_REMOVED_DOCUMENT
            instance.save(update_fields=['status_document'])
            history_args = {'action_type': 'edit', 'new_obj': instance}
            for line in instance.lines.all():
                if line.status_line == magic_numbers.STATUS_REMOVED_DOCUMENT:
                    continue
                old_line = deepcopy(line)
                line.status_line_id = magic_numbers.STATUS_REMOVED_DOCUMENT
                line.save(update_fields=['status_line'])
                sailor.tasks.save_history.s(user_id=user.id,
                                            get_sailor=True,
                                            module='LineInServiceRecord',
                                            content_obj=line,
                                            serializer=sailor.document.serializers.LineInServiceRecordSerializer,
                                            old_obj=old_line,
                                            new_obj=line,
                                            action_type='edit'
                                            ).apply_async(serializer='pickle')
        else:
            instance.delete()
            history_args = {'action_type': 'delete'}
        sailor.tasks.save_history.s(user_id=user.id,
                                    get_sailor=True,
                                    module='ServiceRecord',
                                    content_obj=_instance,
                                    serializer=sailor.document.serializers.ServiceRecordSailorSerializer,
                                    old_obj=_instance,
                                    **history_args,
                                    ).apply_async(serializer='pickle')
        if getattr(instance, 'pk', None):
            return Response(self.serializer_class(instance).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LineInServiceRecordView(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin, mixins.ListModelMixin, ObjectFromQuerySetMixin):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        (sailor.document.permissions.LineInServiceRecordPermission |
         sailor.permissions.PostVerificationChangeStatusPermission)
    )
    queryset = LineInServiceRecord.objects.select_related(
        'type_vessel', 'mode_of_navigation', 'type_geu', 'position', 'status_line',
    ).all()
    serializer_class = sailor.document.serializers.LineInServiceRecordSerializer

    def get_object(self):
        if self.request.version == 'v2':
            self.queryset = self.get_queryset()
        return super(LineInServiceRecordView, self).get_object()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LineInServiceRecord.objects.none()
        if self.request.version == 'v1':
            kwargs_param = 'pk'
        else:
            kwargs_param = 'service_record_pk'
        try:
            service_record = self.kwargs[kwargs_param]
        except KeyError:
            raise ValidationError('ServiceRecord empty')
        qs: QuerySet[LineInServiceRecordView] = self.queryset.filter(
            service_record_id=service_record).order_by('-id')
        userprofile: UserProfile = self.request.user.userprofile
        if userprofile.type_user in [userprofile.DPD, userprofile.MEDICAL]:
            return qs.filter(status_line_id__in=[9, magic_numbers.VERIFICATION_STATUS])
        elif userprofile.type_user in [userprofile.VERIFIER, userprofile.SECRETARY_SQC, userprofile.DPD,
                                       userprofile.MARAD]:
            qs = qs.exclude(status_line_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT,
                                                magic_numbers.STATUS_REMOVED_DOCUMENT])
        elif userprofile.type_user in [UserProfile.BACK_OFFICE] or self.request.user.is_superuser:
            return qs
        return qs.exclude(status_line_id=magic_numbers.STATUS_REMOVED_DOCUMENT)

    def perform_create(self, serializer):
        allow_write = [magic_numbers.status_service_record_valid, magic_numbers.VERIFICATION_STATUS,
                       magic_numbers.STATUS_CREATED_BY_AGENT]
        if serializer.validated_data['service_record'].status_document_id not in allow_write:
            raise ValidationError('Status service record is not valid')
        all_function = serializer.validated_data.pop('service_record_line', None)
        all_function = sailor.misc.check_all_function(all_function)
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
        date_intervals = sailor.misc.check_interval_date(
            all_function=all_function,
            date_start=date_start,
            date_end=date_end,
            days_repair=days_repair,
            repair_date_from=serializer.validated_data.get('repair_date_from'),
            repair_date_to=serializer.validated_data.get('repair_date_to'))
        if all_function:
            all_function += date_intervals
        status_line = self.request.user.userprofile.verification_status_by_user
        ser = serializer.save(date_write=date.today(), status_line_id=status_line, author=self.request.user)
        if all_function:
            all_function = sailor.misc.get_is_repair(repair_date_from, repair_date_to, all_function)
            list_responsibility = [ResponsibilityServiceRecord(
                service_record_line_id=ser.id, responsibility=function.get('responsibility'),
                date_from=function.get('date_from'), date_to=function.get('date_to'),
                days_work=function.get('days_work'), is_repaired=function.get('is_repaired', False))
                for function in all_function]
            ResponsibilityServiceRecord.objects.bulk_create(list_responsibility)
        if ser.status_line.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(ser)
        sailor.tasks.save_history.s(user_id=self.request.user.id,
                                    get_sailor=True,
                                    module='LineInServiceRecord',
                                    action_type='create',
                                    content_obj=ser,
                                    serializer=sailor.document.serializers.LineInServiceRecordSerializer,
                                    new_obj=ser,
                                    ).apply_async(serializer='pickle')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        _instance = deepcopy(instance)
        user = self.request.user
        if instance.status_line.id != magic_numbers.STATUS_REMOVED_DOCUMENT:
            instance.status_line_id = magic_numbers.STATUS_REMOVED_DOCUMENT
            instance.save(update_fields=['status_line'])
            history_args = {'action_type': 'edit', 'new_obj': instance}
        else:
            ResponsibilityServiceRecord.objects.filter(service_record_line_id=instance.id).delete()
            instance.delete()
            history_args = {'action_type': 'delete'}
        sailor.tasks.save_history.s(user_id=user.id,
                                    get_sailor=True,
                                    module='LineInServiceRecord',
                                    content_obj=_instance,
                                    serializer=sailor.document.serializers.LineInServiceRecordSerializer,
                                    old_obj=_instance,
                                    **history_args,
                                    ).apply_async(serializer='pickle')
        if getattr(instance, 'pk', None):
            return Response(self.serializer_class(instance).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExperienceDocumentView(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin, mixins.ListModelMixin, ObjectFromQuerySetMixin):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        (sailor.document.permissions.ExperiencePermission |
         sailor.document.permissions.ExperienceNotConventionalPermission |
         sailor.permissions.PostVerificationChangeStatusPermission)
    )
    queryset = LineInServiceRecord.objects.select_related(
        'type_vessel', 'mode_of_navigation', 'type_geu', 'position', 'status_line',
    ).filter(service_record=None)
    serializer_class = sailor.document.serializers.ExperienceDocumentSerializer

    def get_object(self):
        if self.request.version == 'v2':
            self.queryset = self.get_queryset()
        return super(ExperienceDocumentView, self).get_object()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LineInServiceRecord.objects.none()
        if self.request.version == 'v1':
            kwargs_param = 'pk'
        else:
            kwargs_param = 'sailor_pk'
        try:
            sailor_id = self.kwargs[kwargs_param]
            keys = SailorKeys.objects.get(id=sailor_id)
        except (SailorKeys.DoesNotExist, KeyError):
            raise ValidationError('Sailor does not exists')
        exp_ids = keys.experience_docs
        qs = LineInServiceRecord.objects.filter(id__in=exp_ids).order_by('-id')
        userprofile: UserProfile = self.request.user.userprofile
        if userprofile.type_user in [userprofile.DPD]:
            return qs.filter(status_line_id__in=[9, magic_numbers.VERIFICATION_STATUS])
        elif userprofile.type_user in [userprofile.VERIFIER, userprofile.SECRETARY_SQC, userprofile.DPD,
                                       userprofile.MARAD]:
            qs = qs.exclude(status_line_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT,
                                                magic_numbers.STATUS_REMOVED_DOCUMENT])
        elif userprofile.type_user in [UserProfile.BACK_OFFICE] or self.request.user.is_superuser:
            return qs
        return qs.exclude(status_line_id=magic_numbers.STATUS_REMOVED_DOCUMENT)

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        if (serializer.initial_data.get('date_start') or serializer.initial_data.get('date_end')) and \
                serializer.initial_data.get('days_work'):
            raise ValidationError('Must be only interval or days')
        all_function = serializer.validated_data.pop('service_record_line', None)
        all_function = sailor.misc.check_all_function(all_function)
        date_start = serializer.validated_data['date_start']
        date_end = serializer.validated_data['date_end']
        days_repair = serializer.validated_data.get('days_repair', 0)
        repair_date_from = serializer.validated_data.get('repair_date_from')
        repair_date_to = serializer.validated_data.get('repair_date_to')
        if (repair_date_from and repair_date_to and
                (not (date_start <= repair_date_from <= date_end) or not (date_start <= repair_date_to <= date_end))):
            # период ремонта не входит в рейс
            raise ValidationError('wrong date intervals')
        if (serializer.validated_data['record_type'] !=
                'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'):
            # промежутки времени, которые моряк работал, не выполняя никаких обязанностей
            date_intervals = sailor.misc.check_interval_date(
                all_function=all_function, date_start=date_start,
                date_end=date_end, days_repair=days_repair,
                repair_date_from=repair_date_from, repair_date_to=repair_date_to)
            if all_function:
                all_function += date_intervals
        status_document_id = self.request.user.userprofile.verification_status_by_user
        ser = serializer.save(date_write=date.today(), status_line_id=status_document_id,
                              author=self.request.user)
        if all_function:
            all_function = sailor.misc.get_is_repair(repair_date_from, repair_date_to, all_function)
            list_responsibility = [ResponsibilityServiceRecord(
                service_record_line_id=ser.id, responsibility=function.get('responsibility'),
                date_from=function.get('date_from'), date_to=function.get('date_to'),
                days_work=function.get('days_work'), is_repaired=function.get('is_repaired', False))
                for function in all_function]
            ResponsibilityServiceRecord.objects.bulk_create(list_responsibility)
        sailor_qs.experience_docs.append(ser.id)
        sailor_qs.save(update_fields=['experience_docs'])
        if ser.status_line.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(ser)
        sailor.tasks.save_history.s(user_id=self.request.user.id, module='ExperienceDoc', action_type='create',
                                    content_obj=ser,
                                    serializer=sailor.document.serializers.ExperienceDocumentSerializer,
                                    new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        key = SailorKeys.objects.filter(experience_docs__overlap=[instance.id]).first()
        if not key:
            raise ValidationError(sailor_not_exists_error)
        _instance = deepcopy(instance)
        if instance.status_line.id != magic_numbers.STATUS_REMOVED_DOCUMENT:
            instance.status_line_id = magic_numbers.STATUS_REMOVED_DOCUMENT
            instance.save(update_fields=['status_line'])
            history_args = {'action_type': 'edit', 'new_obj': instance}
        else:
            ResponsibilityServiceRecord.objects.filter(service_record_line_id=instance.id).delete()
            key.experience_docs.remove(instance.id)
            key.save(update_fields=['experience_docs'])
            instance.delete()
            history_args = {'action_type': 'delete'}
        sailor.tasks.save_history.s(user_id=self.request.user.id,
                                    sailor_key_id=key.id,
                                    module='ExperienceDoc',
                                    content_obj=_instance,
                                    serializer=sailor.document.serializers.ExperienceDocumentSerializer,
                                    old_obj=_instance,
                                    **history_args,
                                    ).apply_async(serializer='pickle')
        if getattr(instance, 'pk', None):
            return Response(self.serializer_class(instance).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EducationView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        (sailor.document.permissions.GraduationDocumentPermission |
         sailor.permissions.PostVerificationChangeStatusPermission))
    queryset = Education.objects.all()
    serializer_class = sailor.document.serializers.EducationSerializer
    model = Education
    basename = 'education'
    select_related = ('status_document', 'type_document', 'extent', 'name_nz', 'qualification',
                      'speciality', 'specialization', 'statement_advanced_training',)

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        expired_date = serializer.initial_data.get('experied_date')
        if serializer.initial_data.get('type_document') == 3:
            expired_date = datetime.strptime(serializer.initial_data.get('date_issue_document'),
                                             '%Y-%m-%d').date() + relativedelta(years=5)
        status_document = self.request.user.userprofile.verification_status_by_user
        ser = serializer.save(status_document_id=status_document, expired_date=expired_date,
                              author=self.request.user)
        if sailor_qs.education:
            sailor_qs.education.append(ser.id)
            sailor_qs.save(update_fields=['education'])
        else:
            sailor_qs.education = [ser.id]
            sailor_qs.save(update_fields=['education'])
        if ser.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(ser)
        sailor.tasks.save_history.s(user_id=self.request.user.id, module='Education', action_type='create',
                                    content_obj=ser, serializer=sailor.document.serializers.EducationSerializer,
                                    new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')

    def get_queryset(self):
        qs: QuerySet[Education] = super().get_queryset()
        userprofile: UserProfile = self.request.user.userprofile
        if userprofile.type_user in [userprofile.VERIFIER, userprofile.SECRETARY_SQC, userprofile.DPD,
                                     userprofile.MEDICAL, userprofile.MARAD, userprofile.ETI_EMPLOYEE,
                                     userprofile.SECRETARY_ATC]:
            qs = qs.exclude(status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT)
        return qs


class ProtocolSQCView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        sailor.document.permissions.ProtocolSQCPermission,
    )
    queryset = ProtocolSQC.objects.all()
    serializer_class = sailor.document.serializers.ProtocolDKKSerializer
    special_serializer_class = sailor.document.serializers.ProtocolDKKWithPositionSerializer
    model = ProtocolSQC
    DEFAULT_VERSION = 'v1'
    select_related = ('branch_create', 'status_document', 'decision')
    prefetch_related = ('related_docs',)

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        statement_dkk = StatementSQC.objects.get(id=serializer.initial_data['statement_dkk'])
        is_printable = True
        if statement_dkk.is_cadet and statement_dkk.status_document_id == magic_numbers.status_cadets_state_dkk_allowed:
            is_printable = False
        has_four_stars = Rating.objects.filter(sailor_key=sailor_id, rating=4).exists()
        if has_four_stars and serializer.validated_data.get('decision').pk == magic_numbers.decision_allow:
            raise ValidationError('You cant create this protocol')
        direction_id = statement_dkk.rank.direction_id
        author = self.request.user
        author_branch = author.userprofile.branch_office_id
        number = sailor.misc.generate_number_for_protocol_dkk(direction_id=direction_id, branch_id=author_branch)
        function_limitation = {}
        if ProtocolSQC.objects.filter(statement_dkk_id=serializer.initial_data['statement_dkk']).exists():
            raise ValidationError('Qualification document with this statement exists')
        if statement_dkk.is_continue == 1:
            diploma = QualificationDocument.objects.prefetch_related('proofofworkdiploma_set') \
                .filter(rank=statement_dkk.rank,
                        list_positions=statement_dkk.list_positions) \
                .latest('date_start')
            if diploma.type_document_id != 49:
                function_limitation = diploma.function_limitation
            else:
                function_limitation = diploma.proofofworkdiploma_set.latest('date_start').function_limitation
        date_meeting = datetime.strptime(serializer.initial_data['date_meeting'], '%Y-%m-%d')
        date_end = (date_meeting + relativedelta(years=1)).strftime('%Y-%m-%d')
        ser = serializer.save(branch_create_id=author.userprofile.branch_office_id, author=author,
                              number_document=number, status_document_id=29, _sailor=sailor_id, date_end=date_end,
                              is_printeble=is_printable, function_limitation=function_limitation)
        if ser.statement_dkk.related_docs.exists():
            ser.related_docs = list(ser.statement_dkk.related_docs.all())
        else:
            docs_set = ser.statement_dkk.get_status_position
        if sailor_qs.protocol_dkk:
            sailor_qs.protocol_dkk.append(ser.id)
            sailor_qs.save(update_fields=['protocol_dkk'])
        else:
            sailor_qs.protocol_dkk = [ser.id]
            sailor_qs.save(update_fields=['protocol_dkk'])
        sailor.tasks.save_history.s(user_id=self.request.user.id, module='ProtocolDKK', action_type='create',
                                    content_obj=ser, serializer=sailor.document.serializers.ProtocolDKKSerializer,
                                    new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')
        if ser.decision_id == magic_numbers.decision_allow:
            update_protocol_in_packet.delay(ser.pk, sailor_id)

    def perform_destroy(self, instance):
        if hasattr(instance, 'statementqualification'):
            raise ValidationError('This protocol has a statement qual doc')
        return super(ProtocolSQCView, self).perform_destroy(instance=instance)

    @action(detail=False, methods=['get'])
    def success(self, request, sailor_pk, *args, **kwargs):
        try:
            keys = SailorKeys.objects.get(id=sailor_pk)
        except (SailorKeys.DoesNotExist, KeyError):
            raise ValidationError(sailor_not_exists_error)
        queryset = self.get_queryset()
        quals_docs = QualificationDocument.objects.filter(id__in=keys.qualification_documents)
        proofs_docs = ProofOfWorkDiploma.objects.filter(diploma__in=quals_docs)
        exclude_list = []
        protocols = queryset.filter(
            Q(statementqualification__isnull=True)
            & Q(status_document_id=magic_numbers.status_protocol_dkk_valid)
            & Q(decision_id=magic_numbers.decision_allow) & Q(is_printeble=True)).order_by('-id')
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
        return Response(self.special_serializer_class(protocols, many=True).data)


class CertificateETIView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        sailor.document.permissions.CertificatesStatusPermission,
    )
    queryset = CertificateETI.objects.all()
    serializer_class = sailor.document.serializers.CertificateNTZSerializer
    model = CertificateETI
    select_related = ('ntz', 'course_training', 'status_document',)
    prefetch_related = ('items',)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(ntz_number=-1)

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        statement: StatementETI = serializer.validated_data.get('statement')
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        if statement:
            statement.status_document_id = StatementETI.StatusDocument.CERTIFICATE_CREATED
            statement.save(update_fields=['status_document'])
        ser = serializer.save(is_red=serializer.validated_data.get('ntz').is_red)
        sailor_qs.sertificate_ntz.append(ser.id)
        sailor_qs.save(update_fields=['sertificate_ntz'])
        sailor.tasks.save_history.s(user_id=self.request.user.id, module='CertificateNTZ', action_type='create',
                                    content_obj=ser, serializer=sailor.document.serializers.CertificateNTZSerializer,
                                    new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')
        if ser.status_document_id in magic_numbers.ALL_VALID_STATUSES:
            update_eti_in_packet.delay(ser.pk, sailor_id)


class MedicalCertificateView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        (sailor.document.permissions.MedicalCertificatePermission |
         sailor.permissions.PostVerificationChangeStatusPermission)
    )
    queryset = MedicalCertificate.objects.all()
    serializer_class = sailor.document.serializers.MedicalCertificateSerializer
    model = MedicalCertificate
    select_related = ('position', 'limitation', 'doctor', 'status_document', 'medical_statement')

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=int(sailor_id))
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        status_document_id = self.request.user.userprofile.verification_status_by_user
        doctor = serializer.validated_data.get('doctor')
        if self.request.user.userprofile.type_user == self.request.user.userprofile.MEDICAL:
            doctor = self.request.user.userprofile.doctor_info
        ser = serializer.save(status_document_id=status_document_id, author=self.request.user, doctor=doctor)
        if ser.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(ser)
        sailor_qs.medical_sertificate.append(ser.id)
        sailor_qs.save(update_fields=['medical_sertificate'])
        sailor.tasks.save_history.s(user_id=self.request.user.id, module='MedicalCertificate', action_type='create',
                                    content_obj=ser,
                                    serializer=sailor.document.serializers.MedicalCertificateSerializer,
                                    new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')

    def get_queryset(self):
        qs: QuerySet[MedicalCertificate] = super().get_queryset()
        up: UserProfile = self.request.user.userprofile
        if up.type_user in [up.MEDICAL]:
            return qs.filter(status_document_id=magic_numbers.status_qual_doc_valid)
        elif up.type_user in [up.VERIFIER, up.SECRETARY_SQC, up.MARAD, up.ETI_EMPLOYEE]:
            qs = qs.exclude(status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT)
        return qs


class QualificationDocumentView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        (sailor.document.permissions.QualificationStatusPermission |
         sailor.permissions.PostVerificationChangeStatusPermission)
    )
    queryset = QualificationDocument.objects.all()
    serializer_class = sailor.document.serializers.QualificationDocumentSerializer
    model = QualificationDocument
    select_related = ('country', 'rank', 'type_document', 'status_document', 'statement', 'port')
    prefetch_related = ('related_docs', 'verification_status', 'items')

    def raise_on_early_non_agent_statement(self, statement: StatementQualification):
        today = date.today()
        created_at = statement.created_at
        td = today - created_at.date()
        if not statement.items.exists() and td.days < 13 and not self.request.user.is_superuser:
            raise ValidationError('Early for create this qualification document')

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        new_document = serializer.initial_data.get('new_document')
        date_end = serializer.initial_data.get('date_end', None)
        function_limitation = serializer.initial_data.get('function_limitation')
        if new_document:
            statement_instance = serializer.validated_data.get('statement')
            date_start = date.today()
            if (QualificationDocument.objects.filter(statement=statement_instance
                                                     ).exclude(status_document_id=17).exists() or
                    ProofOfWorkDiploma.objects.filter(statement=statement_instance
                                                      ).exclude(status_document_id=17).exists()):
                raise ValidationError('Qualification document with this statement exists')
            self.raise_on_early_non_agent_statement(statement=statement_instance)
            if statement_instance.is_continue == 1:
                previous_document = QualificationDocument.objects.filter(rank=statement_instance.rank,
                                                                         list_positions=statement_instance.list_positions)
                function_limitation = previous_document.latest('date_start').function_limitation \
                                                                        if previous_document.exists() else None
            list_positions = statement_instance.list_positions
            type_document = statement_instance.type_document_id
            if type_document == 21:
                certificate_ntz = CertificateETI.objects.filter(id__in=sailor_qs.sertificate_ntz,
                                                                course_training_id=103).exclude(date_end=None) \
                    .order_by('-date_end').first()
                date_end = certificate_ntz.date_end if certificate_ntz else None
            if not date_end and type_document in [57, 85, 86, 88, 89, 3]:
                date_end = statement_instance.protocol_dkk.date_meeting + relativedelta(years=5)
            status_document_id = magic_numbers.status_qual_doc_in_proccess
            port = statement_instance.port
            port_id = port.pk
            country = 2
            year_of_issue = date_start.year
            number_document = QualificationDocument.generate_number(year_of_issue=year_of_issue,
                                                                    port_id=port_id,
                                                                    type_document_id=type_document)
            rank_id = statement_instance.rank_id
        else:
            statement_instance = None
            date_start = serializer.initial_data['date_start']
            list_positions = serializer.initial_data['list_positions']
            type_document = serializer.initial_data['type_document']
            status_document_id = self.request.user.userprofile.verification_status_by_user
            port = serializer.validated_data.get('port')
            port_id = serializer.initial_data['port']
            country = serializer.initial_data['country']
            number_document = serializer.initial_data['number_document']
            rank_id = serializer.initial_data.get('rank', Position.objects.get(id=list_positions[0]).rank_id)
        try:
            fio_captain_ukr = port.fiocapitanofport_set.first().name_ukr
            fio_captain_eng = port.fiocapitanofport_set.first().name_eng
        except (AttributeError, Port.DoesNotExist):
            fio_captain_eng = None
            fio_captain_ukr = None
        ser = serializer.save(status_document_id=status_document_id,
                              list_positions=list_positions, type_document_id=type_document, port_id=port_id,
                              fio_captain_eng=fio_captain_eng, fio_captain_ukr=fio_captain_ukr, country_id=country,
                              number_document=number_document, rank_id=rank_id, date_start=date_start,
                              date_end=date_end, author=self.request.user, function_limitation=function_limitation)
        sailor_qs.qualification_documents.append(ser.id)
        sailor_qs.save(update_fields=['qualification_documents'])
        if ser.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(ser)
        if new_document and type_document in [49, 3]:
            date_end = statement_instance.protocol_dkk.date_meeting + relativedelta(years=5)
            if hasattr(statement_instance, 'protocol_dkk'):
                function_limitation = statement_instance.protocol_dkk.function_limitation
            proof = ProofOfWorkDiploma.objects.create(diploma_id=ser.id,
                                                      number_document=ser.number_document,
                                                      date_start=date_start,
                                                      date_end=date_end,
                                                      author=self.request.user,
                                                      status_document_id=magic_numbers.status_qual_doc_in_proccess,
                                                      is_continue=0,
                                                      port_id=port_id,
                                                      fio_captain_ukr=fio_captain_ukr,
                                                      fio_captain_eng=fio_captain_eng,
                                                      diploma_year=date_start,
                                                      function_limitation=function_limitation,
                                                      statement=statement_instance)
            sailor.tasks.save_history.s(user_id=self.request.user.id, module='ProofOfDiploma', action_type='create',
                                        content_obj=proof,
                                        serializer=sailor.document.serializers.ProofOfWorkDiplomaSerializer,
                                        new_obj=proof,
                                        sailor_key_id=sailor_id).apply_async(serializer='pickle')
        if new_document:
            if ser.statement.related_docs.exists():
                ser.related_docs = list(ser.statement.related_docs.all())

            else:
                docs_set = ser.statement.get_status_position
                all_docs = docs_set.get('all_docs', [])
                ser.related_docs = all_docs
                statement_instance.related_docs = all_docs
            sailor.tasks.change_status_qualification_document.s(exclude_diploma=ser.pk,
                                                                sailor_id=sailor_id).apply_async()
        sailor.tasks.save_history.s(user_id=self.request.user.id, module='QualificationDocument', action_type='create',
                                    content_obj=ser,
                                    serializer=sailor.document.serializers.QualificationDocumentSerializer,
                                    new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        old_pk = instance.pk
        response = super(QualificationDocumentView, self).perform_destroy(instance)
        DependencyItem.objects.filter(content_type__model=QualificationDocument._meta.model_name,
                                      object_id=old_pk).update(content_type=None, object_id=None)
        return response

    @action(detail=False, methods=['get'])
    def diploma_for_proof(self, request, sailor_pk):
        queryset = self.get_queryset()
        queryset = queryset.filter(
            type_document_id__in=[1, 49], status_document_id__in=[magic_numbers.status_qual_doc_valid,
                                                                  magic_numbers.VERIFICATION_STATUS,
                                                                  magic_numbers.STATUS_CREATED_BY_AGENT]
        ).order_by('-id')
        return Response(self.serializer_class(queryset, many=True).data)

    def get_queryset(self):
        qs = super().get_queryset()
        userprofile: UserProfile = self.request.user.userprofile
        if userprofile.type_user in [userprofile.VERIFIER, userprofile.SECRETARY_SQC, userprofile.DPD,
                                     userprofile.MEDICAL, userprofile.MARAD, userprofile.ETI_EMPLOYEE,
                                     userprofile.SECRETARY_ATC]:
            qs = qs.exclude(status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT])
        return qs


class ProofOfWorkDiplomaView(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin, mixins.ListModelMixin, ObjectFromQuerySetMixin):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
        (sailor.document.permissions.QualificationStatusPermission |
         sailor.permissions.PostVerificationChangeStatusPermission)
    )
    queryset = ProofOfWorkDiploma.objects.select_related().prefetch_related().all()
    serializer_class = sailor.document.serializers.ProofOfWorkDiplomaSerializer

    def raise_on_early_non_agent_statement(self, statement: StatementQualification):
        today = date.today()
        created_at = statement.created_at
        td = today - created_at.date()
        if not statement.items.exists() and td.days < 13 and not self.request.user.is_superuser:
            raise ValidationError('Early for create this qualification document')

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProofOfWorkDiploma.objects.none()
        sailor_pk = self.kwargs.get('pk') or self.kwargs.get('sailor_pk')
        try:
            keys = SailorKeys.objects.get(id=sailor_pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        diplomas = list(QualificationDocument.objects.filter(id__in=keys.qualification_documents).
                        values_list('pk', flat=True))
        qs = self.queryset.filter(diploma__in=diplomas).order_by('-pk')
        userprofile: UserProfile = self.request.user.userprofile
        if userprofile.type_user in [userprofile.VERIFIER, userprofile.SECRETARY_SQC, userprofile.DPD,
                                     userprofile.MEDICAL, userprofile.MARAD, userprofile.ETI_EMPLOYEE,
                                     userprofile.SECRETARY_ATC]:
            qs = qs.exclude(status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT,
                                                    magic_numbers.STATUS_REMOVED_DOCUMENT])
        elif userprofile.type_user in [UserProfile.BACK_OFFICE] or self.request.user.is_superuser:
            return qs
        return qs.exclude(status_document_id=magic_numbers.STATUS_REMOVED_DOCUMENT)

    def perform_create(self, serializer):
        diploma = QualificationDocument.objects.get(id=serializer.initial_data['diploma'])
        if diploma.number_document:
            number = diploma.number_document
        else:
            number = diploma.other_number
        diploma_year = diploma.date_start
        statement = serializer.validated_data.get('statement')
        function_limitation = serializer.validated_data.get('function_limitation')
        if statement:
            self.raise_on_early_non_agent_statement(statement=statement)
            if diploma.rank_id != statement.rank_id:
                raise ValidationError('diploma is not suitable for statement')
            date_start = date.today()
            date_end = statement.protocol_dkk.date_meeting + relativedelta(years=5)
            if QualificationDocument.objects.filter(statement=statement).exists() or \
                    ProofOfWorkDiploma.objects.filter(statement=statement).exists():
                raise ValidationError('Qualification document with this statement exists')
            port = statement.port
            status_document = magic_numbers.status_qual_doc_in_proccess
            function_limitation = statement.protocol_dkk.function_limitation
        else:
            port = serializer.validated_data.get('port')
            date_start = serializer.initial_data.get('date_start')
            date_end = serializer.initial_data.get('date_end')
            status_document = self.request.user.userprofile.verification_status_by_user
        try:
            fio_captain_ukr = port.fiocapitanofport_set.first().name_ukr
            fio_captain_eng = port.fiocapitanofport_set.first().name_eng
        except (AttributeError, Port.DoesNotExist):
            fio_captain_eng = None
            fio_captain_ukr = None
        ser = serializer.save(number_document=number, fio_captain_ukr=fio_captain_ukr, fio_captain_eng=fio_captain_eng,
                              port=port, status_document_id=status_document, date_start=date_start,
                              diploma_year=diploma_year, date_end=date_end, author=self.request.user,
                              function_limitation=function_limitation)
        if ser.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(ser)
        if statement:
            sailor.tasks.change_status_proof_of_diploma.s(qual_diploma=ser.diploma_id,
                                                          exclude_proof=ser.pk).apply_async()
        sailor.tasks.save_history.s(
            user_id=self.request.user.id,
            module='ProofOfDiploma',
            action_type='create',
            content_obj=ser,
            serializer=sailor.document.serializers.ProofOfWorkDiplomaSerializer,
            new_obj=ser,
            get_sailor=True
        ).apply_async(serializer='pickle')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        _instance = deepcopy(instance)
        user = self.request.user
        if instance.items.exists():
            raise ValidationError('Document can only be deleted with the packet')
        if instance.status_document.id != magic_numbers.STATUS_REMOVED_DOCUMENT:
            instance.status_document_id = magic_numbers.STATUS_REMOVED_DOCUMENT
            instance.save(update_fields=['status_document'])
            history_args = {'action_type': 'edit', 'new_obj': instance}
        else:
            instance.delete()
            DependencyItem.objects.filter(content_type__model=ProofOfWorkDiploma._meta.model_name,
                                          object_id=_instance.pk).update(content_type=None, object_id=None,
                                                                         item_status=DependencyItem.TO_BUY)
            history_args = {'action_type': 'delete'}
        sailor.tasks.save_history.s(user_id=user.id,
                                    get_sailor=True,
                                    module='ProofOfDiploma',
                                    content_obj=_instance,
                                    serializer=sailor.document.serializers.ProofOfWorkDiplomaSerializer,
                                    old_obj=_instance,
                                    **history_args,
                                    ).apply_async(serializer='pickle')
        if getattr(instance, 'pk', None):
            return Response(self.serializer_class(instance).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)
