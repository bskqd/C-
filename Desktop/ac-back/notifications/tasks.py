import json
from datetime import datetime, timedelta

import botocore
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from communication.models import SailorKeys
from itcs import magic_numbers
from itcs.celery import celery_app
from itcs.settings import PRICE_SERVICE_RECORD
from notifications.misc import client
from notifications.models import DevicesData, HistoryPushData
from sailor.document.models import MedicalCertificate, QualificationDocument, ProofOfWorkDiploma
from sailor.statement.models import StatementServiceRecord, StatementSQC, StatementQualification
from sms_auth.models import HistoryNotification


@celery_app.task(bind=True, max_retries=5)
def save_endpoint_arn(self, id_device=None):
    try:
        endpoint = client.create_platform_endpoint(
            PlatformApplicationArn=settings.AWS_ESAILOR_ARN,
            Token=id_device,
        )
    except botocore.exceptions.ClientError as exc:
        if self.request.retries < self.max_retries - 1:
            self.retry(exc=exc, countdown=60)
        else:
            return str(exc)
    arn = endpoint.get('EndpointArn')
    user_device = DevicesData.objects.get(id_device=id_device)
    user_device.endpoint_arn = arn
    user_device.save()
    return True


@celery_app.task
def save_push_notifications_history(destination=None, message=None,  response=None, service_name=None,
                                    document_id=None):
    id_mailing = response.get('MessageId')
    try:
        status_answer = response['ResponseMetadata']['HTTPStatusCode']
        str_date_answer = response['ResponseMetadata']['HTTPHeaders']['date']
        date_answer = parse(str_date_answer)
    except KeyError:
        status_answer = 400
        date_answer = None

    document_type = None
    if service_name:
        document_type = ContentType.objects.get(model=service_name)

    HistoryNotification.objects.create(destination=destination, type='Push', message=message, id_mailing=id_mailing,
                                       status_answer=status_answer, document_type=document_type, object_id=document_id,
                                       date_answer=date_answer)
    return True


@celery_app.task(bind=True, max_retries=5)
def send_push_notifications(self, user_device_id, title=None, message=None, service_name=None, document_id=None,
                            push_data=None, url_image=None, sound='default',  activity=None, topic=None, color=None,
                            icon=None):
    user_device = DevicesData.objects.get(id=user_device_id)
    if user_device.platform == 'android':
        notification = {
            'notification': {
                'message': message,
                'title': title,
            },
            'data': push_data
        }
    else:
        notification = {
            'notification': {
                'body': message,
                'title': title,
                'sound': sound,
                'badge': 1,
            },
            'apns': {
                'headers': {
                    'apns-priority': '10',
                    'apns-push-type': 'alert',
                },
                'payload': {
                    'aps': {
                        'alert': {
                            'body': message,
                            'title': title,
                            'badge': 1,
                        },
                        'mutable-content': 1,
                    },
                    'image': url_image,
                },
            },
            'data': push_data,
            'mutable_content': 'true',
        }

    data = {'default': 'test', 'GCM': json.dumps(notification)}
    json_data = json.dumps(data)
    try:
        response = client.publish(TargetArn=user_device.endpoint_arn, Message=json_data, MessageStructure='json')
    except botocore.exceptions.ClientError as exc:
        if self.request.retries < self.max_retries - 1:
            self.retry(exc=exc, countdown=60)
        else:
            response = {}
    HistoryPushData.objects.create(push_data=data, user_device_id=user_device_id)
    history_message = f'title - {title}, message - {message}'
    save_push_notifications_history.s(destination=user_device.user.username, message=history_message, response=response,
                                      service_name=service_name, document_id=document_id).apply_async()
    return True


