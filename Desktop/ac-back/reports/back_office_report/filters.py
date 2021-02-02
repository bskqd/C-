from django.db.models import Q
from django_filters import rest_framework as filters


class ItemStatusGlobalFilter(filters.FilterSet):
    item_status = filters.CharFilter(method='item_status_filter')

    def item_status_filter(self, queryset, name, value):
        values = value.split(',')
        values_converter = {'true': 'Was bought', 'false': 'To buy'}
        item_status_filtration = [values_converter[value] for value in values]
        return queryset.filter(item_status__in=item_status_filtration)


class GlobalPacketDateFilter(ItemStatusGlobalFilter):
    payment_from_date = filters.DateFilter(field_name='packet_item__payment_date__date', lookup_expr='gte')
    payment_to_date = filters.DateFilter(field_name='packet_item__payment_date__date', lookup_expr='lte')
    created_from_date = filters.DateFilter(field_name='packet_item__created_at__date', lookup_expr='gte')
    created_to_date = filters.DateFilter(field_name='packet_item__created_at__date', lookup_expr='lte')

    receipt_from_date = filters.DateFilter(method='receipt_from_date_filter')
    receipt_to_date = filters.DateFilter(method='receipt_to_date_filter')

    def receipt_from_date_filter(self, queryset, name, value):
        qs = queryset.filter(
            Q(proof_documents__date_start__gte=value) |
            Q(qualification_documents__date_start__gte=value) |
            Q(sailor_passport_document__date_start__gte=value) |
            Q(sailor_passport_document__date_renewal__gte=value) |
            Q(service_record_documents__date_issued__gte=value) |
            Q(education_documents__date_issue_document__gte=value) |
            Q(protocol_documents__date_meeting__gte=value) |
            Q(cert_item__date_start__gte=value) |
            Q(medical_cert_item__date_start__gte=value)
        )
        return qs

    def receipt_to_date_filter(self, queryset, name, value):
        qs = queryset.filter(
            Q(proof_documents__date_start__lte=value) |
            Q(qualification_documents__date_start__lte=value) |
            Q(sailor_passport_document__date_start__lte=value) |
            Q(sailor_passport_document__date_renewal__lte=value) |
            Q(service_record_documents__date_issued__lte=value) |
            Q(education_documents__date_issue_document__lte=value) |
            Q(protocol_documents__date_meeting__lte=value) |
            Q(cert_item__date_start__lte=value) |
            Q(medical_cert_item__date_start__lte=value)
        )
        return qs


class GlobalPacketGroupFilter(GlobalPacketDateFilter):
    group = filters.NumberFilter(field_name='packet_item__agent__userprofile__agent_group')
    group__is_null = filters.BooleanFilter(field_name='packet_item__agent__userprofile__agent_group',
                                           lookup_expr='isnull')


class GlobalPacketAgentFilter(GlobalPacketGroupFilter):
    agent = filters.NumberFilter(field_name='packet_item__agent')


class GlobalPacketSailorFilter(GlobalPacketAgentFilter):
    sailor_id = filters.NumberFilter(field_name='packet_item__sailor_id')


class GlobalPacketPacketFilter(GlobalPacketSailorFilter):
    packet_item = filters.NumberFilter(field_name='packet_item')


class GlobalPacketDocumentFilter(GlobalPacketSailorFilter):
    id = filters.NumberFilter(field_name='id')


class DPDBaseFilter(GlobalPacketDateFilter, ItemStatusGlobalFilter):
    pass


class DistributionDPDDocumentFilter(DPDBaseFilter):
    branch_office = filters.NumberFilter(field_name='packet_item__service_center')


class AdvTrainingBaseFilter(GlobalPacketDateFilter, ItemStatusGlobalFilter):
    # receipt_from_date = filters.DateFilter(method='receipt_from_date_filter')
    # receipt_to_date = filters.DateFilter(method='receipt_to_date_filter')
    #
    # def receipt_from_date_filter(self, queryset, name, value):
    #     return queryset.filter(
    #         Q(proof_documents__date_start__gte=value) |
    #         Q(qualification_documents__date_start__gte=value)
    #     )
    #
    # def receipt_to_date_filter(self, queryset, name, value):
    #     return queryset.filter(
    #         Q(proof_documents__date_start__lte=value) |
    #         Q(qualification_documents__date_start__lte=value)
    #     )
    pass


