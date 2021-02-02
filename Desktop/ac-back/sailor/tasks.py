import json
from copy import deepcopy
from datetime import datetime, timedelta, date
from functools import reduce
from typing import List

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Max, Q, QuerySet
from django.utils import timezone

from communication.models import SailorKeys
from directory.models import Position, Port
from itcs import magic_numbers
from itcs.celery import celery_app
from sailor.document.models import ServiceRecord, LineInServiceRecord, Education, ProtocolSQC, \
    CertificateETI, MedicalCertificate, QualificationDocument, ProofOfWorkDiploma
from sailor.misc import get_sailor_by_modelname
from sailor.models import (DependencyDocuments, SailorPassport, Profile, ContactInfo, DemandPositionDKK)
from sailor.statement.models import StatementSQC, StatementQualification
from sms_auth.misc import send_message
from sms_auth.models import HistoryNotification
from user_profile.models import FullUserSailorHistory

User = get_user_model()


@celery_app.task
def clear_unsuccess_dkk():
    from sailor.statement import serializers
    minuts_ago = datetime.now() - timedelta(minutes=30)
    statement_dkk = StatementSQC.objects.filter(status_document_id=16, created_at__lt=minuts_ago,
                                                protocolsqc__isnull=True)
    for statement in statement_dkk:
        key = SailorKeys.objects.filter(statement_dkk__overlap=[statement.id]).first()
        if not key:
            continue
        key.statement_dkk.remove(statement.id)
        key.save(update_fields=['statement_dkk'])
        _statement = deepcopy(statement)
        save_history.s(user_id=magic_numbers.celery_user_id, module='StatementDKK', action_type='delete',
                       content_obj=_statement, serializer=serializers.StatementDKKSerializer,
                       old_obj=_statement, sailor_key_id=key.id).apply_async(serializer='pickle')
    length_remove_dkk = len(statement_dkk)
    statement_dkk.delete()
    return length_remove_dkk


@celery_app.task
def clear_unsuccess_qualification():
    from sailor.statement import serializers
    minuts_ago = datetime.now() - timedelta(minutes=30)
    statement_qual = StatementQualification.objects.filter(
        (
            (Q(status_document_id=magic_numbers.status_state_qual_dkk_absense) & Q(
                qualificationdocument__isnull=True))
        ) & Q(created_at__lt=minuts_ago))
    # QualificationDocument.objects.filter(statement__in=statement_qual).delete()
    for statement in statement_qual:
        key = SailorKeys.objects.filter(statement_qualification__overlap=[statement.id]).first()
        if not key:
            continue
        key.statement_qualification.remove(statement.id)
        key.save(update_fields=['statement_qualification'])
        _statement = deepcopy(statement)
        save_history.s(user_id=magic_numbers.celery_user_id, module='StatementQualification', action_type='delete',
                       content_obj=_statement, serializer=serializers.StatementQualificationDocumentSerializer,
                       old_obj=_statement, sailor_key_id=key.id).apply_async(serializer='pickle')
    length_remove_qual = len(statement_qual)
    statement_qual.delete()
    return length_remove_qual


@celery_app.task
def clear_unsuccess_demand():
    from sailor import serializers
    months_ago = date.today() - relativedelta(months=3)
    demand_position_dkk = DemandPositionDKK.objects.filter(created_at__date__lt=months_ago)
    for demand in demand_position_dkk:
        key = SailorKeys.objects.filter(demand_position__overlap=[demand.id]).first()
        if not key:
            continue
        key.demand_position.remove(demand.id)
        key.save(update_fields=['demand_position'])
        _demand = deepcopy(demand)
        save_history.s(user_id=magic_numbers.celery_user_id, module='DemandPositionDKK', action_type='delete',
                       content_obj=_demand, serializer=serializers.DemandPositionDKKSerializer,
                       old_obj=_demand, sailor_key_id=key.id).apply_async(serializer='pickle')
    length_remove_demand_position_dkk = len(demand_position_dkk)
    demand_position_dkk.delete()
    return length_remove_demand_position_dkk


@celery_app.task
def change_status_ntz_to_expired() -> List:
    today = date.today()
    expired_certificate = CertificateETI.objects.filter(date_end__lt=today,
                                                        status_document_id__in=[2, magic_numbers.status_qual_doc_valid,
                                                                                magic_numbers.status_qual_doc_in_proccess])
    for certificate in expired_certificate:
        save_history.s(user_id=magic_numbers.celery_user_id, module='CertificateNTZ', action_type='edit',
                       content_obj=certificate, new_obj={'status_document': magic_numbers.status_qual_doc_expired},
                       old_obj={'status_document': certificate.status_document_id},
                       get_sailor=True).apply_async(serializer='pickle')
    expired_certificate.update(status_document_id=magic_numbers.status_qual_doc_expired)
    return list(expired_certificate.values_list('id', flat=True))