@celery_app.task
def check_end_medical_sertificate():
    date_end_certificate = [datetime.today() + timedelta(days=days) for days in [7, 30]]
    medicals = MedicalCertificate.objects.filter(status_document_id=19, date_end__in=date_end_certificate)
    for certificate in medicals:
        sailor = SailorKeys.by_document.id(instance=certificate)
        if not sailor or not sailor.user_id:
            continue
        str_date = certificate.date_end.strftime('%d.%m.%Y')
        message = f'{str_date} закінчиться строк дії медичної довідки - № {certificate.get_number}'
        title = 'Медична довідка'
        service_name = certificate.__class__.__name__.lower()
        user_devices = DevicesData.objects.filter(user_id=sailor.user_id, is_disable=False, endpoint_arn__isnull=False)
        for device in user_devices:
            send_push_notifications.s(device.id, title, message, service_name=service_name,
                                      document_id=certificate.id).apply_async()
    return True


@celery_app.task
def check_end_proof_of_work_diploma():
    date_end_proof = [datetime.today() + relativedelta(months=month) for month in [1, 6]]
    diplomas = list(QualificationDocument.objects.filter(type_document_id=49).values_list('id', flat=True))
    proof_diplomas = ProofOfWorkDiploma.objects.filter(diploma__in=diplomas,
                                                       status_document_id=magic_numbers.status_qual_doc_valid,
                                                       date_end__in=date_end_proof)
    for proof in proof_diplomas:
        sailor = SailorKeys.by_document.id(instance=proof.diploma)
        if not sailor or not sailor.user_id:
            continue
        str_date = proof.date_end.strftime('%d.%m.%Y')
        title = f'{str_date} закінчиться строк дії підтвердження - № {proof.get_number}'
        message = f'Підтвердження до диплома'
        service_name = proof.__class__.__name__.lower()
        user_devices = DevicesData.objects.filter(user_id=sailor.user_id, is_disable=False, endpoint_arn__isnull=False)
        for device in user_devices:
            send_push_notifications.s(device.id, title, message, service_name=service_name,
                                      document_id=proof.id).apply_async()
    return True


@celery_app.task
def check_end_qual_doc():
    date_end_qual_doc = [datetime.today() + timedelta(days=days) for days in [7, 30]]
    qual_docs = QualificationDocument.objects.filter(type_document__in=magic_numbers.qual_documents_with_end_date,
                                                     date_end__in=date_end_qual_doc,
                                                     status_document=magic_numbers.status_qual_doc_valid)
    for document in qual_docs:
        sailor = SailorKeys.by_document.id(instance=document)
        if not sailor or not sailor.user_id:
            continue
        str_date = document.date_end.strftime('%d.%m.%Y')
        message = f'{str_date} закінчиться строк дії кваліфікаційного документа - № {document.get_number}'
        title = f'{document.type_document.name_ukr}'
        service_name = document.__class__.__name__.lower()
        user_devices = DevicesData.objects.filter(user_id=sailor.user_id, is_disable=False, endpoint_arn__isnull=False)
        for device in user_devices:
            send_push_notifications.s(device.id, title, message, service_name=service_name,
                                      document_id=document.id).apply_async()
    return True


@celery_app.task
def check_unpaid_statement_dkk():
    """
    search for unpaid statements by SQC, and sending sailors push notifications about the need for payment
    """
    title = 'Заява ДКК'
    message = 'У Вас є неоплачена заява ДКК. Будь ласка, виконайте оплату.'
    service_name = StatementSQC.__name__.lower()
    repeated_notification = datetime.today() - timedelta(days=1)
    first_notification = datetime.today() - timedelta(minutes=30)
    unpaid_statement = StatementSQC.objects.filter(
        is_payed=False, created_at__lte=first_notification,
        status_document_id__in=[magic_numbers.status_state_qual_dkk_in_process,
                                magic_numbers.CREATED_FROM_PERSONAL_CABINET])
    for statement in unpaid_statement:
        sailor = SailorKeys.by_document.id(instance=statement)
        if not sailor or not sailor.user_id:
            continue
        history = HistoryNotification.objects.filter(document_type=ContentType.objects.get_for_model(statement).id,
                                                     object_id=statement.id, status_answer=200, type='Push',
                                                     send_time__gte=repeated_notification)
        if history.exists:
            continue
        user_devices = DevicesData.objects.filter(user_id=sailor.user_id, is_disable=False, endpoint_arn__isnull=False)
        for device in user_devices:
            data = {
                'message': message,
                'title': title,
                'type': 'PAYMENT',
                'payment_link': None,
                'sum': statement.rank.price,
                'date_create': f'{datetime.timestamp(datetime.now())}'
            }
            send_push_notifications.s(device.id, title, message, service_name=service_name, document_id=statement.id,
                                      push_data=data).apply_async()
    return True


