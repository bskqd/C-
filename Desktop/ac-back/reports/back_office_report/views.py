from typing import List

from django.db.models import QuerySet, F, Value, Q, When, Case, FloatField, Sum, IntegerField, Count
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

import reports.back_office_report.filters
import reports.back_office_report.serializers
import reports.tasks
import sailor.tasks
from back_office.models import DependencyItem, PriceForPosition, ETIProfitPart
from directory.models import Position
from reports.filters import ShortLinkResultPagination
from sailor.document.models import ProofOfWorkDiploma


class BaseProfitAndDistributionReport(generics.ListAPIView):
    permission_classes = (IsAdminUser,)
    pagination_class = ShortLinkResultPagination

    def get_dependency_item(self) -> QuerySet[DependencyItem]:
        if getattr(self, 'swagger_fake_view', False):
            return DependencyItem.objects.none()
        price_for_position = PriceForPosition.objects.filter(type_of_form='Second').annotate(
            distribution=(F('to_sqc') + F('to_qd') + F('to_sc') + F('to_agent') +
                          F('to_itcs') + F('to_medical') + F('to_cec') +
                          F('to_portal') + F('to_td'))).exclude(type_document_id__in=[11, 12])
        percent_for_course = ETIProfitPart.objects.values('percent_of_eti', 'date_start', 'date_end')
        values_price_for_position = price_for_position.values('distribution', 'date_start',
                                                              'date_end', 'type_document_id')
        annotations = {'distribution': []}
        for price_dates in values_price_for_position:
            if price_dates.get('date_end'):
                annotations['distribution'].append(When(
                    Q(type_document_id=price_dates.get('type_document_id')) &
                    Q(packet_item__payment_date__date__gte=price_dates.get('date_start')) &
                    Q(packet_item__payment_date__date__lte=price_dates.get('date_end')),
                    then=Value(price_dates.get('distribution'))))
            else:
                annotations['distribution'].append(When(
                    Q(type_document_id=price_dates.get('type_document_id')) &
                    Q(packet_item__payment_date__date__gte=price_dates.get('date_start')),
                    then=Value(price_dates.get('distribution'))))
        for course_percent in percent_for_course:
            if course_percent.get('date_end'):
                annotations['distribution'].append(When(
                    Q(type_document_id=12) &
                    Q(packet_item__payment_date__date__gte=course_percent.get('date_start')) &
                    Q(packet_item__payment_date__date__lte=course_percent.get('date_end')),
                    then=F('payment_form2') / Value(100) * Value(course_percent.get('percent_of_eti'))))
            else:
                annotations['distribution'].append(When(
                    Q(type_document_id=12) &
                    Q(packet_item__payment_date__date__gte=course_percent.get('date_start')),
                    then=F('payment_form2') / Value(100) * Value(course_percent.get('percent_of_eti'))))
        qs = DependencyItem.objects.filter(
            item_status__in=[DependencyItem.WAS_BOUGHT, DependencyItem.TO_BUY]
        ).exclude(packet_item__agent__userprofile__type_user='marad').annotate(
            distribution=Case(*annotations.get('distribution'), default=Value(-1), output_field=FloatField()),
            profit=F('payment_form2') - F('distribution'))
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        global_form2_sum = queryset.aggregate(global_sum_form2=Sum('form2_sum'))['global_sum_form2'] or 0
        global_form2_profit = queryset.aggregate(global_profit=Sum('profit_sum'))['global_profit'] or 0
        page = self.paginate_queryset(queryset)
        page_form2_sum = round(sum((instance.get('form2_sum') if isinstance(instance, dict) else instance.form2_sum
                                    for instance in page)), 2)
        page_form2_profit = round(sum((instance.get('profit_sum') if isinstance(instance, dict) else instance.form2_sum
                                       for instance in page)), 2)
        response = {}
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response['data'] = serializer.data
            response['global_form2_sum'] = round(global_form2_sum, 2)
            response['global_form2_profit'] = round(global_form2_profit, 2)
            response['page_form2_sum'] = page_form2_sum
            response['page_form2_profit'] = page_form2_profit
            return self.get_paginated_response(response)
        serializer = self.get_serializer(queryset, many=True)
        response['data'] = serializer.data
        response['global_form2_sum'] = round(global_form2_sum, 2)
        response['global_form2_profit'] = round(global_form2_profit, 2)
        response['page_form2_sum'] = page_form2_sum
        response['page_form2_profit'] = page_form2_profit
        return Response(response)


