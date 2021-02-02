import json
from copy import deepcopy
from datetime import date, timedelta, datetime

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import agent.serializers
from agent.models import StatementAgentSailor, AgentSailor, CodeToStatementAgentSailor
from communication.models import SailorKeys
from itcs import celery_app, magic_numbers
from notifications.models import DevicesData
from notifications.tasks import send_push_notifications
from sailor.models import Profile, ContactInfo
from sailor.tasks import save_history
from sms_auth.misc import send_message

User = get_user_model()

@celery_app.task
def send_agent_email(email=None, username=None, password=None, approved=True):
    if approved:
        html_message = render_to_string('agent/approved_account.html',
                                        {'username': username, 'password': password})
    else:
        html_message = render_to_string('agent/reject_account.html',
                                        )
    # subject, from_email, to = 'Зміна статусу заяви на агента', 'info@e-sailor.com.ua', email
    subject, from_email, to = 'Зміна статусу заяви на довірену особу', 'info@airxpress.com.ua', email
    plain_message = strip_tags(html_message)
    resp = send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    return resp


@celery_app.task
def send_email_about_new_statement(email=None, sailor_full_name=None, sailor_phone=None):
    html_message = render_to_string('agent/new_sailor.html',
                                    {'sailor_full_name': sailor_full_name, 'sailor_phone': sailor_phone,
                                     })
    # subject, from_email, to = 'Нова заява моряка', 'info@e-sailor.com.ua', email
    subject, from_email, to = 'Нова заява моряка', 'info@airxpress.com.ua', email
    plain_message = strip_tags(html_message)
    resp = send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    return resp


@celery_app.task
def send_sms_about_new_statement(phone=None, sailor_full_name=None, agent_full_name=None):
    text = f'Шановний(а), {agent_full_name}, моряк {sailor_full_name} бажає, щоб ви стали його довіренною особою.'
    send_message(phone=phone, message=text, service='sms-fly', alpha_name='AirXpress')
    return True


@celery_app.task
def send_notification_about_wait_sailor(statement_id):
    """
    Send sms message and notification about wait sailor apply
    :param statement_id:
    :return:
    """
    statement = StatementAgentSailor.objects.get(id=statement_id)
    sailor_key = SailorKeys.objects.get(id=statement.sailor_key)
    profile = Profile.objects.get(id=sailor_key.profile)
    sailor_full_name = profile.get_full_name_ukr
    user = User.objects.get(id=sailor_key.user_id)
    if user.username.startswith('+380'):
        phone = user.username
    else:
        contact = ContactInfo.objects.filter(id__in=json.loads(profile.contact_info), type_contact_id=1).first()
        phone = contact.value if contact else None
    if not phone:
        return False
    text = f'Шановний(а), {sailor_full_name}, ваша заява до довіреної особи була схвалена. ' \
           f'Довірена особа очiкує вашого підтвердження з порталу моряка'
    send_message(phone=phone, message=text, service='sms-fly', alpha_name='AirXpress')
    user_device = DevicesData.objects.filter(user=user)
    if not user_device.exists():
        return True
    for device in user_device:
        send_push_notifications.s(
            user_device_id=device.pk,
            title='Зміна статусу заяви до довіреної особи',
            message=text
        ).apply_async()
    return True


@celery_app.task
def deactived_statement(sailor_key=None, user_id=None, exclude_statement=None):
    from agent.serializers import StatementAgentSailorSerializer
    statements = StatementAgentSailor.objects.filter(
        sailor_key=sailor_key, status_document_id=magic_numbers.status_statement_agent_sailor_in_process
    ).exclude(id=exclude_statement)
    for statement in statements:
        _statement = deepcopy(statement)
        statement.status_document_id = magic_numbers.status_statement_agent_sailor_invalid
        statement.save()
        save_history.s(user_id=user_id, module='StatementAgentSailor', action_type='edit',
                       content_obj=statement, serializer=StatementAgentSailorSerializer, new_obj=statement,
                       old_obj=_statement, sailor_key_id=statement.sailor_key).apply_async(serializer='pickle')
    return True


@celery_app.task
def send_sms_about_wait_sailor(statement_id):
    statement = StatementAgentSailor.objects.get(id=statement_id)
    sailor_key = SailorKeys.objects.get(id=statement.sailor_key)
    profile = Profile.objects.get(id=sailor_key.profile)
    sailor_full_name = profile.get_full_name_ukr
    user = User.objects.get(id=sailor_key.user_id)
    if user.username.startswith('+380'):
        phone = user.username
    else:
        contact = ContactInfo.objects.filter(id__in=json.loads(profile.contact_info), type_contact_id=1).first()
        phone = contact.value if contact else None
    if not phone:
        return False
    text = f'Шановний(а), {sailor_full_name}, ваша заява до довіреної особи була схвалена. ' \
           f'Довірена особа очiкує вашого підтвердження з порталу моряка'
    send_message(phone=phone, message=text, service='sms-fly', alpha_name='AirXpress')
    return True


@celery_app.task
def send_email_about_expiration_proxy(email, text, agent=False):
    """
    Sends information about the expiration of the power of attorney (proxy) to an email
    """
    html_message = render_to_string('agent/end_proxy.html',
                                    {'text': text, 'agent': agent})
    # subject, from_email, to = 'Tермін дії довіреності', 'info@e-sailor.com.ua', email
    subject, from_email, to = 'Tермін дії довіреності', 'info@airxpress.com.ua', email
    plain_message = strip_tags(html_message)
    resp = send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    return resp