@celery_app.task
def check_unpaid_statement_service_record():
    """
    search for unpaid statements by SR, and sending sailors push notifications about the need for payment
    """
    title = 'Заява ПКМ'
    message = 'У Вас є неоплачена заява ПКМ. Будь ласка, виконайте оплату.'
    service_name = StatementServiceRecord.__name__.lower()
    repeated_notification = datetime.today() - timedelta(days=1)
    first_notification = datetime.today() - timedelta(minutes=30)
    unpaid_statement = StatementServiceRecord.objects.filter(
        is_payed=False, created_at__lte=first_notification,
        status_id__in=[magic_numbers.status_statement_serv_rec_in_process, magic_numbers.CREATED_FROM_PERSONAL_CABINET])
    for statement in unpaid_statement:
        sailor = SailorKeys.by_document.id(instance=statement)
        if not sailor or not sailor.user_id:
            continue
        history = HistoryNotification.objects.filter(document_type=ContentType.objects.get_for_model(statement).id,
                                                     object_id=statement.id, status_answer=200, type='Push',
                                                     send_time__gte=repeated_notification)
        if history.exists:
            continue
        user_devices = DevicesData.objects.filter(user_id=sailor.user_id, is_disable=False, endpoint_arn__isnull=False)
        for device in user_devices:
            data = {
                'message': message,
                'title': title,
                'type': 'PAYMENT',
                'payment_link': None,
                'sum': PRICE_SERVICE_RECORD,
                'date_create': f'{datetime.timestamp(datetime.now())}'
            }
            send_push_notifications.s(device.id, title, message, service_name=service_name, document_id=statement.id,
                                      push_data=data).apply_async()
    return True


@celery_app.task
def check_unpaid_statement_qual_doc():
    """
    search for unpaid statements by DPD, and sending sailors push notifications about the need for payment
    """
    title = 'Заява ДПВ'
    message = 'У Вас є неоплачена заява ДПВ. Будь ласка, виконайте оплату.'
    service_name = StatementQualification.__name__.lower()
    repeated_notification = datetime.today() - timedelta(days=1)
    first_notification = datetime.today() - timedelta(minutes=30)
    unpaid_statement = StatementQualification.objects.filter(
        is_payed=False, created_at__lte=first_notification,
        status_document_id__in=[magic_numbers.status_state_qual_dkk_in_process,
                                magic_numbers.CREATED_FROM_PERSONAL_CABINET])
    for statement in unpaid_statement:
        sailor = SailorKeys.by_document.id(instance=statement)
        if not sailor or not sailor.user_id:
            continue
        history = HistoryNotification.objects.filter(document_type=ContentType.objects.get_for_model(statement).id,
                                                     object_id=statement.id, status_answer=200, type='Push',
                                                     send_time__gte=repeated_notification)
        if history.exists:
            continue
        user_devices = DevicesData.objects.filter(user_id=sailor.user_id, is_disable=False, endpoint_arn__isnull=False)
        for device in user_devices:
            data = {
                'message': message,
                'title': title,
                'type': 'PAYMENT',
                'payment_link': None,
                'sum': statement.type_document.price,
                'date_create': f'{datetime.timestamp(datetime.now())}'
            }
            send_push_notifications.s(device.id, title, message, service_name=service_name, document_id=statement.id,
                                      push_data=data).apply_async()
    return True
