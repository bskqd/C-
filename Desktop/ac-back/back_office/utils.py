import math
import random
from datetime import date, timedelta
from typing import List

import workdays
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from back_office.models import DependencyItem, PacketItem, PriceForPosition
from certificates.models import TimeForCourse
from communication.models import SailorKeys
from directory.models import ExperinceForDKK
from itcs import magic_numbers
from sailor.document.models import ProtocolSQC
from sailor.models import SailorPassport, DependencyDocuments


def add_sailor_passport_to_packet(sailor, item, include_sailor_passport) -> List[DependencyItem]:
    if not sailor.sailor_passport:
        sailor.sailor_passport = []
    sailor_passport = SailorPassport.objects.filter(
        id__in=sailor.sailor_passport
    ).order_by('-date_end')
    not_renewal_sailor_passport = sailor_passport.order_by('-date_start')
    dependency_bulk = []
    last_passport: SailorPassport = not_renewal_sailor_passport.first()
    can_renewal = (last_passport and
                   last_passport.status_document_id in [magic_numbers.status_qual_doc_expired,
                                                        magic_numbers.status_qual_doc_valid] and
                   not last_passport.date_renewal)
    # Сhecks if POM need to be continued or created
    # rules = TypeOfAccrualRules.objects.filter(
    #     document_type__overlap=['sailor passport', 'seafarer identity card', 'пом',
    #                             'посвідчення особи моряка',
    #                             'паспорт моряка']
    # )
    if include_sailor_passport in [3, 4] and can_renewal:
        rules_id = 6 if include_sailor_passport == 3 else 13
    # if sailor_passport.exists() and not sailor_passport.first().date_renewal:
    #     # Пасспорт существует и не обновлялся
    #     # rule = rules.filter(
    #     #     document_type__overlap=['continue', 'renewal', 'подовження', 'продовження', 'відновдення']
    #     # ).first()   # need to renew
    #     rules_id = 6 if include_sailor_passport == 1 else 13
    else:
        dependency_bulk.append(DependencyItem(packet_item=item, type_document_id=15,
                                              item_status=DependencyItem.TO_BUY))
        rules_id = 5 if include_sailor_passport in [1, 3] else 14
    item_status = DependencyItem.TO_BUY
    dependency_bulk.append(DependencyItem(packet_item=item, type_document_id=rules_id,
                                          item_status=item_status))
    return dependency_bulk


def on_pay_packet_item(packet_id, user_id=None):
    from .tasks import update_service_center_and_agent_in_packet, update_statements_after_payment
    packet = PacketItem.objects.get(id=packet_id)
    response_data = dict()
    for depend in packet.dependencies.filter(item_status=DependencyItem.TO_BUY):
        depend.payment_form1 = depend.get_price_form1
        depend.payment_form2 = depend.get_price_form2
        depend.save(update_fields=['payment_form1', 'payment_form2'])
    response_data['payment_date'] = timezone.now()
    response_data['full_price_form1'] = packet.current_form1_price
    response_data['full_price_form2'] = packet.current_form2_price
    update_service_center_and_agent_in_packet.delay(packet_id)
    update_statements_after_payment.delay(packet_id, user_id)
    return response_data


def get_price_for_agent(price):
    agent_precent = PriceForPosition.today_second_form.get(type_document_id=9)
    return price / 100 * agent_precent.full_price


def hours_to_date(hours, working_day=8):
    days = hours / working_day
    return math.ceil(days)


def get_available_day_for_start_packet(sailor_id, packet_id, add_one_day=True):
    today = date.today()
    packet_after_today = PacketItem.by_sailor.filter_by_sailor(
        sailor_key=sailor_id, date_end_meeting__gt=today,
    ).exclude(id=packet_id)
    if packet_after_today.exists():
        date_start = packet_after_today.order_by('date_end_meeting').last().date_end_meeting
    else:
        date_start = today
    if add_one_day:
        return workdays.workday(date_start, days=1)
    elif date_start.isoweekday() in [6, 7]:
        date_start += timedelta(days=8 - date_start.isoweekday())
        return date_start
    return date_start


