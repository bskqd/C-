import logging
from datetime import date
from json import JSONDecodeError

import requests
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet, F
from django.forms.models import model_to_dict

from back_office.models import ETIMonthRatio, CoursePrice, DependencyItem
from certificates.models import ETIRegistry
from certificates.serializers import FullInfoETIMonthRatioSerializer
from communication.models import SailorKeys
from itcs import celery_app, magic_numbers
from sailor.document.models import CertificateETI
from sailor.models import Profile
from sailor.statement.models import StatementETI
from sailor.tasks import save_history
from user_profile.models import FullUserSailorHistory

eti_integration_logger = logging.getLogger('eti_integration')


@celery_app.task
def history_eti_month_ratio(del_ratio, user_id, course_id):
    content_type = ContentType.objects.get_for_model(model=ETIMonthRatio)
    for ratio in del_ratio:
        FullUserSailorHistory.objects.create(user_id=user_id,
                                             sailor_key=None,
                                             module='ETIMonthRatio',
                                             action_type='delete',
                                             content_type=content_type,
                                             object_id=ratio['id'],
                                             old_obj_json=ratio,
                                             new_obj_json=None)

    for ratio in ETIMonthRatio.objects.filter(course_id=course_id):
        save_history.s(user_id=user_id,
                       module='ETIMonthRatio',
                       action_type='create',
                       content_obj=ratio,
                       serializer=FullInfoETIMonthRatioSerializer,
                       new_obj=ratio,
                       ).apply_async(serializer='pickle')


@celery_app.task(bind=True, max_retries=5, countdown=10)
def send_statement_to_eti(self, statement_id, is_edit=False):
    if not settings.ENABLE_ETI_INTEGRATION:
        return False
    statement = StatementETI.objects.select_related('course', 'institution').get(id=statement_id)
    sailor_key = SailorKeys.objects.filter(statement_eti__overlap=[statement.pk])
    sailor_instance: SailorKeys = sailor_key.first()
    profile = Profile.objects.get(id=sailor_instance.profile)
    rating = profile.get_rating
    headers = {'Authorization': 'Token 4b97bd09bad2666962b82e9b132f2d96e523dba3'}
    eti_integration_logger.info(f'Send statement to eti initial. Is edit:{str(is_edit)}')
    if not sailor_instance:
        error_message = 'Statement ETI has not sailor'
        eti_integration_logger.error(error_message,
                                     extra={'statement_id': statement.pk})
        return 'Statement ETI has not sailor'
    url = 'https://ntz.itcs.org.ua/mariner/api/certApplications/'
    parameters = {'statement_cert_id': statement.pk,
                  'number': statement.number,
                  'course': str(statement.course.uuid),
                  'institution': str(statement.institution.uuid),
                  'is_payed': statement.is_payed,
                  'date_meeting': str(statement.date_meeting),
                  'date_end_meeting': str(statement.date_end_meeting),
                  'is_continue': statement.is_continue,
                  'status_document': statement.status_document_id,
                  'rating': rating
                  }
    sailor_info = model_to_dict(profile,
                                exclude=['sex', 'contact_info', 'photo', 'id', 'middle_name_eng', 'date_birth',
                                         'created_at', 'author', 'modified_at'])
    sailor_info.update({'date_birth': str(profile.date_birth)})
    parameters.update(sailor_info)
    eti_integration_logger.info({'statement_id': statement_id,
                                 'request_data': parameters})
    if is_edit:
        url = f'https://ntz.itcs.org.ua/mariner/api/certApplications/{statement.pk}/'
        resp = requests.put(url, json=parameters, headers=headers)
    else:
        resp = requests.post(url, json=parameters, headers=headers)
    if resp.status_code not in [200, 201]:
        eti_integration_logger.error(f'Send create({str(is_edit)}) statement ETI: {resp.text}',
                                     extra={'response_data': resp.text, 'request_data': parameters,
                                            'url': url})
        try:
            json_resp = resp.json()
            message = json_resp.get('message')
            if message == 'Application Not Found':
                eti_integration_logger.error(f'Send create from edit({str(is_edit)}) statement ETI: {resp.text}',
                                             extra={'response_data': resp.text, 'request_data': parameters,
                                                    'url': url})
                send_statement_to_eti.s(statement_id).apply_async()
                return
            self.retry(countdown=10, exc=resp.text)
        except JSONDecodeError:
            eti_integration_logger.error(f'Decode error from create({str(is_edit)}) statement ETI: {resp.text}',
                                         extra={'response_data': resp.text, 'request_data': parameters,
                                                'url': url})
            self.retry(countdown=10, exc=resp.text)
    else:
        eti_integration_logger.info(f'Send create({str(is_edit)}) statement ETI success: {resp.text}',
                                    extra={'response_data': resp.text, 'request_data': parameters,
                                           'url': url})
    return True