@celery_app.task
def change_status_proof_diploma_to_expired() -> List:
    today = date.today()
    expired_proof_diploma = ProofOfWorkDiploma.objects.filter(date_end__lt=today,
                                                              status_document_id__in=[
                                                                  magic_numbers.status_qual_doc_in_proccess,
                                                                  magic_numbers.status_qual_doc_valid])
    for proof in expired_proof_diploma:
        save_history.s(user_id=magic_numbers.celery_user_id, module='ProofOfDiploma', action_type='edit',
                       content_obj=proof, new_obj={'status_document': magic_numbers.status_qual_doc_expired},
                       old_obj={'status_document': proof.status_document_id},
                       get_sailor=True).apply_async(serializer='pickle')
    expired_proof_diploma.update(status_document_id=magic_numbers.status_qual_doc_expired)
    return list(expired_proof_diploma.values_list('id', flat=True))


@celery_app.task
def change_status_certificate_qual() -> List:
    today = date.today()
    expired_qual_certificates = QualificationDocument.objects.filter(date_end__lt=today,
                                                                     status_document_id__in=[
                                                                         magic_numbers.status_qual_doc_valid,
                                                                         magic_numbers.status_qual_doc_in_proccess],
                                                                     type_document_id__in=magic_numbers.qual_documents_with_end_date)
    for qual_doc in expired_qual_certificates:
        save_history.s(user_id=magic_numbers.celery_user_id, module='QualificationDocument', action_type='edit',
                       content_obj=qual_doc, new_obj={'status_document': magic_numbers.status_qual_doc_expired},
                       old_obj={'status_document': qual_doc.status_document_id}, get_sailor=True). \
            apply_async(serializer='pickle')
    # TODO: change update() to save() for signals
    # expired_qual_certificates.update(status_document_id=magic_numbers.status_qual_doc_expired)
    for cert in expired_qual_certificates:
        cert.status_document_id = magic_numbers.status_qual_doc_expired
        cert.save()
    return list(expired_qual_certificates.values_list('id', flat=True))


@celery_app.task
def change_status_medical_certificate() -> List:
    today = date.today()
    expired_medical_doc = MedicalCertificate.objects.filter(status_document_id__in=[
        magic_numbers.status_qual_doc_in_proccess, magic_numbers.status_qual_doc_valid, 2], date_end__lt=today)
    for medical in expired_medical_doc:
        save_history.s(user_id=magic_numbers.celery_user_id, module='MedicalCertificate', action_type='edit',
                       content_obj=medical, new_obj={'status_document': magic_numbers.status_qual_doc_expired},
                       old_obj={'status_document': medical.status_document.id}, get_sailor=True). \
            apply_async(serializer='pickle')
    expired_medical_doc.update(status_document_id=magic_numbers.status_qual_doc_expired)
    return list(expired_medical_doc.values_list('id', flat=True))


@celery_app.task
def change_status_sailor_passport() -> List:
    today = date.today()
    expired_sailor_passport = SailorPassport.objects.filter(status_document_id__in=[14, 2], date_end__lt=today).exclude(
        date_renewal__gt=today)
    for passport in expired_sailor_passport:
        save_history.s(user_id=magic_numbers.celery_user_id, module='SailorPassport', action_type='edit',
                       content_obj=passport, new_obj={'status_document': magic_numbers.status_qual_doc_expired},
                       old_obj={'status_document': passport.status_document_id}, get_sailor=True). \
            apply_async(serializer='pickle')
    expired_sailor_passport.update(status_document_id=magic_numbers.status_qual_doc_expired)
    return list(expired_sailor_passport.values_list('id', flat=True))


@celery_app.task
def change_status_protocol_dkk() -> List:
    today = date.today()
    expired_protocol_dkk = ProtocolSQC.objects.filter(status_document_id=magic_numbers.status_protocol_dkk_valid,
                                                      date_end__lt=today)
    for protocol_dkk in expired_protocol_dkk:
        save_history.s(user_id=magic_numbers.celery_user_id, module='ProtocolDKK', action_type='edit',
                       content_obj=protocol_dkk, new_obj={'status_document': magic_numbers.status_protocol_dkk_expired},
                       old_obj={'status_document': protocol_dkk.status_document_id}, get_sailor=True). \
            apply_async(serializer='pickle')
    # DONE: change update() to save() for signals
    # expired_protocol_dkk.update(status_document_id=magic_numbers.status_protocol_dkk_expired)
    for prot in expired_protocol_dkk:
        prot.status_document_id = magic_numbers.status_protocol_dkk_expired
        prot.save()
    return list(expired_protocol_dkk.values_list('id', flat=True))


