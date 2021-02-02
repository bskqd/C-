from copy import deepcopy
from datetime import date, datetime, timedelta
from typing import Optional

import workdays
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Sum, Q, QuerySet

import back_office.utils
import sailor.misc
from back_office.models import PacketItem, DependencyItem, ETIMonthRatio
from communication.models import SailorKeys
from directory.models import Course, NTZ, NZ, LevelQualification
from itcs import celery_app, magic_numbers
from itcs.magic_numbers import AccrualTypes
from notifications.models import UserNotification
from sailor.document.models import (Education, ProtocolSQC, CertificateETI, MedicalCertificate, QualificationDocument,
                                    ProofOfWorkDiploma)
from sailor.models import (SailorPassport)
from sailor.statement.models import (StatementAdvancedTraining, StatementMedicalCertificate, StatementSQC,
                                     StatementETI, StatementSailorPassport, StatementQualification)
from sailor.tasks import save_history
from user_profile.models import UserProfile


def search_sailor_by_field(document_id, search_field):
    filtering = {f'{search_field}__overlap': [document_id]}
    return SailorKeys.objects.filter(**filtering).first()


@celery_app.task
def update_eti_in_packet(certificate_id, sailor_id=None, search_sailor=False):
    if not sailor_id or search_sailor is True:
        sailor = search_sailor_by_field(certificate_id, 'sertificate_ntz')
    else:
        sailor = SailorKeys.objects.get(id=sailor_id)
    certificate = CertificateETI.objects.get(id=certificate_id)
    if not sailor or not sailor.packet_item:
        return False
    packets = PacketItem.objects.filter(id__in=sailor.packet_item, is_payed=True)
    for packet in packets:
        edi_dependencies = packet.dependencies.filter(
            content_type__model__in=['dependencydocuments', 'statementeti'], type_document_id=AccrualTypes.CERTIFICATE)
        for dependency_item in edi_dependencies:
            if (
                    (dependency_item.content_type and dependency_item.content_type.model == 'dependencydocuments' and
                     certificate.course_training_id in dependency_item.item.key_document)
                    or
                    (certificate.course_training_id == dependency_item.item.course_id) and
                    certificate.ntz_id == dependency_item.item.institution_id) and \
                    certificate.date_start >= date.today():
                dependency_item.item = certificate
                dependency_item.item_status = DependencyItem.WAS_BOUGHT
                dependency_item.save(force_update=True)
    return True


@celery_app.task
def update_medical_in_packet(medical_id, sailor_id=None, search_sailor=False):
    if search_sailor is True:
        sailor = search_sailor_by_field(medical_id, 'medical_sertificate')
    else:
        sailor = SailorKeys.objects.get(id=sailor_id)
    medical = MedicalCertificate.objects.get(id=medical_id)
    if not sailor.packet_item:
        return False
    packets = PacketItem.objects.filter(id__in=sailor.packet_item, is_payed=True)
    for packet in packets:
        eti_dependencies = packet.dependencies.filter(
            content_type__model__in=['dependencydocuments', 'statementmedicalcertificate'], type_document_id=7)
        for dependency_item in eti_dependencies:
            try:
                medical_dependency_id = [x['position'] for x in dependency_item.item.key_document]
            except AttributeError:
                medical_dependency_id = [dependency_item.item.position.pk]
            if medical.position_id in medical_dependency_id:
                dependency_item: DependencyItem
                dependency_item.item = medical
                dependency_item.item_status = DependencyItem.WAS_BOUGHT
                dependency_item.save(force_update=True)
    return True


@celery_app.task
def update_protocol_in_packet(protocol_id, sailor_id):
    sailor = SailorKeys.objects.get(id=sailor_id)
    protocol = ProtocolSQC.objects.get(id=protocol_id)
    if not sailor.packet_item:
        return False
    packets = PacketItem.objects.filter(id__in=sailor.packet_item, is_payed=True)
    for packet in packets:
        list_positions_of_packet = list(packet.position.values_list('pk', flat=True))
        eti_dependencies = packet.dependencies.filter(
            (Q(content_type__model__in=['statementsqc']) | Q(content_type=None)) &
            Q(type_document_id__in=AccrualTypes.LIST_SQC)
        )
        for dependency_item in eti_dependencies:
            if sorted(protocol.statement_dkk.list_positions) == sorted(list_positions_of_packet):
                dependency_item: DependencyItem
                dependency_item.item = protocol
                dependency_item.item_status = DependencyItem.WAS_BOUGHT
                dependency_item.save(force_update=True)
                create_statement_qual_doc.delay(packet.id, sailor_id, protocol.pk, protocol.statement_dkk.is_continue)


