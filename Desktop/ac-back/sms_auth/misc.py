import json
import random
import xml.etree.ElementTree as ET
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import requests
import turbosmsua
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from communication.models import SailorKeys
from personal_cabinet.models import PersonalDataProcessing
from sailor.models import Passport, ContactInfo, Profile, PhotoProfile
from sms_auth.models import HistoryNotification, PhotoDocumentForVerification, SecurityCode, UserStatementVerification

User = get_user_model()


def xml_parser(xml_str):
    obj = ET.fromstring(xml_str)
    state = obj.find('state')
    if state is None:
        return {}
    return state.attrib


def _send_sms_via_sms_fly(phone, message, alpha_name='ITCS'):
    text = f'''
        <?xml version="1.0" encoding="utf-8"?>
        <request>
    	    <operation>SENDSMS</operation>
    	    <message start_time="AUTO" end_time="AUTO" lifetime="4" rate="120" desc="" source="{alpha_name}">
    		    <body>{message}</body>
    		    <recipient>{phone}</recipient>
    	    </message>
        </request>
        '''
    headers = {'Content-Type': 'application/xml; charset=UTF-8'}
    sending = requests.post('http://sms-fly.com/api/api.php', data=text.encode('utf-8'), headers=headers,
                            auth=settings.SMS_AUTH)
    response = {}
    if sending.status_code == 200:
        response = xml_parser(sending.text)
    return {'id_mailing': response.get('campaignID'), 'status_answer': sending.status_code,
            'distance_code': response.get('code'), 'date_answer': response.get('date')}


def _send_sms_via_turbosms(phone, message, alpha_name='Mariner'):
    t = turbosmsua.Turbosms(*settings.TURBO_SMS_AUTH)
    send_statuses = t.send_text(alpha_name, str(phone), text=message)
    return {'distance_code': send_statuses.get('status'), 'status_answer': send_statuses.get('status'),
            'id_mailing': send_statuses.get('campaignID'), 'date_answer': send_statuses.get('date'),
            }


def send_message(phone, message, document_obj=None, alpha_name='ITCS', service='sms-fly'):
    time_end_sms = datetime.now(timezone.utc) - timedelta(minutes=1)
    sms_sending = HistoryNotification.objects.filter(destination=phone, send_time__gt=time_end_sms)
    if sms_sending.exists():
        return None
    if service == 'sms-fly':
        response = _send_sms_via_sms_fly(phone, message, alpha_name)
    else:
        response = _send_sms_via_turbosms(phone, message, alpha_name)
    HistoryNotification.objects.create(destination=phone, message=message, content_object=document_obj, type='Phone',
                                       **response)
    return True


def generic_password(len_password):
    """Генератор пароля"""
    chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    symbols = [random.choice(chars) for _ in range(len_password)]
    return ''.join(symbols)


def create_user_for_personal_cabinet(statement: UserStatementVerification = None, user_ver=None):
    from sailor.serializers import ProfileMainInfoSerializer
    from sailor.tasks import save_history
    """Создаение пользователя для ЛК"""
    username = statement.phone
    if not username:
        raise ValidationError({'error': 'Not username'})
    if username.startswith('+') is False:
        username = '+' + username
    sailor = SailorKeys.objects.filter(id=statement.sailor_id).first()
    if sailor is None:
        raise ValidationError({'error': 'Sailor not exists'})
    if sailor.user_id:
        raise ValidationError({'error': 'Sailor has user'})
    try:
        User.objects.get(username=username)
        raise ValidationError({'error': 'A user with this name is already registered'})
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password=generic_password(8))
    sailor.user_id = user.id
    sailor.save()
    user.last_name = sailor.pk
    user.save(update_fields=['last_name'])
    profile = Profile.objects.get(id=sailor.profile)
    old_profile = deepcopy(profile)
    update_sailor_main_info(statement=statement, sailor=sailor)
    if not user_ver:
        user_ver = user.id
    save_history.s(user_id=user_ver, sailor_key_id=sailor.pk, module='UserVerification', action_type='edit',
                   content_obj=old_profile, serializer=ProfileMainInfoSerializer, new_obj=profile,
                   old_obj=old_profile).apply_async(serializer='pickle')
    # вызвать функцию отправки смс (передать Celery)
    if statement.service == statement.ETRANSPORT:
        text = (f'Шановний {profile.first_name_ukr} {profile.middle_name_ukr}, Ви зареєстровани в Кабінеті Моряка. '
                f'Скористатися послугами Кабінета Моряка Ви можете за посиланням sea.e-transport.gov.ua')
        send_message(username, text, service='sms-fly')
    elif statement.service == statement.MORRICHSERVICE:
        text = (f'Шановний {profile.first_name_ukr} {profile.middle_name_ukr}, '
                f'Ви зареєстровани в Особистому Кабінеті Моряка. '
                f'Скористатися послугами Особистому Кабінета Моряка '
                f'Ви можете за посиланням cabinet.morrichservice.com.ua')
        send_message(username, text, service='sms-fly', alpha_name='AirXpress')
    else:
        text = (f'Шановний {profile.first_name_ukr} {profile.middle_name_ukr}, Ви зареєстровани в Порталі моряка. '
                f'Скористатися послугами порталу Ви можете в мобільному додатку MDU або за '
                f'посиланням MDU')
        send_message(username, text, service='sms-fly')
    PersonalDataProcessing.objects.create(sailor=sailor.pk, is_accepted=True)