class GlobalPacketByGroupReportView(BaseProfitAndDistributionReport):
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = reports.back_office_report.filters.GlobalPacketGroupFilter
    serializer_class = reports.back_office_report.serializers.GlobalPacketByGroupReportSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item()
        return queryset.values(
            'packet_item__agent__userprofile__agent_group'
        ).annotate(
            distribution_sum=Sum('distribution'),
            profit_sum=Sum('profit'),
            form2_sum=Sum('payment_form2'),
            form1_sum=Sum('payment_form1')
        )


class GlobalPacketByAgentReportView(BaseProfitAndDistributionReport):
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = reports.back_office_report.filters.GlobalPacketAgentFilter
    serializer_class = reports.back_office_report.serializers.GlobalPacketByAgentReportSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item()
        return queryset.values(
            'packet_item__agent'
        ).annotate(
            distribution_sum=Sum('distribution'),
            profit_sum=Sum('profit'),
            form2_sum=Sum('payment_form2'),
            form1_sum=Sum('payment_form1')
        )


class GlobalPacketBySailorReportView(BaseProfitAndDistributionReport):
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = reports.back_office_report.filters.GlobalPacketSailorFilter
    serializer_class = reports.back_office_report.serializers.GlobalPacketBySailorReportSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item()
        return queryset.values(
            'packet_item__sailor_id'
        ).annotate(
            distribution_sum=Sum('distribution'),
            profit_sum=Sum('profit'),
            form2_sum=Sum('payment_form2'),
            form1_sum=Sum('payment_form1')
        )


class GlobalPacketByPacketReportView(BaseProfitAndDistributionReport):
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = reports.back_office_report.filters.GlobalPacketPacketFilter
    serializer_class = reports.back_office_report.serializers.GlobalPacketByPacketReportSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item()
        return queryset.values(
            'packet_item', 'packet_item__sailor_id'
        ).annotate(
            distribution_sum=Sum('distribution'),
            profit_sum=Sum('profit'),
            form2_sum=Sum('payment_form2'),
            form1_sum=Sum('payment_form1')
        )


class GlobalPacketByDocumentReportView(BaseProfitAndDistributionReport):
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = reports.back_office_report.filters.GlobalPacketPacketFilter
    serializer_class = reports.back_office_report.serializers.GlobalPacketByDocumentReportSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item()
        return queryset.annotate(
            distribution_sum=Sum('distribution'),
            profit_sum=Sum('profit'),
            form2_sum=Sum('payment_form2'),
            form1_sum=Sum('payment_form1')
        )


class BaseDistributionReport(generics.ListAPIView):
    filter_backends = (filters.DjangoFilterBackend,)
    permission_classes = (IsAdminUser,)
    pagination_class = ShortLinkResultPagination

    def get_dependency_item(self, type_document: List[int], name_field: str) -> QuerySet[DependencyItem]:
        if getattr(self, 'swagger_fake_view', False):
            return DependencyItem.objects.none()
        price_for_position = PriceForPosition.objects.filter(
            type_of_form='Second', type_document_id__in=type_document).annotate(
            distribution=(F(name_field)))
        values_price_for_position = price_for_position.values('distribution', 'date_start', 'date_end',
                                                              'type_document_id')
        annotations = {'distribution': []}
        for price_dates in values_price_for_position:
            if price_dates.get('date_end'):
                annotations['distribution'].append(When(
                    Q(type_document_id=price_dates.get('type_document_id')) &
                    Q(packet_item__payment_date__date__gte=price_dates.get('date_start')) &
                    Q(packet_item__payment_date__date__lte=price_dates.get('date_end')),
                    then=Value(price_dates.get('distribution'))))
            else:
                annotations['distribution'].append(When(
                    Q(type_document_id=price_dates.get('type_document_id')) &
                    Q(packet_item__payment_date__date__gte=price_dates.get('date_start')),
                    then=Value(price_dates.get('distribution'))))
        qs = DependencyItem.objects.filter(
            type_document_id__in=type_document, packet_item__is_payed=True,
        ).exclude(
            content_type__id=76
        ).exclude(
            item_status=DependencyItem.WAS_BE
        ).exclude(packet_item__agent__userprofile__type_user='marad').annotate(
            distribution=Case(*annotations.get('distribution'), default=Value(-1), output_field=FloatField()),
            profit=F('payment_form2') - F('distribution')
        )
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        response = {}
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response['data'] = serializer.data
            return self.get_paginated_response(response)
        serializer = self.get_serializer(queryset, many=True)
        response['data'] = serializer.data
        return Response(response)


class DistributionDPDReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DPDBaseFilter
    serializer_class = reports.back_office_report.serializers.DistributionDPDSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[3, 4, 5, 6, 13, 14], name_field='to_qd')
        return queryset.values(
            'packet_item__service_center'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2')
        )


class DistributionDPDDocumentReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionDPDDocumentFilter
    serializer_class = reports.back_office_report.serializers.DistributionDPDDocumentSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[3, 4, 5, 6, 13, 14], name_field='to_qd')
        return queryset.values(
            'packet_item__service_center'
        ).annotate(
            distribution_sum_sailor_pasport=Sum('distribution', filter=Q(type_document_id__in=[5, 6, 13, 14])),
            profit_sum_sailor_pasport=Sum('profit', filter=Q(type_document_id__in=[5, 6, 13, 14])),
            form2_sum_sailor_pasport=Sum('payment_form2', filter=Q(type_document_id__in=[5, 6, 13, 14])),
            distribution_sum_qual_doc=Sum('distribution', filter=Q(type_document_id__in=[3, 4])),
            profit_sum_qual_doc=Sum('profit', filter=Q(type_document_id__in=[3, 4])),
            form2_sum_qual_doc=Sum('payment_form2', filter=Q(type_document_id__in=[3, 4])),
        )


class DistributionDPDSailorPassportReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionDPDDocumentFilter
    serializer_class = reports.back_office_report.serializers.DistributionDPDSailorPassportSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[5, 6, 13, 14], name_field='to_qd')
        return queryset.annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2'))


class DPDSailorPassportXlsxReportView(DistributionDPDSailorPassportReportView):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        sailor.tasks.save_history.s(
            user_id=self.request.user.pk,
            module='Report BO DPD sailor passport',
            action_type='generate xlsx',
            new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)},
        ).apply_async()
        attrs = [
            [
                ('ID моряка', dep.packet_item.sailor_id),
                ('ПІБ моряка', dep.packet_item.sailor_full_name),
                ('Роздача', dep.distribution_sum),
                ('Прибуток', dep.profit_sum),
                ('Прихід', dep.form2_sum),
                ('Подовження', True if dep.packet_item.include_sailor_passport in [3, 4] else False),
                ('Номер', dep.item.get_number if dep.item else None),
                ('Дата створення пакету', dep.packet_item.created_at.strftime('%d-%m-%Y')),
                ('ДПО', dep.packet_item.service_center.name_ukr),
            ] for dep in queryset]
        if not queryset.exists():
            attrs.append([
                ('ID моряка', ''),
                ('ПІБ моряка', ''),
                ('Роздача', ''),
                ('Прибуток', ''),
                ('Прихід', ''),
                ('Подовження', ''),
                ('Номер', ''),
                ('Дата створення пакету', ''),
                ('ДПО', ''),
            ])
        reports.tasks.generate_report_back_office.s('Роздача прихід ДПО (ПОМ)', request.user, attrs).apply_async()
        return Response(status=200)


class DistributionDPDQualDocReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionDPDDocumentFilter
    serializer_class = reports.back_office_report.serializers.DistributionDPDQualDocSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[3, 4], name_field='to_qd')
        return queryset.annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2'))


