from django_filters import rest_framework as filters

from certificates.models import ETIRegistry


class ETIRegistryFilters(filters.FilterSet):
    institution = filters.CharFilter(method='institution_filter', label='Array of institutions')
    is_red = filters.BooleanFilter(field_name='institution__is_red')
    course = filters.NumberFilter(field_name='course_id')

    class Meta:
        model = ETIRegistry
        fields = ('date_start', 'date_end', 'number_protocol', 'institution', 'course')

    def institution_filter(self, queryset, name, value):
        institution_id = value.split(',')
        return queryset.filter(id__in=institution_id)


class ETIMonthRatioFilter(filters.FilterSet):
    city = filters.CharFilter(field_name='institution__address', lookup_expr='icontains')
    course = filters.NumberFilter(field_name='course_id')
