from django.db import models
from mixins.communication_attr import COMMUNICATION_ATTR_CONVERTER


class ByDocumentManager(models.Manager):

    def id(self, instance):
        from .models import SailorKeys
        model_label = instance._meta.label
        if model_label == 'document.ProofOfWorkDiploma':
            filtering = {f'qualification_documents__overlap': [instance.diploma_id]}
            communication_attr = 'qualification_documents'
        elif model_label == 'sailor.Profile':
            communication_attr = 'profile'
            filtering = {'profile': instance.pk}
        else:
            communication_attr = COMMUNICATION_ATTR_CONVERTER[model_label]
            filtering = {f'{communication_attr}__overlap': [instance.pk]}
        key: SailorKeys = SailorKeys.objects.only(communication_attr).filter(**filtering).first()
        return key
