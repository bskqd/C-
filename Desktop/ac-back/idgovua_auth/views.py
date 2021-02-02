import base64
from datetime import timedelta

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.authtoken.models import Token
# Create your views here.
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from communication.models import SailorKeys
from idgovua_auth.models import AuthorizationLog
from sailor.models import Passport, Profile
from sms_auth.misc import generic_password

User = get_user_model()


class IDGovUARegistration(APIView):

    def __init__(self):
        self.description_eng = 'Please, register with passport values'
        self.description_ukr = 'Зареєструйтесь будь ласка з використанням паспортних данних'
        self.token = None
        self.bearer = None
        self.refresh = None
        self.status = 2
        self.client_id = '852de4828b31cd9a1953f03fb84b119c'
        self.client_secret = 'ed62bff413c907e4d21d1c44794d05c461600f9f'
        self.log_auth_response = None
        self.log_inn = ''
        self.log_phone = ''
        self.response_self_data = False
        super(IDGovUARegistration, self).__init__()

    def _get_sailor_key_and_create_user(self, params):
        """
        Находим sailor_key и создаем юзера.
        Если sailor_key не найден - выкидываем ошибку
        :param params: {'first_name_ukr:'', 'middle_name_ukr':'', 'last_name_ukr':'', 'inn':'', 'phone':''}
        :return: User object
        """
        first_name_ukr = params['first_name_ukr']
        middle_name_ukr = params['middle_name_ukr']
        last_name_ukr = params['last_name_ukr']
        inn = params['inn']
        phone = params['phone']
        email = params['email']
        if phone and phone.startswith('+') is False:
            phone = '+' + phone
        passport = Passport.objects.filter(Q(inn=inn) | Q(serial=inn))
        if not passport.exists():
            AuthorizationLog.objects.create(auth_response=self.log_auth_response, status_response=2,
                                            descr=self.description_ukr, inn=inn, phone=phone,
                                            first_name=first_name_ukr, last_name=last_name_ukr,
                                            middle_name=middle_name_ukr, line_exit=52)
            self.status = 2
            response = {'status': self.status,
                        'token': self.token,
                        'description': {'ua': self.description_ukr, 'en': self.description_eng},
                        'refresh': self.refresh}
            if self.response_self_data:
                response.update({
                    'first_name': first_name_ukr,
                    'last_name': last_name_ukr,
                    'middle_name': middle_name_ukr,
                    'tax_code': inn,
                    'phone': phone,
                    'email': email
                })
            return Response(response)
        profile_filter = {'first_name_ukr__iexact': first_name_ukr.strip(),
                          'last_name_ukr__iexact': last_name_ukr.strip()}
        if middle_name_ukr:
            profile_filter['middle_name_ukr__iexact'] = middle_name_ukr.strip()
        profile = Profile.objects.filter(**profile_filter)
        profile_list_id = list(profile.values_list('id', flat=True))
        passport_list_id = list(passport.values_list('id', flat=True))
        sailor_key = SailorKeys.objects.filter(profile__in=profile_list_id,
                                               citizen_passport__overlap=passport_list_id)
        if not sailor_key.exists():
            AuthorizationLog.objects.create(auth_response=self.log_auth_response, status_response=2,
                                            descr=self.description_ukr, inn=inn, phone=phone,
                                            first_name=first_name_ukr, last_name=last_name_ukr,
                                            middle_name=middle_name_ukr, line_exit=69)
            self.status = 2
            response = {'status': self.status, 'token': self.token, 'description': {'ua': self.description_ukr,
                                                                                    'en': self.description_eng},
                        'bearer': self.bearer, 'refresh': self.refresh}
            if self.response_self_data:
                response.update({
                    'first_name': first_name_ukr,
                    'last_name': last_name_ukr,
                    'middle_name': middle_name_ukr,
                    'tax_code': inn,
                    'phone': phone,
                    'email': email
                })
            return Response(response)
        sailor_key = sailor_key.first()
        original_phone = phone
        if not phone:
            phone = f'key_{sailor_key.pk}'
        if User.objects.filter(
                Q(username__icontains=phone) | Q(
                    username__icontains='key_{}'.format(sailor_key.pk)) | (Q(last_name=sailor_key.pk))).exists():

            self.status = 0
            self.description_eng = None
            self.description_ukr = None
            user = User.objects.filter(
                Q(username__contains=phone) | Q(username__contains='key_{}'.format(sailor_key.pk)) | (
                    Q(last_name=sailor_key.pk))).first()
            if user.username.startswith('key_') and not phone.startswith('key_'):
                user.username = phone
                user.save(update_fields=['username'])
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            access.set_exp(lifetime=timedelta(hours=8))
            self.refresh = str(refresh)
            bearer = str(access)
            self.bearer = bearer
            token, _ = Token.objects.get_or_create(user=user)
            self.token = token.key
            AuthorizationLog.objects.create(auth_response=self.log_auth_response, status_response=self.status,
                                            descr=self.description_ukr, inn=inn, phone=phone,
                                            first_name=first_name_ukr, last_name=last_name_ukr,
                                            middle_name=middle_name_ukr, line_exit=92, user_id=user.pk)
            response = {'status': self.status, 'token': self.token, 'bearer': self.bearer,
                        'description': {'ua': self.description_ukr, 'en': self.description_eng},
                        'refresh': self.refresh}
            if self.response_self_data:
                response.update({
                    'first_name': first_name_ukr,
                    'last_name': last_name_ukr,
                    'middle_name': middle_name_ukr,
                    'tax_code': inn,
                    'phone': original_phone,
                    'email': email
                })
            return Response(response)
        else:
            user = User.objects.create_user(username=phone, password=generic_password(8))
            user.last_name = sailor_key.pk
            user.save(update_fields=['last_name'])
            sailor_key.user_id = user.pk
            sailor_key.save(update_fields=['user_id'])
            return user

    def _get_access_token_and_userid_gov(self, code):
        """
        Get "Access token" and "user_id govua" for getting info for user
        :param code: code from frontend
        :return: {'user_id' - user_id_govua, 'access_token': access_token }
        """
        url = 'https://id.gov.ua/get-access-token?'
        params = {'grant_type': 'authorization_code', 'client_id': self.client_id, 'client_secret': self.client_secret,
                  'code': code}
        r = requests.get(url=url, params=params)
        response = r.json()
        keys = list(response.keys())
        if 'error' in keys or not 'user_id' in keys or not 'access_token' in keys:
            AuthorizationLog.objects.create(auth_response=response, status_response=self.status,
                                            descr=self.description_ukr,
                                            line_exit=120)
            response = {'status': self.status, 'token': self.token, 'bearer': self.bearer,
                        'description': {'ua': self.description_ukr, 'en': self.description_eng},
                        'refresh': self.refresh}
            if self.response_self_data:
                response.update({
                    'first_name': None,
                    'last_name': None,
                    'middle_name': None,
                    'tax_code': None,
                    'phone': None,
                    'email': None
                })
            return Response(response)
        else:
            return {'user_id': response['user_id'], 'access_token': response['access_token']}

    def _get_user_info(self, gov_user_id, access_token):
        """
        Get user info from govua
        :param gov_user_id:
        :param access_token:
        :return: {'first_name_ukr': first_name_ukr, 'middle_name_ukr': middle_name_ukr,
                    'last_name_ukr': last_name_ukr, 'inn': inn, 'phone': phone}
        """
        url = 'https://id.gov.ua/get-user-info?'
        params = {'access_token': access_token, 'user_id': gov_user_id}
        r = requests.get(url=url, params=params)
        response = r.json()
        keys_response = list(response.keys())
        self.log_auth_response = response
        if 'error' in keys_response:
            AuthorizationLog.objects.create(auth_response=self.log_auth_response, status_response=self.status,
                                            descr=self.description_ukr, line_exit=143)
            response = {'status': self.status, 'token': self.token, 'bearer': self.bearer,
                        'description': {'ua': self.description_ukr, 'en': self.description_eng},
                        'refresh': self.refresh}
            if self.response_self_data:
                response.update({
                    'first_name': None,
                    'last_name': None,
                    'middle_name': None,
                    'tax_code': None,
                    'phone': None,
                    'email': None
                }
                )
            return Response(response)
        else:
            first_name_ukr = response['givenname']
            middle_name_ukr = response['middlename']
            last_name_ukr = response['lastname']
            inn = response['drfocode']
            phone = response['phone']
            email = response['email']
            self.log_inn = inn
            self.log_phone = phone
            if not inn or not first_name_ukr or not last_name_ukr:
                self.status = 2
                AuthorizationLog.objects.create(auth_response=self.log_auth_response, status_response=self.status,
                                                descr=self.description_ukr, inn=inn, phone=phone,
                                                first_name=first_name_ukr, last_name=last_name_ukr,
                                                middle_name=middle_name_ukr, line_exit=160)
                response = {'status': self.status, 'token': self.token, 'description': {'ua': self.description_ukr,
                                                                                        'en': self.description_eng},
                            'bearer': self.bearer, 'refresh': self.refresh}
                if self.response_self_data:
                    response.update({'first_name': first_name_ukr,
                                     'last_name': last_name_ukr,
                                     'middle_name': middle_name_ukr,
                                     'tax_code': inn,
                                     'phone': phone,
                                     'email': email
                                     })
                return Response(response)
            return {'first_name_ukr': first_name_ukr, 'middle_name_ukr': middle_name_ukr,
                    'last_name_ukr': last_name_ukr, 'inn': inn, 'phone': phone, 'email': email}

    def post(self, request):
        user_code = request.data.get('code')
        timestamp = request.data.get('timestamp')
        state = request.data.get('state')
        if state and timestamp:
            key = base64.b64decode(settings.CRYPTO_KEY)
            fernet_alg = Fernet(key)
            try:
                decoded_timestamp = fernet_alg.decrypt(str(state).encode()).decode()
                if str(decoded_timestamp) != str(timestamp):
                    raise ValidationError('Can\'t decode code param')
            except (InvalidToken, InvalidSignature):
                raise ValidationError('Can\'t decode code param')
        if user_code is None:
            response = {'status': self.status, 'token': self.token, 'bearer': self.bearer,
                        'description': {'ua': self.description_ukr, 'en': self.description_eng},
                        'refresh': self.refresh}
            if self.response_self_data:
                response.update({'first_name': None,
                                 'last_name': None,
                                 'middle_name': None,
                                 'tax_code': None,
                                 'phone': None,
                                 'email': None
                                 })
            return Response(response)
        access_datas = self._get_access_token_and_userid_gov(code=user_code)
        if isinstance(access_datas, Response) is True:
            return access_datas
        govua_user_id = access_datas['user_id']
        access_token = access_datas['access_token']
        user_info = self._get_user_info(gov_user_id=govua_user_id, access_token=access_token)
        if isinstance(user_info, Response) is True:
            return user_info
        user = self._get_sailor_key_and_create_user(user_info)
        if isinstance(user, Response) is True:
            return user
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        access.set_exp(lifetime=timedelta(hours=8))
        bearer = str(access)
        token, _ = Token.objects.get_or_create(user=user)
        self.token = token.key
        self.bearer = bearer
        self.refresh = str(refresh)
        self.status = 0
        self.description_ukr = None
        self.description_eng = None
        AuthorizationLog.objects.create(auth_response=self.log_auth_response, status_response=self.status,
                                        descr=self.description_ukr, inn=user_info['inn'], phone=user_info['phone'],
                                        first_name=user_info['first_name_ukr'], last_name=user_info['last_name_ukr'],
                                        middle_name=user_info['middle_name_ukr'], line_exit=194, user_id=user.pk)
        response = {'status': self.status, 'token': self.token, 'bearer': self.bearer,
                    'description': {'ua': self.description_ukr, 'en': self.description_eng},
                    'refresh': self.refresh}
        if self.response_self_data:
            response.update({'first_name': user_info['first_name_ukr'],
                             'last_name': user_info['last_name_ukr'],
                             'middle_name': user_info['middle_name_ukr'],
                             'tax_code': user_info['inn'],
                             'phone': user_info['phone'],
                             'email': user_info.get('email')})
        return Response(response)


class ESailorIDGovUaRegistration(IDGovUARegistration):
    def __init__(self):
        super().__init__()
        self.description_eng = 'Please, register with passport values'
        self.description_ukr = 'Зареєструйтесь будь ласка з використанням паспортних данних'
        self.token = None
        self.bearer = None
        self.refresh = None
        self.status = 2
        self.client_id = '6d26d8fffc388b1462a7540f2ab2f288'
        self.client_secret = '69335bf097a98412c8e5571e319573fdc5d78e31'
        self.log_auth_response = None
        self.log_inn = ''
        self.log_phone = ''
        self.response_self_data = True


class MDUIDGovUaRegistration(IDGovUARegistration):

    def __init__(self):
        super().__init__()
        self.client_id = settings.MDU_ID_GOV_UA_CLIENT_ID
        self.client_secret = settings.MDU_ID_GOV_UA_CLIENT_SECRET
