import base64

import requests
import rest_framework.parsers
from django.conf import settings
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

import core.permissions
import signature.permissions
import signature.serializers
from core.models import User
from signature.models import Signature, IORequestSign, CenterCertificationKey


class SignatureView(viewsets.ModelViewSet):
    queryset = Signature.objects.all()
    serializer_class = signature.serializers.SignatureSerializer
    permission_classes = (permissions.IsAuthenticated,
                          (IsAdminUser |
                           core.permissions.IsUserMarad |
                           core.permissions.IsHarborMaster |
                           core.permissions.IsAgent |
                           core.permissions.IsHeadAgency |
                           signature.permissions.HarborWorkerReadOnlySignature
                           )
                          )
    parser_classes = (rest_framework.parsers.FormParser,
                      rest_framework.parsers.MultiPartParser,
                      rest_framework.parsers.JSONParser)

    def perform_create(self, serializer):
        data = serializer.validated_data
        type_signature = data.get('type_signature')
        port = serializer.validated_data.get('port')
        agent = serializer.validated_data.get('agent')
        user: User = self.request.user
        is_captain_upload_sign = user.type_user == user.HARBOR_MASTER_CH and type_signature == Signature.SIGN
        if user.type_user == user.HARBOR_MASTER_CH and type_signature == 'stamp' and \
                not user.harbor_master.ports.filter(pk=port.pk).exists():
            raise ValidationError('Please set a agent or port')
        elif user.type_user in [user.HEAD_AGENCY_CH, user.AGENT_CH]:
            agent = user
        if not port and not agent and not is_captain_upload_sign:
            raise ValidationError('Please set a agent or port')
        if is_captain_upload_sign:
            Signature.objects.filter(
                type_signature=type_signature, port__in=user.harbor_master.ports.all()
            ).update(is_actual=False)
        elif port:
            Signature.objects.filter(
                type_signature=type_signature, port=port
            ).update(is_actual=False)
        elif agent:
            Signature.objects.filter(type_signature=type_signature, agent=agent).update(is_actual=False)
        serializer.save(port=port, agent=agent)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        user = self.request.user
        if user.type_user in [user.MARAD_CH, user.ADMIN_CH]:
            queryset = self.queryset.filter(is_actual=True)
        elif user.type_user in [user.HARBOR_MASTER_CH]:
            queryset = self.queryset.filter(
                is_actual=True,
                port__in=user.get_port,
                type_signature__in=[Signature.SIGN, Signature.STAMP])
        elif user.type_user == user.HARBOR_WORKER_CH:
            queryset = self.queryset.filter(is_actual=True, port__in=user.get_port)
        elif user.type_user in [user.AGENT_CH, user.HEAD_AGENCY_CH]:
            queryset = self.queryset.filter(is_actual=True, agent=user)
        else:
            queryset = self.queryset.none()
        return queryset

    @action(methods=['get'], detail=False)
    def actual_stamp(self, request):
        queryset = self.get_queryset()
        queryset = queryset.filter(type_signature=Signature.STAMP)
        return Response(self.serializer_class(instance=queryset.first()).data)

    @action(methods=['get'], detail=False)
    def actual_sign(self, request):
        queryset = self.get_queryset()
        queryset = queryset.filter(type_signature=Signature.SIGN)
        return Response(self.serializer_class(instance=queryset.first()).data)


class PlainTextParser(rest_framework.parsers.BaseParser):
    """
    Plain text parser.
    """
    media_type = 'X-user/base64-data'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        return stream.read()


class ProxyView(APIView):
    parser_classes = (PlainTextParser,)

    def post(self, request):
        url = request.GET.get('address')
        data = base64.b64decode(request.data)
        headers = {'Content-type': 'X-user/base64-data; charset=utf-8',
                   'Cache-Control': 'no-store, no-cache, must-revalidate',
                   }
        response = requests.post(url, data, headers=headers)
        proxy_response = HttpResponse(
            base64.b64encode(response.content).decode('utf-8'),
            status=response.status_code)

        return proxy_response


class IORequestSignView(viewsets.ModelViewSet):
    queryset = IORequestSign.objects.all()
    serializer_class = signature.serializers.IORequestSignSerializer
    parser_classes = (rest_framework.parsers.FormParser, rest_framework.parsers.MultiPartParser)
    permission_classes = (permissions.IsAuthenticated,
                          (IsAdminUser |
                           core.permissions.IsUserMarad |
                           core.permissions.IsHarborMaster |
                           core.permissions.IsUserMarad |
                           core.permissions.IsHarborWorker),
                          )


class CenterCertificateKeyView(viewsets.ModelViewSet):
    queryset = CenterCertificationKey.objects.all()
    serializer_class = signature.serializers.CenterCertificationKeySerializer
    permission_classes = (permissions.IsAuthenticated,)


class CifraMediaView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, path):
        headers = {'Authorization': f'Bearer {settings.CIFRA_DIR_KEY}'}
        url_cifra = f'{settings.CIFRA_URL}media/' + path
        cifra_response = requests.get(url=url_cifra, headers=headers)
        return HttpResponse(content=cifra_response.content, status=cifra_response.status_code,
                            content_type=cifra_response.headers['Content-Type'])
