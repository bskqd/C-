import rest_framework.permissions
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters

import notifications.serializers
from core.mixins import StandardResultsSetPagination
from notifications.models import UserNotification


class NotificationByUser(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet,):
    queryset = UserNotification.objects.all()
    serializer_class = notifications.serializers.NotificationByUserSerializer
    permission_classes = (rest_framework.permissions.IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['is_hidden']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserNotification.objects.none()
        return self.queryset.filter(recipient=self.request.user)

    @action(methods=['get'], detail=False)
    def count(self, request, *args, **kwargs):
        count_notification = self.get_queryset().filter(is_hidden=False).count()
        return Response({'count': count_notification})

    @action(methods=['post'], detail=False)
    def clear_notifications(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(is_hidden=False).update(is_hidden=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
