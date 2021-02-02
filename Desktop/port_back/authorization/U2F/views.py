from datetime import datetime

from django.conf import settings
from django.contrib import auth
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from u2flib_server import u2f

from authorization.U2F.models import TempToken, U2FKey
from core.models import User


class U2FAuthorization(APIView):
    """
    Принимает пост запрос с параметрами:
    tmp_key: - временный ключ, для того чтобы найти пользователя который уже авторизировался по логину,
    паролю и ждем авторизацию по ключу
    response: - параметры которые отдает нажатие на юбикей
    :return 400 http code  - если не найден тмп кей или не прошла авторизация по сигнатуре.
    :return: 200 http code and {token: }

    """

    def get_temp_token_and_user(self):
        """
        :return: temp token and user or None
        """
        try:
            temp_token = self.request.data.get('temp_token')
            temp_token = TempToken.objects.get(key=temp_token)
            user = temp_token.user
            return user, temp_token
        except (KeyError, AssertionError, TempToken.DoesNotExist):
            return None

    def validate_second_factor(self, temp_token, u2f_response):
        try:
            device, login_counter, _ = u2f.complete_authentication(temp_token.sign_req, u2f_response)
            device = temp_token.user.u2f_keys.get(key_handle=device['keyHandle'])
            device.last_used_at = timezone.now()
            device.save()
            temp_token.sign_req = None
            temp_token.delete()
            return True
        except ValueError:
            temp_token.delete()
            raise ValidationError('U2F validation failed -- bad signature.')

    def post(self, request):
        """
        response = {'keyHandle': '', 'clientData': '', 'signatureData': ''}
        :return: token for Token authorization
        """
        user, temp_token = self.get_temp_token_and_user()
        u2f_response = request.data.get('u2f_response')
        if user is None:
            raise ValidationError('Token incorrect')
        status_validate = self.validate_second_factor(temp_token, u2f_response)
        if not status_validate:
            return status_validate
        token, created = Token.objects.get_or_create(user=temp_token.user, defaults={'created': timezone.now()})
        auth.login(self.request, temp_token.user)
        try:
            temp_token.delete()
        except AssertionError:
            pass
        return Response({'token': token.key})


class U2FAddKeys(APIView):
    def get(self, request):
        user = request.user
        register_request = u2f.begin_registration(app_id=settings.HOST_DOMAIN)
        TempToken.objects.filter(user=user).delete()
        TempToken.objects.create(sign_req=register_request, user=user)
        return Response({'register_request': register_request})

    def post(self, request):
        request_data = request.data
        data = {'challenge': request_data.get('challenge'),
                'clientData': request_data.get('clientData'),
                'registrationData': request_data.get('registrationData'),
                'version': request_data.get('version')}
        user_id = request_data.get('user_id', self.request.user.pk)
        user = User.objects.get(id=user_id)
        tmp_token = TempToken.objects.get(user=request.user)
        device_details, facets = u2f.complete_registration(request=tmp_token.sign_req, response=data)
        if not U2FKey.objects.filter(user=user).exists():
            U2FKey.objects.create(user_id=user_id, public_key=device_details['publicKey'],
                                  key_handle=device_details['keyHandle'], app_id=device_details['appId'],
                                  last_used_at=datetime.now())
            tmp_token.delete()
            return Response({'status': 'created'})
        else:
            tmp_token.delete()
            return Response({'status': 'device exist'})
