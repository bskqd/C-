import json

from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from communication.models import SailorKeys
from sailor.models import PhotoProfile


class SailorGetQuerySetMixin:
    """
    Mixin with get_queryset for getting objects by sailor key
    It uses BySilorManager for filtering by keys
    You must override model variable for filtering by model
    """

    def get_exclude_status_document(self):
        return self.exclude_status_document

    def get_queryset(self):
        from sailor.views import sailor_not_exists_error
        if getattr(self, 'swagger_fake_view', False):
            return self.model.objects.none()
        try:
            sailor_key = SailorKeys.objects.get(user_id=self.request.user.id)
            qs = self.model.by_sailor.filter_by_sailor(sailor_key)
            if hasattr(qs.first(), 'status_document'):
                qs = qs.exclude(status_document_id__in=self.get_exclude_status_document())
            elif hasattr(qs.first(), 'status'):
                qs = qs.exclude(status_id__in=self.get_exclude_status_document())
            return qs
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error, code=404)


class PhotoUploadMixin:
    """
    Mixin to upload a photo to the documents created by the sailor
    """
    model = None

    @action(methods=['post'], detail=True)
    def upload_file(self, request, *args, **kwargs):
        obj = self.get_object()
        files = request.FILES.getlist('photo')
        files = [PhotoProfile.objects.create(photo=file).pk for file in files]
        if obj.photo is None:
            obj.photo = json.dumps(files)
        else:
            photo = json.loads(obj.photo)
            obj.photo = json.dumps(photo + files)
        obj.save(update_fields=['photo'])
        return Response({'status': 'success'})
