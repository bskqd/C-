from django_filters import rest_framework as filters

from .models import City


class CityFilter(filters.FilterSet):
    value = filters.CharFilter(field_name='value', lookup_expr='icontains')

    class Meta:
        model = City
        fields = ['value', 'region']
