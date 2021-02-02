from rest_framework import serializers

from notifications.models import DevicesData, HistoryPushData, UserNotification


class SaveDeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevicesData
        fields = ['device', 'platform', 'id_device', 'user_id']

    def create(self, validated_data):
        id_device = validated_data['id_device']
        device = DevicesData.objects.filter(id_device=id_device)
        if device.exists():
            return device.first()
        return DevicesData.objects.create(**validated_data)


class HistoryPushDataSerializer(serializers.ModelSerializer):
    date_create = serializers.DateTimeField(source='created_at')

    class Meta:
        model = HistoryPushData
        fields = ('id', 'push_data', 'date_create')


class NotificationByUserSerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = ('id', 'title', 'text', 'is_hidden', 'date_send', 'content_type', 'object_id', 'sailor_id')
        read_only_fields = ('title', 'text', 'date_send', 'content_type', 'object_id', 'sailor_id')

    def get_content_type(self, instance):
        if instance.content_type:
            return instance.content_type.model
        return None
