from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from notifications.models import UserNotification


class NotificationByUserSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(slug_field='model', queryset=ContentType.objects.all())

    class Meta:
        model = UserNotification
        fields = ('id', 'title', 'text', 'is_hidden', 'date_send', 'content_type', 'object_id', 'ship_id')
        read_only_fields = ('title', 'text', 'date_send', 'content_type', 'object_id', 'ship_id')
