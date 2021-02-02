from django.db.models import Q

from django_filters import rest_framework as filters

INPUT_FORMATS_DATE = ['%d.%m.%Y']


class UserFilters(filters.FilterSet):
    type_user = filters.CharFilter(field_name='type_user')
    search = filters.CharFilter(method='search_filter')
    date_joined = filters.DateTimeFilter(field_name='date_joined', lookup_expr='date',
                                         input_formats=INPUT_FORMATS_DATE)
    is_active = filters.BooleanFilter(field_name='is_active')

    def search_filter(self, queryset, name, value):
        queryset = queryset.filter(
            Q(full_name__icontains=value) | Q(email__icontains=value)
        )
        return queryset

    ordering = filters.OrderingFilter(
        fields=(
            ('date_joined', 'date_joined'),
            ('email', 'email'),
            ('type_user', 'type_user'),
            ('full_name', 'full_name'),
        )
    )