class DistributionAdvTrainingSailorFilter(AdvTrainingBaseFilter):
    level = filters.NumberFilter(field_name='adv_training_item__level_qualification')


class DistributionMedicalInstitutionFilter(AdvTrainingBaseFilter):
    medical = filters.CharFilter(method='medical_institution_filter')

    def medical_institution_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(medical_cert_item__doctor__medical_institution=value) |
                                   Q(statement_medical_cert_item__medical_institution=value))
        return queryset


class DistributionDoctorFilter(DistributionMedicalInstitutionFilter, ItemStatusGlobalFilter):
    doctor = filters.CharFilter(method='doctor_filter')

    def doctor_filter(self, queryset, name, value):
        if value == '0':
            queryset = queryset.filter(statement_medical_cert_item__medical_institution__isnull=False)
        else:
            queryset = queryset.filter(medical_cert_item__doctor=int(value))
        return queryset


class DistributionSQCFilter(GlobalPacketDateFilter, ItemStatusGlobalFilter):
    with_exp = filters.CharFilter(method='with_exp_filter')
    is_cadet = filters.BooleanFilter(method='cadet_filter')

    def with_exp_filter(self, queryset, name, value):
        if value == 'true':
            return queryset.filter(type_document_id=2)
        elif value == 'false':
            return queryset.filter(type_document_id=1)
        return queryset

    def cadet_filter(self, queryset, name, value):
        if value:
            return queryset.filter(type_document_id=17)
        return queryset


class DistributionSQCGroupFilter(DistributionSQCFilter, ItemStatusGlobalFilter):
    group = filters.CharFilter(method='sqc_group_filter')

    def sqc_group_filter(self, queryset, name, value):
        if value == '0':
            return queryset.filter(packet_item__agent__userprofile__agent_group__isnull=True)
        return queryset.filter(packet_item__agent__userprofile__agent_group=int(value))


class DistributionSQCSailorFilter(GlobalPacketAgentFilter, DistributionSQCGroupFilter,
                                  ItemStatusGlobalFilter):
    pass


class DistributionServiceCenterFilter(GlobalPacketDateFilter, ItemStatusGlobalFilter):
    branch_office = filters.NumberFilter(field_name='packet_item__service_center')


class DistributionServiceCenterAgentFilter(DistributionServiceCenterFilter, ItemStatusGlobalFilter):
    agent = filters.NumberFilter(field_name='packet_item__agent')


class DistributionETICoursesFilter(GlobalPacketDateFilter, ItemStatusGlobalFilter):
    institution = filters.CharFilter(method='institution_eti_filter')

    def institution_eti_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(statement_eti_item__institution=value) |
                                   Q(cert_item__ntz=value))
        return queryset


class DistributionETISailorFilter(DistributionETICoursesFilter):
    course = filters.CharFilter(method='courses_eti_filter')

    def courses_eti_filter(self, queryset, name, value):
        queryset = queryset.filter(Q(statement_eti_item__course=value) |
                                   Q(cert_item__course_training=value))
        return queryset


class DistributionAgentGroupFilter(GlobalPacketDateFilter, ItemStatusGlobalFilter):
    is_cadet = filters.BooleanFilter(method='cadet_filter')

    def cadet_filter(self, queryset, name, value):
        if value:
            return queryset.filter(type_document_id=20)
        return queryset.exclude(type_document_id=20)


class DistributionGroupFilter(DistributionAgentGroupFilter, ItemStatusGlobalFilter):
    group = filters.CharFilter(method='agent_group_filter')

    def agent_group_filter(self, queryset, name, value):
        if value == '0':
            return queryset.filter(packet_item__agent__userprofile__agent_group__isnull=True)
        return queryset.filter(packet_item__agent__userprofile__agent_group=int(value))


class DistributionAgentFilter(DistributionGroupFilter, ItemStatusGlobalFilter):
    agent = filters.NumberFilter(field_name='packet_item__agent')
