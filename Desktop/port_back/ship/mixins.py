from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import GenericViewSet

from communication.models import ShipKey


class GetQuerySetMixin(GenericViewSet):
    kwargs_param = 'ship_pk'

    def get_queryset(self):
        kwargs_param = self.kwargs_param
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.model.objects.none()
        ship_key_id = self.kwargs.get(kwargs_param)
        if not ship_key_id:
            return self.queryset.all()
        try:
            ship_key = ShipKey.objects.get(pk=ship_key_id)
            filtering = {'id__in': getattr(ship_key, self.queryset.model._meta.model_name)}
            qs = self.queryset.filter(**filtering)
        except (ObjectDoesNotExist, AttributeError, ValueError) as e:
            raise ValidationError('Ship does not exists')
        return qs
