import os

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
# Create your views here.
from django.utils.encoding import iri_to_uri
from django_filters import rest_framework as filters, utils
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import reports.serializers
from cadets.models import StudentID
from communication.models import SailorKeys
from itcs import magic_numbers
from payments.platon.models import PlatonPayments
from reports.filters import (NTZFilter, ProtocolDkkFilter, StatementDkkFilter,
                             QualificationDocumentAllFilter, QualificationDocumentCertificatesFilter,
                             ProofOfWorkDiplomaFilter, EducationDocumentFilter, ShortLinkResultPagination,
                             StatementETIFilter, PaymentStatementETIFilter, PaymentBranchOfficeFilter,
                             StatementAdvancedTrainingFilter, SailorPassportFilter)
from reports.models import ProtocolFiles
from reports.permissions import (ReportProtocolSQCPermission, ReportStatementSQCPermission, ReportNTZPermission,
                                 ReportQualificationDocumentPermission, ReportEducationDocumentPermission,
                                 ReportListOfFilesPermission, StatementQualDocFromPacketPermission,
                                 ReportStatementETIPermission, PaymentsStatementETIPermission,
                                 PaymentsBranchOfficePermission, ReportStatementAdvTrainingPermission,
                                 ReportSailorPassportPermission)
from sailor.document.models import Education, ProtocolSQC, CertificateETI, QualificationDocument, \
    ProofOfWorkDiploma
from sailor.models import (Profile, SailorPassport)
from sailor.permissions import CheckApprovStatementDKK, CheckInProcessStatementDKK
from sailor.statement.models import (StatementServiceRecord, StatementSQC, StatementQualification, StatementETI,
                                     StatementAdvancedTraining)
from sailor.statement.permissions import StatementServiceRecordPermission
from sailor.statement.serializers import StatementServiceRecordSerializer, ShortStatementQualificationDocumentSerializer
from sailor.tasks import save_history
from user_profile.models import BranchOfficeRestrictionForPermission
from .tasks import generate_report


class ProtocolDkkBase(generics.ListAPIView):
    permission_classes = [ReportProtocolSQCPermission]

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ProtocolDkkFilter

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProtocolSQC.objects.none()
        if self.request.user.is_superuser is False:
            branch_office_restr = BranchOfficeRestrictionForPermission.objects. \
                filter(user=self.request.user, perm__codename__icontains='reportSqcProtocol')
            branch_office_list = branch_office_restr.values_list('branch_office__id', flat=True)
            return ProtocolSQC.objects.select_related(). \
                filter(branch_create__id__in=list(branch_office_list))
        return ProtocolSQC.objects.select_related().all()


