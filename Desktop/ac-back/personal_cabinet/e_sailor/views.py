from django.conf import settings
# Create your views here.
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from personal_cabinet.models import HistoryUserInPersonalCabinet, CurrentAppVersion
from personal_cabinet.serializers import HistoryUserInPersonalCabinetSerializer, CurrentAppVersionSerializer


class HistoryUserInPersonalCabinetView(mixins.CreateModelMixin, GenericViewSet):
    queryset = HistoryUserInPersonalCabinet.objects.all()
    serializer_class = HistoryUserInPersonalCabinetSerializer
    permission_classes = (IsAuthenticated,)


class PriceServiceRecord(APIView):
    """
    The cost of a service record
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({'price_service_record': float(settings.PRICE_SERVICE_RECORD)})


class CurrentAppVersionView(APIView):
    """
    Current version of the app
    """

    def get(self, request):
        version = CurrentAppVersion.objects.order_by('-date_create')
        if not version.exists():
            return Response({'version': '0.0'})
        return Response({'version': version.first().version})

    def post(self, request, *args, **kwargs):
        serializer = CurrentAppVersionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_version = CurrentAppVersion.objects.create(**serializer.data)
        return Response({'status': 'success', 'version': new_version.version})
