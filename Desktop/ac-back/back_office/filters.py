from django_filters import rest_framework as filters


class ETIReportFilter(filters.FilterSet):
    from_date = filters.DateFilter(field_name='date_start', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='date_start', lookup_expr='lte')


class PacketReportFilter(filters.FilterSet):
    number = filters.CharFilter(method='packet_number_filter')
    sailor_id = filters.CharFilter(method='packet_sailor_id_filter')
    price_f1_eq = filters.CharFilter(field_name='payment_form1')
    price_f1_gte = filters.CharFilter(field_name='payment_form1', lookup_expr='gte')
    price_f1_lte = filters.CharFilter(field_name='payment_form1', lookup_expr='lte')
    price_f2_eq = filters.CharFilter(field_name='payment_form2')
    price_f2_gte = filters.CharFilter(field_name='payment_form2', lookup_expr='gte')
    price_f2_lte = filters.CharFilter(field_name='payment_form2', lookup_expr='lte')
    type_document = filters.CharFilter(method='packet_type_document_filter')
    payment_date_eq = filters.DateFilter(field_name='packet_item__payment_date', lookup_expr='date')
    payment_date_from = filters.DateFilter(field_name='packet_item__payment_date__date', lookup_expr='gte')
    payment_date_to = filters.DateFilter(field_name='packet_item__payment_date__date', lookup_expr='lte')

    def packet_number_filter(self, queryset, name, value):
        packet_numbers = value.split(',')
        return queryset.filter(packet_item__number__in=packet_numbers)

    def packet_sailor_id_filter(self, queryset, name, value):
        sailor_ids = value.split(',')
        return queryset.filter(packet_item__sailor_id__in=sailor_ids)

    def packet_type_document_filter(self, queryset, name, value):
        type_documents = value.split(',')
        return queryset.filter(type_document_id__in=type_documents)

    ordering = filters.OrderingFilter(
        fields=(
            ('packet_item__payment_date', 'paymentDate'),
            ('payment_form1', 'paymentF1'),
            ('payment_form2', 'paymentF2'),
            ('packet_item__number', 'packetNumber'),
            ('packet_item__sailor_id', 'sailorID'),
            ('type_document__value', 'typeDocument'),
        )
    )