@celery_app.task
def send_sms_sailor(phone, text, sailor_id=None):
    """
    Sends an SMS message to the sailor
    """
    if sailor_id:
        sailor_key = SailorKeys.objects.get(id=sailor_id)
        user = User.objects.get(id=sailor_key.user_id)
        if user.username.startswith('+380'):
            phone = user.username
    if not phone:
        return False
    send_message(phone=phone, message=text, service='sms-fly', alpha_name='AirXpress')
    return True


@celery_app.task
def send_notification_about_expiration_proxy(sailor_id, text):
    """
    Sends notification about the expiration of the power of attorney (proxy)0
    """
    sailor_key = SailorKeys.objects.get(id=sailor_id)
    user = User.objects.get(id=sailor_key.user_id)
    user_device = DevicesData.objects.filter(user=user)
    if not user_device.exists():
        return False
    for device in user_device:
        send_push_notifications.s(
            user_device_id=device.pk,
            title='Термін дії довіреності',
            message=text
        ).apply_async()
    return True


@celery_app.task
def informing_agent_about_expiration_proxy(list_contacts, text_for_agent):
    """
    Informing the agent about the expiration of the power of attorney (proxy) between him and the sailor
    """
    agent_contacts = ContactInfo.objects.filter(id__in=list_contacts)
    agent_email = agent_contacts.filter(type_contact_id=2).first().value
    send_email_about_expiration_proxy.delay(agent_email, text_for_agent, agent=True)
    agent_phone = agent_contacts.filter(type_contact_id=1).first().value
    send_sms_sailor.delay(agent_phone, text_for_agent)


@celery_app.task
def informing_sailor_about_expiration_proxy(list_contacts, text_for_sailor, sailor_id):
    """
    Informing the sailor about the expiration of the power of attorney (proxy) between him and the agent
    """
    sailor_phone = None
    if list_contacts:
        sailor_contacts = ContactInfo.objects.filter(id__in=list_contacts)
        sailor_emails = sailor_contacts.filter(type_contact_id=2)
        if sailor_emails.exists():
            sailor_email = sailor_emails.first().value
            send_email_about_expiration_proxy.delay(sailor_email, text_for_sailor)
        sailor_phone = sailor_contacts.filter(type_contact_id=1).first()
        if sailor_phone:
            sailor_phone = sailor_phone.value
    send_sms_sailor.delay(sailor_phone, text_for_sailor, sailor_id)
    send_notification_about_expiration_proxy.delay(sailor_id, text_for_sailor)


@celery_app.task
def work_with_relationship_agent_sailor(filtering: dict, endswith_text, action_delete=False):
    """
    Informs sailors and agents about the status of the power of attorney (proxy).
    If action_delete=True removes the connection agent sailor
    """
    agent_sailor = AgentSailor.objects.filter(**filtering)
    time_sending_sms = datetime.utcnow() + timedelta(hours=14)
    for relation in agent_sailor:
        relation: AgentSailor
        agent_profile = relation.agent.userprofile
        agent_full_name = agent_profile.full_name_ukr
        sailor_key = SailorKeys.objects.get(id=relation.sailor_key)
        profile = Profile.objects.get(id=sailor_key.profile)
        sailor_full_name = profile.get_full_name_ukr
        text_for_agent = f'Шановний(а), {agent_full_name}. Між Вами та моряком - {sailor_full_name}, {endswith_text}.'
        text_for_sailor = f'Шановний(а), {sailor_full_name}. ' \
                          f'Між Вами та Вашою довіренною особою - {agent_full_name}, {endswith_text}.'
        if profile.contact_info:
            sailor_list_contacts = json.loads(profile.contact_info)
            informing_sailor_about_expiration_proxy.s(sailor_list_contacts, text_for_sailor, sailor_key.pk
                                                      ).apply_async(eta=time_sending_sms)
        informing_agent_about_expiration_proxy.s(agent_profile.contact_info, text_for_agent
                                                 ).apply_async(eta=time_sending_sms)
        if action_delete:
            sailor_key.agent_id = None
            sailor_key.save(update_fields=['agent_id'])
            save_history.s(user_id=magic_numbers.celery_user_id,
                           module='AgentSailor',
                           action_type='delete',
                           content_obj=relation,
                           serializer=agent.serializers.AgentSailorSerializer,
                           old_obj=relation,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
    if action_delete:
        agent_sailor.all().delete()
    return True


@celery_app.task
def delete_relationship_agent_sailor():
    """
    Terminates the contract between the sailor and the agent upon expiry of the power of attorney (proxy)
    """
    filtering = {'date_end_proxy__lt': date.today().strftime('%Y-%m-%d')}
    endswith_text = 'закінчився термін дії довіреності'
    work_with_relationship_agent_sailor.delay(filtering=filtering, endswith_text=endswith_text, action_delete=True)


@celery_app.task
def informing_agent_sailor_about_expiration_proxy():
    """
    Informing the sailor and the agent about the imminent expiration of the power of attorney (proxy) between them
    """
    days = 60
    date_end = date.today() + timedelta(days=days)
    filtering = {'date_end_proxy': date_end.strftime('%Y-%m-%d')}
    endswith_text = f'через {days} днів закінчиться термін дії довіреності'
    work_with_relationship_agent_sailor.delay(filtering=filtering, endswith_text=endswith_text)


@celery_app.task
def clear_security_code_to_statement_agent_sailor():
    """
    Removes unused secret codes to create a statement Agent-Sailor
    """
    code_lifetime_in_days = 1
    clear_date = datetime.today() - timedelta(hours=24 * code_lifetime_in_days)
    security_code = CodeToStatementAgentSailor.objects.filter(created_at__lt=clear_date)
    security_code.delete()
    return True
