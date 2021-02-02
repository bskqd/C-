from collections import OrderedDict

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from reports.filters import ShortLinkResultPagination
from sailor.document.models import CertificateETI
from sailor.statement.models import StatementETI
from integrations.eti_online import serializers
from rest_framework import mixins
import rest_framework.permissions
from django_filters import rest_framework as filters


class ETIOnlinePaginator(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 500

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('current', self.page.number),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('total_pages', self.page.paginator.num_pages),
        ]))


class StatementETIView(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.RetrieveModelMixin):
    queryset = StatementETI.objects.all()
    serializer_class = serializers.ETIOnlineStatementSerializer
    pagination_class = ShortLinkResultPagination
    permission_classes = (rest_framework.permissions.IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('status_document',)

    def get_queryset(self):
        institution_id = self.kwargs.get('institution_id')
        return self.queryset.filter(
            institution_id=institution_id,
            status_document_id__in=(StatementETI.StatusDocument.APPROVED, StatementETI.StatusDocument.COURSE_ASSIGNED)
        )


class CertificateETIView(viewsets.GenericViewSet,
                         mixins.CreateModelMixin, mixins.UpdateModelMixin):
    queryset = CertificateETI.objects.all()
    serializer_class = serializers.ETIOnlineCertificateETISerializer
    permission_classes = (rest_framework.permissions.IsAuthenticated, )