@celery_app.task
def save_history(user_id=None, sailor_key_id=None, module=None, action_type=None,
                 content_obj=None, serializer=None, old_obj=None, new_obj=None, get_sailor=False):
    if get_sailor is True and content_obj:
        try:
            if module == 'ServiceRecord':
                sailor_key_id = SailorKeys.objects.filter(service_records__overlap=[content_obj.id]).first().id
            elif module == 'Education':
                sailor_key_id = SailorKeys.objects.filter(education__overlap=[content_obj.id]).first().id
            elif module == 'CertificateNTZ':
                sailor_key_id = SailorKeys.objects.filter(sertificate_ntz__overlap=[content_obj.id]).first().id
            elif module == 'QualificationDocument':
                sailor_key_id = SailorKeys.objects.filter(qualification_documents__overlap=[content_obj.id]).first().id
            elif module == 'MedicalCertificate':
                sailor_key_id = SailorKeys.objects.filter(medical_sertificate__overlap=[content_obj.id]).first().id
            elif module == 'SailorPassport':
                sailor_key_id = SailorKeys.objects.filter(sailor_passport__overlap=[content_obj.id]).first().id
            elif module == 'StatementDKK':
                sailor_key_id = SailorKeys.objects.filter(statement_dkk__overlap=[content_obj.id]).first().id
            elif module == 'CitizenPassport':
                sailor_key_id = SailorKeys.objects.filter(citizen_passport__overlap=[content_obj.id]).first().id
            elif module == 'ExperienceDoc':
                sailor_key_id = SailorKeys.objects.filter(experience_docs__overlap=[content_obj.id]).first().id
            elif module == 'ProtocolSQC':
                sailor_key_id = SailorKeys.objects.filter(protocol_dkk__overlap=[content_obj.id]).first().id
            elif module == 'StatementQualification':
                sailor_key_id = SailorKeys.objects.filter(statement_qualification__overlap=[content_obj.id]).first().id
            elif module == 'ProofOfDiploma':
                diploma_id = content_obj.diploma.id
                sailor_key_id = SailorKeys.objects.filter(qualification_documents__overlap=[diploma_id]).first().id
            elif module in ['LineInServiceRecord', 'document.LineInServiceRecord']:
                if getattr(content_obj.service_record, 'id', None):
                    service_record = content_obj.service_record.id
                    sailor_key_id = SailorKeys.objects.filter(service_records__overlap=[service_record]).first().id
                else:
                    sailor_key_id = SailorKeys.objects.filter(experience_docs__overlap=[content_obj.id]).first().id
            elif module == 'DemandPositionDKK':
                sailor_key_id = SailorKeys.objects.filter(demand_position__overlap=[content_obj.id]).first().id
            elif module == 'StatementServiceRecord':
                sailor_key_id = SailorKeys.objects.filter(
                    statement_service_records__overlap=[content_obj.id]).first().id
            elif module == 'StatementETI':
                sailor_key_id = SailorKeys.objects.filter(statement_eti__overlap=[content_obj.id]).first().id
            elif module == 'StatementSailorPassport':
                sailor_key_id = SailorKeys.objects.filter(
                    statement_sailor_passport__overlap=[content_obj.id]).first().id
            elif module == 'StatementMedicalCertificate':
                sailor_key_id = SailorKeys.objects.filter(
                    statement_medical_certificate__overlap=[content_obj.id]).first().id
            elif module == 'StatementAdvancedTraining':
                sailor_key_id = SailorKeys.objects.filter(
                    statement_advanced_training__overlap=[content_obj.id]).first().id
            elif content_obj and module == content_obj._meta.object_name:
                sailor_key_id = SailorKeys.by_document.id(instance=content_obj).pk
        except AttributeError:
            sailor_key_id = None
    if new_obj and serializer:
        new_obj_ser = serializer(new_obj).data
    else:
        new_obj_ser = new_obj
    if old_obj and serializer:
        old_obj_ser = serializer(old_obj).data
    else:
        old_obj_ser = old_obj
    _new_obj_ser = json.loads(json.dumps(new_obj_ser, sort_keys=True, indent=1, cls=DjangoJSONEncoder))
    _old_obj_ser = json.loads(json.dumps(old_obj_ser, sort_keys=True, indent=1, cls=DjangoJSONEncoder))
    FullUserSailorHistory.objects.create(user_id=user_id, sailor_key=sailor_key_id, module=module,
                                         action_type=action_type,
                                         content_object=content_obj, old_obj_json=_old_obj_ser,
                                         new_obj_json=_new_obj_ser)
    return True


