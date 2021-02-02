import json
from copy import deepcopy

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from communication.models import SailorKeys
from itcs import celery_app, magic_numbers
from sailor.models import Profile, ContactInfo, SailorPassport
from sailor.serializers import SailorPassportSerializer
from sailor.statement.models import StatementSQC
from sailor.tasks import save_history

User = get_user_model()


@celery_app.task
def sync_statement_sqc(statement_id):
    instance = StatementSQC.objects.get(id=statement_id)
    if (instance.date_meeting and instance.is_payed and
            instance.status_document_id == magic_numbers.status_state_qual_dkk_approv):
        # Create userexam in AST
        ast_url = settings.AST_URL
        sailor_key = SailorKeys.by_document.id(instance=instance)
        profile = Profile.objects.get(id=sailor_key.profile)
        try:
            user = User.objects.get(id=sailor_key.user_id)
            phone = user.username if user.username.startswith('+380') else None
        except User.DoesNotExist:
            phone = None
        if not phone:
            phone = ContactInfo.objects.filter(id__in=json.loads(profile.contact_info), type_contact_id=1).first()
        data = {
            'positions': instance.list_positions,
            'statement_number': instance.get_number,
            'statement_id': instance.id,
            'date_meeting': instance.date_meeting.strftime('%Y-%m-%d'),
            'branch_office': instance.branch_office.id,
            'first_name': profile.first_name_ukr,
            'last_name': profile.last_name_ukr,
            'middle_name': profile.middle_name_ukr,
            'birth_date': profile.date_birth.strftime('%Y-%m-%d'),
            'is_continue': instance.is_continue,
            'is_cadet': instance.is_cadet,
            'id': statement_id,
            'phone': phone
        }
        refresh_token = RefreshToken.for_user(User.objects.get(id=16))
        access_token = str(refresh_token.access_token)
        response = requests.post(url=f'{ast_url}administration/autocreate/{sailor_key.id}/', json=data,
                                 headers={'Authorization': f'Token {access_token}'})
        if response.status_code in (200, 201):
            resp_data = response.json()
            userexam_id = resp_data.get('user_exam_id')
            instance.userexam_id = userexam_id
            instance.save(update_fields=['userexam_id'])


@celery_app.task
def disable_statement_sqc(statement_id):
    refresh_token = RefreshToken.for_user(User.objects.get(id=16))
    access_token = str(refresh_token.access_token)
    ast_url = settings.AST_URL
    response = requests.get(url=f'{ast_url}/administration/cancel_exam/{statement_id}/',
                            headers={'Authorization': f'Token {access_token}'})
    print(response)
    return True if response.status_code == 204 else False


@celery_app.task
def disable_old_sailor_passport(sailor_id, exclude_id):
    try:
        sailor = SailorKeys.objects.get(id=sailor_id)
    except SailorKeys.DoesNotExist:
        return
    old_passport = SailorPassport.objects.filter(
        id__in=sailor.sailor_passport, status_document_id=magic_numbers.status_qual_doc_valid
    ).exclude(id=exclude_id)
    for passport in old_passport:
        old_object = deepcopy(passport)
        passport.status_document_id = magic_numbers.status_qual_doc_canceled
        passport.save()
        save_history.s(user_id=13, module='SailorPassport', action_type='edit', content_obj=passport,
                       serializer=SailorPassportSerializer, new_obj=passport, old_obj=old_object,
                       sailor_key_id=sailor.pk).apply_async(serializer='pickle')
    return True