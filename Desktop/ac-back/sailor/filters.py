from django_filters import rest_framework as filters

from user_profile.models import FullUserSailorHistory


class FullUserSailorHistoryFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name='datetime__date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='datetime__date', lookup_expr='lte')
    user = filters.CharFilter(method='user_filter')
    sailor_key = filters.NumberFilter(field_name='sailor_key')

    class Meta:
        model = FullUserSailorHistory
        fields = ('date_from', 'date_to')

    def user_filter(self, queryset, name, value):
        user_ids = value.split(',')
        return queryset.filter(user_id__in=user_ids)