class DPDQualDocXlsxReportView(DistributionDPDQualDocReportView):
    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        sailor.tasks.save_history.s(
            user_id=self.request.user.pk,
            module='Report BO DPD qual document',
            action_type='generate xlsx',
            new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)},
        ).apply_async()
        attrs = []
        for dep in queryset:
            if isinstance(dep.item, ProofOfWorkDiploma):
                name_document = 'Підтвердження робочого диплому'
                positions = Position.objects.filter(id__in=dep.item.diploma.list_positions).values_list('name_ukr',
                                                                                                        flat=True)
            else:
                name_document = dep.item.type_document.name_ukr if dep.item else False
                positions = Position.objects.filter(id__in=dep.item.list_positions).values_list('name_ukr', flat=True)
            position_ukr = ', '.join(positions)
            attrs.append(
                [
                    ('ID моряка', dep.packet_item.sailor_id),
                    ('ПІБ моряка', dep.packet_item.sailor_full_name),
                    ('Роздача', dep.distribution_sum),
                    ('Прибуток', dep.profit_sum),
                    ('Прихід', dep.form2_sum),
                    ('Назва документу', name_document),
                    ('Номер', dep.item.get_number if dep.item else None),
                    ('Дата створення заяви', dep.item.statement.created_at.strftime('%d-%m-%Y')
                    if (dep.item and hasattr(dep.item.statement, 'created_at')) else None),
                    ('Звання', dep.packet_item.rank['name_ukr']),
                    ('Посада', position_ukr),
                    ('ДПО', dep.packet_item.service_center.name_ukr),
                ])
        if not queryset.exists():
            attrs.append([
                ('ID моряка', ''),
                ('ПІБ моряка', ''),
                ('Роздача', ''),
                ('Прибуток', ''),
                ('Прихід', ''),
                ('Назва документу', ''),
                ('Номер', ''),
                ('Дата створення заяви', ''),
                ('Звання', ''),
                ('Посада', ''),
                ('ДПО', ''),
            ])
        reports.tasks.generate_report_back_office.s('Роздача прихід ДПО (КД)', request.user, attrs).apply_async()
        return Response(status=200)


class DistributionAdvTrainingReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DPDBaseFilter
    serializer_class = reports.back_office_report.serializers.DistributionAdvTrainingSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[8], name_field='to_cec')
        return queryset.exclude(content_type_id=61).values(
            'adv_training_item__level_qualification').annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('distribution'),
            form2_sum=Sum('payment_form2')
        )


class DistributionAdvTrainingSailorReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionAdvTrainingSailorFilter
    serializer_class = reports.back_office_report.serializers.DistributionAdvTrainingSailorSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[8], name_field='to_cec')
        return queryset.exclude(content_type_id=61).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2')
        )


class AdvTrainingXlsxReportView(DistributionAdvTrainingSailorReportView):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        sailor.tasks.save_history.s(
            user_id=self.request.user.pk,
            module='Report BO КПК',
            action_type='generate xlsx',
            new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)},
        ).apply_async()
        attrs = [
            [
                ('ID моряка', dep.packet_item.sailor_id),
                ('ПІБ моряка', dep.packet_item.sailor_full_name),
                ('Роздача', dep.distribution_sum),
                ('Прибуток', dep.profit_sum),
                ('Прихід', dep.form2_sum),
                ('Кваліфікація', dep.item.qualification.name_ukr),
                ('Дата створення заявки', dep.item.statement_advanced_training.created_at.strftime('%d-%m-%Y')
                if hasattr(dep.item.statement_advanced_training, 'created_at') else None),
            ] for dep in queryset]
        if not queryset.exists():
            attrs.append([
                ('ID моряка', ''),
                ('ПІБ моряка', ''),
                ('Роздача', ''),
                ('Прибуток', ''),
                ('Прихід', ''),
                ('Кваліфікація', ''),
                ('Дата створення заявки', ''),
            ])
        reports.tasks.generate_report_back_office.s('Роздача прихід КПК', request.user, attrs).apply_async()
        return Response(status=200)


class DistributionMedicalInstitutionReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.GlobalPacketDateFilter
    serializer_class = reports.back_office_report.serializers.DistributionMedicalInstitutionSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[7], name_field='to_medical')
        queryset = queryset.annotate(medical=Case(
            When(Q(medical_cert_item__isnull=False),
                 then='medical_cert_item__doctor__medical_institution'),
            When(Q(statement_medical_cert_item__isnull=False),
                 then='statement_medical_cert_item__medical_institution'),
            output_field=IntegerField()
        ))
        return queryset.values(
            'medical'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2'),
            count=Count('medical')
        )


class DistributionDoctorReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionMedicalInstitutionFilter
    serializer_class = reports.back_office_report.serializers.DistributionDoctorSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[7], name_field='to_medical')
        queryset = queryset.annotate(doctor=Case(
            When(Q(medical_cert_item__isnull=False),
                 then='medical_cert_item__doctor'),
            When(Q(statement_medical_cert_item__isnull=False),
                 then=0),
            output_field=IntegerField()
        ))
        return queryset.values(
            'doctor'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2'),
            count=Count('doctor')
        )


class DistributionMedicalSailorReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionDoctorFilter
    serializer_class = reports.back_office_report.serializers.DistributionMedicalSailorSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[7], name_field='to_medical')
        return queryset.annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2'))


class MedicalXlsxReportView(DistributionMedicalSailorReportView):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        sailor.tasks.save_history.s(
            user_id=self.request.user.pk,
            module='Report BO Medical',
            action_type='generate xlsx',
            new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)},
        ).apply_async()
        attrs = [
            [
                ('ID моряка', dep.item.sailor_id),
                ('ПІБ моряка', dep.item.sailor_full_name),
                ('Роздача', dep.distribution_sum),
                ('Прибуток', dep.profit_sum),
                ('Прихід', dep.form2_sum),
                ('Посада', dep.item.position.name_ukr),
                ('Дата створення заявки',
                 dep.item.medical_statement.created_at if hasattr(dep.item.medical_statement, 'created_at') else None),
                ('Доктор', dep.item.doctor.FIO),
                ('Мед заклад', dep.item.doctor.medical_institution.value),
            ] for dep in queryset]
        if not queryset.exists():
            attrs.append([
                ('ID моряка', ''),
                ('ПІБ моряка', ''),
                ('Роздача', ''),
                ('Прибуток', ''),
                ('Прихід', ''),
                ('Посада', ''),
                ('Дата створення заявки', ''),
                ('Доктор', ''),
                ('Мед заклад', ''),
            ])
        reports.tasks.generate_report_back_office.s('Роздача прихід Мед заклади', request.user, attrs).apply_async()
        return Response(status=200)


class DistributionSQCReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionSQCFilter
    serializer_class = reports.back_office_report.serializers.DistributionSQCSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[1, 2, 17], name_field='to_sqc')
        return queryset.values(
            'packet_item__agent__userprofile__agent_group'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('distribution'),
            form2_sum=Sum('payment_form2')
        )


class DistributionSQCAgentReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionSQCGroupFilter
    serializer_class = reports.back_office_report.serializers.DistributionSQCGroupSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[1, 2, 17], name_field='to_sqc')
        return queryset.values(
            'packet_item__agent'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('distribution'),
            form2_sum=Sum('payment_form2')
        )


class DistributionSQCSailorReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionSQCSailorFilter
    serializer_class = reports.back_office_report.serializers.DistributionSQCSailorSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[1, 2, 17], name_field='to_sqc')
        return queryset.annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2')
        )


class SQCXlsxReportView(DistributionSQCSailorReportView):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        is_exp = False
        if request.query_params['with_exp'] == 'true':
            is_exp = True
        queryset = self.filter_queryset(self.get_queryset())
        sailor.tasks.save_history.s(
            user_id=self.request.user.pk,
            module='Report BO SQC {}'.format('with exp' if is_exp else 'without exp'),
            action_type='generate xlsx',
            new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)},
        ).apply_async()
        attrs = [
            [
                ('ID моряка', dep.packet_item.sailor_id),
                ('ПІБ моряка', dep.packet_item.sailor_full_name),
                ('Роздача', dep.distribution_sum),
                ('Прибуток', dep.profit_sum),
                ('Прихід', dep.form2_sum),
                ('Дата створення заяви', dep.item.created_at.strftime('%d-%m-%Y')),
                ('Звання', dep.packet_item.rank['name_ukr']),
                ('Довірена особа', dep.packet_item.get_agent_full_name),
                ('Група',
                 dep.packet_item.agent.userprofile.agent_group.first().name_ukr
                 if dep.packet_item.agent.userprofile.agent_group.exists() else None),
            ] for dep in queryset]
        if not queryset.exists():
            attrs.append([
                ('ID моряка', ''),
                ('ПІБ моряка', ''),
                ('Роздача', ''),
                ('Прибуток', ''),
                ('Прихід', ''),
                ('Дата створення заяви', ''),
                ('Звання', ''),
                ('Довірена особа', ''),
                ('Група', ''),
            ])
        description = 'Роздача прихід ДКК {}'.format('зі стажем' if is_exp else 'без стажу')
        reports.tasks.generate_report_back_office.s(description, request.user, attrs).apply_async()
        return Response(status=200)


class DistributionServiceCenterReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.GlobalPacketDateFilter
    serializer_class = reports.back_office_report.serializers.DistributionServiceCenterSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[10], name_field='to_sc')
        return queryset.values(
            'packet_item__service_center'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('distribution'),
            form2_sum=Sum('payment_form2')
        )


class DistributionServiceCenterAgentReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionServiceCenterFilter
    serializer_class = reports.back_office_report.serializers.DistributionSQCGroupSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[10], name_field='to_sc')
        return queryset.values(
            'packet_item__agent'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('distribution'),
            form2_sum=Sum('payment_form2')
        )


class DistributionServiceCenterSailorReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionServiceCenterAgentFilter
    serializer_class = reports.back_office_report.serializers.DistributionServiceCenterSailorSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[10], name_field='to_sc')
        return queryset.annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2')
        )


class ServiceCenterXlsxReportView(DistributionServiceCenterSailorReportView):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        sailor.tasks.save_history.s(
            user_id=self.request.user.pk,
            module='Report BO Service Center',
            action_type='generate xlsx',
            new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)},
        ).apply_async()
        attrs = [
            [
                ('ID моряка', dep.packet_item.sailor_id),
                ('ПІБ моряка', dep.packet_item.sailor_full_name),
                ('Роздача', dep.distribution_sum),
                ('Прибуток', dep.profit_sum),
                ('Прихід', dep.form2_sum),
                ('Дата створення пакету', dep.packet_item.created_at.strftime('%d-%m-%Y')),
                ('Звання', dep.packet_item.rank['name_ukr']),
                ('Довірена особа', dep.packet_item.get_agent_full_name),
                ('Сервісний Центр', dep.packet_item.service_center.name_ukr),
            ] for dep in queryset]
        if not queryset.exists():
            attrs.append([
                ('ID моряка', ''),
                ('ПІБ моряка', ''),
                ('Роздача', ''),
                ('Прибуток', ''),
                ('Прихід', ''),
                ('Дата створення пакету', ''),
                ('Звання', ''),
                ('Довірена особа', ''),
                ('Сервісний Центр', ''),
            ])
        reports.tasks.generate_report_back_office.s('Роздача прихід Сервісний Центр', request.user, attrs).apply_async()
        return Response(status=200)


class DistributionPortalReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.GlobalPacketDateFilter
    serializer_class = reports.back_office_report.serializers.DistributionServiceCenterSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=list(range(1, 15)), name_field='to_portal')
        return queryset.exclude(
            distribution=0
        ).values(
            'packet_item__service_center'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('distribution'),
            form2_sum=Sum('payment_form2')
        )


class DistributionPortalAgentReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionServiceCenterFilter
    serializer_class = reports.back_office_report.serializers.DistributionSQCGroupSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=list(range(1, 15)), name_field='to_portal')
        return queryset.exclude(
            distribution=0
        ).values(
            'packet_item__agent'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('distribution'),
            form2_sum=Sum('payment_form2')
        )


class DistributionPortalSailorReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionServiceCenterAgentFilter
    serializer_class = reports.back_office_report.serializers.DistributionServiceCenterSailorSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=list(range(1, 15)), name_field='to_portal')
        return queryset.exclude(
            distribution=0
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2')
        )