@celery_app.task
def create_statement_qual_doc(packet_id, sailor_id, protocol_sqc_id, is_continue):
    import sailor.statement.serializers
    port_converter = {41: 70, 3: 69, 47: 21, 2: 0, 22: 67, 48: 38, 1: 0, 4: 66, 5: 64, 21: 1}
    sailor_key = SailorKeys.objects.get(id=sailor_id)
    packet = PacketItem.objects.get(id=packet_id)
    positions = packet.position.all()
    rank = positions.first().rank
    list_positions = list(positions.values_list('pk', flat=True))
    dependency_items = DependencyItem.objects.filter(packet_item=packet, item_status=DependencyItem.TO_BUY)
    dependency_qual_doc = dependency_items.filter(
        type_document_id__in=(AccrualTypes.LIST_QUALIFICATION + AccrualTypes.LIST_PROOF)
    )
    type_document_id = rank.type_document_id
    count_quals = dependency_qual_doc.count()
    if type_document_id == 49 and is_continue and count_quals == 1:
        type_document_id = 16
    if dependency_qual_doc.exists():
        dependency_qualification: DependencyItem = dependency_qual_doc.first()
        statement_qual_doc = StatementQualification.objects.create(
            status_document_id=magic_numbers.status_state_qual_dkk_in_process,
            port_id=port_converter.get(packet.service_center_id, 0),
            is_payed=True,
            rank=rank,
            list_positions=list_positions,
            type_document_id=type_document_id,
            number=StatementQualification.generate_number(),
            sailor=sailor_id,
            is_continue=is_continue,
            date_meeting=packet.date_end_meeting,
            protocol_dkk_id=protocol_sqc_id,
        )
        sailor_key.statement_qualification.append(statement_qual_doc.pk)
        sailor_key.save(update_fields=['statement_qualification'])
        dependency_qualification.item = statement_qual_doc
        dependency_qualification.save(force_update=True)
        save_history.s(user_id=magic_numbers.celery_user_id,
                       module='StatementQualification',
                       action_type='create',
                       content_obj=statement_qual_doc,
                       serializer=sailor.statement.serializers.StatementQualificationDocumentSerializer,
                       new_obj=statement_qual_doc,
                       sailor_key_id=sailor_key.pk,
                       ).apply_async(serializer='pickle')
    return True


@celery_app.task
def update_qualification_in_packet(qualification_id, sailor_id=None, search_sailor=False):
    qualification = QualificationDocument.objects.get(id=qualification_id)
    if search_sailor is True:
        sailor = search_sailor_by_field(qualification.pk, 'qualification_documents')
    else:
        sailor = SailorKeys.objects.get(id=sailor_id)
    if not sailor.packet_item:
        return False
    packets = PacketItem.objects.filter(id__in=sailor.packet_item, is_payed=True)
    for packet in packets:
        list_positions_of_packet = list(packet.position.values_list('pk', flat=True))
        eti_dependencies = packet.dependencies.filter(
            (Q(content_type__model__in=['statementqualification']) |
             Q(content_type=None)) & Q(type_document_id__in=AccrualTypes.LIST_QUALIFICATION))
        for dependency_item in eti_dependencies:
            if sorted(qualification.list_positions) == sorted(list_positions_of_packet):
                dependency_item.item = qualification
                dependency_item.item_status = DependencyItem.WAS_BOUGHT
                dependency_item.save(force_update=True)
                return True


@celery_app.task
def update_proof_in_packet(proof_id, sailor_id=None, search_sailor=False):
    proof = ProofOfWorkDiploma.objects.get(id=proof_id)
    if search_sailor is True:
        sailor = search_sailor_by_field(proof.diploma.pk, 'qualification_documents')
    else:
        sailor = SailorKeys.objects.get(id=sailor_id)
    if not sailor.packet_item:
        return False
    packets = PacketItem.objects.filter(id__in=sailor.packet_item, is_payed=True)
    for packet in packets:
        list_positions_of_packet = list(packet.position.values_list('pk', flat=True))
        eti_dependencies = packet.dependencies.filter(
            Q(content_type__model__in=['statementqualification']) |
            Q(content_type=None) & Q(type_document_id__in=AccrualTypes.LIST_PROOF))
        for dependency_item in eti_dependencies:
            if sorted(proof.diploma.list_positions) == sorted(list_positions_of_packet):
                dependency_item.item = proof
                dependency_item.item_status = DependencyItem.WAS_BOUGHT
                dependency_item.save(force_update=True)
                return True
    return False


@celery_app.task
def update_education_in_packet(education_id, sailor_id=None, search_sailor=False):
    education = Education.objects.get(id=education_id)
    if search_sailor is True:
        sailor = search_sailor_by_field(education_id, 'education')
    else:
        sailor = SailorKeys.objects.get(id=sailor_id)
    if not sailor.packet_item or education.type_document_id not in AccrualTypes.LIST_QUALIFICATION:
        return False
    packets = PacketItem.objects.filter(id__in=sailor.packet_item, is_payed=True)
    for packet in packets:
        eti_dependencies = packet.dependencies.filter(
            content_type__model__in=['dependencydocuments', 'statementadvancedtraining'],
            type_document_id=AccrualTypes.ADVANCED_TRAINING)
        for dependency_item in eti_dependencies:
            try:
                level_qual_id = [x['qualitification'] for x in dependency_item.item.key_document]
            except AttributeError:
                level_qual_id = [dependency_item.item.level_qualification.pk]
            if education.qualification_id in level_qual_id:
                dependency_item.item = education
                dependency_item.item_status = DependencyItem.WAS_BOUGHT
                dependency_item.save(force_update=True)
                return True
    return True


@celery_app.task
def update_sailor_passport_in_packet(sailor_passport_id, sailor_id=None, search_sailor=False):
    passport = SailorPassport.objects.get(id=sailor_passport_id)
    if search_sailor is True:
        sailor = search_sailor_by_field(sailor_passport_id, 'sailor_passport')
    else:
        sailor = SailorKeys.objects.get(id=sailor_id)
    if not sailor.packet_item:
        return False
    packets = PacketItem.objects.filter(id__in=sailor.packet_item, is_payed=True)
    for packet in packets:
        eti_dependencies = packet.dependencies.filter(
            (Q(content_type__model__in=['statementsailorpassport']) | Q(content_type=None))
            & Q(type_document_id__in=(AccrualTypes.LIST_SAILOR_PASSPORT + AccrualTypes.LIST_BLANK_SAILOR_PASSPORT)))
        for dependency_item in eti_dependencies:
            dependency_item.item = passport
            dependency_item.item_status = DependencyItem.WAS_BOUGHT
            dependency_item.save(force_update=True)
            return True
    return True


