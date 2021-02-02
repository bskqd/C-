from rest_framework import serializers
from collections import OrderedDict

from rest_framework.fields import SkipField
from rest_framework.response import Response


class ModifiedRelatedField(serializers.RelatedField):
    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([
            (
                item.pk,
                self.display_value(item)
            )
            for item in queryset
        ])


class NameAbstractSerializator(ModifiedRelatedField):
    """
    Используется для полей first_name и last_name
    входные данные
    objct = Model
    """
    objct = object()

    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        response = {'name_ukr': qs.name, 'name_eng': qs.name_en}
        return response

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('set data')
        if type(data) is not dict:
            raise serializers.ValidationError('Data error')
        else:
            try:
                name_ukr = data['name_ukr']
                name_eng = data['name_eng']
            except KeyError:
                raise serializers.ValidationError('Incorect dictinary')
            try:
                return self.objct.objects.get(name=name_ukr, name_en=name_eng)
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            except ValueError:
                raise serializers.ValidationError('id must be a integer field')
            except self.objct.DoesNotExist:
                new_first_name = self.objct.objects.create(name=name_ukr, name_en=name_eng)
                return new_first_name


class UpdateModelMixinOnlyPatch(object):
    """
    Update a model instance. Disable put update, but patch still enable
    """
    def partial_update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class ToReprMixin(object):
    def to_representation(self, instance):
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if not field.write_only]

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue
            if attribute is None and field.field_name != 'photo':
                ret[field.field_name] = ''

            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class PrivateField(serializers.ReadOnlyField):

    def get_attribute(self, instance):
        """
        Given the *outgoing* object instance, return the primitive value
        that should be used for this field.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if self.context['request'].user.has_perm('sailor.writeCheckDocuments') is True or\
                    self.context['request'].user.has_perm('sailor.readAuthorCreate') is True:
                return super(PrivateField, self).get_attribute(instance)
            return None
        return super(PrivateField, self).get_attribute(instance)


class PrivateVerificationField(serializers.ReadOnlyField):
    def get_attribute(self, instance):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if self.context['request'].user.has_perm('sailor.readAuthorApprov') is True:
                return super(PrivateVerificationField, self).get_attribute(instance)
            return None
        return super(PrivateVerificationField, self).get_attribute(instance)
