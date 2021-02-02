from django.contrib.auth import get_user_model
from django.db.models import Value
from django.db.models.functions import Concat

from django_filters import rest_framework as filters

from agent.models import StatementAgentSailor
from communication.models import SailorKeys
from sailor.models import Profile

User = get_user_model()


class AgentListFilter(filters.FilterSet):
    agent_name = filters.CharFilter(method='agent_name_filter')

    class Meta:
        model = User
        fields = ('agent_name',)

    def agent_name_filter(self, queryset, name, value):
        queryset = queryset.annotate(fullname=Concat('last_name', Value(' '), 'first_name', Value(' '),
                                                     'userprofile__middle_name'))
        return queryset.filter(fullname__icontains=value)


class StatementAgentSailorFilter(filters.FilterSet):
    agent_name = filters.CharFilter(method='agent_name_filter')
    sailor_name = filters.CharFilter(method='sailor_name_filter')
    sailor_key = filters.NumberFilter(field_name='sailor_key')
    date_create_from = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_create_to = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    date_create = filters.DateFilter(field_name='created_at', lookup_expr='date')
    date_end_proxy_from = filters.DateFilter(field_name='date_end_proxy', lookup_expr='gte')
    date_end_proxy_to = filters.DateFilter(field_name='date_end_proxy', lookup_expr='lte')
    date_end_proxy = filters.DateFilter(field_name='date_end_proxy')
    status_document = filters.CharFilter(method='status_document_filter')
    city = filters.CharFilter(field_name='agent__userprofile__city__value', lookup_expr='iexact')

    class Meta:
        model = StatementAgentSailor
        fields = ('agent_name', 'sailor_name', 'status_document', 'city')

    def agent_name_filter(self, queryset, name, value):
        queryset = queryset.annotate(fullname=Concat('agent__last_name', Value(' '), 'agent__first_name', Value(' '),
                                                     'agent__userprofile__middle_name'))
        return queryset.filter(fullname__icontains=value)

    def sailor_name_filter(self, queryset, name, value):
        qs = Profile.objects.annotate(fullname_ukr=Concat('last_name_ukr', Value(' '), 'first_name_ukr', Value(' '),
                                                          'middle_name_ukr'))
        profiles = list(qs.filter(fullname_ukr__icontains=value).values_list('id', flat=True))
        sailor_ids = list(SailorKeys.objects.filter(profile__in=profiles).values_list('id', flat=True))
        return queryset.filter(sailor_key__in=sailor_ids)

    def status_document_filter(self, queryset, name, value):
        status_ids = value.split(',')
        return queryset.filter(status_document_id__in=status_ids)

    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'dateCreate'),
            ('date_end_proxy', 'dateEndProxy'),
            ('status_document__name_ukr', 'statusDocument')
        )
    )