@celery_app.task
def update_service_center_and_agent_in_packet(packet_id):
    packet = PacketItem.objects.get(id=packet_id)
    try:
        agent_dependency = packet.dependencies.get(type_document_id__in=AccrualTypes.LIST_AGENT)
    except DependencyItem.DoesNotExist:
        return
    agent_dependency.item = packet.agent
    agent_dependency.item_status = DependencyItem.WAS_BOUGHT
    # service_center_dependency = packet.dependencies.get(type_document_id=10)
    # service_center_dependency.item_status = DependencyItem.WAS_BOUGHT
    # service_center_dependency.save(update_fields=['item_status'])
    agent_dependency.save(force_update=True)
    try:
        morrich_dependency = packet.dependencies.get(type_document_id=AccrualTypes.MORRICHSERVICE)
        morrich_dependency.item_status = DependencyItem.WAS_BOUGHT
        morrich_dependency.save(update_fields=['item_status'])
        return True
    except DependencyItem.DoesNotExist:
        pass
    return True


@celery_app.task
def update_ntz_month_amount(course_id=None):
    td = date.today() - relativedelta(months=1)
    if course_id:
        courses = Course.objects.filter(id=course_id)
    else:
        courses = Course.objects.filter(is_disable=False)
    for course in courses:
        payments = DependencyItem.objects.filter(
            type_document_id=AccrualTypes.CERTIFICATE,
            content_type__model='certificateeti',
            updated_at__year=td.year,
            updated_at__month=td.month,
            cert_item__course=course
        ).values('cert_item__ntz_id').annotate(sum=Sum('payment_form2'))
        if not payments.exists():
            return False
        with transaction.atomic():
            for payment in payments:
                ETIMonthRatio.objects.filter(ntz_id=payment['cert_item__ntz_id']).update(month_amount=payment['sum'])
        ETIMonthRatio.reorder()
    return True


