from django.conf import settings
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, exceptions
from rest_framework import viewsets

import verification.serializers
import verification.utils
from communication.models import ShipKey
from ship.models import IORequest, MainInfo


@method_decorator(name='retrieve', decorator=(
        swagger_auto_schema(query_serializer=verification.serializers.PublicVerificationQuerySerializer)
))
class PublicVerificationView(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = IORequest.objects.select_related('port', 'status_document').all()
    serializer_class = verification.serializers.PublicVerificationSerializer

    def get_object(self):
        serializer = verification.serializers.PublicVerificationQuerySerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_query_params = serializer.validated_data
        io_number = validated_query_params.get('io_number')
        imo_number = validated_query_params.get('imo_number')
        qr_code = validated_query_params.get('qr_code')
        if io_number and imo_number:
            number, year = io_number.split('/')
            main_info = MainInfo.objects.get(imo_number=imo_number)
            keys = ShipKey.objects.get(pk=main_info.pk)
            request = self.queryset.filter(pk__in=keys.iorequest, number=number,
                                           created_at__year=year).first()
            if not request:
                raise exceptions.NotFound
            return request
        elif qr_code:
            decrypt_aes = verification.utils.AESCipher(key=settings.DECODE_VERIFICATION_KEY)
            decrypted_data = decrypt_aes.decrypt(qr_code)
            _, _, document_pk = decrypted_data.split(';')
            return self.queryset.get(pk=document_pk)
        else:
            raise exceptions.NotFound