class ProtocolDkkList(ProtocolDkkBase):
    pagination_class = ShortLinkResultPagination
    serializer_class = reports.serializers.ListProtocolDKKSerializer

    def list(self, request, *args, **kwargs):
        save_history.s(user_id=self.request.user.pk, module='Report ProtocolDKK', action_type='generate',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        return super(ProtocolDkkList, self).list(request, *args, **kwargs)


class ProtocolDkkListXlsx(ProtocolDkkBase):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        # from sailor.tasks import generate_report
        save_history.s(user_id=self.request.user.pk, module='Report ProtocolDKK', action_type='generate xlsx',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.count() > 1000:
            queryset = queryset[:1000]
        titles = [
            ('Номер протоколу засідання ДКК', 'get_number'),
            ('Філія', 'branch'),
            ('Дата складання', 'date_meeting'),
            ('Номер заяви', 'get_full_number_statement'),
            ('ID моряка', 'sailor'),
            ('ПІБ моряка', 'sailor_full_name'),
            ('Дата народження моряка', 'sailor_birth_date'),
            ('Рішення', '_document_property_name'),
            ('Посада', 'positions'),
            ('Звання', 'rank_name'),
            ('Вимоги до стажу', 'is_exp_required_ukr'),
            ('Кадет', 'get_is_cadet'),
            ('Голова комісії', 'get_committe_head_full_name'),
            ('Члени комісії', 'get_commissioners_full_name'),
        ]
        generate_report.s([queryset], titles, 'Протоколи засідання ДКК', request.user).apply_async()
        # results = task.get()
        return Response(status=200)


class StatementDkkBase(generics.ListAPIView):
    """Фильтрация заявок ДКК"""
    permission_classes = [ReportStatementSQCPermission]
    queryset = StatementSQC.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = StatementDkkFilter


class StatementDkkList(StatementDkkBase):
    pagination_class = ShortLinkResultPagination
    serializer_class = reports.serializers.ListStatementDKKSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        queryset = self.queryset.all()
        if not self.request.user.is_superuser:
            queryset = queryset.exclude(status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT,
                                                                magic_numbers.STATUS_REMOVED_DOCUMENT])
        if self.request.user.has_perm('statement.readApplicationSQCApproved') and not self.request.user.is_superuser:
            return queryset.filter(status_document_id=24)
        if not self.request.user.has_perm('statement.readReportApplicationSQC') and not self.request.user.is_superuser:
            return queryset.filter(status_document_id=42)
        return queryset

    def list(self, request, *args, **kwargs):
        save_history.s(user_id=self.request.user.pk, module='Report StatementDKK', action_type='generate',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        return super(StatementDkkList, self).list(request, *args, **kwargs)


class StatementDkkListXlsx(StatementDkkBase):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        queryset = self.queryset.all()
        if not self.request.user.is_superuser:
            queryset = queryset.exclude(status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT,
                                                                magic_numbers.STATUS_REMOVED_DOCUMENT])
        if self.request.user.has_perm('statement.readReportApplicationSQC') is False:
            return queryset.filter(status_document_id=42)
        return queryset

    def list(self, request, *args, **kwargs):
        save_history.s(user_id=self.request.user.pk, module='Report StatementDKK', action_type='generate xlsx',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.count() > 1000:
            queryset = queryset[:1000]
        titles = [
            ('Номер заяви', 'get_number'),
            ('Філія', 'branch'),
            ('Дата оформлення', 'create_date'),
            ('Номер протоколу ДКК', 'protocol_number'),
            ('ID моряка', 'sailor'),
            ('ПІБ моряка', 'sailor_full_name'),
            ('Дата народження моряка', 'sailor_birth_date'),
            ('Посада', 'positions'),
            ('Звання', 'rank_name'),
            ('Вимоги до стажу', 'is_exp_required_ukr'),
            ('Статус', 'status_ukr'),
            ('Кадет', 'is_cadet'),
        ]
        generate_report.s([queryset], titles, 'Заяви ДКК', request.user).apply_async()
        # results = task.get()
        return Response(status=200)


class LoadXlsx(APIView):
    """Загрузчик xlsx файлов"""

    def get(self, request, token):
        xlsx_file = get_object_or_404(ProtocolFiles, token=token)

        file_name = xlsx_file.file_path.split('/')[-1]
        open_file = open('{}'.format(xlsx_file.file_path), 'rb')
        response = HttpResponse(open_file,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}'.format(iri_to_uri(file_name))
        open_file.close()
        os.remove(xlsx_file.file_path)
        xlsx_file.delete()
        return response


class NTZBase(generics.ListAPIView):
    permission_classes = [ReportNTZPermission]

    queryset = CertificateETI.objects.select_related().all()

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = NTZFilter


class NTZList(NTZBase):
    pagination_class = ShortLinkResultPagination
    serializer_class = reports.serializers.CertificateNTZListSerializer

    def list(self, request, *args, **kwargs):
        save_history.s(user_id=self.request.user.pk, module='Report NTZList', action_type='generate',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        return super(NTZList, self).list(request, *args, **kwargs)


class NTZListXlsx(NTZBase):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        # from sailor.tasks import generate_report
        save_history.s(user_id=self.request.user.pk, module='Report NTZList', action_type='generate xlsx',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.count() > 3000:
            queryset = queryset[:3000]
        titles = [
            # ('Номер протоколу засідання ДКК', 'get_number'),
            # ('Філія', 'branch'),
            # ('Дата складання', 'create_date'),
            ('Номер', 'ntz_number'),
            ('ID моряка', 'sailor_id'),
            ('ПІБ моряка', 'sailor_full_name'),
            ('Дата народження моряка', 'sailor_birth_date'),
            ('Назва навчального закладу', 'institution_name_ukr'),
            ('Курс', 'course_name_ukr'),
            ('Дата видачі', 'start_date'),
            ('Дата припинення', 'end_date'),
        ]
        generate_report.s([queryset], titles, 'Сертифікати НТЗ', request.user).apply_async()
        # results = task.get()
        return Response(status=200)


class QualificationDocumentFilterBackend(filters.DjangoFilterBackend):

    def get_filterset_proof_diploma(self, request, queryset, view):
        filterset_class = ProofOfWorkDiplomaFilter
        kwargs = self.get_filterset_kwargs(request, queryset, view)
        return filterset_class(**kwargs)

    def filter_queryset(self, request, queryset, view):
        if queryset.model.__name__ == 'ProofOfWorkDiploma':
            filterset = self.get_filterset_proof_diploma(request, queryset, view)
        else:
            filterset = self.get_filterset(request, queryset, view)
        if filterset is None:
            return queryset

        if not filterset.is_valid() and self.raise_exception:
            raise utils.translate_validation(filterset.errors)
        return filterset.qs


class QualificationDocumentBase(generics.ListAPIView):
    """Базовый класс фильтрации квалификационных документов"""

    permission_classes = [ReportQualificationDocumentPermission]
    filter_backends = [QualificationDocumentFilterBackend]

    # queryset = QualificationDocument.objects.all()
    filterset_class = QualificationDocumentAllFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.exclude(status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT,
                                                                magic_numbers.STATUS_REMOVED_DOCUMENT])
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.query_params.get('type_document') is None:
            proof = ProofOfWorkDiploma.objects.all()
            proof_filter = self.filter_queryset(proof)
            page = self.paginate_queryset([1] * (queryset.count() + proof_filter.count()))
            if page is not None:
                page_size = self.paginator.page_size
                num_page = self.paginator.page.number
                if num_page * page_size < len(queryset):
                    serializer = self.get_serializer(queryset[page_size * (num_page - 1):page_size * num_page],
                                                     many=True)
                elif num_page * page_size - len(queryset) < page_size:
                    quantity_add_proof = page_size - (num_page * page_size - len(queryset))
                    slice_start_qual_doc = page_size * (num_page - 1)
                    slice_end_qual_doc = page_size * num_page + quantity_add_proof
                    slice_end_proof_diploma = page_size - quantity_add_proof
                    serializer = self.get_serializer(queryset[slice_start_qual_doc:slice_end_qual_doc], many=True)
                    self.serializer_class = reports.serializers.ListQualificationDocumentProofDiplomaSerializer
                    proof_serializer = self.get_serializer(proof_filter[0:slice_end_proof_diploma], many=True)
                    return self.get_paginated_response(serializer.data + proof_serializer.data)
                else:
                    page_proof = (num_page - (len(queryset) // page_size + 1))
                    slice_start_proof_diploma = page_size * (page_proof - 1) + (page_size - len(queryset) % page_size)
                    slice_end_proof_diploma = page_size * page_proof + (page_size - len(queryset) % page_size)
                    self.serializer_class = reports.serializers.ListQualificationDocumentProofDiplomaSerializer
                    serializer = self.get_serializer(proof_filter[slice_start_proof_diploma:slice_end_proof_diploma],
                                                     many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            self.serializer_class = reports.serializers.ListQualificationDocumentProofDiplomaSerializer
            proof_serializer = self.get_serializer(proof_filter, many=True)
            return Response(serializer.data + proof_serializer.data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # def list(self, request, *args, **kwargs):  # TODO Need to test. May work incorrectly
    #     queryset = self.filter_queryset(self.get_queryset())
    #     if request.query_params.get('type_document') is None:
    #         proof = ProofOfWorkDiploma.objects.only(
    #             'id', 'status_document', 'port', 'date_start', 'date_end', 'number_document', 'other_port').all()
    #         proof_filter = self.filter_queryset(proof)
    #         all_qs = queryset.union(proof_filter)
    #         page = self.paginate_queryset(all_qs)
    #
    #         if page is not None:
    #             serializer = self.get_serializer(page, many=True)
    #             return self.get_paginated_response(serializer.data)
    #         serializer = self.get_serializer(all_qs, many=True)
    #         return Response(serializer.data)
    #
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


class QualificationDocumentList(QualificationDocumentBase):
    """Фильтрация квалификационных документов"""

    pagination_class = ShortLinkResultPagination

    # serializer_class = reports.serializers.ListQualificationDocumentAllSerializer

    def get(self, request, *args, **kwargs):
        save_history.s(user_id=self.request.user.pk, module='Report QualDoc', action_type='generate',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        if request.query_params.get('type_document') is None:
            self.queryset = QualificationDocument.objects.only(
                'id', 'status_document', 'port', 'date_start', 'date_end', 'number_document', 'other_port').all()
            self.filterset_class = QualificationDocumentAllFilter
            self.serializer_class = reports.serializers.ListQualificationDocumentAllSerializer
        elif int(request.query_params['type_document']) == 16:
            self.queryset = ProofOfWorkDiploma.objects.all()
            self.filterset_class = ProofOfWorkDiplomaFilter
            self.serializer_class = reports.serializers.ListQualificationDocumentProofDiplomaSerializer
        elif int(request.query_params['type_document']) not in [3, 49, 87]:
            self.queryset = QualificationDocument.objects.all()
            self.filterset_class = QualificationDocumentCertificatesFilter
            self.serializer_class = reports.serializers.ListQualificationDocumentCertificatesSerializer
        else:
            self.queryset = QualificationDocument.objects.all()
            self.filterset_class = QualificationDocumentAllFilter
            self.serializer_class = reports.serializers.ListQualificationDocumentAllSerializer
        return self.list(request, *args, **kwargs)


class QualificationDocumentListXlsx(QualificationDocumentList):
    """Информация для формирования excel файла квалификационных документов"""

    # from sailor.tasks import generate_report
    def list(self, request, *args, **kwargs):
        save_history.s(user_id=self.request.user.pk, module='Report QualDoc', action_type='generate xlsx',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        list_queryset = []
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.count() > 3000:
            queryset = queryset[:3000]
        list_queryset.append(queryset)
        if request.query_params.get('type_document') is None:
            proof = ProofOfWorkDiploma.objects.all()
            proof_filter = self.filter_queryset(proof)
            list_queryset.append(proof_filter)

        if request.query_params.get('type_document') is None or \
                int(request.query_params.get('type_document')) in [3, 16, 49, 87]:
            titles = [
                ('ID моряка', 'sailor_id'),
                ('ПІБ моряка', 'sailor_full_name'),
                ('Дата народження моряка', 'sailor_birth_date'),
                ('Номер документа', 'get_number'),
                ('Порт', 'port_ukr'),
                ('Інший порт', 'other_port_name'),
                ('Звання', 'rank_name'),
                ('Посада', 'positions'),
                ('Дата видачі', 'start_date'),
                ('Дата припинення', 'end_date'),
                ('Статус', 'status_ukr'),
                ('Тип документа', 'type_document_name'),
            ]
        else:
            titles = [
                ('ID моряка', 'sailor_id'),
                ('ПІБ моряка', 'sailor_full_name'),
                ('Дата народження моряка', 'sailor_birth_date'),
                ('Номер документа', 'get_number'),
                ('Назва свідоцтва', 'type_document_name'),
                ('Порт', 'port_ukr'),
                ('Інший порт', 'other_port_name'),
                ('Дата видачі', 'start_date'),
                ('Дата припинення', 'end_date'),
                ('Статус', 'status_ukr'),
            ]
        generate_report.s(list_queryset, titles, 'Кваліфікаційні документи', request.user).apply_async()
        # results = task.get()
        return Response(status=200)


class EducationDocumentBase(generics.ListAPIView):
    permission_classes = [ReportEducationDocumentPermission]
    queryset = Education.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = EducationDocumentFilter

    def get_queryset(self):
        queryset = self.queryset.all()
        if not self.request.user.is_superuser:
            queryset = queryset.exclude(status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT,
                                                                magic_numbers.STATUS_REMOVED_DOCUMENT])
        return queryset


class EducationDocumentList(EducationDocumentBase):
    """Фильтрация образовательных документов"""
    pagination_class = ShortLinkResultPagination
    serializer_class = reports.serializers.EducationDocumentBaseSerializer

    def list(self, request, *args, **kwargs):
        save_history.s(user_id=self.request.user.pk, module='Report EducDoc', action_type='generate',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        return super().list(request, *args, **kwargs)


class EducationDocumentListXlsx(EducationDocumentBase):
    """Информация для формирования excel файла образовательных документов"""

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    # from sailor.tasks import generate_report
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        save_history.s(user_id=self.request.user.pk, module='Report EducDoc', action_type='generate xlsx',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        if request.query_params.get('type_document') and int(request.query_params.get('type_document')) == 1:
            titles = [
                ('ID моряка', 'sailor_id'),
                ('ПІБ моряка', 'sailor_full_name'),
                ('Дата народження моряка', 'sailor_birth_date'),
                ('Назва навчального закладу', 'name_nz_ukr'),
                ('Серія', 'serial_document'),
                ('Номер документа', 'get_number'),
                ('Реєстраційний номер', 'registry_number_document'),
                ('Ступінь вищої освіти', 'extent_ukr'),
                ('Кваліфікація', 'qualification_ukr'),
                ('Спеціальність', 'speciality_ukr'),
                ('Спеціалізація', 'specialization_ukr'),
                ('Дата видачі', 'date_start_document'),
                ('Статус', 'status_ukr'),
                ('Тип документа', 'type_document_ukr'),
            ]
        else:
            titles = [
                ('ID моряка', 'sailor_id'),
                ('ПІБ моряка', 'sailor_full_name'),
                ('Дата народження моряка', 'sailor_birth_date'),
                ('Реєстраційний номер', 'registry_number_document'),
                ('Серія', 'serial_document'),
                ('Номер документа', 'get_number'),
                ('Назва навчального закладу', 'name_nz_ukr'),
                ('Кваліфікація', 'qualification_ukr'),
                ('Дата видачі', 'date_start_document'),
                ('Дата припинення дії', 'date_end_document'),
                ('Статус', 'status_ukr'),
                ('Тип документа', 'type_document_ukr'),
            ]
        print('generate')
        generate_report.s([queryset], titles, 'Освітні документи', request.user).apply_async()
        return Response(status=200)


class ListOfFiles(generics.ListAPIView):
    permission_classes = (ReportListOfFilesPermission,)
    serializer_class = reports.serializers.ListOfFileSerializer

    def get_queryset(self):
        files = ProtocolFiles.objects.filter(user=self.request.user)
        self.headers['Count'] = files.count()
        return files


class AllSuccessStatementDKKViewset(APIView):
    """
    Все одобреные заявки на дкк без протокола ДКК
    """

    permission_classes = (IsAuthenticated, CheckApprovStatementDKK,)

    def get(self, request, *args, **kwargs):
        response = []
        statements = StatementSQC.objects.prefetch_related('rank', 'branch_office').filter(
            protocolsqc__isnull=True, created_at__gte='2020-02-07',
            status_document_id=magic_numbers.status_state_qual_dkk_approv)
        for statement in statements:
            try:
                sailor_key = SailorKeys.objects.get(id=statement.sailor)
                if statement.pk not in sailor_key.statement_dkk:
                    sailor_key = SailorKeys.objects.filter(statement_dkk__overlap=[statement.pk])
                    if sailor_key.exists() is True:

                        statement.sailor = sailor_key.first().pk
                        statement.save(update_fields=['sailor'])
                        sailor_key = sailor_key.first()
                    else:
                        try:
                            statement.delete()
                        except:
                            continue
                        continue
                profile = Profile.objects.get(id=sailor_key.profile)
                response.append({'number': statement.get_number, 'branch_office': statement.branch_office.name_ukr,
                                 'sailor_id': sailor_key.id, 'full_name_ukr': profile.get_full_name_ukr})
            except SailorKeys.DoesNotExist:
                sailor_key = SailorKeys.objects.filter(statement_dkk__overlap=[statement.pk])
                if sailor_key.exists() is True:
                    statement.sailor = sailor_key.first().pk
                    statement.save(update_fields=['sailor'])
                    sailor_key = sailor_key.first()
                    profile = Profile.objects.get(id=sailor_key.profile)
                    response.append({'number': statement.get_number, 'branch_office': statement.branch_office.name_ukr,
                                     'sailor_id': sailor_key.id, 'full_name_ukr': profile.get_full_name_ukr})
                else:
                    statement.delete()
                    continue
        return Response(response)


class CountAllSuccessStatementDKK(APIView):
    permission_classes = (IsAuthenticated, CheckApprovStatementDKK,)

    def get(self, request, *args, **kwargs):
        statements = StatementSQC.objects.prefetch_related('rank', 'branch_office').filter(
            protocolsqc__isnull=True, created_at__gte='2020-02-07',
            status_document_id=magic_numbers.status_state_qual_dkk_approv).count()
        return Response({'count_doc': statements})


class AllInProcessStatementDKK(APIView):
    permission_classes = (CheckInProcessStatementDKK, IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        response = []
        statements = StatementSQC.objects.prefetch_related('rank', 'branch_office').filter(
            status_document_id=magic_numbers.status_state_qual_dkk_in_process, is_payed=True). \
            order_by('-created_at')
        for statement in statements:
            try:
                sailor_key = SailorKeys.objects.get(id=statement.sailor)
                if statement.pk not in sailor_key.statement_dkk:
                    sailor_key = SailorKeys.objects.filter(statement_dkk__overlap=[statement.pk])
                    if sailor_key.exists() is True:

                        statement.sailor = sailor_key.first().pk
                        statement.save(update_fields=['sailor'])
                        sailor_key = sailor_key.first()
                    else:
                        try:
                            statement.delete()
                        except:
                            continue
                        continue
                profile = Profile.objects.get(id=sailor_key.profile)
                response.append({'number': statement.get_number, 'branch_office': statement.branch_office.name_ukr,
                                 'sailor_id': sailor_key.id, 'full_name_ukr': profile.get_full_name_ukr})
            except SailorKeys.DoesNotExist:
                sailor_key = SailorKeys.objects.filter(statement_dkk__overlap=[statement.pk])
                if sailor_key.exists() is True:
                    statement.sailor = sailor_key.first().pk
                    statement.save(update_fields=['sailor'])
                    sailor_key = sailor_key.first()
                    profile = Profile.objects.get(id=sailor_key.profile)
                    response.append({'number': statement.get_number, 'branch_office': statement.branch_office.name_ukr,
                                     'sailor_id': sailor_key.id, 'full_name_ukr': profile.get_full_name_ukr})
                else:
                    statement.delete()
                    continue
        return Response(response)


class CountAllInProcessStatementDKK(APIView):
    permission_classes = (CheckInProcessStatementDKK, IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        statements = StatementSQC.objects.prefetch_related('rank', 'branch_office').filter(
            status_document_id=magic_numbers.status_state_qual_dkk_in_process).count()
        return Response({'count_doc': statements})


class StudentIDReport(generics.ListAPIView):
    queryset = StudentID.objects.all()
    serializer_class = reports.serializers.StudentIDReportSerializer
    pagination_class = ShortLinkResultPagination
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = reports.filters.StudentIDFilter

    def list(self, request, *args, **kwargs):
        save_history.s(user_id=self.request.user.pk, module='Report StudentsID', action_type='generate',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        return super().list(request, *args, **kwargs)


class ListStatementServiceRecordViewset(viewsets.ModelViewSet):
    """
    Все заявки на ПКМ
    """
    permission_classes = (IsAuthenticated, StatementServiceRecordPermission)
    queryset = StatementServiceRecord.objects.exclude(
        status_id__in=(magic_numbers.status_statement_serv_rec_created,
                       magic_numbers.STATUS_REMOVED_DOCUMENT))
    serializer_class = StatementServiceRecordSerializer
    pagination_class = ShortLinkResultPagination
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = reports.filters.StatementServiceRecordFilter


class ListStatementQualDocInPacket(generics.ListAPIView):
    permission_classes = (StatementQualDocFromPacketPermission,)
    pagination_class = ShortLinkResultPagination
    serializer_class = ShortStatementQualificationDocumentSerializer
    queryset = StatementQualification.objects.filter(items__isnull=False).exclude(
        status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT, magic_numbers.STATUS_REMOVED_DOCUMENT]
    ).order_by('date_meeting')

    def get_queryset(self):
        port_converter = {41: 70, 3: 69, 47: 21, 2: 0, 22: 67, 48: 38, 1: 0, 4: 66, 5: 64, 21: 1}
        qs = self.queryset.all()
        user = self.request.user
        userprofile = user.userprofile
        if userprofile.type_user in [userprofile.DPD, userprofile.SECRETARY_SQC] and user.pk != 6056:
            qs = qs.filter(port=port_converter[userprofile.branch_office_id])

        return qs


class StatementETIList(generics.ListAPIView):
    permission_classes = (ReportStatementETIPermission,)
    queryset = StatementETI.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = StatementETIFilter
    pagination_class = ShortLinkResultPagination
    serializer_class = reports.serializers.StatementETIListSerializer

    def get_queryset(self):
        user = self.request.user
        userprofile = user.userprofile
        if userprofile.type_user in [userprofile.BACK_OFFICE]:
            return self.queryset.all()
        return self.queryset.filter(institution=userprofile.eti_institution)


class PaymentStatementETIList(generics.ListAPIView):
    permission_classes = (PaymentsStatementETIPermission,)
    queryset = PlatonPayments.objects.filter(content_type__model='statementeti',
                                             statement_eti_payments__isnull=False
                                             ).exclude(platon_id='')
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = PaymentStatementETIFilter
    pagination_class = ShortLinkResultPagination
    serializer_class = reports.serializers.PaymentStatementETISerializer

    def get_queryset(self):
        user = self.request.user
        userprofile = user.userprofile
        if userprofile.type_user in [userprofile.BACK_OFFICE]:
            return self.queryset.all()
        return self.queryset.filter(statement_eti_payments__institution=userprofile.eti_institution)


class PaymentBranchOfficeList(generics.ListAPIView):
    permission_classes = (PaymentsBranchOfficePermission,)
    queryset = PlatonPayments.objects.filter(content_type__model='dependencyitem',
                                             dependecy_payments__isnull=False,
                                             ).exclude(platon_id='')
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = PaymentBranchOfficeFilter
    pagination_class = ShortLinkResultPagination
    serializer_class = reports.serializers.PaymentBranchOfficeSerializer


class StatementAdvancedTrainingList(generics.ListAPIView):
    permission_classes = (ReportStatementAdvTrainingPermission,)
    queryset = StatementAdvancedTraining.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = StatementAdvancedTrainingFilter
    pagination_class = ShortLinkResultPagination
    serializer_class = reports.serializers.StatementAdvancedTrainingListSerializer

    def get_queryset(self):
        user = self.request.user
        userprofile = user.userprofile
        if userprofile.type_user in [userprofile.BACK_OFFICE]:
            return self.queryset.all()
        return self.queryset.filter(educational_institution=userprofile.education_institution)


class SailorPassportList(generics.ListAPIView):
    permission_classes = (ReportSailorPassportPermission,)
    queryset = SailorPassport.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SailorPassportFilter
    pagination_class = ShortLinkResultPagination
    serializer_class = reports.serializers.SailorPassportListSerializer
