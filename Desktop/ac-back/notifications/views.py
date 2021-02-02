from datetime import datetime

import telebot
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework import viewsets, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
import rest_framework.permissions
from .models import DevicesData, HistoryPushData, UserNotification
from .serializer import SaveDeviceTokenSerializer, HistoryPushDataSerializer, NotificationByUserSerializer
from .tasks import save_endpoint_arn, send_push_notifications

TELEGRAM_URL = 'https://api.telegram.org/bot'
INFO_BOT_TOKEN = "1382186593:AAGked0FEQQw9ib-7wM1VTFPRCNtU46tD9g"
tbot = telebot.TeleBot(INFO_BOT_TOKEN)

User = get_user_model()


class UserDeviceInfo(CreateAPIView):
    """Информация об устройствах пользователей, использующих моб. приложение"""
    serializer_class = SaveDeviceTokenSerializer
    queryset = DevicesData.objects.all()
    permission_classes = (rest_framework.permissions.IsAuthenticated, rest_framework.permissions.IsAdminUser)

    def perform_create(self, serializer):
        username = serializer.initial_data['user']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError('User does not exists')
        id_device = serializer.initial_data['id_device']
        serializer.save(user=user)
        save_endpoint_arn.s(id_device=id_device).apply_async()


class HistoryPushDataView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin):
    queryset = HistoryPushData.objects.all()
    serializer_class = HistoryPushDataSerializer
    permission_classes = (rest_framework.permissions.IsAuthenticated, rest_framework.permissions.IsAdminUser)

    def get_queryset(self):
        return self.queryset.filter(user_device__user_id=self.request.user.id).order_by('created_at')


class NotificationByUser(mixins.ListModelMixin, viewsets.GenericViewSet, mixins.UpdateModelMixin):
    queryset = UserNotification.objects.all().order_by('-date_send')
    serializer_class = NotificationByUserSerializer
    permission_classes = (rest_framework.permissions.IsAuthenticated, rest_framework.permissions.IsAdminUser)
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['is_hidden']

    def get_queryset(self):
        return self.queryset.filter(recipient=self.request.user)