@celery_app.task
def change_status_qualification_document(sailor_id=None, exclude_diploma=None):
    def _get_filter(list_positions=[]):
        queries = [Q(list_positions__contains=[position]) for position in list_positions]
        query = reduce(lambda x, y: x & y, queries)
        return query

    def _disable_diploma_and_proofs(diplomas: QuerySet):
        from sailor.document.serializers import QualificationDocumentSerializer, ProofOfWorkDiplomaSerializer
        if diplomas.exists():
            _old_diploma = [_ for _ in deepcopy(diplomas)]
            for old_diploma, new_diploma in zip(_old_diploma, diplomas):
                new_diploma.status_document_id = magic_numbers.status_qual_doc_canceled
                new_diploma.save()
                save_history.s(user_id=magic_numbers.celery_user_id, module='QualificationDocument', action_type='edit',
                               content_obj=new_diploma,
                               serializer=QualificationDocumentSerializer,
                               new_obj=new_diploma, old_obj=old_diploma, sailor_key_id=sailor_id) \
                    .apply_async(serializer='pickle')
        else:
            return False
        sailor_proof_diploma_in_qual_doc = ProofOfWorkDiploma.objects.filter(
            diploma__in=[_diploma.pk for _diploma in _old_diploma])
        if sailor_proof_diploma_in_qual_doc.exists():
            _old_proof = [_ for _ in deepcopy(sailor_proof_diploma_in_qual_doc)]
            for old_proof, new_proof in zip(_old_proof, sailor_proof_diploma_in_qual_doc):
                new_proof.status_document_id = magic_numbers.status_qual_doc_canceled
                new_proof.save()
                save_history.s(user_id=magic_numbers.celery_user_id, module='ProofOfDiploma', action_type='edit',
                               content_obj=new_proof, serializer=ProofOfWorkDiplomaSerializer,
                               new_obj=new_proof, old_obj=old_proof, sailor_key_id=sailor_id) \
                    .apply_async(serializer='pickle')

    try:
        sailor_instance = SailorKeys.objects.get(id=sailor_id)
    except SailorKeys.DoesNotExist:
        raise ValueError('SailorKey Does not exists')
    excl_positions = [22, 2, 41, 4, 5, 361, 62, 6, 23, 21]
    sailor_qualification_document = QualificationDocument.objects.filter(
        id__in=sailor_instance.qualification_documents)  # .exclude(list_positions__overlap=excl_positions, id=exclude_diploma)
    exclude_diploma_obj = QualificationDocument.objects.get(pk=exclude_diploma)
    diploma_with_this_rank_without_pos = sailor_qualification_document.filter(rank_id=exclude_diploma_obj.rank_id). \
        exclude(_get_filter(exclude_diploma_obj.list_positions))  # дипломы с таким же рангом но с другими позишнами
    if diploma_with_this_rank_without_pos.exists() is True:
        positions_new_diploma = Position.objects.filter(id__in=exclude_diploma_obj.list_positions)
        for diploma in diploma_with_this_rank_without_pos:
            list_positions_old_diploma = Position.objects.filter(id__in=diploma.list_positions)
            if len(set(positions_new_diploma.values_list('level', flat=True)).intersection(
                    list_positions_old_diploma.values_list('level', flat=True))) != 0:
                # print(QualificationDocument.objects.filter(pk=diploma))
                _disable_diploma_and_proofs(QualificationDocument.objects.filter(pk=diploma.pk))
    elif (sailor_qualification_document.filter(rank_id=22, status_document_id=19).exists() and
          sailor_qualification_document.filter(rank_id=21, status_document_id=19) and
          exclude_diploma_obj.rank_id == 61):
        _disable_diploma_and_proofs(sailor_qualification_document.filter(rank_id__in=[21, 22], status_document_id=19))
    elif exclude_diploma_obj.type_document_id in [89, 88, 57, 21, 85, 86]:
        to_disable = sailor_qualification_document.filter(type_document_id__in=[89, 88, 57, 21, 85, 86],
                                                          status_document_id=19, rank_id=exclude_diploma_obj.rank_id). \
            exclude(id=exclude_diploma_obj.pk)
        _disable_diploma_and_proofs(to_disable)
    elif (exclude_diploma_obj.rank_id == 98 and
          sailor_qualification_document.filter(rank_id=99, status_document_id=19).exists()):
        to_disable = sailor_qualification_document.filter(rank_id=99, status_document_id=19)
        _disable_diploma_and_proofs(to_disable)

    else:
        list_key_document = DependencyDocuments.objects.filter(position_id__in=exclude_diploma_obj.list_positions,
                                                               for_what='start',
                                                               type_document__in=['Диплом', 'Свідоцтво фахівця']). \
            values_list('key_document', flat=True)
        position_diploma = [key['position'] for key_document in list_key_document for key in key_document]
        position_diploma = position_diploma + exclude_diploma_obj.list_positions
        sailor_diploma_in_qual_doc = sailor_qualification_document.filter(list_positions__overlap=position_diploma). \
            exclude(id=exclude_diploma)
        if exclude_diploma_obj.rank_id in [21, 22]:
            sailor_diploma_in_qual_doc = sailor_diploma_in_qual_doc.exclude(list_positions__overlap=excl_positions)
        _disable_diploma_and_proofs(sailor_diploma_in_qual_doc)

    return True


