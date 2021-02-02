from django.contrib.auth import get_user_model
from rest_framework import serializers

from communication.models import SailorKeys
from sailor.models import Profile

User = get_user_model()

class PhotoSerializer(serializers.RelatedField):
    """Загрузчик скан документов для верификации в ЛК"""
    def to_representation(self, obj):
        if not obj or obj == []:
            return [{'id': 0, 'photo': 'default_profile.png'}]
        if type(obj) is list:
            qs = list(self.queryset.filter(id__in=obj).values('id', 'photo'))
        else:
            return [{'id': 0, 'photo': 'default_profile.png'}]
        return qs

    def to_internal_value(self, data):
        pass


class ProfileSerializer(serializers.RelatedField):
    """Дополнительная информация о пользователе для верификации в ЛК"""
    def to_representation(self, obj):
        try:
            user = User.objects.get(username=obj)
        except User.DoesNotExist:
            return None
        try:
            sailor = SailorKeys.objects.get(user_id=user.id)
        except SailorKeys.DoesNotExist:
            return None
        try:
            profile = Profile.objects.get(id=sailor.profile)
        except Profile.DoesNotExist:
            return None
        return {'first_name_ukr': profile.first_name_ukr, 'last_name_ukr': profile.last_name_ukr,
                'middle_name_ukr': profile.middle_name_ukr, 'first_name_eng': profile.first_name_eng,
                'last_name_eng': profile.last_name_eng, 'middle_name_eng': profile.middle_name_eng,
                'date_birth': profile.date_birth}
