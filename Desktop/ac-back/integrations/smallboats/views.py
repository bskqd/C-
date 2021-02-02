# Create your views here.
import json

import requests
from django.conf import settings
from django.forms import model_to_dict
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from communication.models import SailorKeys
from sailor.models import Profile, ContactInfo, Passport, FullAddress

SMALLBOATS_AUTHORIZATION_TOKEN = 'fa3de137d6313610d55b0fba87875cca30bff83f'


class SmallBoatsCreateUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        url = f'{settings.SMALLBOATS_URL}api/v1/integrations/ac_itcs/create_account/'
        user = self.request.user
        sailor_instance = SailorKeys.objects.get(user_id=user.pk)
        profile = Profile.objects.get(id=sailor_instance.profile)
        data_to_send = model_to_dict(profile,
                                     ['first_name_ukr', 'last_name_ukr', 'middle_name_ukr',
                                      'first_name_eng', 'last_name_eng',
                                      ])
        try:
            contact_info = ContactInfo.objects.filter(id__in=json.loads(profile.contact_info), type_contact_id=2)
            email = contact_info.first().value or ''
        except (ValueError, AttributeError):
            email = ''
        passport = Passport.objects.filter(id__in=sailor_instance.citizen_passport).first()
        passport_data = None
        if passport:
            try:
                registration_address = FullAddress.objects.get(id=passport.city_registration)
                registration_address_data = {
                    'city_id': registration_address.city_id,
                    'index': registration_address.index or '',
                    'street': registration_address.street or '',
                    'house': registration_address.house or '',
                    'flat': registration_address.flat or ''
                }
            except FullAddress.DoesNotExist:
                registration_address_data = None
            try:
                resident_address = FullAddress.objects.get(id=passport.resident)
                resident_address_data = {
                    'city_id': resident_address.city_id,
                    'index': resident_address.index or '',
                    'street': resident_address.street or '',
                    'house': resident_address.house or '',
                    'flat': resident_address.flat or ''
                }
            except FullAddress.DoesNotExist:
                resident_address_data = None
            passport_data = {
                'serial': passport.serial,
                'issued_date': str(passport.date) if passport.date else None,
                'issued_by': passport.issued_by or '',
                'country_id': passport.country_id,
                'registration_address': registration_address_data,
                'resident_address': resident_address_data,
                'inn': passport.inn,
                'country_birth_id': passport.city_birth.region.country_id if passport.city_birth else None,
                'type': 'Civil'
            }
        data_to_send.update({'phone': user.username, 'email': email, 'date_birth': str(profile.date_birth),
                             'sex_id': profile.sex_id, 'passport': passport_data})
        headers = {'Authorization': f'Token {SMALLBOATS_AUTHORIZATION_TOKEN}'}
        response = requests.post(url=url, json=data_to_send,
                                 headers=headers)
        if response.status_code != 201:
            raise ValidationError('Error while create user in smallboats')
        return Response(response.json(), status=201)
