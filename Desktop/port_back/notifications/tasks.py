from datetime import date

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import port_back.constants
from core.models import User
from notifications.models import UserNotification
from port_back.celery import celery_app
from ship.models import IORequest


@celery_app.task
def send_email(email: str, title, template_name: str, data_for_template: dict):
    html_message = render_to_string(template_name, data_for_template)
    subject, from_email, to = title, 'info@port.in.ua', email
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    return True


@celery_app.task
def informing_about_change_status_iorequest(io_request_id: int, ship_key: int, text_status: str, id_author_changes: int,
                                            remarks=None):
    io_request = IORequest.objects.get(id=io_request_id)
    title = f'Changed the status of request No. {io_request.full_number}'
    author = io_request.author
    data_for_template = {
        'name': author.get_user_full_name,
        'full_number': io_request.full_number,
        'event': 'input' if io_request.type == IORequest.INPUT else 'output',
        'ship_name': io_request.ship_name,
        'name_port': io_request.port.name,
        'status': text_status,
        'remarks': remarks,
        'link': f'{settings.HOST_DOMAIN}/request/{io_request_id}/{ship_key}/view/'
    }
    create_notification_about_change_status_iorequest.s(iorequest_id=io_request_id,
                                                        text_status=text_status,
                                                        id_author_changes=id_author_changes,
                                                        ship_id=ship_key,
                                                        ).apply_async()
    send_email(email=author.email,
               title=title,
               template_name='change_status_iorequest.html',
               data_for_template=data_for_template)
    return True


@celery_app.task
def create_notification_about_new_iorequest(iorequest_id, ship_id):
    io_request = IORequest.objects.get(id=iorequest_id)
    author = io_request.author
    user_recipients = []
    if author.type_user == User.AGENT_CH:
        head_agency = author.agent.agency.agency_user.user.pk
        user_recipients.append(head_agency)
    user_recipients += [io_request.port.harbor_master.user_id]
    user_recipients += list(io_request.port.harborworker_set.all().values_list('user_id', flat=True))
    event = 'in' if io_request.type == IORequest.INPUT else 'from'
    text_message = f'{author.get_user_full_name} created a new {io_request.type} request ' \
                   f'No. {io_request.full_number} of the {io_request.ship_name} vessel {event} ' \
                   f'the port of {io_request.port.name}. ' \
                   f'Please view the request.'
    bulk_notification = [UserNotification(recipient_id=recipient_id,
                                          title=f'A new {io_request.type} request has been created',
                                          text=text_message,
                                          content_object=io_request,
                                          ship_id=ship_id)
                         for recipient_id in user_recipients]
    UserNotification.objects.bulk_create(bulk_notification)
    return True


@celery_app.task
def create_notification_about_change_status_iorequest(iorequest_id, text_status, id_author_changes, ship_id):
    io_request = IORequest.objects.get(id=iorequest_id)
    author = io_request.author
    user_recipients = [author.pk]
    if author.type_user == User.AGENT_CH:
        head_agency = author.agent.agency.agency_user.user.pk
        user_recipients.append(head_agency)
    user_recipients += [io_request.port.harbor_master.user_id]
    user_recipients += list(io_request.port.harborworker_set.all().values_list('user_id', flat=True))
    if id_author_changes in user_recipients:
        user_recipients.remove(id_author_changes)
    event = 'in' if io_request.type == IORequest.INPUT else 'from'
    text_message = f'The status of the request No. {io_request.full_number} for the {io_request.type} ' \
                   f'of the {io_request.ship_name} vessel {event} the port of {io_request.port.name} ' \
                   f'has been changed to {text_status}. ' \
                   f'Please view the request.'
    bulk_notification = [UserNotification(recipient_id=recipient_id,
                                          title=f'Changed the status of request No. {io_request.full_number}',
                                          text=text_message,
                                          content_object=io_request,
                                          ship_id=ship_id)
                         for recipient_id in user_recipients]
    UserNotification.objects.bulk_create(bulk_notification)
    return True


@celery_app.task
def clear_user_notifications():
    min_valid_date = date.today() - relativedelta(months=port_back.constants.VALID_NOTIFICATIONS_MONTHS)
    UserNotification.objects.filter(date_send__lte=min_valid_date).delete()
    return True
