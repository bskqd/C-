import base64
from datetime import datetime

import requests
from django.contrib.auth import get_user_model
from django.http import HttpResponse
# Create your views here.
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import BaseParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from directory.models import Commisioner
from docs.views import GenerateDocForProtocolDKK
from reports.filters import ShortLinkResultPagination
from sailor.document.models import ProtocolSQC
from signature.misc import upload_document_to_vchasno, upload_sign
from signature.models import CommissionerSignProtocol
from signature.serializers import DocumentToSignForUserSerialzier, ListCommissionerForProtocolSerializer

User = get_user_model()


class PlainTextParser(BaseParser):
    """
    Plain text parser.
    """
    media_type = 'X-user/base64-data'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        return stream.read()


class Proxy(APIView):
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


class UploadSignatureForDKK(APIView):
    parser_classes = (FormParser, MultiPartParser)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        protocol_id = data.get('protocol_dkk')
        signature_base64 = data.get('signature_base64')
        files = request.FILES.get('signature_file')
        type_signature = data.get('type_signature')
        protocol_dkk = ProtocolSQC.objects.get(id=protocol_id)
        token_vchasno = request.user.userprofile.vchasno_token
        self_commissioner, _ = Commisioner.objects.get_or_create(
            user=request.user, defaults={'name': request.user.userprofile.full_name_ukr})
        if type_signature == 'stamp':
            stamp_obj = CommissionerSignProtocol.objects.get_or_create(protocol_dkk=protocol_dkk,
                                                                       signer=self_commissioner,
                                                                       signature_type=type_signature,
                                                                       defaults={'signature_base64': signature_base64,
                                                                                 'signature_file': files,
                                                                                 'is_signatured': False})
            return Response({'status': 'success'}, status=201)
        elif type_signature == 'signature' and CommissionerSignProtocol.objects.filter(
                protocol_dkk=protocol_dkk,
                is_signatured=False).count() == 1:
            raise ValidationError({'status': 'error', 'detail': 'Please upload stamp'})
        try:
            stamp_obj = CommissionerSignProtocol.objects.get(protocol_dkk=protocol_dkk, signer=self_commissioner,
                                                             signature_type='stamp', is_signatured=False,
                                                             signature_base64__isnull=False)
            stamp_base64 = stamp_obj.signature_base64
        except CommissionerSignProtocol.DoesNotExist:
            stamp_obj = None
            stamp_base64 = None
        if not token_vchasno:
            raise ValidationError({'status': 'error', 'detail': 'Integration not found'})
        if not protocol_dkk.document_file_pdf:
            generation = GenerateDocForProtocolDKK()
            generation.generate_doc_main(protocol_obj=protocol_dkk)
        if not protocol_dkk.vchasno_id:
            filename = f'25958804_25958804_{datetime.today().strftime("%Y%m%d")}_protocol_{protocol_dkk.get_number}.pdf'
            response = upload_document_to_vchasno(protocol_dkk.document_file_pdf.path, file_name=filename)
            protocol_dkk.vchasno_id = response['documents'][0]['id']
            protocol_dkk.save(update_fields=['vchasno_id'])
        resp_sign = upload_sign(base64_sign=signature_base64, document_id=protocol_dkk.vchasno_id,
                                token_vchasno=token_vchasno, base64_stamp=stamp_base64)
        sign = CommissionerSignProtocol.objects.filter(signer__user=self.request.user, protocol_dkk=protocol_dkk).last()
        if sign.signature_base64 and sign.signature_file:
            raise ValidationError({'status': 'error', 'error': 'Protocol was signed'})
        sign.signature_file = files
        sign.signature_base64 = signature_base64
        sign.is_signatured = True
        sign.save(update_fields=['signature_file', 'signature_base64', 'is_signatured'])
        # upload_to_s3.delay(sign.pk)
        if resp_sign.status_code != 201:
            resp = resp_sign.json()
            resp.update({'status': 'error'})
            return Response(resp, status=resp_sign.status_code)
        if stamp_obj:
            stamp_obj.is_signatured = True
            stamp_obj.save(update_fields=['is_signatured'])
        return Response({'status': 'success'}, status=201)


class ListCommissionerForProtocolViewset(generics.ListAPIView, viewsets.GenericViewSet):
    queryset = User.objects.filter(userprofile__is_commissioner=True)
    serializer_class = ListCommissionerForProtocolSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DocumentToSignForUserViewset(generics.ListAPIView, viewsets.GenericViewSet):
    queryset = CommissionerSignProtocol.objects.all()
    serializer_class = DocumentToSignForUserSerialzier
    pagination_class = ShortLinkResultPagination
    permissions_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CommissionerSignProtocol.objects.filter(
            signer__user=self.request.user
        ).order_by('-is_signatured', 'protocol_dkk__date_meeting')
