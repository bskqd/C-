from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from news.models import News
from news.serializers import NewsSerializer, DetailNewsSerializer
import directory.permissions

# Create your views here.
from reports.filters import ShortLinkResultPagination


class NewsListViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = NewsSerializer
    detail_serializer_class = DetailNewsSerializer
    queryset = News.objects.all().order_by('-created_at')
    pagination_class = ShortLinkResultPagination
    permission_classes = (directory.permissions.IsSuperUserEdit, )

    def get_serializer_class(self):
        if self.action == 'retrieve' and hasattr(self, 'detail_serializer_class'):
            return self.detail_serializer_class
        return super(NewsListViewset, self).get_serializer_class()
