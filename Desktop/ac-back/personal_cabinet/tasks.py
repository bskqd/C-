import json
from copy import deepcopy

from itcs.celery import celery_app
from sailor.models import Profile, ContactInfo
from sailor.tasks import save_history
from sailor.serializers import ShortMainInfoSerializer


@celery_app.task
def added_phone_to_profile(profile_id=None, phone_number=None, sailor_id=None, user_id=None):
    """
    Добавление номера телефона к контактам моряка
    """
    profile = Profile.objects.get(id=profile_id)
    if profile.contact_info:
        sailor_contacts = json.loads(profile.contact_info)
    else:
        sailor_contacts = []
    sailor_phones = list(ContactInfo.objects.filter(id__in=sailor_contacts, type_contact=1).values_list('value',
                                                                                                        flat=True))
    if phone_number not in sailor_phones:
        old_profile = deepcopy(profile)
        new_contact, _ = ContactInfo.objects.get_or_create(value=phone_number, type_contact_id=1)
        sailor_contacts.append(new_contact.id)
        profile.contact_info = json.dumps(sailor_contacts)
        profile.save()
        save_history.s(user_id=user_id, module='Profile', action_type='edit', content_obj=profile,
                       serializer=ShortMainInfoSerializer, new_obj=profile, sailor_key_id=sailor_id,
                       old_obj=old_profile).apply_async(serializer='pickle')
    return True