@celery_app.task
def change_status_proof_of_diploma(qual_diploma=None, exclude_proof=None, sailor_id=None):
    import sailor.document.serializers
    if sailor_id is None:
        sailor_id = SailorKeys.objects.filter(qualification_documents__contains=[qual_diploma]).first().pk
    qual_diploma = QualificationDocument.objects.get(id=qual_diploma)
    proofs_by_diploma = qual_diploma.proofofworkdiploma_set.filter(
        status_document_id=magic_numbers.status_qual_doc_valid).exclude(id=exclude_proof)
    _old_proof = [_ for _ in deepcopy(proofs_by_diploma)]
    proofs_by_diploma.update(status_document_id=magic_numbers.status_qual_doc_canceled)
    for old_proof, new_proof in zip(_old_proof, proofs_by_diploma):
        save_history.s(user_id=magic_numbers.celery_user_id, module='ProofOfDiploma', action_type='edit',
                       content_obj=new_proof, serializer=sailor.document.serializers.ProofOfWorkDiplomaSerializer,
                       new_obj=new_proof, old_obj=old_proof, sailor_key_id=sailor_id) \
            .apply_async(serializer='pickle')


@celery_app.task
def create_duplicate_qual_doc(old_instance: QualificationDocument, user_id):
    from sailor.document.serializers import ProofOfWorkDiplomaSerializer
    from sailor.document.serializers import QualificationDocumentSerializer
    key = SailorKeys.objects.filter(qualification_documents__contains=[old_instance.pk]).first()
    user = User.objects.get(id=user_id)
    user_profile = user.userprofile
    port_converter = {41: 70, 3: 69, 47: 21, 2: 0, 22: 67, 48: 38, 1: 0, 4: 66, 5: 64, 21: 1}
    port_id = port_converter[user_profile.branch_office_id]
    try:
        fio_captain_ukr = Port.objects.get(id=port_id).fiocapitanofport_set.all().first().name_ukr
        fio_captain_eng = Port.objects.get(id=port_id).fiocapitanofport_set.all().first().name_eng
    except (AttributeError, Port.DoesNotExist):
        fio_captain_eng = None
        fio_captain_ukr = None
    if not key:
        return False
    if old_instance.type_document_id in [49, 1, 87, 89, 88, 88, 57, 86, 85, 21, 3]:
        if old_instance.type_document_id in [49, 1]:
            filtering_type_doc = [49, 1]
        else:
            filtering_type_doc = [87, 89, 88, 88, 57, 86, 85, 21]
        number = QualificationDocument.objects.filter(date_start__year=date.today().year, port_id=port_id,
                                                      type_document_id__in=filtering_type_doc). \
            aggregate(number_doc=Max('number_document'))
        if number['number_doc'] is not None:
            number_document = number['number_doc'] + 1
        else:
            number_document = 1
        new_instance = deepcopy(old_instance)
        new_instance.pk = None
        if old_instance.type_document_id == 3:
            new_instance.type_document_id = 49
        new_instance.date_start = date.today()
        new_instance.number_document = number_document
        new_instance.status_document_id = 19
        new_instance.port_id = port_id
        new_instance.strict_blank = None
        new_instance.fio_captain_ukr = fio_captain_ukr
        new_instance.fio_captain_eng = fio_captain_eng
        new_instance.save()
        save_history.s(user_id=magic_numbers.celery_user_id, module='QualificationDocument', action_type='create',
                       content_obj=new_instance, serializer=QualificationDocumentSerializer, new_obj=new_instance,
                       sailor_key_id=key.pk).apply_async(serializer='pickle')
        key.qualification_documents = list(set(key.qualification_documents + [new_instance.pk]))
        key.save(update_fields=['qualification_documents'])
        if old_instance.proofofworkdiploma_set.filter(status_document_id=19).exists():
            for proof in old_instance.proofofworkdiploma_set.filter(status_document_id=19):
                _old_proof = deepcopy(proof)
                proof.status_document_id = old_instance.status_document_id
                proof.save(update_fields=['status_document_id'])
                save_history.s(user_id=magic_numbers.celery_user_id, module='ProofOfDiploma',
                               action_type='edit',
                               content_obj=_old_proof, serializer=ProofOfWorkDiplomaSerializer,
                               new_obj=proof, old_obj=_old_proof,
                               sailor_key_id=key.pk).apply_async(serializer='pickle')
                new_proof = deepcopy(proof)
                new_proof.status_document_id = magic_numbers.status_qual_doc_in_proccess
                new_proof.strict_blank = None
                new_proof.fio_captain_eng = fio_captain_eng
                new_proof.fio_captain_ukr = fio_captain_ukr
                new_proof.pk = None
                new_proof.port_id = port_id
                new_proof.date_start = date.today()
                new_proof.diploma = new_instance
                new_proof.save()
                save_history.s(user_id=magic_numbers.celery_user_id, module='ProofOfDiploma',
                               action_type='create',
                               content_obj=new_proof, serializer=ProofOfWorkDiplomaSerializer,
                               new_obj=new_proof,
                               sailor_key_id=key.pk).apply_async(serializer='pickle')


