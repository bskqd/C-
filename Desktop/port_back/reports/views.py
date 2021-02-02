from datetime import datetime, timedelta

from django.db.models import Case, When, F, IntegerField, Q
from django_filters import rest_framework as filters
from rest_framework import mixins, viewsets, permissions

import reports.filters
import reports.serializers
from core.mixins import StandardResultsSetPagination
from core.models import User
from ship.models import IORequest


class IORequestView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = IORequest.objects.all().annotate(agency=Case(
        When(author__type_user=User.AGENT_CH, then=F('author__agent__agency')),
        When(author__type_user=User.HEAD_AGENCY_CH, then=F('author__head_agency__agency')),
        output_field=IntegerField()
    ))
    serializer_class = reports.serializers.IORequestReportSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = reports.filters.IORequestFilters
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.type_user in [User.HARBOR_MASTER_CH, User.HARBOR_WORKER_CH]:
            return queryset.filter(port__in=user.get_port)
        elif user.type_user in [User.BORDER_GUARD_CH, User.PORT_MANAGER_CH]:
            return queryset.filter(port__in=user.get_port,
                                   datetime_issued__gte=datetime.now() - timedelta(days=2))
        elif user.type_user in [User.HEAD_AGENCY_CH, User.AGENT_CH]:
            agency = user.get_agency
            return queryset.filter(Q(author__agent__agency=agency) | Q(author__head_agency__agency=agency))
        return queryset
