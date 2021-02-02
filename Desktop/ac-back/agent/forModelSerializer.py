from rest_framework import serializers

from communication.models import SailorKeys
from sailor.models import Profile


class SailorKeySerializer(serializers.RelatedField):

    def to_representation(self, obj):
        if type(obj) is int:
            try:
                qs = self.queryset.get(id=obj)
            except SailorKeys.DoesNotExist:
                return None
        else:
            qs = obj
        profile = Profile.objects.filter(id=qs.profile).first()
        return {'id': qs.id, 'last_name_ukr': profile.last_name_ukr, 'first_name_ukr': profile.first_name_ukr,
                'middle_name_ukr': profile.middle_name_ukr}

    def to_internal_value(self, data):
        if isinstance(data, int) or isinstance(data, str):
            return SailorKeys.objects.get(id=data)