@celery_app.task
def create_duplicate_proof_diploma(old_instance: ProofOfWorkDiploma, user_id):
    from sailor.document.serializers import ProofOfWorkDiplomaSerializer
    key = SailorKeys.objects.filter(qualification_documents__contains=[old_instance.diploma.pk]).first()
    user = User.objects.get(id=user_id)
    user_profile = user.userprofile
    port_converter = {41: 70, 3: 69, 47: 21, 2: 0, 22: 67, 48: 38, 1: 0, 4: 66, 5: 64, 21: 1}
    port_id = port_converter[user_profile.branch_office_id]
    try:
        fio_captain_ukr = Port.objects.get(id=port_id).fiocapitanofport_set.all().first().name_ukr
        fio_captain_eng = Port.objects.get(id=port_id).fiocapitanofport_set.all().first().name_eng
    except (AttributeError, Port.DoesNotExist):
        fio_captain_eng = None
        fio_captain_ukr = None
    if not key:
        return False
    new_instance = deepcopy(old_instance)
    new_instance.status_document_id = magic_numbers.status_qual_doc_in_proccess
    new_instance.date_start = date.today()
    new_instance.port_id = port_id
    new_instance.fio_captain_ukr = fio_captain_ukr
    new_instance.fio_captain_eng = fio_captain_eng
    new_instance.strict_blank = None
    new_instance.pk = None
    new_instance.save()
    save_history.s(user_id=magic_numbers.celery_user_id, module='ProofOfDiploma',
                   action_type='create',
                   content_obj=new_instance, serializer=ProofOfWorkDiplomaSerializer,
                   new_obj=new_instance,
                   sailor_key_id=key.pk).apply_async(serializer='pickle')


@celery_app.task
def send_sms_with_id(sailor_key, phone):
    sailor_key = SailorKeys.objects.get(id=sailor_key)
    profile = Profile.objects.get(id=sailor_key.profile)
    if profile.sex_id in [1, 3]:
        appeal_to_sailor = 'Шановний'
    else:
        appeal_to_sailor = 'Шановна'

    name_middle_ukr = '{} {}'.format(profile.first_name_ukr, profile.middle_name_ukr)
    text = ('{} {}, в автоматизованій системі Реєстру'
            ' документів моряків України створен Ваш обліковий запис під номером {}.'.format(appeal_to_sailor,
                                                                                             name_middle_ukr,
                                                                                             sailor_key.pk))
    send_message(phone=phone, message=text)
    return True


@celery_app.task
def delete_old_phone(old_instance: Profile, new_instance: Profile):
    if type(new_instance.contact_info) is list:
        new_contacts = new_instance.contact_info
    else:
        new_contacts = []
    try:
        old_contacts = json.loads(old_instance.contact_info)
    except:
        old_contacts = []
    contact_to_del = set(old_contacts) - set(new_contacts)
    ContactInfo.objects.filter(id__in=list(contact_to_del)).delete()
    return True


