from django_filters import rest_framework as filters


class InvitationFilters(filters.FilterSet):
    agents = filters.BooleanFilter(field_name='created_user', lookup_expr='isnull')
