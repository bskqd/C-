from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, generics

from .serializer import (AreaSerializer, NovaPoshtaCitySerializer, NovaPoshtaWarehouseSerializer,
                         NovaPoshtaStreetSerializer)
from .models import NovaPoshtaArea, NovaPoshtaCity, NovaPoshtaWarehouse, NovaPoshtaStreet
import delivery.permissions


class AreaView(viewsets.ModelViewSet):
    permission_classes = (delivery.permissions.IsSuperUserEdit,)
    queryset = NovaPoshtaArea.objects.all()
    serializer_class = AreaSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class NovaPoshtaCityView(viewsets.ModelViewSet):
    permission_classes = (delivery.permissions.IsSuperUserEdit,)
    queryset = NovaPoshtaCity.objects.all()
    serializer_class = NovaPoshtaCitySerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class NovaPoshtaWarehouseView(generics.ListAPIView):
    permission_classes = (delivery.permissions.IsSuperUserEdit,)
    serializer_class = NovaPoshtaWarehouseSerializer

    def get_queryset(self):
        city = self.kwargs['city']
        return NovaPoshtaWarehouse.objects.filter(city__id=city)

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class NovaPoshtaStreetView(generics.ListAPIView):
    permission_classes = (delivery.permissions.IsSuperUserEdit,)
    serializer_class = NovaPoshtaStreetSerializer

    def get_queryset(self):
        city = self.kwargs['city']
        return NovaPoshtaStreet.objects.filter(city__id=city)

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