@celery_app.task
def check_document_to_additional_verification(model_name, object_id, sailor_key=None):
    """
    Check document to additional verification
    :param model_name:
    :param object_id:
    :param sailor_key:
    :return:
    """
    from sailor.misc import get_sailor_by_modelname
    start_time = settings.TIME_START_SEND_ADDITIONAL_VERIFICATION
    now = datetime.now()
    start_time_obj = datetime.now().replace(**start_time)
    end_time = settings.TIME_END_SEND_ADDITIONAL_VERIFICATION
    end_time_obj = datetime.now().replace(**end_time)
    if (now < start_time_obj) or (now > end_time_obj):
        return False
    model_cls = ContentType.objects.get(model=model_name).model_class()
    obj = model_cls.objects.get(pk=object_id)
    if not sailor_key:
        try:
            sailor_key = get_sailor_by_modelname(model_name, obj).pk
        except AttributeError:
            sailor_key = ''
    phone_message = f'Вам необходимо провести аудит на' \
                    f' верифицированный документ у моряка № {sailor_key} {obj._meta.verbose_name} № {obj.get_number}'
    # email_message = f'Добавлен новый документ на верификацию. ' \
    #                 f'Пожалуйста обработайте {obj._meta.verbose_name} №{obj.get_number} у моряка № {sailor_key}'
    send_message(settings.PHONE_TO_ADDITIONAL_VERIFICATION, phone_message, obj)
    subject = f'[{obj._meta.verbose_name}] Аудит на верификацию'
    mail_resp = send_mail(subject, phone_message, 'help@itcs.net.ua', [settings.EMAIL_TO_ADDITIONAL_VERIFICATION])
    HistoryNotification.objects.create(destination=settings.EMAIL_TO_ADDITIONAL_VERIFICATION,
                                       message=phone_message, status_answer=mail_resp,
                                       date_answer=timezone.now(), content_object=obj, type='Mail')
    return True


@celery_app.task
def resend_sms_about_additional_verification(ct_id, object_id, sailor_key=None):
    """
    Check all documents time to additional status and if its created and in verification more then N hours
     then resend sms and mail
    :param ct_id:
    :param object_id:
    :param sailor_key:
    :return:
    """
    model_cls = ContentType.objects.get(id=ct_id).model_class()
    obj = model_cls.objects.get(pk=object_id)

    if not sailor_key:
        try:
            sailor_key = get_sailor_by_modelname(model_cls._meta.model_name, obj).pk
        except AttributeError:
            sailor_key = ''
    phone_message = f'Вам необходимо провести аудит на' \
                    f' верифицированный документ у моряка № {sailor_key} {obj._meta.verbose_name} № {obj.get_number}'
    # email_message = f'{obj._meta.verbose_name} №{obj.get_number} у моряка №{sailor_key} слишком долго находится' \
    #                 f' на верификации. Пожалуйста подтвердите документ.'
    send_message(settings.PHONE_TO_ADDITIONAL_VERIFICATION, phone_message, obj)
    subject = f'[{obj._meta.verbose_name}] Аудит на верификацию'
    mail_resp = send_mail(subject, phone_message, 'help@itcs.net.ua', [settings.EMAIL_TO_ADDITIONAL_VERIFICATION])
    HistoryNotification.objects.create(destination=settings.EMAIL_TO_ADDITIONAL_VERIFICATION, message=phone_message,
                                       status_answer=mail_resp, date_answer=timezone.now(), content_object=obj,
                                       type='Mail')


@celery_app.task
def check_to_resend_sms_additional_verification():
    start_time = settings.TIME_START_SEND_ADDITIONAL_VERIFICATION
    now = datetime.now()
    start_time_obj = datetime.now().replace(**start_time)
    end_time = settings.TIME_END_SEND_ADDITIONAL_VERIFICATION
    end_time_obj = datetime.now().replace(**end_time)
    if (now < start_time_obj) or (now > end_time_obj):
        return False
    sailor_passport = SailorPassport.objects.filter(status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION)
    education_doc = Education.objects.filter(status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION)
    qual_doc = QualificationDocument.objects.filter(status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION)
    service_record = ServiceRecord.objects.filter(status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION)
    line_in_serv = LineInServiceRecord.objects.filter(status_line_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION,
                                                      service_record__isnull=False)
    exp_doc = LineInServiceRecord.objects.filter(status_line_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION,
                                                 service_record__isnull=True)
    medical_cert = MedicalCertificate.objects.filter(status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION)

    list_of_qs_docs = [sailor_passport, education_doc, qual_doc, service_record, line_in_serv, exp_doc, medical_cert]
    for qs_doc in list_of_qs_docs:
        ct = ContentType.objects.get_for_model(qs_doc.model)
        history_notification = HistoryNotification.objects.filter(
            document_type=ct, object_id__in=list(qs_doc.values_list('pk', flat=True)),
            type='Phone').order_by('document_type', 'object_id', '-send_time').distinct('document_type', 'object_id')
        now = timezone.now()
        for notification in history_notification:
            if (now - notification.send_time) > timedelta(hours=2):
                resend_sms_about_additional_verification.delay(notification.document_type_id, notification.object_id)