def update_sailor_main_info(statement=None, sailor=None):
    """Обновление/добавление информанции о моряке"""
    profile = Profile.objects.get(id=sailor.profile)
    if profile.contact_info:
        sailor_contacts = json.loads(profile.contact_info)
    else:
        sailor_contacts = []
    new_contacts = []
    try:
        phone = ContactInfo.objects.update_or_create(value=statement.phone, type_contact_id=1,
                                                     defaults={'is_actual': True})[0]
        new_contacts.append(phone.id)
    except ContactInfo.MultipleObjectsReturned:
        pass
    try:
        email = ContactInfo.objects.update_or_create(value=statement.email, type_contact_id=2,
                                                     defaults={'is_actual': True})[0]
        new_contacts.append(email.id)
    except ContactInfo.MultipleObjectsReturned:
        pass
    sailor_contacts = list(set(sailor_contacts + new_contacts))
    profile.contact_info = json.dumps(sailor_contacts)
    profile.save(update_fields=['contact_info'])

    citizen_passport = sailor.citizen_passport
    name_photo_in_statement = list(PhotoDocumentForVerification.objects.filter(id__in=statement.photo).
                                   values_list('photo', flat=True))
    photos_profile = [PhotoProfile(photo=photo) for photo in name_photo_in_statement]
    photo_profile = PhotoProfile.objects.bulk_create(photos_profile)
    ids_photoprofile = [photo.pk for photo in photo_profile]
    if not citizen_passport:
        create_new_citizen_passport(sailor=sailor, statement=statement, ids_photoprofile=ids_photoprofile)
    else:
        passport = Passport.objects.filter(id__in=citizen_passport)
        if passport.exists():
            passport = passport.first()
            if not passport.serial:
                passport.serial = statement.passport
            if not passport.inn:
                passport.inn = statement.inn
            if passport.photo is None:
                passport_photo = []
            else:
                passport_photo = json.loads(passport.photo)
            passport.photo = json.dumps(passport_photo + ids_photoprofile)
            passport.save()
        else:
            create_new_citizen_passport(sailor=sailor, statement=statement, ids_photoprofile=ids_photoprofile)


def create_new_citizen_passport(sailor=None, statement=None, ids_photoprofile=None):
    """
    Создание нового гражданского паспорта для моряка
    """
    passport = Passport.objects.create(serial=statement.passport, inn=statement.inn,
                                       photo=json.dumps(ids_photoprofile))
    sailor.citizen_passport = [passport.id]
    sailor.save(update_fields=['citizen_passport'])


def create_sms_code(phone_number=None):
    sms_code, created = SecurityCode.objects.get_or_create(phone=phone_number)
    random_security_code = random.randint(100000, 999999)
    sms_code.security_code = random_security_code
    if not created:
        sms_code.created_at = datetime.now()
    sms_code.save()
    return random_security_code