@celery_app.task(bind=True, max_retries=5)
def edit_statement_to_eti(self, statement_id, initial_data):
    if not settings.ENABLE_ETI_INTEGRATION:
        return False
    statement = StatementETI.objects.select_related('course', 'institution').get(id=statement_id)
    sailor_key = SailorKeys.objects.filter(statement_eti__overlap=[statement.pk])
    sailor_instance: SailorKeys = sailor_key.first()
    if not sailor_instance:
        return 'Statement ETI has not sailor'
    headers = {'Authorization': 'Token 4b97bd09bad2666962b82e9b132f2d96e523dba3'}
    url = f'https://ntz.itcs.org.ua/mariner/api/certApplications/{statement_id}/'
    resp = requests.patch(url, json=initial_data, headers=headers)
    if resp.status_code not in [200, 201]:
        eti_integration_logger.error(f'Response Edit statement ETI: {resp.text}',
                                     extra={'response_data': resp.text,
                                            'statement_id': statement_id})
        self.retry(countdown=10, exc=ValueError(resp.text))
    else:
        eti_integration_logger.info(f'Response update statement ETI success: {resp.text}',
                                    extra={'response_data': resp.text,
                                           'statement_id': statement_id})
    return True


@celery_app.task(bind=True, max_retries=5)
def delete_statement_to_eti(self, statement_id):
    if not settings.ENABLE_ETI_INTEGRATION:
        return False
    headers = {'Authorization': 'Token 4b97bd09bad2666962b82e9b132f2d96e523dba3'}
    url = f'https://ntz.itcs.org.ua/mariner/api/certApplications/{statement_id}/'
    resp = requests.delete(url, headers=headers)
    eti_integration_logger.info(f'Send delete statementETI: {statement_id}',
                                extra={'statement_id': statement_id})
    if resp.status_code not in [204, 200]:
        eti_integration_logger.error(f'Response delete statement ETI: {resp.text}',
                                     extra={'statement_id': statement_id,
                                            'response_data': resp.text,
                                            'url': url})
        self.retry(countdown=10, exc=ValueError(resp.text))
    else:
        eti_integration_logger.info('Response delete statement ETI success: {resp.text}',
                                    extra={'response_data': resp.text,
                                           'statement_id': statement_id,
                                           'url': url})
    return True


@celery_app.task
def add_month_sum(statement_id):
    statement = StatementETI.objects.get(id=statement_id)
    if not statement.is_payed:
        return False
    month_ratio = ETIMonthRatio.objects.get(course_id=statement.course_id, ntz=statement.institution)
    course_price: CoursePrice = CoursePrice.for_date.date(date=statement.date_meeting,
                                                          type_of_form='Second',
                                                          course_id=statement.course_id).first()
    month_ratio.month_amount = month_ratio.month_amount + course_price.price
    month_ratio.save(update_fields=['month_amount'])
    ETIMonthRatio.reorder(course=statement.course)
    return True


@celery_app.task
def add_certificate_to_packet(certificate_id):
    cert_instance: CertificateETI = CertificateETI.objects.select_related('statement').get(id=certificate_id)
    if cert_instance.status_document_id != magic_numbers.status_qual_doc_valid:
        return False
    statement_instance: StatementETI = cert_instance.statement
    ct: ContentType = ContentType.objects.get_for_model(statement_instance)
    dependency_item_qs: QuerySet[DependencyItem] = DependencyItem.objects.filter(
        content_type=ct, object_id=statement_instance.pk)
    for dependency_item in dependency_item_qs:
        dependency_item.item = cert_instance
        dependency_item.item_status = DependencyItem.WAS_BOUGHT
        dependency_item.save(force_update=True)
    # dependency_item_qs.update(item=cert_instance, item_status=DependencyItem.WAS_BOUGHT)
    return True


@celery_app.task
def delete_month_ratio_on_end_course():
    dt = date.today()
    for registry in ETIRegistry.objects.filter(date_end=dt).exclude(
            institution_id=F('institution_id'), course_id=F('course_id'), date_end__gt=dt
    ):
        ETIMonthRatio.objects.filter(ntz_id=registry.institution_id, course_id=registry.course_id).delete()