@celery_app.task
def on_reject_line_in_service(line_id):
    notify_BO_on_reject_line_in_service.s(line_id).apply_async()
    start_time = settings.TIME_START_SEND_ADDITIONAL_VERIFICATION
    now = datetime.now()
    start_time_obj = datetime.now().replace(**start_time)
    end_time = settings.TIME_END_SEND_ADDITIONAL_VERIFICATION
    end_time_obj = datetime.now().replace(**end_time)
    if (now < start_time_obj) or (now > end_time_obj):
        return False
    instance = LineInServiceRecord.objects.get(id=line_id)
    if instance.service_record:
        sailor_key = SailorKeys.objects.filter(service_records__overlap=[instance.service_record_id]).first()
        type_doc = 'запись в послужной книжке'
    else:
        sailor_key = SailorKeys.objects.filter(experience_docs__overlap=[instance.pk]).first()
        type_doc = 'справку про стаж'
    phone_message = email_message = f'У моряка № {sailor_key.pk} {type_doc} сменили статус на "Отклонено".' \
                                    f' Перейдите на моряка и перевроверьте пожалуйста документ'
    send_message(settings.PHONE_TO_ADDITIONAL_VERIFICATION, phone_message)
    subject = f'[{sailor_key.pk}] Отклонённый стаж'
    mail_resp = send_mail(subject, email_message, 'help@itcs.net.ua', [settings.EMAIL_TO_ADDITIONAL_VERIFICATION])
    HistoryNotification.objects.create(destination=settings.EMAIL_TO_ADDITIONAL_VERIFICATION, message=email_message,
                                       status_answer=mail_resp, date_answer=timezone.now(),
                                       type='Mail')


@celery_app.task
def notify_BO_on_reject_line_in_service(line_id):
    instance = LineInServiceRecord.objects.get(id=line_id)
    if instance.service_record:
        sailor_key = SailorKeys.objects.filter(service_records__overlap=[instance.service_record_id]).first()
        type_doc = 'запись в послужной книжке'
    else:
        sailor_key = SailorKeys.objects.filter(experience_docs__overlap=[instance.pk]).first()
        type_doc = 'справку про стаж'
    email_message = f'У моряка № {sailor_key.pk} {type_doc} сменили статус на "Отклонено".' \
                    f' Перейдите на моряка и перевроверьте пожалуйста документ'
    subject = f'[{sailor_key.pk}] Отклонённый стаж'
    mail_resp = send_mail(subject, email_message, 'help@itcs.net.ua', [settings.MONTANA_MAIL])
    HistoryNotification.objects.create(destination=settings.MONTANA_MAIL, message=email_message,
                                       status_answer=mail_resp, date_answer=timezone.now(),
                                       type='Mail')


@celery_app.task
def on_approving_reject_line_in_service(line_id):
    instance = LineInServiceRecord.objects.get(id=line_id)
    if instance.service_record:
        sailor_key = SailorKeys.objects.filter(service_records__overlap=[instance.service_record_id]).first()
        type_doc = 'запись в послужной книжке'
    else:
        sailor_key = SailorKeys.objects.filter(experience_docs__overlap=[instance.pk]).first()
        type_doc = 'справку про стаж'
    email_message = f'У моряка № {sailor_key.pk} {type_doc} сменили статус с  "Отклонено" на "Схвалено".' \
                    f' Перейдите на моряка и перевроверьте пожалуйста документ'
    subject = f'[{sailor_key.pk}] Одобрение отклонённого стажа'
    mail_resp = send_mail(subject, email_message, 'help@itcs.net.ua', [settings.MONTANA_MAIL])
    HistoryNotification.objects.create(destination=settings.EMAIL_TO_ADDITIONAL_VERIFICATION, message=email_message,
                                       status_answer=mail_resp, date_answer=timezone.now(),
                                       type='Mail')
