from datetime import timedelta

from django.contrib.auth import authenticate
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from u2flib_server import u2f

import authorization.serializers
import authorization.utils
from authorization.U2F.models import TempToken
from core.models import User
from port_back.settings import HOST_DOMAIN


class EmailAuthView(GenericAPIView):
    """
    Login to get:
     - If 2FA required -  JWT token (expiration - 10 min) for 10 step of 2fa or create 2FA token
     - If 2FA not required - Token key
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = authorization.serializers.EmailAuthorizationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = authenticate(username=request.data['email'],
                            password=request.data['password'])
        if user and not user.is_active:
            raise ValidationError('User is not active')
        if user and user.type_authorization == user.BASIC:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'type_authorization': user.type_authorization,
                             'has_device': False}, status=status.HTTP_200_OK)
        elif user and user.type_authorization == user.TOTP:
            has_device = user.totpdevice_set.filter(confirmed=True).exists()
            refresh_token = RefreshToken.for_user(user=user)
            access_token = refresh_token.access_token
            access_token.set_exp(lifetime=timedelta(minutes=10))
            return Response({'bearer': str(refresh_token.access_token), 'type_authorization': user.type_authorization,
                             'has_device': has_device},
                            status=status.HTTP_200_OK)
        elif user and user.type_authorization == user.YUBIKEY:
            tmp_token, _ = TempToken.objects.get_or_create(user=user)
            if not user.u2f_keys.exists():
                raise ValidationError('U2F key for this user does not exists.')
            sign_request = u2f.begin_authentication(HOST_DOMAIN, [d.to_json() for d in user.u2f_keys.all()])
            tmp_token.sign_req = sign_request
            tmp_token.save()
            refresh_token = RefreshToken.for_user(user=user)
            access_token = refresh_token.access_token
            access_token.set_exp(lifetime=timedelta(minutes=10))
            return Response({'bearer': str(refresh_token.access_token), 'type_authorization': user.type_authorization,
                             'temp_token': tmp_token.key, 'sign_request': sign_request},
                            status=status.HTTP_200_OK)
        return Response({'status': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)
