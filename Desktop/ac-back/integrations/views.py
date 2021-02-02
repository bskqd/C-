# Create your views here.
import json

from rest_framework import exceptions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from communication.models import SailorKeys
from core.models import User
from sailor.models import Profile, ContactInfo
from rest_framework import permissions


class SearchSailorView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, sailor_id):
        try:
            sailor_key = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise exceptions.NotFound('Sailor does not found')
        profile = Profile.objects.get(id=sailor_key.profile)
        user = User.objects.filter(id=sailor_key.user_id).first()
        if user and user.username.startswith('+380'):
            phone = user.username
        elif profile.contact_info:
            contacts = ContactInfo.objects.filter(id__in=json.loads(profile.contact_info), type_contact_id=1)
            phone = contacts.first().value if contacts.first() else None
        else:
            phone = None
        return Response({'last_name_uk': profile.last_name_ukr,
                         'first_name_uk': profile.first_name_ukr,
                         'middle_name_uk': profile.middle_name_ukr,
                         'date_birth': profile.date_birth,
                         'phone': phone})
