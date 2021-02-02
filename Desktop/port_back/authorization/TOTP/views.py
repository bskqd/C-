import pyqrcode
from rest_framework import permissions, status, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

import authorization.TOTP.serializers
import authorization.TOTP.utils


class TOTPAuthView(GenericAPIView):
    """
    Authorization with 2FA with JWT Token.
    :return: Token for authorization
    """
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = authorization.TOTP.serializers.TokenSerializer

    def post(self, request):
        user = request.user
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.data.get('token')
        device = authorization.TOTP.utils.get_user_totp_device(user)
        if device is not None and device.verify_token(token):
            if not device.confirmed:
                device.confirmed = True
                device.save()
            user_token, _ = Token.objects.get_or_create(user=self.request.user)
            return Response({'token': user_token.key}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TOTPCreateView(views.APIView):
    """
    Use this endpoint for create TOTP for self user
    """
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication, TokenAuthentication)

    def post(self, request):
        user = request.user
        device = authorization.TOTP.utils.get_user_totp_device(user)
        if not device:
            device = user.totpdevice_set.create(confirmed=False, name='Port.in.ua')
        url = device.config_url
        url_qr = pyqrcode.create(url)
        qr_code = url_qr.png_as_base64_str(scale=8)
        return Response({'qr_code': qr_code}, status=status.HTTP_201_CREATED)


class TOTPVerifyView(GenericAPIView):
    """
    Use this endpoint to verify/enable a TOTP device
    """
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication, TokenAuthentication)
    serializer_class = authorization.TOTP.serializers.TokenSerializer

    def post(self, request):
        user = request.user
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.data.get('token')
        device = authorization.TOTP.utils.get_user_totp_device(user)
        if device is not None and device.verify_token(token):
            if not device.confirmed:
                device.confirmed = True
                device.save()
            return Response(True, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
