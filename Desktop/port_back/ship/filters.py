from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import CharField, Q, Value
from django.db.models.functions import Cast, Concat
from django_filters import rest_framework as filters

from communication.models import ShipKey
from ship.models import IORequest, MainInfo, ShipAgentNomination
import port_back.constants

INPUT_FORMATS_DATE = ['%d.%m.%Y']


class IORequestFilters(filters.FilterSet):
    type = filters.TypedChoiceFilter(field_name='type')


class BaseShipFilter(filters.FilterSet):
    port = filters.CharFilter(method='port_filters')
    search = filters.CharFilter(method='search_ship_filter')

    def port_filters(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(port_id__in=ids)

    def search_ship_filter(self, queryset, name, value):
        ship_keys = list(MainInfo.objects.annotate(
            imo_number_char=Cast('imo_number', CharField())
        ).filter(
            Q(imo_number_char__contains=value) | Q(name__icontains=value)
        ).values_list('pk', flat=True))
        return queryset.filter(ship_key__in=ship_keys)


class ShipStaffFilters(filters.FilterSet):
    last_staff = filters.BooleanFilter(method='last_staff_filter')

    def last_staff_filter(self, queryset, name, value):
        """
        if value == True - get all staff of the ship from the last IO Request
        if value == False - get all staff of the ship excluding sailors from the last IO Request
        """
        ship_pk = self.request.parser_context['kwargs']['ship_pk']
        ship_key = ShipKey.objects.get(pk=ship_pk)
        io_request = IORequest.objects.filter(id__in=ship_key.iorequest).order_by('datetime_issued')
        if not io_request.exists():
            return queryset.none()
        last_staff = io_request.last().ship_staff.all()
        if value:
            return last_staff
        else:
            last_staff_ids = list(last_staff.values_list('id', flat=True))
            return queryset.exclude(id__in=last_staff_ids)


class AgentNominationFilter(BaseShipFilter):
    from_created_at = filters.DateFilter(field_name='created_at', lookup_expr='date__gte',
                                         input_formats=INPUT_FORMATS_DATE)
    to_created_at = filters.DateFilter(field_name='created_at', lookup_expr='date__lte',
                                       input_formats=INPUT_FORMATS_DATE)
    from_date_verification = filters.DateFilter(field_name='date_verification', lookup_expr='date__gte',
                                                input_formats=INPUT_FORMATS_DATE)
    to_date_verification = filters.DateFilter(field_name='date_verification', lookup_expr='date__lte',
                                              input_formats=INPUT_FORMATS_DATE)
    status = filters.CharFilter(method='status_filters')
    agency = filters.CharFilter(method='agency_filters')
    agent = filters.CharFilter(method='agent_filter')

    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('date_verification', 'date_verification'),
            ('agency__name', 'agency'),
            ('port__name', 'port'),
            ('status_document__name', 'status_document')
        )
    )

    def status_filters(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(status_document_id__in=ids)

    def agency_filters(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(agent__agency_id__in=ids)

    def agent_filter(self, queryset, name, value):
        queryset = queryset.annotate(
            agent_full_name=Concat('agent__last_name', Value(' '), 'agent__first_name', Value(' '),
                                   'agent__middle_name')
        ).filter(agent_full_name__icontains=value)
        return queryset


class ShipInPortFilter(BaseShipFilter):
    from_input_date = filters.DateFilter(field_name='input_datetime', lookup_expr='date__gte',
                                         input_formats=INPUT_FORMATS_DATE)
    to_input_date = filters.DateFilter(field_name='input_datetime', lookup_expr='date__lte',
                                       input_formats=INPUT_FORMATS_DATE)
    input_date = filters.DateFilter(field_name='input_datetime', lookup_expr='date',
                                    input_formats=INPUT_FORMATS_DATE)
    agency = filters.CharFilter(method='agency_filters')

    ordering = filters.OrderingFilter(
        fields=(
            ('input_datetime', 'input_datetime'),
            ('agency__name', 'agency'),
            ('port__name', 'port'),
        )
    )

    def agency_filters(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(agency_id__in=ids)


class ShipFilters(filters.FilterSet):
    search = filters.CharFilter(method='search_ship_filter')
    from_gross_tonnage = filters.NumberFilter(field_name='gross_tonnage', lookup_expr='gte')
    to_gross_tonnage = filters.NumberFilter(field_name='gross_tonnage', lookup_expr='lte')
    gross_tonnage = filters.NumberFilter(field_name='gross_tonnage')
    type_vessel = filters.CharFilter(method='type_vessel_filters')
    flag = filters.CharFilter(method='flag_filters')
    hide_without_nomination = filters.BooleanFilter(method='hide_without_nomination_filter')

    def hide_without_nomination_filter(self, queryset, name, value):
        user = self.request.user
        if value:
            nominations = ShipAgentNomination.objects.filter(
                Q(status_document_id=port_back.constants.ISSUED) &
                Q(date_verification__gte=datetime.now() - relativedelta(
                    months=port_back.constants.VALID_NOMINATION_MONTHS)) &
                (Q(agent__agent__agency=user.get_agency) | Q(agent__head_agency__agency=user.get_agency))
            )
            return queryset.filter(pk__in=list(nominations.values_list('ship_key', flat=True)))
        else:
            return queryset

    def search_ship_filter(self, queryset, name, value):
        queryset = queryset.annotate(
            imo_number_char=Cast('imo_number', CharField())
        ).filter(
            Q(imo_number_char__contains=value) | Q(name__icontains=value)
        )
        return queryset

    def type_vessel_filters(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(type_vessel_id__in=ids)

    def flag_filters(self, queryset, name, value):
        ids = value.split(',')
        return queryset.filter(flag_id__in=ids)

    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('imo_number', 'imo_number'),
            ('gross_tonnage', 'gross_tonnage'),
            ('type_vessel__name', 'type_vessel'),
            ('flag__name', 'flag'),
        )
    )
