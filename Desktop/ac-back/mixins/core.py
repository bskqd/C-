from copy import deepcopy

from django.contrib.auth import get_user_model
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from communication.models import SailorKeys
from itcs import magic_numbers
from mixins.communication_attr import COMMUNICATION_ATTR_CONVERTER
from user_profile.models import UserProfile

User = get_user_model()


class DeprecatedApi:

    @swagger_auto_schema(deprecated=True)
    def retrieve(self, *args, **kwargs):
        return super(DeprecatedApi, self).retrieve(*args, **kwargs)

    @swagger_auto_schema(deprecated=True)
    def list(self, *args, **kwargs):
        return super(DeprecatedApi, self).list(*args, **kwargs)

    @swagger_auto_schema(deprecated=True)
    def create(self, *args, **kwargs):
        return super(DeprecatedApi, self).create(*args, **kwargs)

    @swagger_auto_schema(deprecated=True)
    def destroy(self, *args, **kwargs):
        return super(DeprecatedApi, self).destroy(*args, **kwargs)

    @swagger_auto_schema(deprecated=True)
    def update(self, *args, **kwargs):
        return super(DeprecatedApi, self).update(*args, **kwargs)

    @swagger_auto_schema(deprecated=True)
    def partial_update(self, *args, **kwargs):
        return super(DeprecatedApi, self).partial_update(*args, **kwargs)


class ObjectFromQuerySetMixin(GenericViewSet):
    """
    Миксин для получения объекта из queryset экземпляра, беза исплользвания метода get_queryset()
    """

    def get_object(self):
        queryset = self.queryset.all()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj


class SailorGetQuerySetMixin:
    """
    Mixin with get_queryset for getting objects by sailor key
    It uses BySilorManager for filtering by keys
    You must override model variable for filtering by model
    """
    model = None
    select_related = ()
    prefetch_related = ()

    def get_queryset(self):
        kwargs_param = 'sailor_pk'
        if getattr(self, 'swagger_fake_view', False):
            return self.model.objects.none()
        sailor_key = self.kwargs.get(kwargs_param)
        user: User = self.request.user
        type_user = user.userprofile.type_user if hasattr(user, 'userprofile') else None
        try:
            # qs = self.model.by_sailor.filter_by_sailor(sailor_key=sailor_key)
            qs = self.model.by_sailor.select_related(
                *self.select_related
            ).prefetch_related(*self.prefetch_related).filter_by_sailor(sailor_key=sailor_key)
        except (SailorKeys.DoesNotExist, TypeError, ValueError, ValidationError):
            raise Http404
        if type_user not in [UserProfile.BACK_OFFICE] and not user.is_superuser and \
                hasattr(self.model, 'status_document_id'):
            qs = qs.exclude(status_document_id=magic_numbers.STATUS_REMOVED_DOCUMENT)
        elif type_user not in [UserProfile.BACK_OFFICE] and not user.is_superuser and hasattr(self.model, 'status_id'):
            qs = qs.exclude(status_id=magic_numbers.STATUS_REMOVED_DOCUMENT)
        return qs

    def perform_destroy(self, instance):
        from sailor.views import sailor_not_exists_error
        from sailor.tasks import save_history
        key = SailorKeys.by_document.id(instance)
        if hasattr(instance, 'items') and instance.items.exists():
            raise ValidationError('Document can only be deleted with the packet')
        if not key:
            raise ValidationError(sailor_not_exists_error, code=404)
        attr = COMMUNICATION_ATTR_CONVERTER[instance._meta.label]
        status_document = getattr(instance, 'status_document', None) or getattr(instance, 'status', None)
        if status_document and status_document.pk != magic_numbers.STATUS_REMOVED_DOCUMENT:
            self.change_status_document_on_removed_by_agent(instance, key.pk, save_history)
            return instance
        else:
            old_list = getattr(key, attr)
            new_list = list(set(old_list) - {instance.pk})
            setattr(key, attr, new_list)
            key.save(update_fields=[attr])
            _instance = deepcopy(instance)
            instance.delete()
            save_history.s(user_id=self.request.user.id, sailor_key_id=key.id,
                           module=instance._meta.object_name, action_type='delete',
                           content_obj=_instance, serializer=self.serializer_class,
                           old_obj=_instance).apply_async(serializer='pickle')

    def change_status_document_on_removed_by_agent(self, instance, sailor_id, save_history):
        old_instance = deepcopy(instance)
        instance.status_document_id = magic_numbers.STATUS_REMOVED_DOCUMENT
        instance.status_id = magic_numbers.STATUS_REMOVED_DOCUMENT
        instance.save(force_update=True)
        save_history.s(user_id=self.request.user.pk,
                       sailor_key_id=sailor_id,
                       module=instance._meta.object_name,
                       action_type='edit',
                       content_obj=instance,
                       serializer=self.serializer_class,
                       old_obj=old_instance,
                       new_obj=instance,
                       ).apply_async(serializer='pickle')


class FullSailorViewSet(SailorGetQuerySetMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    Sailor ViewSet which have all methods(GET, POST, DELETE, UPDATE, LIST) and use for override GetQuerySet and getObject
    """
    sailor_lookup = 'sailor_pk'

    def get_object(self):
        # if self.request.version == 'v2':
        return super().get_object()
        # return super(FullSailorViewSet, self).get_object()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = self.perform_destroy(instance)
        return Response(self.serializer_class(response).data, status=status.HTTP_200_OK) \
            if response else Response(status=status.HTTP_204_NO_CONTENT)
