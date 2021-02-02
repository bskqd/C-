import json
import os
from datetime import datetime

import pytz
import rest_framework.permissions
from django.contrib import auth
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import parsers, renderers, mixins, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from u2flib_server import u2f

from user_profile.models import ToChangePassword
from yubikey_api_auth.serializer import UserSerializer, CheckPasswordSerializer, ChangePasswordSerializer, \
    AuthorizationLogSerializer
from .models import TmpToken, U2FKey, AuthorizationLog

User = get_user_model()


def index(request):
    return render(request=request, template_name='index.html')


class OriginMixin:
    def get_origin(self, request):
        return os.getenv('FRONT_DOMAIN', 'https://ac.itcs.net.ua')


class LoginPasswordAuth(OriginMixin, APIView):
    """
    Авторизация по логину/паролю
    """
    throttle_classes = ()
    permission_classes = (rest_framework.permissions.AllowAny,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="username",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Username",
                        description="Valid username for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tmp_token, created = TmpToken.objects.get_or_create(user=user)
        if user.u2f_keys.exists():
            sign_request = u2f.begin_authentication(self.get_origin(request), [
                d.to_json() for d in user.u2f_keys.all()])
            tmp_token.sign_req = sign_request
            tmp_token.save()
            return Response({'redirect': 'yubikey', 'tmpToken': tmp_token.key, 'sign_request': sign_request})
        else:
            tmp_token.delete()
            raise ValidationError('Token not exist')


class U2FAuthorization(APIView, OriginMixin):
    """
    Принимает пост запрос с параметрами:
    tmp_key: - временный ключ, для того чтобы найти пользователя который уже авторизировался по логину, паролю и ждем авторизацию по ключу
    response: - параметры которые отдает нажатие на юбикей
    :return {'status': 'redirect_to_login'} - если не найден тмп кей или не прошла авторизация по сигнатуре.
    {'status': 'authorizated', 'token': token} - статус "авторизиривано" и токен который нужно добавлять в хеадер при запросах

    """

    def __init__(self):
        self.errors = []
        super().__init__()

    def get_user(self):
        try:
            tmp_token = self.request.data.get('tmp_key')
            user = TmpToken.objects.get(key=tmp_token).user
            return user
        except (KeyError, AssertionError, TmpToken.DoesNotExist):
            return None

    def validate_second_factor(self, request):
        tmp_key = request.data.get('tmp_key')  # VUE
        tmp_token = TmpToken.objects.get(key=tmp_key)
        response = request.data.get('response')
        try:
            # response должен быть без тмп кей
            device, login_counter, _ = u2f.complete_authentication(tmp_token.sign_req, response)
            device = tmp_token.user.u2f_keys.get(key_handle=device['keyHandle'])
            device.last_used_at = timezone.now()
            device.save()
            tmp_token.sign_req = None
            tmp_token.delete()
            return True
        except ValueError:
            tmp_token.delete()
            self.errors.append({'error': 'U2F validation failed -- bad signature.'})
        return False

    def post(self, request):
        """
        response = {'keyHandle': '', 'clientData': '', 'signatureData': ''}
        :return:
        """
        user = self.get_user()
        if user is None:
            return JsonResponse({'status': 'redirect_to_login'})
        tmp_key = self.request.data.get('tmp_key')
        tmp_token = TmpToken.objects.get(key=tmp_key)
        status_validate = self.validate_second_factor(request)
        if not status_validate or self.errors:
            return JsonResponse({'status': 'redirect_to_login', 'err': status_validate or self.errors})
        token, created = Token.objects.update_or_create(user=tmp_token.user, defaults={'created': timezone.now()})
        auth.login(self.request, tmp_token.user)
        must_change_password = ToChangePassword.objects.filter(user=tmp_token.user, is_changed=False).exists()

        return JsonResponse(
            {'status': 'authorizated', 'token': token.key, 'must_change_password': must_change_password})


class U2FAddKeys(APIView, OriginMixin):
    permission_classes = (rest_framework.permissions.IsAuthenticated, rest_framework.permissions.IsAdminUser)

    def get(self, request):
        user = request.user
        register_request = u2f.begin_registration(app_id=self.get_origin(request))
        TmpToken.objects.filter(user=user).delete()
        tmp_token = TmpToken.objects.create(sign_req=register_request, user=user)
        return Response({'register_request': register_request})

    def post(self, request):
        try:
            received_json_data = json.loads(request.body.decode("utf-8"))
            data = {'challenge': received_json_data['challenge'],
                    'clientData': received_json_data['clientData'],
                    'registrationData': received_json_data['registrationData'],
                    'version': received_json_data['version'],
                    }
        except (KeyError, json.decoder.JSONDecodeError):
            data = {'challenge': request.data.get('challenge'),
                    'clientData': request.data.get('challenge'),
                    'registrationData': request.data.get('registrationData'),
                    'version': request.data.get('version')}
        try:
            user_id = received_json_data['user_id']
        except (KeyError, UnboundLocalError):
            user_id = request.user.id
        user = User.objects.get(id=user_id)
        tmp_token = TmpToken.objects.get(user=request.user)
        device_details, facets = u2f.complete_registration(request=tmp_token.sign_req, response=data)
        if not U2FKey.objects.filter(user=user).exists():
            new_yubikey = U2FKey.objects.create(user_id=user_id, public_key=device_details['publicKey'],
                                                key_handle=device_details['keyHandle'], app_id=device_details['appId'],
                                                last_used_at=datetime.now())
            tmp_token.delete()
            return Response({'status': 'created'})
        else:
            tmp_token.delete()
            return Response({'status': 'device exist'})


class CreateUserView(CreateAPIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated, rest_framework.permissions.IsAdminUser)
    model = get_user_model()
    serializer_class = UserSerializer


class CheckAuthorization(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(False)
        else:
            return Response(True)


obtain_auth_token = LoginPasswordAuth.as_view()
u2f_authorization = U2FAuthorization.as_view()
add_key = U2FAddKeys.as_view()


class LoginAuthorization(APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'},
                            status=HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid Credentials'},
                            status=HTTP_404_NOT_FOUND)
        try:
            if user.userprofile.yubikey_authorization:
                yubi_auth = LoginPasswordAuth()
                return yubi_auth.post(request=request)
        except ObjectDoesNotExist:
            raise ValidationError('Please contact administration')
        token, _ = Token.objects.update_or_create(user=user,
                                                  defaults={'created': timezone.now(),
                                                            })
        must_change_password = ToChangePassword.objects.filter(user=user, is_changed=False).exists()
        return Response({'token': token.key, 'must_change_password': must_change_password},
                        status=HTTP_200_OK)


class CheckPassword(GenericAPIView):
    """
    Проверить логин+пароль юзера
    """
    permission_classes = (rest_framework.permissions.IsAuthenticated, rest_framework.permissions.IsAdminUser,)
    serializer_class = CheckPasswordSerializer

    def post(self, request):
        serializer = CheckPasswordSerializer(data=request.data)
        if serializer.is_valid() is False:
            return Response(serializer.errors)
        user_id = serializer.data.get('user')
        password = serializer.data.get('password')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({'detail': 'User not found'})
        is_valid_password = user.check_password(password)
        if is_valid_password is True:
            return Response({'detail': 'Valid'})
        else:
            return Response({'detail': 'Not valid'})


class ChangePassword(GenericAPIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        _context = {'request': request}
        serializer = ChangePasswordSerializer(data=request.data, context=_context)
        if serializer.is_valid(raise_exception=True):
            user = self.request.user
            user.set_password(serializer.data.get('new_password'))
            user.save()
            to_change = ToChangePassword.objects.filter(user=user, is_changed=False)
            if to_change.exists():
                to_change.update(is_changed=True)
            return Response({'status': 'success'})


class AuthorizationLogViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = AuthorizationLog.objects.all()
    serializer_class = AuthorizationLogSerializer
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
