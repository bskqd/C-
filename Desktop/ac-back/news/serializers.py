from django.conf import settings
from rest_framework.serializers import ModelSerializer

from news.models import News
from news.utils import get_base64_encoded


class NewsSerializer(ModelSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.pk,
            'image': get_base64_encoded(instance.image.path) or get_base64_encoded(
                settings.MEDIA_ROOT + '/default_profile.png'),
            'title': instance.title,
            'description': instance.short_text or instance.full_text[:100],
            'created_at': instance.created_at.isoformat(),
            'source_url': instance.source_url
        }

    class Meta:
        model = News
        fields = ('id', 'image', 'title', 'short_text', 'full_text', 'created_at', 'source_url')


class DetailNewsSerializer(ModelSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.pk,
            'image': get_base64_encoded(instance.image.path) or get_base64_encoded(
                settings.MEDIA_ROOT + '/default_profile.png'),
            'title': instance.title,
            'description': instance.full_text,
            'created_at': instance.created_at.isoformat(),
            'source_url': instance.source_url
        }

    class Meta:
        model = News
        fields = ('id', 'image', 'title', 'full_text', 'created_at', 'source_url')
