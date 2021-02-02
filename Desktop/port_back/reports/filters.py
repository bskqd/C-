from itertools import chain

from django.db.models import CharField, Q
from django.db.models.functions import Cast
from django_filters import rest_framework as filters

from communication.models import ShipKey
from ship.models import MainInfo

INPUT_FORMATS_DATE = ['%d.%m.%Y']


class IORequestFilters(filters.FilterSet):
    type = filters.CharFilter(field_name='type')
    from_datetime_issued = filters.DateFilter(field_name='datetime_issued', lookup_expr='date__gte',
                                              input_formats=INPUT_FORMATS_DATE)
    to_datetime_issued = filters.DateFilter(field_name='datetime_issued', lookup_expr='date__lte',
                                            input_formats=INPUT_FORMATS_DATE)
    from_datetime_io = filters.DateFilter(field_name='datetime_io', lookup_expr='date__gte',
                                          input_formats=INPUT_FORMATS_DATE)
    to_datetime_io = filters.DateFilter(field_name='datetime_io', lookup_expr='date__lte',
                                        input_formats=INPUT_FORMATS_DATE)
    port = filters.CharFilter(method='port_filters')
    number = filters.NumberFilter()
    next_port = filters.CharFilter(lookup_expr='icontains')
    cargo = filters.CharFilter(lookup_expr='icontains')
    status = filters.CharFilter(method='status_filters')
    search = filters.CharFilter(method='search_ship_filter')
    agency = filters.CharFilter(method='agency_filters')
    is_payed = filters.BooleanFilter(field_name='is_payed')

    ordering = filters.OrderingFilter(
        fields=(
            ('datetime_issued', 'datetime_issued'),
            ('datetime_io', 'datetime_io'),
            ('number', 'number'),
            ('created_at__year', 'second_number'),
            ('port__name', 'port'),
            ('status_document__name', 'status_document'),
            ('created_at', 'created_at'),
            ('modified_at', 'modified_at'),
            ('agency', 'agency')
        )
    )

    def port_filters(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(port_id__in=ids)

    def status_filters(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(status_document_id__in=ids)

    def search_ship_filter(self, queryset, name, value):
        ships = list(MainInfo.objects.annotate(imo_number_char=Cast('imo_number', CharField())
                                               ).filter(Q(imo_number_char__contains=value) | Q(name__icontains=value)
                                                        ).values_list('id', flat=True))
        io_request_list = list(ShipKey.objects.filter(maininfo__in=ships).values_list('iorequest', flat=True))
        io_request_ids = set(chain.from_iterable(io_request_list))
        queryset = queryset.filter(Q(id__in=io_request_ids) | Q(ship_name__icontains=value))
        return queryset

    def agency_filters(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(author__agent__agency_id__in=ids)
