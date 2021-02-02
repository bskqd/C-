from django.db import models

from communication.models import SailorKeys
from mixins.communication_attr import COMMUNICATION_ATTR_CONVERTER


class BySailorQuerySet(models.QuerySet):
    def filter_by_sailor(self, sailor_key, **kwargs):
        communication_attr = COMMUNICATION_ATTR_CONVERTER[self.model._meta.label]
        if type(sailor_key) in [int, str]:
            sailor_key_obj = SailorKeys.objects.only('id', communication_attr).get(id=sailor_key)
            object_id = getattr(sailor_key_obj, communication_attr) or []
        else:
            object_id = getattr(sailor_key, communication_attr) or []
        return self.filter(id__in=object_id, **kwargs)

    # def id(self, sailor_key, **kwargs):
    #     communication_attr = COMMUNICATION_ATTR_CONVERTER[self.model._meta.label]
    #     if type(sailor_key) in [int, str]:
    #         sailor_key_obj = SailorKeys.objects.only('id', communication_attr).get(id=sailor_key)
    #         object_id = getattr(sailor_key_obj, communication_attr) or []
    #     else:
    #         object_id = getattr(sailor_key, communication_attr) or []
    #     return self.filter(id__in=object_id, **kwargs)


class BySailorManager(models.Manager):
    """
    Manager for filter item by sailor key
    for filtering use: Education.by_sailor.id(37473)
    """

    def id(self, sailor_key, **kwargs):
        """
        :param sailor_key: SailorKeys object or integer
        :return: QuerySet[Model] with filtered by sailor
        :exception SailorKeys.DoesNotExists if sailor by id not found
        """
        communication_attr = COMMUNICATION_ATTR_CONVERTER[self.model._meta.label]
        if type(sailor_key) in [int, str]:
            sailor_key_obj = SailorKeys.objects.only('id', communication_attr).get(id=sailor_key)
            object_id = getattr(sailor_key_obj, communication_attr) or []
        else:
            object_id = getattr(sailor_key, communication_attr) or []
        return self.get_queryset().filter(id__in=object_id, **kwargs)
