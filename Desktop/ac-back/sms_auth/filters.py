from django.db.models import Value
from django.db.models.functions import Concat
from django_filters import rest_framework as filters


class SailorStatementVerificationFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    sailor_name = filters.CharFilter(method='sailor_name_filter')

    def sailor_name_filter(self, queryset, name, value):
        qs = queryset.annotate(fullname_ukr=Concat('last_name', Value(' '), 'first_name', Value(' '), 'middle_name'))
        return qs.filter(fullname_ukr__icontains=value)