class PortalXlsxReportView(DistributionPortalSailorReportView):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        sailor.tasks.save_history.s(
            user_id=self.request.user.pk,
            module='Report BO Portal',
            action_type='generate xlsx',
            new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)},
        ).apply_async()
        attrs = [
            [
                ('ID моряка', dep.packet_item.sailor_id),
                ('ПІБ моряка', dep.packet_item.sailor_full_name),
                ('Роздача', dep.distribution_sum),
                ('Прибуток', dep.profit_sum),
                ('Прихід', dep.form2_sum),
                ('Дата створення пакету', dep.packet_item.created_at.strftime('%d-%m-%Y')),
                ('Звання', dep.packet_item.rank['name_ukr']),
                ('Довірена особа', dep.packet_item.get_agent_full_name),
                ('Портал', dep.packet_item.service_center.name_ukr),
            ] for dep in queryset]
        if not queryset.exists():
            attrs.append([
                ('ID моряка', ''),
                ('ПІБ моряка', ''),
                ('Роздача', ''),
                ('Прибуток', ''),
                ('Прихід', ''),
                ('Дата створення пакету', ''),
                ('Звання', ''),
                ('Довірена особа', ''),
                ('Портал', ''),
            ])
        reports.tasks.generate_report_back_office.s('Роздача прихід Портал', request.user, attrs).apply_async()
        return Response(status=200)


class DistributionAgentGroupReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionAgentGroupFilter
    serializer_class = reports.back_office_report.serializers.DistributionSQCSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[9, 20], name_field='to_agent')
        return queryset.values(
            'packet_item__agent__userprofile__agent_group'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('distribution'),
            form2_sum=Sum('payment_form2')
        )


class DistributionAgentsReportView(BaseDistributionReport):
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = reports.back_office_report.filters.DistributionGroupFilter
    serializer_class = reports.back_office_report.serializers.DistributionSQCGroupSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[9, 20], name_field='to_agent')
        return queryset.values(
            'packet_item__agent'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('distribution'),
            form2_sum=Sum('payment_form2')
        )


class DistributionAgentSailorReportView(BaseDistributionReport):
    filter_class = reports.back_office_report.filters.DistributionAgentFilter
    serializer_class = reports.back_office_report.serializers.DistributionServiceCenterSailorSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item(type_document=[9, 20], name_field='to_agent')
        return queryset.annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2')
        )


class AgentXlsxReportView(DistributionAgentSailorReportView):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        sailor.tasks.save_history.s(
            user_id=self.request.user.pk,
            module='Report BO Довірена особа',
            action_type='generate xlsx',
            new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)},
        ).apply_async()
        attrs = [
            [
                ('ID моряка', dep.packet_item.sailor_id),
                ('ПІБ моряка', dep.packet_item.sailor_full_name),
                ('Роздача', dep.distribution_sum),
                ('Прибуток', dep.profit_sum),
                ('Прихід', dep.form2_sum),
                ('Дата створення пакету', dep.packet_item.created_at.strftime('%d-%m-%Y')),
                ('Звання', dep.packet_item.rank['name_ukr']),
                ('Довірена особа', dep.packet_item.get_agent_full_name),
                ('Група',
                 dep.packet_item.agent.userprofile.agent_group.first().name_ukr
                 if dep.packet_item.agent.userprofile.agent_group.exists() else None),
            ] for dep in queryset]
        if not queryset.exists():
            attrs.append([
                ('ID моряка', ''),
                ('ПІБ моряка', ''),
                ('Роздача', ''),
                ('Прибуток', ''),
                ('Прихід', ''),
                ('Дата створення пакету', ''),
                ('Звання', ''),
                ('Довірена особа', ''),
                ('Група', ''),
            ])
        reports.tasks.generate_report_back_office.s('Роздача прихід Довірена особа', request.user, attrs).apply_async()
        return Response(status=200)


