import json
from itertools import chain

from django.db.models.fields.files import FileField
from django.db.models.fields.related import ManyToManyField, OneToOneField

import port_back.constants
from core.models import Photo
from ship.models import ShipHistory


def custom_model_to_dict(instance, fields=None, exclude=None):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if isinstance(f, ManyToManyField):
            for val in f.value_from_object(instance):
                if f.name in data.keys():
                    data[f.name].append(custom_model_to_dict(val))
                else:
                    data[f.name] = [custom_model_to_dict(val)]
            continue
        if isinstance(f, OneToOneField):
            val = getattr(instance, f.name, None)
            if val:
                data[f.name] = custom_model_to_dict(val)
            else:
                data[f.name] = f.value_from_object(instance)
            continue
        if isinstance(f, FileField):
            val = getattr(instance, f.name, None)
            if val:
                data[f.name] = val.path
            else:
                data[f.name] = None
            continue
        if not getattr(f, 'editable', False):
            continue
        if fields is not None and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        data[f.name] = f.value_from_object(instance)
    data.pop('password', None)
    return data


def last_change_object(request, model, object_id):
    """
    Last changes to an object saved in history
    """
    response = {}
    history = ShipHistory.objects.filter(
        content_type__model=model._meta.model_name,
        object_id=int(object_id),
        history_type__in=[ShipHistory.EDIT, ShipHistory.CREATE]).order_by('-created_at')
    if history.count() in [0, 1]:
        return response
    for index_history in range(port_back.constants.NUMBER_RECENT_CHANGES):
        try:
            last_history = history[index_history]
            pre_last_history = history[index_history + 1]
        except IndexError:
            break
        last_change = last_history.serialized_data
        pre_last_change = pre_last_history.serialized_data
        date = last_history.created_at.strftime('%d.%m.%Y %H:%M:%S')
        changes_list = finding_changes(request, model, last_change, pre_last_change)
        create_obj_and_load_photo = bool(pre_last_history.history_type == ShipHistory.CREATE and
                                         len(changes_list) == 1 and changes_list[0]['new'].get('photo'))
        if not create_obj_and_load_photo and changes_list:
            response.update({date: changes_list})
    return response


def finding_changes(request, model, last_change, pre_last_change):
    """
    Finding differences in information
    """
    changes_list = []
    for key in last_change.keys():
        if key == 'created_at':
            continue
        elif key == '_photo' and pre_last_change[key] != last_change[key]:
            _photo = check_photo_upload(request, last_change, pre_last_change, model)
            if not _photo:
                break
            changes_list.append(_photo)
        elif pre_last_change.get(key) != last_change.get(key):
            changes_list.append({'old': {key: pre_last_change.get(key)},
                                 'new': {key: last_change.get(key)},
                                 'description': key})
    return changes_list


def check_photo_upload(request, last_change, pre_last_change, model):
    """
    Check upload photo for object
    """
    response = []
    last_change_photo = json.loads(last_change.get('_photo'))
    pre_last_change_photo = json.loads(pre_last_change.get('_photo'))
    if len(pre_last_change_photo) > len(last_change_photo):
        return False
    photo_ids = set(last_change_photo) - set(pre_last_change_photo)
    for photo in Photo.objects.filter(id__in=photo_ids):
        photo_info = {
            'id': photo.pk,
            'type_photo': photo.type_photo,
            'file': request.build_absolute_uri(photo.file.url),
            'content_type': model._meta.model_name,
        }
        response.append(photo_info)
    if not response:
        return False
    return {'old': {'photo': []}, 'new': {'photo': response}, 'description': 'photo'}
