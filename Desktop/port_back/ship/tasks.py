import json

from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder

from communication.models import ShipKey
from port_back.celery import celery_app
from ship.models import ShipHistory, MainInfo
from ship.utils import custom_model_to_dict


@celery_app.task(serializer='pickle')
def save_history(instance, history_type, user_id=None, ship_id=None):
    serializer_data = json.loads(json.dumps(custom_model_to_dict(instance), cls=DjangoJSONEncoder))
    field_name = instance._meta.model_name
    if not ship_id and isinstance(instance, MainInfo):
        ship_id = instance.pk
    if not ship_id and hasattr(ShipKey, field_name):
        if isinstance(ShipKey._meta.get_field(field_name), ArrayField):
            filtering = {f'{field_name}__overlap': [instance.pk]}
        else:
            filtering = {field_name: instance.pk}
        ship_id = ShipKey.objects.filter(**filtering).first()
        ship_id = ship_id.pk if ship_id else None
    if not ship_id:
        ship_id = getattr(instance, 'ship_key', None)
    if not ship_id:
        old_history = ShipHistory.objects.filter(content_type__model=instance._meta.model_name,
                                                 object_id=instance.pk).first()
        ship_id = old_history.ship_id if old_history else None
    ShipHistory.objects.create(
        content_object=instance,
        serialized_data=serializer_data,
        ship_id=ship_id,
        history_type=history_type,
        user_id=user_id)