class DistributionETIReportView(BaseDistributionReport):
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = reports.back_office_report.filters.GlobalPacketDateFilter
    serializer_class = reports.back_office_report.serializers.DistributionETISerializer

    def get_dependency_item(self) -> QuerySet[DependencyItem]:
        if getattr(self, 'swagger_fake_view', False):
            return DependencyItem.objects.none()
        percent_for_course = ETIProfitPart.objects.values('percent_of_eti', 'date_start', 'date_end')
        annotations = {'distribution': []}
        for course_percent in percent_for_course:
            if course_percent.get('date_end'):
                annotations['distribution'].append(When(
                    Q(type_document_id=12) &
                    Q(packet_item__payment_date__date__gte=course_percent.get('date_start')) &
                    Q(packet_item__payment_date__date__lte=course_percent.get('date_end')),
                    then=F('payment_form2') / Value(100) * Value(course_percent.get('percent_of_eti'))))
            else:
                annotations['distribution'].append(When(
                    Q(type_document_id=12) &
                    Q(packet_item__payment_date__date__gte=course_percent.get('date_start')),
                    then=F('payment_form2') / Value(100) * Value(course_percent.get('percent_of_eti'))))
        qs = DependencyItem.objects.filter(
            type_document_id=12, packet_item__is_payed=True
        ).exclude(
            content_type__id=76
        ).exclude(
            item_status=DependencyItem.WAS_BE
        ).exclude(packet_item__agent__userprofile__type_user='marad').annotate(
            distribution=Case(*annotations.get('distribution'), default=Value(-1), output_field=FloatField()),
            profit=F('payment_form2') - F('distribution')
        )
        return qs

    def get_queryset(self):
        queryset = self.get_dependency_item()
        queryset = queryset.annotate(eti=Case(
            When(Q(statement_eti_item__isnull=False),
                 then='statement_eti_item__institution'),
            When(Q(cert_item__isnull=False),
                 then='cert_item__ntz'),
            output_field=IntegerField()
        ))
        return queryset.values(
            'eti'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('eti'),
            form2_sum=Sum('payment_form2')
        )


class DistributionETICoursesReportView(DistributionETIReportView):
    filter_class = reports.back_office_report.filters.DistributionETICoursesFilter
    serializer_class = reports.back_office_report.serializers.DistributionETICoursesSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item()
        queryset = queryset.annotate(course=Case(
            When(Q(statement_eti_item__isnull=False),
                 then='statement_eti_item__course'),
            When(Q(cert_item__isnull=False),
                 then='cert_item__course_training'),
            output_field=IntegerField()
        ))
        return queryset.values(
            'course'
        ).annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), count=Count('course'),
            form2_sum=Sum('payment_form2')
        )


class DistributionETISailorReportView(DistributionETIReportView):
    filter_class = reports.back_office_report.filters.DistributionETISailorFilter
    serializer_class = reports.back_office_report.serializers.DistributionETISailorSerializer

    def get_queryset(self):
        queryset = self.get_dependency_item()
        return queryset.annotate(
            distribution_sum=Sum('distribution'), profit_sum=Sum('profit'), form2_sum=Sum('payment_form2')
        )


class ETIXlsxReportView(DistributionETISailorReportView):

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        sailor.tasks.save_history.s(
            user_id=self.request.user.pk,
            module='Report BO ETI',
            action_type='generate xlsx',
            new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)},
        ).apply_async()
        attrs = [
            [
                ('ID моряка', dep.packet_item.sailor_id),
                ('ПІБ моряка', dep.packet_item.sailor_full_name),
                ('Номер сертифіката/заяви', dep.item.number),
                ('Роздача', dep.distribution_sum),
                ('Прибуток', dep.profit_sum),
                ('Прихід', dep.form2_sum),
                ('Дата початку дії сертифіката/Дата події', dep.item.date_for_report),
                ('НТЗ', dep.item.institution_name_ukr),
                ('Курс', dep.item.course_name_ukr),
                ('Довірена особа', dep.packet_item.agent.userprofile.full_name_ukr),
            ]
            for dep in queryset]
        if not queryset.exists():
            attrs.append([
                ('ID моряка', ''),
                ('ПІБ моряка', ''),
                ('Номер сертифіката/заяви', ''),
                ('Роздача', ''),
                ('Прибуток', ''),
                ('Прихід', ''),
                ('Дата початку дії сертифіката/Дата події', ''),
                ('НТЗ', ''),
                ('Курс', ''),
                ('Довірена особа', ''),
            ])
        reports.tasks.generate_report_back_office.s('Роздача прихід НТЗ', request.user, attrs).apply_async()
        return Response(status=200)
