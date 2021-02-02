import json

from django.core.serializers.json import DjangoJSONEncoder

from core.models import UserHistory
from port_back.celery import celery_app
from ship.utils import custom_model_to_dict


@celery_app.task(serializer='pickle')
def save_user_history(instance, history_type, author_id=None):
    serializer_data = json.loads(json.dumps(custom_model_to_dict(instance), cls=DjangoJSONEncoder))
    UserHistory.objects.create(
        content_object=instance,
        serialized_data=serializer_data,
        history_type=history_type,
        author_id=author_id)