def get_date_end_meeting_for_certificate_eti(date_meeting, course_id, is_continue):
    default_time = 8 * 10
    try:
        time = TimeForCourse.objects.get(is_continue=is_continue, course_id=course_id).full_time
    except TimeForCourse.DoesNotExist:
        try:
            time = TimeForCourse.objects.get(is_continue=False, course_id=course_id).full_time
        except TimeForCourse.DoesNotExist:
            time = default_time
    return workdays.workday(date_meeting, hours_to_date(time, working_day=12))


def check_diploma_of_higher_education(docs):
    """
    Checks that the required educational documents (Diploma of Higher Education) in the status 'Valid' for creating
    the packet are available from the sailor
    """
    diploma_of_higher_education = 1
    for document in docs['all_docs']:
        if document.__class__.__name__ == 'Education' and document.type_document_id == diploma_of_higher_education and \
                document.status_document_id == magic_numbers.VERIFICATION_STATUS:
            raise ValidationError('Not diploma of higher education')
    for dependency_document in docs['not_exists_docs']:
        dependency_document: DependencyDocuments
        if dependency_document.type_document == 'Диплом про вищу освіту':
            raise ValidationError('Not diploma of higher education')
    return True


def check_repeat_statement_sqc(sailor_key: SailorKeys, list_positions: List[int]):
    """
    Checks the availability of not passed SQC exams before submitting a statement from the packet
    :return tuple
    :param[0] - [bool] True - if the last protocol was allow
    :param[0] - [int] - quantity the last protocols were reject
    :param[0] - [date or None] - creation date of the last rejected protocol
    """
    protocol_sqc = ProtocolSQC.objects.filter(
        id__in=sailor_key.protocol_dkk,
        statement_dkk__list_positions=list_positions,
    ).order_by('-date_meeting')
    if not protocol_sqc or protocol_sqc.first().decision.id == magic_numbers.decision_allow:
        return True, 0, None
    date_meeting = protocol_sqc.first().date_meeting
    quantity_reject_protocol = 0
    for protocol in protocol_sqc:
        if protocol.decision.id == magic_numbers.decision_reject:
            quantity_reject_protocol += 1
        else:
            break
    return False, quantity_reject_protocol, date_meeting


def get_last_date_date_meeting_sqc(last_date: date, sailor_key: SailorKeys, list_positions: List[int]):
    """
    Returns the date meeting of the exam for SQC
    """
    last_protocol_allow, quantity_reject, date_meeting = check_repeat_statement_sqc(sailor_key, list_positions)
    if last_protocol_allow:
        return last_date
    if quantity_reject == 1:
        min_date_meeting = date_meeting + relativedelta(weeks=2)
    else:
        min_date_meeting = date_meeting + relativedelta(months=3)
    if min_date_meeting > last_date:
        return min_date_meeting
    return last_date


def add_statement_sqc_to_packet(sailor_key: SailorKeys,
                                packet_item: PacketItem,
                                is_continue: int,
                                education_with_sqc: bool = False):
    positions = list(packet_item.position.all().values_list('pk', flat=True))
    protocols = ProtocolSQC.objects.filter(id__in=sailor_key.protocol_dkk, status_document_id__in=[19, 29],
                                           statement_dkk__list_positions=positions, statementqualification__isnull=True,
                                           decision_id=1)
    if education_with_sqc:
        rule_id = 17
    elif is_continue in [0, 2] and ExperinceForDKK.objects.filter(position_id__in=positions).exists():
        rule_id = 2  # With experience
    else:
        rule_id = 1  # Without experience
    if protocols.exists():
        return DependencyItem(packet_item=packet_item, type_document_id=rule_id, item_status=DependencyItem.WAS_BE,
                              item=protocols.first())
    else:
        return DependencyItem(packet_item=packet_item, type_document_id=rule_id, item_status=DependencyItem.TO_BUY,
                              is_etransport_pay=random.choice((True, False)))
