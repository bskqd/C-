from datetime import timedelta, date

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

import back_office.serializers
from back_office.models import PriceIORequest, DeadweightPricePeriod


class PriceIORequestViewset(viewsets.ModelViewSet):
    queryset = PriceIORequest.objects.all()
    serializer_class = back_office.serializers.PriceIORequestSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

    def perform_create(self, serializer):
        date_start = serializer.validated_data['date_start']
        form = serializer.validated_data['type_of_form']
        date_end_current_coef = date_start - timedelta(days=1)
        today = date.today()
        try:
            last_coefficient = self.get_queryset().get(date_end__isnull=True, type_of_form=form)
        except PriceIORequest.DoesNotExist:
            serializer.save()
            return None
        if last_coefficient.date_start > today:
            raise ValidationError('New coefficient exists - use update')
        last_coefficient.date_end = date_end_current_coef
        last_coefficient.save(update_fields=['date_end'])
        serializer.save()

    def perform_destroy(self, instance):
        today = date.today()
        date_end = instance.date_start - timedelta(days=1)
        if date_end < today:
            raise ValidationError('cannot delete record')
        current_coeff = self.queryset.get(date_end=date_end, type_of_form=instance.type_of_form)
        current_coeff.date_end = None
        current_coeff.save(update_fields=['date_end'])
        instance.delete()


class DeadweightPriceViewset(viewsets.ModelViewSet):
    queryset = DeadweightPricePeriod.objects.all().order_by('date_start')
    serializer_class = back_office.serializers.DeadweightPricePeriodSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)

    def perform_destroy(self, instance):
        if instance.date_start <= date.today():
            raise ValidationError('Prices are used')
        date_end = instance.date_start - timedelta(days=1)
        DeadweightPricePeriod.objects.filter(date_end=date_end).update(date_end=None)
        instance.delete()