@celery_app.task
def create_statements(packet_id, user_id=None):
    import sailor.statement.serializers
    port_converter = {41: 70, 3: 69, 47: 21, 2: 0, 22: 67, 48: 38, 1: 0, 4: 66, 5: 64, 21: 1}
    packet = PacketItem.objects.get(id=packet_id)
    dependency_items = DependencyItem.objects.filter(packet_item=packet, item_status=DependencyItem.TO_BUY)
    dependency_certificates = dependency_items.filter(type_document_id=AccrualTypes.CERTIFICATE)
    dependency_sailor_passport = dependency_items.filter(type_document_id__in=AccrualTypes.LIST_SAILOR_PASSPORT)
    dependency_blank_sailor_passport = dependency_items.filter(
        type_document_id=AccrualTypes.BLANK_SERVICE_RECORD
    ).first()
    dependency_medical = dependency_items.filter(type_document_id=7)
    #  medical statements
    dependency_protocol = dependency_items.filter(type_document_id__in=AccrualTypes.LIST_SQC)
    dependency_qual_doc = dependency_items.filter(
        type_document_id__in=AccrualTypes.LIST_QUALIFICATION + AccrualTypes.LIST_PROOF
    ).order_by('type_document_id')
    dependency_advanced_training = dependency_items.filter(type_document_id=AccrualTypes.ADVANCED_TRAINING)
    positions = packet.position.all()
    sailor_key = SailorKeys.by_document.id(instance=packet)
    last_date = back_office.utils.get_available_day_for_start_packet(sailor_key.pk, packet.pk)
    certificates_qs = CertificateETI.objects.filter(id__in=sailor_key.sertificate_ntz)
    if dependency_sailor_passport.exists():
        is_continue_converter = {AccrualTypes.SAILOR_PASSPORT_GETTING_20: (False, 1),
                                 AccrualTypes.SAILOR_PASSPORT_CONTINUE_20: (True, 3),
                                 AccrualTypes.SAILOR_PASSPORT_CONTINUE_7: (True, 4),
                                 AccrualTypes.SAILOR_PASSPORT_GETTING_7: (False, 2)}
        dependency_passport_instance: DependencyItem = dependency_sailor_passport.first()
        is_continue = is_continue_converter[dependency_passport_instance.type_document_id][0]

        sailor_passport = SailorPassport.objects.filter(
            id__in=sailor_key.sailor_passport
        ).order_by('-date_end').first()
        statement_sailor_passport = StatementSailorPassport.objects.create(
            status_document_id=magic_numbers.status_statement_sailor_passport_in_process,
            port_id=port_converter.get(packet.service_center_id, 0),
            is_payed=False,
            is_continue=is_continue,
            date_meeting=last_date,
            sailor_passport=sailor_passport if is_continue else None,
            type_receipt=is_continue_converter[dependency_passport_instance.type_document_id][1],
        )
        sailor_key.statement_sailor_passport.append(statement_sailor_passport.pk)
        dependency_passport_instance.item = statement_sailor_passport
        dependency_passport_instance.save(force_update=True)
        if dependency_blank_sailor_passport:
            dependency_blank_sailor_passport.item = statement_sailor_passport
            dependency_blank_sailor_passport.save(force_update=True)
        last_date = workdays.workday(last_date, back_office.utils.hours_to_date(8))
        if user_id:
            save_history.s(user_id=user_id,
                           module='StatementSailorPassport',
                           action_type='create',
                           content_obj=statement_sailor_passport,
                           serializer=sailor.statement.serializers.StatementSailorPassportSerializer,
                           new_obj=statement_sailor_passport,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
    for dependency in dependency_certificates:
        courses_list = dependency.item.key_document
        exists_certificates = certificates_qs.filter(
            course_training_id__in=courses_list
        ).exclude(status_document_id=magic_numbers.STATUS_REMOVED_DOCUMENT).order_by('course_training__continue_merge')
        course_id = None
        is_continue = False
        if (exists_certificates.exists() and
                exists_certificates.first().course_training.continue_merge):
            certificate: CertificateETI = exists_certificates.first()
            course = Course.objects.filter(continue_merge=certificate.course_training.continue_merge,
                                           is_continue=True).first()
            course_id = course.pk if course else None
            is_continue = True
        if not course_id:
            pre_course = Course.objects.filter(id__in=courses_list, is_disable=False).order_by('is_continue')
            course_id = pre_course.first().pk
            is_continue = False
        eti = NTZ.objects.filter(is_red=True, ntz_ratio__course_id=course_id,
                                 address__icontains=packet.service_center.name_ukr,
                                 ).order_by('ntz_ratio__order')

        red_eti = NTZ.objects.filter(is_red=True, ntz_ratio__course_id=course_id)
        eti = eti.filter(address__icontains=packet.service_center.name_ukr)
        if eti:
            eti_instance = eti.order_by('ntz_ratio__order').first()
        elif red_eti:
            eti_instance = red_eti.order_by('ntz_ratio__order').first()
        else:
            continue
        date_end_meeting = back_office.utils.get_date_end_meeting_for_certificate_eti(last_date, course_id, is_continue)
        statement = StatementETI.objects.create(
            institution=eti_instance, course_id=course_id, is_payed=False,
            status_document_id=magic_numbers.status_statement_eti_in_process, date_meeting=last_date,
            date_end_meeting=date_end_meeting, is_continue=is_continue
        )
        sailor_key.statement_eti.append(statement.pk)
        dependency.item = statement
        dependency.save(force_update=True)
        last_date = date_end_meeting
        # certificates.tasks.send_statement_to_eti.s(statement_id=statement.pk).apply_async(countdown=10)
        if user_id:
            save_history.s(user_id=user_id,
                           module='StatementETI',
                           action_type='create',
                           content_obj=statement,
                           serializer=sailor.statement.serializers.StatementETISerializer,
                           new_obj=statement,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
    # if dependency_medical.exists():
    #     medical_institution = MedicalInstitution.objects.filter(address__icontains=packet.service_center.name_ukr). \
    #         order_by('?').first()
    #     dependency_medical_instance: DependencyItem = dependency_medical.first()
    #     statement_medical_certificate = StatementMedicalCertificate.objects.create(
    #         position_id=dependency_medical_instance.item.key_document[0].get('position'),
    #         status_document_id=magic_numbers.status_statement_medical_cert_in_process,
    #         medical_institution=medical_institution,
    #         is_payed=False,
    #         date_meeting=last_date
    #     )
    #     sailor_key.statement_medical_certificate.append(statement_medical_certificate.pk)
    #     dependency_medical_instance.item = statement_medical_certificate
    #     dependency_medical_instance.save(force_update=True)
    #     last_date = workdays.workday(last_date, back_office.utils.hours_to_date(8))
    #     if user_id:
    #         save_history.s(user_id=user_id,
    #                        module='StatementMedicalCertificate',
    #                        action_type='create',
    #                        content_obj=statement_medical_certificate,
    #                        serializer=sailor.statement.serializers.StatementMedicalCertificateSerializer,
    #                        new_obj=statement_medical_certificate,
    #                        sailor_key_id=sailor_key.pk,
    #                        ).apply_async(serializer='pickle')
    if dependency_protocol.exists():
        list_positions = list(positions.values_list('pk', flat=True))
        last_date = back_office.utils.get_last_date_date_meeting_sqc(last_date, sailor_key, list_positions)
        statement_dkk = StatementSQC.objects.create(
            is_payed=False, sailor=sailor_key.pk, rank=positions.first().rank,
            list_positions=list_positions,
            status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT,
            branch_office=packet.service_center, is_continue=packet.position_type,
            is_cadet=packet.education_with_sqc,
            date_meeting=last_date,
            is_etransport_pay=dependency_protocol.first().is_etransport_pay,
        )
        sailor_key.statement_dkk.append(statement_dkk.pk)
        dependency_protocol_instance: DependencyItem = dependency_protocol.first()
        dependency_protocol_instance.item = statement_dkk
        dependency_protocol_instance.save(force_update=True)
        last_date = workdays.workday(last_date, back_office.utils.hours_to_date(8))
        if user_id:
            save_history.s(user_id=user_id,
                           module='StatementSQC',
                           action_type='create',
                           content_obj=statement_dkk,
                           serializer=sailor.statement.serializers.StatementDKKSerializer,
                           new_obj=statement_dkk,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
    elif dependency_qual_doc.exists():
        rank = positions.first().rank
        list_positions = list(positions.values_list('pk', flat=True))
        is_continue = sailor.misc.check_is_continue(sailor_qs=sailor_key,
                                                    rank_id=rank.pk,
                                                    list_positions=list_positions)
        if rank.type_document_id == 49 and dependency_qual_doc.count() == 1:
            type_document = 16
        else:
            type_document = rank.type_document_id

        dependency_exists_protocol = DependencyItem.objects.filter(packet_item=packet,
                                                                   item_status=DependencyItem.WAS_BE,
                                                                   content_type__model='protocolsqc').first()
        protocol = dependency_exists_protocol.item if dependency_exists_protocol else None
        statement_qual_doc = StatementQualification.objects.create(
            status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT,
            port_id=port_converter.get(packet.service_center_id, 0),
            is_payed=False,
            rank=rank,
            list_positions=list_positions,
            type_document_id=type_document,
            number=StatementQualification.generate_number(),
            sailor=sailor_key.pk,
            is_continue=is_continue,
            date_meeting=last_date,
            protocol_dkk=protocol
        )
        last_date = workdays.workday(last_date, back_office.utils.hours_to_date(8))
        sailor_key.statement_qualification.append(statement_qual_doc.pk)
        sailor_key.save(update_fields=['statement_qualification'])
        dependency_qual_doc: DependencyItem = dependency_qual_doc.first()
        dependency_qual_doc.item = statement_qual_doc
        dependency_qual_doc.save(force_update=True)
        if user_id:
            save_history.s(user_id=magic_numbers.celery_user_id,
                           module='StatementQualification',
                           action_type='create',
                           content_obj=statement_qual_doc,
                           serializer=sailor.statement.serializers.StatementQualificationDocumentSerializer,
                           new_obj=statement_qual_doc,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
    if dependency_advanced_training.exists():
        institution = NZ.objects.filter(type_nz_id=3, postal_address__icontains=packet.service_center.name_ukr)
        dependency_advanced_instance: DependencyItem = dependency_advanced_training.first()
        qualification = LevelQualification.objects.get(
            id=dependency_advanced_instance.item.key_document[0].get('qualitification')
        )
        date_end_meeting = workdays.workday(last_date, back_office.utils.hours_to_date(qualification.course_time_hours))
        statement_advanced = StatementAdvancedTraining.objects.create(
            level_qualification=qualification,
            status_document_id=magic_numbers.status_statement_adv_training_in_process,
            educational_institution=institution.first(),
            is_payed=False,
            date_meeting=last_date,
            date_end_meeting=date_end_meeting
        )
        sailor_key.statement_advanced_training.append(statement_advanced.pk)
        dependency_advanced_instance.item = statement_advanced
        dependency_advanced_instance.save(force_update=True)
        last_date = workdays.workday(last_date, back_office.utils.hours_to_date(qualification.course_time_hours))
        if user_id:
            save_history.s(user_id=user_id,
                           module='StatementAdvancedTraining',
                           action_type='create',
                           content_obj=statement_advanced,
                           serializer=sailor.statement.serializers.StatementAdvancedTrainingSerializer,
                           new_obj=statement_advanced,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
    if dependency_protocol.exists():
        last_date = workdays.workday(last_date, back_office.utils.hours_to_date(8))
    packet.date_end_meeting = last_date
    packet.save(update_fields=['date_end_meeting'])
    sailor_key.save(force_update=True)


@celery_app.task
def added_statement_eti_in_dependency(statement_id=None, date_end_meeting=None, sailor_key=None, course_id=None):
    """
    добавление в зависимиости созданого из АС отдельного заявленияния на НТЗ
    """
    sailor_qs = SailorKeys.objects.get(id=sailor_key)
    statement = StatementETI.objects.get(id=statement_id)
    packets = PacketItem.objects.filter(id__in=sailor_qs.packet_item, is_payed=True)
    for packet in packets:
        edi_dependencies = packet.dependencies.filter(content_type__model='dependencydocuments',
                                                      type_document_id=AccrualTypes.CERTIFICATE)
        for dependency_item in edi_dependencies:
            if course_id in dependency_item.item.key_document:
                dependency_item.item = statement
                dependency_item.save()
                if packet.date_end_meeting >= date_end_meeting:
                    return True
                packet.date_end_meeting = date_end_meeting
                packet.save(update_fields=['date_end_meeting'])
                return True


@celery_app.task
def added_statement_adv_training_in_dependency(statement_id=None, date_end_meeting=None, sailor_key=None,
                                               qualification_id=None):
    """
    добавление в зависимиости созданого из АС отдельного заявленияния на свидетельсвто на повышение квалификации
    """
    sailor_qs = SailorKeys.objects.get(id=sailor_key)
    statement = StatementAdvancedTraining.objects.get(id=statement_id)
    packets = PacketItem.objects.filter(id__in=sailor_qs.packet_item, is_payed=True)
    for packet in packets:
        edi_dependencies = packet.dependencies.filter(content_type__model='dependencydocuments',
                                                      type_document_id=AccrualTypes.ADVANCED_TRAINING)
        for dependency_item in edi_dependencies:
            if qualification_id == dependency_item.item.key_document[0]['qualitification']:
                dependency_item.item = statement
                dependency_item.save()
                if packet.date_end_meeting >= date_end_meeting:
                    return True
                packet.date_end_meeting = date_end_meeting
                packet.save(update_fields=['date_end_meeting'])
                return True


@celery_app.task
def added_statement_med_certificate_in_dependency(statement_id=None, date_meeting=None, sailor_key=None, position=None):
    """
    добавление в зависимиости созданого из АС отдельного заявленияния на медицинское свидетельство
    """
    sailor_qs = SailorKeys.objects.get(id=sailor_key)
    statement = StatementMedicalCertificate.objects.get(id=statement_id)
    packets = PacketItem.objects.filter(id__in=sailor_qs.packet_item, is_payed=True)
    for packet in packets:
        edi_dependencies = packet.dependencies.filter(content_type__model='dependencydocuments',
                                                      type_document_id=AccrualTypes.MEDICAL)
        for dependency_item in edi_dependencies:
            all_position = [dep['position'] for dep in dependency_item.item.key_document]
            if position in all_position:
                dependency_item.item = statement
                dependency_item.save()
                if packet.date_end_meeting >= date_meeting:
                    return True
                packet.date_end_meeting = date_meeting
                packet.save(update_fields=['date_end_meeting'])
                return True


@celery_app.task
def added_statement_sailor_passport_in_dependency(statement_id=None, date_meeting=None, sailor_key=None,
                                                  is_continue=None):
    """
    добавление в зависимиости созданого из АС отдельного заявленияния на ПОМ (посвідчення особи моряка)
    """
    sailor_qs = SailorKeys.objects.get(id=sailor_key)
    statement = StatementSailorPassport.objects.get(id=statement_id)
    packets = PacketItem.objects.filter(id__in=sailor_qs.packet_item, is_payed=True)
    type_continue = {True: [AccrualTypes.SAILOR_PASSPORT_CONTINUE_7, AccrualTypes.SAILOR_PASSPORT_CONTINUE_20],
                     False: [AccrualTypes.SAILOR_PASSPORT_GETTING_7, AccrualTypes.SAILOR_PASSPORT_GETTING_20]}
    for packet in packets:
        edi_dependencies = packet.dependencies.filter(content_type__model='dependencydocuments',
                                                      type_document_id__in=type_continue[is_continue])
        for dependency_item in edi_dependencies:
            dependency_item.item = statement
            dependency_item.save()
            if packet.date_end_meeting >= date_meeting:
                return True
            packet.date_end_meeting = date_meeting
            packet.save(update_fields=['date_end_meeting'])
            return True


@celery_app.task
def create_notification_about_new_packet(packet_id):
    packet = PacketItem.objects.select_related('agent').get(id=packet_id)
    author = packet.agent
    group = author.userprofile.agent_group.first()
    managers_in_group = group.userprofile_set.filter(
        type_user__in=[UserProfile.HEAD_AGENT, UserProfile.SECRETARY_SERVICE]
    )
    text_message = f'Довірена особа {author.get_full_name()} створив нову заяву з номером {packet.full_number}. ' \
                   f'Будь ласка перейдіть та підівиться заяву'
    bulk_notification = [UserNotification(recipient=secretary.user,
                                          title='Довірена особа створила нову заяву',
                                          text=text_message,
                                          obj=packet, sailor_id=packet.sailor_id)
                         for secretary in managers_in_group]
    UserNotification.objects.bulk_create(bulk_notification)
    return True


@celery_app.task
def check_payed_packet_item():
    """
    Finds packets not paid for within an hour and deletes them
    """
    time_to_pay = datetime.now() - timedelta(hours=1)
    packets = PacketItem.objects.filter(created_at__lte=time_to_pay, is_payed=False)
    for packet in packets:
        delete_statement_and_packet.s(packet.pk).apply_async()
    return True


@celery_app.task
def delete_statement_and_packet(packet_id: int, only_statement: bool = False):
    """
    Removes the statements created in the packet or changes status_document to 'Canceled' if the statement was paid
    and remove the packet itself
    :param packet_id: PacketItem identifier
    """
    import sailor.statement.serializers
    import back_office.serializers
    packet = PacketItem.objects.get(id=packet_id)
    _packet = deepcopy(packet)
    try:
        sailor_key = SailorKeys.objects.get(packet_item__overlap=[packet.pk])
    except SailorKeys.DoesNotExist:
        return False
    statement_medical_cert = packet.dependencies.filter(content_type__model='statementmedicalcertificate')
    if statement_medical_cert.exists():
        statement_medical_cert = statement_medical_cert.first()
        try:
            statement_inst = StatementMedicalCertificate.objects.get(id=statement_medical_cert.object_id)
        except StatementMedicalCertificate.DoesNotExist:
            statement_inst = None
        if not statement_inst:
            statement_medical_cert.delete()
        elif not statement_inst.is_payed:
            _statement = deepcopy(statement_inst)
            sailor_key.statement_medical_certificate.remove(statement_inst.id)
            sailor_key.save(update_fields=['statement_medical_certificate'])
            statement_inst.delete()
            save_history.s(user_id=magic_numbers.celery_user_id,
                           module='StatementMedicalCertificate',
                           action_type='delete',
                           content_obj=_statement,
                           serializer=sailor.statement.serializers.StatementMedicalCertificateSerializer,
                           old_obj=_statement,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
        else:
            change_status_document_statement.s(statement_inst, sailor_key.pk).apply_async(serializer='pickle')
    statement_adv_training = packet.dependencies.filter(content_type__model='statementadvancedtraining')
    if statement_adv_training.exists():
        statement_adv_training = statement_adv_training.first()
        try:
            statement_inst = StatementAdvancedTraining.objects.get(id=statement_adv_training.object_id)
        except StatementAdvancedTraining.DoesNotExist:
            statement_inst = None
        if not statement_inst:
            statement_adv_training.delete()
        elif not statement_inst.is_payed:
            _statement = deepcopy(statement_inst)
            sailor_key.statement_advanced_training.remove(statement_inst.id)
            sailor_key.save(update_fields=['statement_advanced_training'])
            statement_inst.delete()
            save_history.s(user_id=magic_numbers.celery_user_id,
                           module='StatementAdvancedTraining',
                           action_type='delete',
                           content_obj=_statement,
                           serializer=sailor.statement.serializers.StatementAdvancedTrainingSerializer,
                           old_obj=_statement,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
        else:
            change_status_document_statement.s(statement_inst, sailor_key.pk).apply_async(serializer='pickle')
    statement_sailor_passport = packet.dependencies.filter(content_type__model='statementsailorpassport')
    if statement_sailor_passport.exists():
        statement_sailor_passport = statement_sailor_passport.first()
        try:
            statement_inst = StatementSailorPassport.objects.get(id=statement_sailor_passport.object_id)
        except StatementSailorPassport.DoesNotExist:
            statement_inst = None
        if not statement_inst:
            statement_sailor_passport.delete()
        elif not statement_inst.is_payed:
            _statement = deepcopy(statement_inst)
            sailor_key.statement_sailor_passport.remove(statement_inst.id)
            sailor_key.save(update_fields=['statement_sailor_passport'])
            statement_inst.delete()
            save_history.s(user_id=magic_numbers.celery_user_id,
                           module='StatementSailorPassport',
                           action_type='delete',
                           content_obj=_statement,
                           serializer=sailor.statement.serializers.StatementSailorPassportSerializer,
                           old_obj=_statement,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
        else:
            change_status_document_statement.s(statement_inst, sailor_key.pk).apply_async(serializer='pickle')
    statement_sqc = packet.dependencies.filter(content_type__model='statementsqc')
    if statement_sqc.exists():
        statement_sqc = statement_sqc.first()
        try:
            statement_inst = StatementSQC.objects.get(id=statement_sqc.object_id)
        except StatementSQC.DoesNotExist:
            statement_inst = None
        if not statement_inst:
            statement_sqc.delete()
        elif not statement_inst.is_payed:
            _statement = deepcopy(statement_inst)
            try:
                sailor_key.statement_dkk.remove(statement_inst.id)
                sailor_key.save(update_fields=['statement_dkk'])
            except ValueError:
                pass
            statement_inst.delete()
            save_history.s(user_id=magic_numbers.celery_user_id,
                           module='StatementSQC',
                           action_type='delete',
                           content_obj=_statement,
                           serializer=sailor.statement.serializers.StatementDKKSerializer,
                           old_obj=_statement,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
        else:
            change_status_document_statement.s(statement_inst, sailor_key.pk).apply_async(serializer='pickle')
    statement_qual_doc = packet.dependencies.filter(content_type__model='statementqualification')
    if statement_qual_doc.exists():
        statement_qual_doc = statement_qual_doc.first()
        try:
            statement = StatementQualification.objects.get(id=statement_qual_doc.object_id)
        except StatementQualification.DoesNotExist:
            statement = None
        if not statement:
            statement_qual_doc.delete()
        elif not statement.is_payed:
            _statement = deepcopy(statement)
            try:
                sailor_key.statement_qualification.remove(statement.id)
                sailor_key.save(update_fields=['statement_qualification'])
            except ValueError:
                pass
            statement.delete()
            save_history.s(user_id=magic_numbers.celery_user_id,
                           module='StatementQualification',
                           action_type='delete',
                           content_obj=_statement,
                           serializer=sailor.statement.serializers.StatementQualificationDocumentSerializer,
                           old_obj=_statement,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
        elif not DependencyItem.objects.filter(content_type__model='statementqualification', object_id=statement.pk,
                                               packet_item__is_payed=True):
            change_status_document_statement.s(statement, sailor_key.pk).apply_async(serializer='pickle')
    all_statement_eti = packet.dependencies.filter(content_type__model='statementeti')
    for statement_eti in all_statement_eti:
        try:
            statement = StatementETI.objects.get(id=statement_eti.object_id)
        except StatementETI.DoesNotExist:
            statement = None
        if not statement:
            statement_eti.delete()
        elif not statement.is_payed:
            _statement = deepcopy(statement)
            try:
                sailor_key.statement_eti.remove(statement.id)
                sailor_key.save(update_fields=['statement_eti'])
            except ValueError:
                pass
            statement.delete()
            save_history.s(user_id=magic_numbers.celery_user_id,
                           module='StatementETI',
                           action_type='delete',
                           content_obj=_statement,
                           serializer=sailor.statement.serializers.StatementETISerializer,
                           old_obj=_statement,
                           sailor_key_id=sailor_key.pk,
                           ).apply_async(serializer='pickle')
        else:
            change_status_document_statement.s(statement, sailor_key.pk).apply_async(serializer='pickle')
    if not packet.is_payed and not only_statement:
        sailor_key.packet_item.remove(packet.id)
        sailor_key.save(update_fields=['packet_item'])
        packet.delete()
        save_history.s(user_id=magic_numbers.celery_user_id,
                       module='PacketItem',
                       action_type='delete',
                       content_obj=_packet,
                       serializer=back_office.serializers.PacketSerializer,
                       old_obj=_packet,
                       sailor_key_id=sailor_key.pk,
                       ).apply_async(serializer='pickle')
    return True


@celery_app.task
def change_status_document_statement(statement, sailor_key: int):
    """
    Changes the status_document of a paid statement to 'Canceled' when the packet is removed
    :param statement: sailor's object statement
    :param sailor_key: SailorKeys identifier
    """
    import sailor.statement.serializers
    from certificates.tasks import send_statement_to_eti
    COLLECTION_SERIALIZER = {
        'StatementMedicalCertificate': sailor.statement.serializers.StatementMedicalCertificateSerializer,
        'StatementAdvancedTraining': sailor.statement.serializers.StatementAdvancedTrainingSerializer,
        'StatementSailorPassport': sailor.statement.serializers.StatementSailorPassportSerializer,
        'StatementSQC': sailor.statement.serializers.StatementDKKSerializer,
        'StatementETI': sailor.statement.serializers.StatementETISerializer,
        'StatementQualification': sailor.statement.serializers.StatementQualificationDocumentSerializer,
    }
    old_statement = deepcopy(statement)
    statement.status_document_id = magic_numbers.status_statement_canceled
    statement.save(update_fields=['status_document'])
    model_name = statement._meta.object_name
    if model_name == 'StatementQualificationDocument':
        model_name = 'StatementQualification'
    elif isinstance(statement, StatementETI):
        send_statement_to_eti.s(statement.pk, True).apply_async()
    save_history.s(user_id=magic_numbers.celery_user_id,
                   module=model_name,
                   action_type='edit',
                   content_obj=statement,
                   serializer=COLLECTION_SERIALIZER.get(model_name),
                   new_obj=statement,
                   old_obj=old_statement,
                   sailor_key_id=sailor_key,
                   ).apply_async(serializer='pickle')
    return True


@celery_app.task
def update_statements_after_payment(packet_id: int, user_id: Optional[int] = None):
    """
    After paying for the packet, it finds the statements created in the packet and transfers them to the state of paid
    :param packet_id: PacketItem identifier
    :param user_id: User identifier
    """
    packet: PacketItem = PacketItem.objects.get(id=packet_id)
    try:
        sailor_key: SailorKeys = SailorKeys.objects.get(packet_item__overlap=[packet.pk])
    except SailorKeys.DoesNotExist:
        return False
    # TODO Replace get every element for item
    statement_medical_cert: QuerySet[DependencyItem] = packet.dependencies.filter(
        content_type__model='statementmedicalcertificate')
    if statement_medical_cert.exists():
        statement_medical_cert: DependencyItem = statement_medical_cert.first()
        statement = StatementMedicalCertificate.objects.get(id=statement_medical_cert.object_id)
        update_payment_statement.s(statement, sailor_key.pk, user_id).apply_async(serializer='pickle')
    statement_adv_training: QuerySet[DependencyItem] = packet.dependencies.filter(
        content_type__model='statementadvancedtraining')
    if statement_adv_training.exists():
        statement_adv_training: DependencyItem = statement_adv_training.first()
        statement = StatementAdvancedTraining.objects.get(id=statement_adv_training.object_id)
        update_payment_statement.s(statement, sailor_key.pk, user_id).apply_async(serializer='pickle')
    statement_sailor_passport: QuerySet[DependencyItem] = packet.dependencies.filter(
        content_type__model='statementsailorpassport')
    if statement_sailor_passport.exists():
        statement_sailor_passport: DependencyItem = statement_sailor_passport.first()
        statement = StatementSailorPassport.objects.get(id=statement_sailor_passport.object_id)
        update_payment_statement.s(statement, sailor_key.pk, user_id).apply_async(serializer='pickle')
        if not statement.is_continue:
            statement.is_payed_blank = True
            statement.save(force_update=True)
    # statement_sqc: QuerySet[DependencyItem] = packet.dependencies.filter(content_type__model='statementsqc')
    statement_qual_doc: QuerySet[DependencyItem] = packet.dependencies.filter(
        content_type__model='statementqualification')
    # if statement_sqc.exists():
    #     statement_sqc: DependencyItem = statement_sqc.first()
    #     statement = StatementSQC.objects.get(id=statement_sqc.object_id)
    #     if not statement.is_etransport_pay:
    #         update_payment_statement.s(statement, sailor_key.pk, user_id).apply_async(serializer='pickle')
    if statement_qual_doc.exists():
        statement_qual_doc: DependencyItem = statement_qual_doc.first()
        statement = StatementQualification.objects.get(id=statement_qual_doc.object_id)
        update_payment_statement.s(statement, sailor_key.pk, user_id).apply_async(serializer='pickle')
    dependencies_statement_eti: QuerySet[DependencyItem] = packet.dependencies.filter(
        content_type__model='statementeti')
    statement_eti_ids = list(dependencies_statement_eti.values_list('object_id', flat=True))
    all_statement_eti = StatementETI.objects.filter(id__in=statement_eti_ids)
    for statement in all_statement_eti:
        if not statement.institution.can_pay_platon:
            update_payment_statement.s(statement, sailor_key.pk, user_id).apply_async(serializer='pickle')
    return True


@celery_app.task
def update_payment_statement(statement, sailor_key_id: int, user_id: Optional[int] = None):
    """
    Changes the state of the statement to - paid
    :param statement: sailor's object statement that has been paid
    :param sailor_key_id: SailorKeys identifier
    :param user_id: User identifier
    """
    import sailor.statement.serializers
    from certificates.tasks import add_month_sum
    COLLECTION_SERIALIZER = {
        'StatementMedicalCertificate': sailor.statement.serializers.StatementMedicalCertificateSerializer,
        'StatementAdvancedTraining': sailor.statement.serializers.StatementAdvancedTrainingSerializer,
        'StatementSailorPassport': sailor.statement.serializers.StatementSailorPassportSerializer,
        'StatementSQC': sailor.statement.serializers.StatementDKKSerializer,
        'StatementETI': sailor.statement.serializers.StatementETISerializer,
        'StatementQualification': sailor.statement.serializers.StatementQualificationDocumentSerializer,
    }
    old_statement = deepcopy(statement)
    statement.is_payed = True
    statement.save(update_fields=['is_payed'])
    model_name = statement._meta.object_name
    if model_name == 'StatementQualificationDocument':
        model_name = 'StatementQualification'
    if isinstance(statement, StatementETI):
        add_month_sum.s(statement.pk).apply_async()
    if user_id:
        save_history.s(user_id=user_id,
                       module=model_name,
                       action_type='edit',
                       content_obj=statement,
                       serializer=COLLECTION_SERIALIZER.get(model_name),
                       new_obj=statement,
                       old_obj=old_statement,
                       sailor_key_id=sailor_key_id,
                       ).apply_async(serializer='pickle')
    return True


@celery_app.task
def check_for_adding_diploma_to_proof(diploma_packet_id):
    diploma_packet = PacketItem.objects.get(id=diploma_packet_id)
    if (diploma_packet.dependencies.count() == 1 or
            diploma_packet.dependencies.filter(type_document_id__in=AccrualTypes.LIST_QUALIFICATION,
                                               packet_item__is_payed=True,
                                               item_status=DependencyItem.TO_BUY,
                                               content_type__model='statementqualification').exists()):
        dependency_item = diploma_packet.dependencies.first()
        if not isinstance(dependency_item.item, StatementQualification):
            return False
        dependency_item.item.type_document_id = 49
        dependency_item.item.save(update_fields=['type_document'])
        return True
    return False
