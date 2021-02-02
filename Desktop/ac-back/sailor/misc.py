import re
from copy import deepcopy
from datetime import date, timedelta, datetime
from itertools import chain

import workdays
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Case, Value, When, BooleanField, Max, IntegerField
from docxtpl import RichText
from rest_framework.exceptions import ValidationError

from agent.models import StatementAgentSailor, AgentSailor
from back_office.models import PacketItem
from back_office.utils import hours_to_date
from cadets.models import StudentID
from communication.models import SailorKeys
from directory.models import Position, ExperinceForDKK, VerificationStage
from itcs import magic_numbers
from sailor.document.models import (ServiceRecord, LineInServiceRecord, Education, ProtocolSQC, CertificateETI,
                                    MedicalCertificate, QualificationDocument, ProofOfWorkDiploma,
                                    ResponsibilityServiceRecord)
from sailor.models import (DependencyDocuments, Passport, SailorPassport, DocumentInVerification, Profile)
from sailor.statement.models import StatementSQC, StatementQualification, StatementServiceRecord

User = get_user_model()

def count_doc_sailor(sailor_key: SailorKeys):
    def get_list(cls, attr):
        objects = getattr(cls, attr)
        if objects:
            return objects
        else:
            return []

    educ_list = get_list(sailor_key, 'education')
    document_about_education_count = Education.objects.filter(id__in=educ_list, status_document_id=2).count()
    cert_ntz_list = get_list(sailor_key, 'sertificate_ntz')
    sertificate_ntz_count = CertificateETI.objects.filter(id__in=cert_ntz_list, status_document_id=19).count()
    qual_doc_list = get_list(sailor_key, 'qualification_documents')
    qualitifaction_doc_count = QualificationDocument.objects.filter(id__in=qual_doc_list,
                                                                    status_document_id=19).count()
    proof_of_diplomas = ProofOfWorkDiploma.objects.filter(diploma__in=sailor_key.qualification_documents,
                                                          status_document_id=19).count()
    qualitifaction_doc_count = qualitifaction_doc_count + proof_of_diplomas

    medical_cert_list = get_list(sailor_key, 'medical_sertificate')
    medical_sertificate = MedicalCertificate.objects.filter(id__in=medical_cert_list, status_document_id=19).count()
    summ = (document_about_education_count + sertificate_ntz_count + qualitifaction_doc_count +
            medical_sertificate)
    return summ


class CheckSailorForPositionDKK:
    def __init__(self, sailor, is_continue=0, list_position=None, statement_qual=False,
                 demand_position=False, perform_check=False, statement_creation_date: date = None, packet=False):
        self.sailor = sailor
        self.position = None
        self.is_continue = is_continue
        self.list_position = list_position
        if self.position and not self.list_position:
            self.list_position = [self.position]
        self.statement_qual = statement_qual
        self.demand_position = demand_position
        self.perform_check = perform_check
        self.statement_creation_date = statement_creation_date or date.today()
        self.packet = packet

    def __get_higher_education_response(self, education, sert):
        is_having = []
        educ_docs = None
        resp = {
            'statement_qual_doc': None, 'all_docs': None, 'exists_doc': None, 'not_exists_doc': None, 'having': None
        }
        if any('specialization' in key for key in sert.key_document):
            for key in sert.key_document:
                filtering = dict()
                filtering = self.add_param_to_dict(key, filtering, 'priority', 'extent__priority__gte')
                filtering = self.add_param_to_dict(key, filtering, 'speciality', 'speciality')
                filtering['type_document_id'] = 1
                filtering['status_document_id'] = 2
                filtering = self.add_param_to_dict(key, filtering, 'specialization', 'specialization')
                educ_docs = education.filter(**filtering).order_by('-date_issue_document')
                is_having.append(educ_docs.exists())
                if any(is_having):
                    break
        else:
            min_prior = min([int(key['priority']) for key in sert.key_document])
            all_speciality = [key['speciality'] for key in sert.key_document]
            filtering = {'extent__priority__gte': min_prior,
                         'type_document_id': 1, 'status_document_id': 2}
            if 'any' not in all_speciality:
                filtering['speciality_id__in'] = all_speciality
            educ_docs = education.filter(**filtering).order_by('-date_issue_document')
            is_having.append(educ_docs.exists())
        having = any(is_having)
        resp_dict = {'document_descr': sert.document_description,
                     'standarts_text': sert.standarts_text, 'exists': having,
                     'type_document': 'Документ про освіту',
                     }
        if having is True:
            number_doc = educ_docs.first().number_document
            date_issued = educ_docs.first().date_issue_document
            resp['exists_doc'] = educ_docs.first().get_info_for_statement
            resp['all_docs'] = educ_docs.first()
        else:
            number_doc = ''
            date_issued = ''
            resp['not_exists_doc'] = resp_dict
        if self.statement_qual is True:
            resp_dict['number'] = number_doc
            resp_dict['issued_date'] = date_issued
            resp_dict['doc_name'] = 'Копія Учбового диплому  з додатком.'
            resp['statement_qual_doc'] = resp_dict
        resp['having'] = having
        return resp

    def __get_education_response(self, education, sert):
        is_having = []
        educ_docs = None
        resp = {
            'statement_qual_doc': None, 'all_docs': None, 'exists_doc': None, 'not_exists_doc': None, 'having': None
        }
        for key in sert.key_document:
            filtering = {'status_document_id': 2, 'type_document_id': key['type_doc_nz']}
            if 'qualification' in key:
                filtering['qualification_id'] = key['qualification']
            elif 'speciality' in key and key['speciality'] != 'any':
                filtering['speciality_id'] = key['speciality']
            educ_docs = education.filter(**filtering).order_by('-date_issued')
            is_having.append(educ_docs.exists())
            if any(is_having):
                break
        having = any(is_having)
        resp_dict = {'document_descr': sert.document_description,
                     'standarts_text': sert.standarts_text, 'exists': having,
                     'type_document': 'Документ про освіту'}
        if having is True:
            resp['all_docs'] = educ_docs.first()
            number_doc = educ_docs.first().number_document
            date_issued = educ_docs.first().date_issue_document
            resp['exists_doc'] = educ_docs.first().get_info_for_statement
        else:
            number_doc = ''
            date_issued = ''
            resp['not_exists_doc'] = resp_dict
        if self.statement_qual is True:
            resp_dict['number'] = number_doc
            resp_dict['issued_date'] = date_issued
            resp_dict['doc_name'] = 'Копія Учбового диплому  з додатком.'
            resp['statement_qual_doc'] = resp_dict
        resp['having'] = having
        return resp

    @staticmethod
    def add_param_to_dict(from_dict, resp_dict, get_param, set_param):
        try:
            _p = from_dict[get_param]
            if _p == 'any':
                return resp_dict
            resp_dict[set_param] = _p
            return resp_dict
        except KeyError:
            return resp_dict

    @staticmethod
    def get_value_or_none(_list, attr):
        try:
            return _list[attr]
        except KeyError:
            pass

    def check_documents_for_protocol_dkk_list_pos(self):
        key = SailorKeys.objects.get(id=self.sailor)
        education = Education.objects.filter(id__in=key.education)
        NTZ = CertificateETI.objects.filter(id__in=key.sertificate_ntz)
        qual_doc = QualificationDocument.objects.filter(id__in=key.qualification_documents)
        dependencies = DependencyDocuments.objects.filter(position_id__in=self.list_position). \
            order_by('type_document', 'key_document').distinct('type_document', 'key_document')

        filtering = {'for_what__in': ['start', 'both']} if not self.is_continue else \
            {'for_what__in': ['continue', 'both']}
        dependencies = dependencies.filter(**filtering)
        education_dependencies = dependencies.filter(type_document__in=['Диплом про вищу освіту', 'Образование'])
        qualification_dependencies = dependencies.filter(type_document__in=['Свідоцтво фахівця', 'Диплом'])
        eti_dependencies = dependencies.filter(type_document='NTZ', key_document__contained_by=[219, 27, 104])
        advanced_training = dependencies.filter(type_document='Свідоцтво про підвищення кваліфікації')
        response = []
        _resp = []
        for dependency in education_dependencies:
            if dependency.type_document == 'Диплом про вищу освіту':
                edc = Education.objects.none()
                if any('specialization' in key for key in dependency.key_document):
                    for key in dependency.key_document:
                        filtering = dict()
                        filtering = self.add_param_to_dict(key, filtering, 'priority', 'extent__priority__gte')
                        filtering = self.add_param_to_dict(key, filtering, 'speciality', 'speciality')
                        filtering['type_document_id'] = 1
                        filtering['status_document_id'] = 2
                        filtering = self.add_param_to_dict(key, filtering, 'specialization', 'specialization')
                        edc |= education.filter(**filtering)
                else:

                    min_prior = min([int(key['priority']) for key in dependency.key_document])
                    all_speciality = [self.get_value_or_none(key, 'speciality') for key in dependency.key_document]
                    all_speciality = list(filter(None, all_speciality))
                    filtering = {'extent__priority__gte': min_prior,
                                 'type_document_id': 1, 'status_document_id': 2}
                    if 'any' not in all_speciality:
                        filtering['speciality_id__in'] = all_speciality
                    resp_filtering = Q(**filtering)
                    all_other_specialization = [self.get_value_or_none(key, 'specializ_other') for key in
                                                dependency.key_document]
                    all_other_specialization = list(filter(None, all_other_specialization))
                    if all_other_specialization:
                        or_filtering = {'extent__priority__gte': min_prior, 'type_document_id': 1,
                                        'status_document_id': 2, 'specialization_id__in': all_other_specialization}
                        resp_filtering = (Q(**filtering) | Q(**or_filtering))
                    edc |= education.filter(resp_filtering)
                try:
                    date_end_educ = edc.first().date_end_educ.strftime('%Y')
                except AttributeError:
                    date_end_educ = '__________________'
                try:
                    name_nz = edc.first().name_nz.name_ukr
                except AttributeError:
                    name_nz = '________________________________________'
                try:
                    speciality = edc.first().speciality.name_ukr
                except AttributeError:
                    speciality = '__________________________________________'
                try:
                    qualification = edc.first().qualification.name_ukr
                except AttributeError:
                    qualification = '________________________________________'
                response.append({'text_education': RichText('У {} році закінчив {}\nза спеціальністю {}\nта здобув'
                                                            ' кваліфікацію {}'.format(date_end_educ, name_nz,
                                                                                      speciality, qualification),
                                                            font='Times New Roman')})
            elif dependency.type_document == 'Образование':
                educc = Education.objects.none()
                for key in dependency.key_document:
                    if 'qualification' in key:
                        educc |= dependency.filter(qualification=key['qualification'],
                                                   type_document_id=key['type_doc_nz'],
                                                   status_document_id=2)
                    else:
                        if key['speciality'] == 'any':
                            educc |= dependency.filter(type_document_id=key['type_doc_nz'],
                                                       status_document_id=2)
                        else:
                            educc |= dependency.filter(type_document_id=key['type_doc_nz'],
                                                       status_document_id=2,
                                                       speciality_id=key['speciality'])
                try:
                    date_end_educ = educc.first().date_end_educ.strftime('%Y')
                except AttributeError:
                    date_end_educ = '__________________'
                try:
                    name_nz = educc.first().name_nz.name_ukr
                except AttributeError:
                    name_nz = '________________________________________'
                try:
                    speciality = educc.first().speciality.name_ukr
                except AttributeError:
                    speciality = 'Немає'
                try:
                    qualification = educc.first().qualification.name_ukr
                except AttributeError:
                    qualification = '________________________________________'
                response.append({'text_education': RichText('У {} році закінчив {}\nза спеціальністю {}\nта здобув '
                                                            'кваліфікацію {}'.format(date_end_educ, name_nz,
                                                                                     speciality,
                                                                                     qualification),
                                                            font='Times New Roman')})
        if qualification_dependencies.exists():
            _resp = []
            for dependency in qualification_dependencies:
                all_position = [pos['position'] for pos in dependency.key_document]
                all_types = [doc['type_document'] for doc in dependency.key_document]
                if 'any' in all_position:
                    having = qual_doc.filter(type_document_id__in=all_types,
                                             status_document_id__in=[2, 19]).order_by('-date_start')
                else:
                    having = qual_doc.filter(list_positions__overlap=all_position,
                                             type_document_id__in=all_types,
                                             status_document_id__in=[2, 19]).order_by('-date_start')
                captain = '_______________________'
                try:
                    number = having.first().get_number
                    date_issued = having.first().date_start.strftime('%d.%m.%Y')
                    rank = having.first().rank
                    rank_name_ukr = rank.name_ukr
                    if having.first().port:
                        captain = having.first().port.position_capitan_ukr
                        captain = captain.replace('Капітан', '')
                    else:
                        captain = '___________________'
                    if rank.type_rank_id == 3:
                        type_r_text = 'кваліфікацію'
                    else:
                        type_r_text = 'звання'
                except AttributeError:
                    number = '___________________________'
                    date_issued = '_______________________'
                    rank_name_ukr = '___________________________'
                    type_r_text = 'звання / кваліфікацію'
                _resp.append('{} № {} на {} {} виданий / видане {} року '
                             'капітаном {}'.format(dependency.type_document, number, type_r_text,
                                                   rank_name_ukr, date_issued, captain))
            response.append({'text_qual_doc': RichText('\n'.join(_resp), font='Times New Roman')})
        if eti_dependencies.exists():
            _resp = []
            for dependency in eti_dependencies:
                ntz = NTZ.filter(course_training_id=dependency.key_document[0],
                                 status_document_id__in=[2, magic_numbers.status_qual_doc_valid])
                try:
                    date_issued_ntz = ntz.first().date_start.year
                    name_course = ntz.first().course_training.name_ukr
                    name_ntz = ntz.first().ntz.name
                    number_doc = ntz.first().ntz_number
                    date_issued_full = ntz.first().date_start.strftime('%d.%m.%Y')
                except AttributeError:
                    date_issued_ntz = '__________________'
                    name_course = '____________________________________________________________________________________'
                    name_ntz = '_______________________________________________________________________________________'
                    number_doc = '__________________'
                    date_issued_full = '_________________'
                _resp.append(
                    'У {} році закінчив {} в {}. \nСвідоцтво №{} видано {}'.format(date_issued_ntz, name_course,
                                                                                   name_ntz, number_doc,
                                                                                   date_issued_full))
            response.append({'text_ntz': RichText('\n'.join(_resp), font='Times New Roman')})
        elif advanced_training.exists():
            _resp = []
            for dependency in advanced_training:
                all_qual = [pos['qualitification'] for pos in dependency.key_document]
                educ = dependency.filter(qualification_id__in=all_qual, type_document_id=3,
                                         status_document_id=2)
                try:
                    date_issued_educ = educ.first().date_end_educ.strftime('%Y')
                    name_qual = educ.first().qualification.name_ukr
                    name_educ = educ.first().name_nz.name_ukr
                except AttributeError:
                    date_issued_educ = '__________________'
                    name_qual = '____________________________________________________________________________________'
                    name_educ = '______________________________________________________________________________________'
                response.append({'text_ntz': 'У {} році закінчив курси {} в {}'.format(date_issued_educ,
                                                                                       name_qual, name_educ)})
        return response

    def get_docs_with_status(self):
        sailor_key = SailorKeys.objects.get(id=self.sailor)
        education = Education.objects.filter(id__in=sailor_key.education).annotate(is_verification=Case(
            When(status_document_id=34, then=Value(True)),
            output_field=BooleanField(), default=Value(False)
        ))
        educ_exists = []
        certificates = CertificateETI.objects.filter(id__in=sailor_key.sertificate_ntz)
        qual_doc = QualificationDocument.objects.select_related().filter(
            id__in=sailor_key.qualification_documents
        ).annotate(
            is_verification=Case(
                When(status_document_id=34, then=Value(True)),
                output_field=BooleanField(), default=Value(False)
            ))
        proof_diploma = ProofOfWorkDiploma.objects.select_related().prefetch_related().filter(
            diploma__in=qual_doc
        ).annotate(is_verification=Case(
            When(status_document_id=34, then=Value(True)),
            output_field=BooleanField(), default=Value(False)
        ))
        medical_certificate = MedicalCertificate.objects.select_related().prefetch_related().filter(
            id__in=sailor_key.medical_sertificate
        ).annotate(
            is_verification=Case(
                When(status_document_id=34, then=Value(True)),
                output_field=BooleanField(), default=Value(False)
            ))

        if any(list(Position.objects.filter(id__in=self.list_position).values_list('rank__is_dkk', flat=True))):
            certificates = certificates.exclude(is_only_dpd=True)

        dependencies = DependencyDocuments.objects.filter(position_id__in=self.list_position). \
            order_by('type_document', 'key_document').distinct('type_document', 'key_document')
        if self.packet and not self.check_list_position_and_student_id(sailor_key):
            certificates = certificates.filter(
                Q(ntz__is_red=True) | (
                        Q(ntz_id__in=[525, 218]) & Q(date_start__lt='2020-04-30'))
            )
        if self.packet:
            created_date = self.statement_creation_date
            year_later = created_date + relativedelta(years=1)
            four_month_later = created_date + relativedelta(months=4)
            certificates = certificates.exclude(date_end__lte=year_later)
            medical_certificate = medical_certificate.exclude(date_end__lte=four_month_later)

        filtering = {'for_what__in': ['start', 'both']} if not self.is_continue else \
            {'for_what__in': ['continue', 'both']}
        dependencies = dependencies.filter(**filtering)
        position = Position.objects.prefetch_related('rank').get(id=self.list_position[0])
        have_all_doc = []
        all_docs = []
        not_have_educ_doc = True
        exists_doc = list()
        not_exists_doc = list()
        statement_qual_doc = list()
        demand_exists_doc = []
        demand_not_exists_doc = []
        year_end = datetime.now() + relativedelta(years=1)
        for dependency in dependencies:
            qual_types = ['Диплом', 'Свідоцтво', 'Свідоцтво фахівця', 'Свідоцтво фахівця з підготовки за '
                                                                      'розширеною програмою для здійснення '
                                                                      'вантажних операцій на танкерах (на '
                                                                      'нафтових танкерах)',
                          'Свідоцтво фахівця з підготовки за розширеною програмою для здійснення вантажних '
                          'операцій на танкерах (на танкерах-газовозах)',
                          'Свідоцтво фахівця з підготовки за розширеною програмою для здійснення вантажних '
                          'операцій на танкерах (на танкерах-хімовозах)',
                          'Свідоцтво фахівця з початкової підготовки для здійснення вантажних операцій на '
                          'танкерах (на нафтових танкерах і танкерах – хімовозах)',
                          'Свідоцтво фахівця з початкової підготовки для здійснення вантажних операцій на '
                          'танкерах (на танкерах-газовозах)',
                          'Свідоцтво кваліфікованого матроса', 'Свідоцтво кваліфікованого моториста',
                          'Кваліфікаційне свідоцтво']
            if dependency.type_document in qual_types:
                all_position = [pos['position'] for pos in dependency.key_document]
                type_document = [pos['type_document'] for pos in dependency.key_document]
                filtering = {'type_document_id__in': type_document,
                             'status_document_id__in': [2, 19, magic_numbers.status_qual_doc_expired,
                                                        magic_numbers.VERIFICATION_STATUS,
                                                        magic_numbers.STATUS_CREATED_BY_AGENT]}
                if 'any' not in all_position:
                    filtering['list_positions__overlap'] = all_position
                docs = qual_doc.filter(**filtering).annotate(status=Case(
                    When(status_document_id__in=[2, 19], then=Value(0)),
                    When(status_document_id__in=[
                        magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT], then=Value(1)),
                    output_field=IntegerField(), default=Value(2)
                )).order_by('status', '-date_start')
                having = docs.exists()
                resp_dict = {'document_descr': dependency.document_description,
                             'standarts_text': dependency.standarts_text, 'exists': having,
                             'type_document': 'Кваліфікаційний документ моряка'}
                if having is True and docs.first().is_verification is True:
                    exists_doc.append(docs.first().get_info_for_statement)
                    demand_exists_doc.append(docs.first())
                    number_doc = '       '
                    date_issued = '         '
                    having = False
                    not_have_educ_doc = False
                elif having is True:
                    number_doc = docs.first().get_number
                    date_issued = docs.first().date_start
                    exists_doc.append(docs.first().get_info_for_statement)
                    all_docs.append(docs.first())
                    demand_exists_doc.append(docs.first())
                else:
                    number_doc = '       '
                    date_issued = '         '
                    not_exists_doc.append(resp_dict)
                    demand_not_exists_doc.append(dependency)
                    not_have_educ_doc = False
                if self.statement_qual is True:
                    resp_dict['number'] = number_doc
                    resp_dict['issued_date'] = date_issued
                    if 123 in all_position or 105 in all_position:
                        resp_dict['doc_name'] = 'Копія диплома оператора ГМЗЛБ та підтвердження до нього.'
                    else:
                        resp_dict['doc_name'] = 'Оригінали і копії робочого диплому та підтвердження до нього.'
                    statement_qual_doc.append(resp_dict)
                have_all_doc.append(having)

            elif dependency.type_document == 'Підтвердження робочого диплому':
                all_position = [pos['position'] for pos in dependency.key_document]
                filtering = dict()
                if dependency.for_what != 'continue':
                    filtering['status_document_id__in'] = [2, 19, 7, magic_numbers.VERIFICATION_STATUS,
                                                           magic_numbers.STATUS_CREATED_BY_AGENT]
                if 'any' not in all_position:
                    filtering['diploma__list_positions__overlap'] = all_position
                proofs = proof_diploma.filter(**filtering).annotate(status=Case(
                    When(status_document_id__in=[2, 19], then=Value(0)),
                    When(status_document_id__in=[
                        magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT], then=Value(1)),
                    output_field=IntegerField(), default=Value(2)
                )).order_by('status', '-date_start')
                having = proofs.exists()
                if having is True and proofs.first().is_verification is True:
                    exists_doc.append(proofs.first().get_info_for_statement)
                    demand_exists_doc.append(proofs.first())
                    having = False
                    not_have_educ_doc = False
                elif having:
                    all_docs.append(proofs.first())
                    exists_doc.append(proofs.first().get_info_for_statement)
                    demand_exists_doc.append(proofs.first())
                else:
                    not_exists_doc.append({'document_descr': dependency.document_description,
                                           'standarts_text': dependency.standarts_text,
                                           'exists': having,
                                           'type_document': 'Кваліфікаційний документ моряка'})
                    demand_not_exists_doc.append(dependency)
                    not_have_educ_doc = False
                have_all_doc.append(having)

            elif dependency.type_document == 'Medical':
                all_position = [pos['position'] for pos in dependency.key_document]
                medicals = medical_certificate.filter(
                    position_id__in=all_position,
                    status_document_id__in=[2, 19, magic_numbers.VERIFICATION_STATUS,
                                            magic_numbers.STATUS_CREATED_BY_AGENT]
                ).annotate(status=Case(
                    When(status_document_id__in=[2, 19], then=Value(0)),
                    When(status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                                 magic_numbers.STATUS_CREATED_BY_AGENT], then=Value(1)),
                    output_field=IntegerField(), default=Value(2)
                )).order_by('status', '-date_start')
                having = medicals.exists()
                resp_dict = {'document_descr': dependency.document_description,
                             'standarts_text': dependency.standarts_text,
                             'exists': having, 'type_document': 'Медичне свідоцтво'}
                if having is True and medicals.first().is_verification is True:
                    exists_doc.append(medicals.first().get_info_for_statement)
                    demand_exists_doc.append(medicals.first())
                    number_doc = '     '
                    date_issued = '     '
                    having = False
                    not_have_educ_doc = False
                elif having:
                    all_docs.append(medicals.first())
                    number_doc = medicals.first().number
                    date_issued = medicals.first().date_start
                    exists_doc.append(medicals.first().get_info_for_statement)
                    if self.perform_check:
                        medicals_checked = medicals.filter(
                            ntz__is_red=True,
                            date_start_lt=self.statement_creation_date + relativedelta(year=3)
                        )
                        if medicals_checked.exists():
                            demand_exists_doc.append(medicals_checked.first())
                        else:
                            demand_not_exists_doc.append(dependency)
                    else:
                        demand_exists_doc.append(medicals.first())
                else:
                    number_doc = '     '
                    date_issued = '     '
                    not_exists_doc.append(resp_dict)
                    demand_not_exists_doc.append(dependency)
                    not_have_educ_doc = False
                if self.statement_qual is True:
                    resp_dict['number'] = number_doc
                    resp_dict['issued_date'] = date_issued
                    resp_dict['doc_name'] = 'Копія медичної довідки. '
                    statement_qual_doc.append(resp_dict)
                have_all_doc.append(having)

            elif dependency.type_document == 'NTZ':
                by_qual = False
                ntz = certificates

                ntz = ntz.filter(
                    course_training_id__in=dependency.key_document,
                    status_document_id__in=[2, magic_numbers.status_qual_doc_valid, 39]
                ).order_by('-date_start').exclude(date_start__isnull=True)

                having = ntz.exists()
                reason = ''
                # if set(sert.key_document).issubset([103, 242]):
                #     if having is True:
                #         with_date = ntz.filter(date_end__gte=year_end).exists()
                #     else:
                #         with_date = True
                #     if having is True and with_date is False:
                #         reason = 'У документа закінчеться дія'
                #         having = False
                #     elif having is True and with_date is True:
                #         reason = 'all good'
                #     else:
                #         reason = ' Документ відсутній'
                if having is False and dependency.key_document == [103, 242]:
                    qual = qual_doc.filter(
                        type_document_id=21,
                        status_document_id__in=[2, 19, magic_numbers.VERIFICATION_STATUS,
                                                magic_numbers.STATUS_CREATED_BY_AGENT]
                    ).annotate(status=Case(
                        When(status_document_id__in=[2, 19], then=Value(0)),
                        When(status_document_id__in=[
                            magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT
                        ], then=Value(1)),
                        output_field=IntegerField(), default=Value(2)
                    )).order_by('status', '-date_start')
                    having = qual.exists()
                    if having is True:
                        by_qual = True
                resp_dict = {'document_descr': dependency.document_description,
                             'standarts_text': dependency.standarts_text,
                             'exists': having, 'type_document': 'Свідоцтво НТЗ'}
                if having is True and by_qual is True and qual.first().is_verification is True:
                    exists_doc.append(qual.first().get_info_for_statement)
                    demand_exists_doc.append(qual.first())
                    having = False
                    number_doc = ''
                    date_issued = ''
                    result = ''
                    not_have_educ_doc = False
                elif having is True and by_qual is True:
                    exists_doc.append(qual.first().get_info_for_statement)
                    all_docs.append(qual.first())
                    demand_exists_doc.append(qual.first())
                    number_doc = ''
                    date_issued = ''
                    result = ''
                    not_have_educ_doc = False
                elif having is True:
                    exists_doc.append(ntz.first().get_info_for_statement)
                    number_doc = ntz.first().ntz_number
                    date_issued = ntz.first().date_start
                    all_docs.append(ntz.first())
                    if self.perform_check:
                        ntz_checked = ntz.filter(
                            ntz__is_red=True,
                            date_start_lt=self.statement_creation_date - relativedelta(year=3)
                        )
                        if ntz_checked.exists():
                            demand_exists_doc.append(ntz_checked.first())
                        else:
                            demand_not_exists_doc.append(dependency)
                    else:
                        demand_exists_doc.append(ntz.first())
                    try:
                        result = re.findall(r'[cсС]відоцтво "(.+)"', dependency.document_description)[0]
                    except IndexError:
                        result = ''
                else:
                    resp_dict['reason'] = reason
                    number_doc = ''
                    date_issued = ''
                    result = ''
                    not_exists_doc.append(resp_dict)
                    demand_not_exists_doc.append(dependency)
                    not_have_educ_doc = False

                if self.statement_qual is True:
                    resp_dict['number'] = number_doc
                    resp_dict['issued_date'] = date_issued
                    resp_dict['doc_name'] = result
                    statement_qual_doc.append(resp_dict)
                have_all_doc.append(having)

            elif dependency.type_document == 'Диплом про вищу освіту':
                is_having = []
                educ_docs = None
                if self.is_continue:
                    initial_qual_doc = qual_doc.filter(rank=position.rank_id).order_by('date_start').first()
                    excluding = {'date_end_educ__gte': initial_qual_doc.date_start} if initial_qual_doc else {}
                else:
                    excluding = {}
                if any('specialization' in key for key in dependency.key_document):
                    for key in dependency.key_document:
                        filtering = dict()
                        filtering = self.add_param_to_dict(key, filtering, 'priority', 'extent__priority__gte')
                        filtering = self.add_param_to_dict(key, filtering, 'speciality', 'speciality')
                        filtering['type_document_id'] = 1
                        filtering['status_document_id'] = 2
                        filtering = self.add_param_to_dict(key, filtering, 'specialization', 'specialization')
                        educ_docs = education.filter(**filtering).exclude(**excluding).order_by('-date_issue_document')
                        is_having.append(educ_docs.exists())
                        if any(is_having):
                            break
                else:
                    min_prior = min([int(key['priority']) for key in dependency.key_document])
                    all_speciality = [self.get_value_or_none(key, 'speciality') for key in dependency.key_document]
                    all_speciality = list(filter(None, all_speciality))
                    filtering = {'extent__priority__gte': min_prior, 'type_document_id': 1,
                                 'status_document_id__in': [2, magic_numbers.VERIFICATION_STATUS,
                                                            magic_numbers.STATUS_CREATED_BY_AGENT]}
                    if 'any' not in all_speciality:
                        filtering['speciality_id__in'] = all_speciality
                    resp_filtering = Q(**filtering)
                    all_other_specialization = [self.get_value_or_none(key, 'specializ_other') for key in
                                                dependency.key_document]
                    all_other_specialization = list(filter(None, all_other_specialization))
                    if all_other_specialization:
                        or_filtering = {'extent__priority__gte': min_prior, 'type_document_id': 1,
                                        'status_document_id__in': [2, magic_numbers.VERIFICATION_STATUS,
                                                                   magic_numbers.STATUS_CREATED_BY_AGENT],
                                        'specialization_id__in': all_other_specialization}
                        resp_filtering = (Q(**filtering) | Q(**or_filtering))
                    educ_docs = education.filter(
                        resp_filtering
                    ).exclude(
                        id__in=educ_exists
                    ).exclude(**excluding).order_by('-date_issue_document')
                    is_having.append(educ_docs.exists())
                educ_docs = educ_docs.annotate(status=Case(
                    When(status_document_id=2, then=Value(0)),
                    When(status_document_id__in=[
                        magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT], then=Value(1)),
                    output_field=IntegerField(), default=Value(2)
                )).order_by('status', '-date_issue_document')
                having = any(is_having)
                resp_dict = {'document_descr': dependency.document_description,
                             'standarts_text': dependency.standarts_text, 'exists': having,
                             'type_document': 'Документ про освіту',
                             }
                portflot_educ = []
                if having is True and position.rank_id in [24, 81, 82, 83] and self.is_continue:
                    portflot_educ = self.check_educ_portflot(educ_docs)
                if having is True and portflot_educ:
                    for educ in portflot_educ:
                        if educ.is_verification is True:
                            number_doc = ''
                            date_issued = ''
                            having = False
                        else:
                            number_doc = educ.number_document
                            date_issued = educ.date_issue_document
                            all_docs.append(educ)
                        exists_doc.append(educ.get_info_for_statement)
                        demand_exists_doc.append(educ)
                    not_have_educ_doc = False
                elif having is True and educ_docs.first().is_verification is True:
                    exists_doc.append(educ_docs.first().get_info_for_statement)
                    demand_exists_doc.append(educ_docs.first())
                    number_doc = ''
                    date_issued = ''
                    having = False
                    not_have_educ_doc = False
                elif having is True:
                    number_doc = educ_docs.first().number_document
                    date_issued = educ_docs.first().date_issue_document
                    exists_doc.append(educ_docs.first().get_info_for_statement)
                    all_docs.append(educ_docs.first())
                    demand_exists_doc.append(educ_docs.first())
                    not_have_educ_doc = False
                else:
                    number_doc = ''
                    date_issued = ''
                    not_exists_doc.append(resp_dict)
                    demand_not_exists_doc.append(dependency)
                if self.statement_qual is True:
                    resp_dict['number'] = number_doc
                    resp_dict['issued_date'] = date_issued
                    resp_dict['doc_name'] = 'Копія Учбового диплому  з додатком.'
                    statement_qual_doc.append(resp_dict)
                have_all_doc.append(having)

            elif dependency.type_document == 'Образование':
                is_having = []
                educ_docs = None
                for key in dependency.key_document:
                    filtering = {'status_document_id__in': [2, magic_numbers.VERIFICATION_STATUS,
                                                            magic_numbers.STATUS_CREATED_BY_AGENT],
                                 'type_document_id': key['type_doc_nz']}
                    if 'qualification' in key and key['qualification'] != 'any':
                        filtering['qualification_id'] = key['qualification']
                    elif 'speciality' in key and key['speciality'] != 'any':
                        filtering['speciality_id'] = key['speciality']
                    elif 'specializ_other' in key and key['specializ_other'] != 'any':
                        filtering['specialization_id'] = key['specializ_other']
                    educ_docs = education.filter(**filtering).annotate(status=Case(
                        When(status_document_id=2, then=Value(0)),
                        When(status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                                     magic_numbers.STATUS_CREATED_BY_AGENT], then=Value(1)),
                        output_field=IntegerField(), default=Value(2)
                    )).order_by('status', '-date_issue_document')
                    is_having.append(educ_docs.exists())
                    if any(is_having):
                        break
                having = any(is_having)
                resp_dict = {'document_descr': dependency.document_description,
                             'standarts_text': dependency.standarts_text, 'exists': having,
                             'type_document': 'Документ про освіту'}
                if having is True and educ_docs.first().is_verification is True:
                    exists_doc.append(educ_docs.first().get_info_for_statement)
                    demand_exists_doc.append(educ_docs.first())
                    having = False
                    number_doc = ''
                    date_issued = ''
                    not_have_educ_doc = False
                elif having is True:
                    all_docs.append(educ_docs.first())
                    number_doc = educ_docs.first().number_document
                    date_issued = educ_docs.first().date_issue_document
                    exists_doc.append(educ_docs.first().get_info_for_statement)
                    demand_exists_doc.append(educ_docs.first())
                else:
                    number_doc = ''
                    date_issued = ''
                    not_exists_doc.append(resp_dict)
                    demand_not_exists_doc.append(dependency)
                    not_have_educ_doc = False
                if self.statement_qual is True:
                    resp_dict['number'] = number_doc
                    resp_dict['issued_date'] = date_issued
                    resp_dict['doc_name'] = 'Копія Учбового диплому  з додатком.'
                    statement_qual_doc.append(resp_dict)
                have_all_doc.append(having)

            elif dependency.type_document == 'Свідоцтво про підвищення кваліфікації':
                all_qual = [pos['qualitification'] for pos in dependency.key_document]
                educ = education.filter(
                    qualification_id__in=all_qual, type_document_id=3,
                    status_document_id__in=[2, magic_numbers.VERIFICATION_STATUS,
                                            magic_numbers.STATUS_CREATED_BY_AGENT]).annotate(status=Case(
                    When(status_document_id=2, then=Value(0)),
                    When(status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                                 magic_numbers.STATUS_CREATED_BY_AGENT], then=Value(1)),
                    output_field=IntegerField(), default=Value(2)
                )).order_by('status', '-date_issue_document')
                having = educ.exists()
                if position.rank.type_rank_id == 21:
                    if having is True:
                        with_date = educ.filter(expired_date__gte=year_end).exists()
                    else:
                        with_date = False
                    if having is True and with_date is False:
                        reason = 'У документа закінчеться дія'
                        having = False
                    elif having is True and with_date is True:
                        reason = 'all good'
                    else:
                        reason = 'Документ відсутній'
                else:
                    reason = ''
                resp_dict = {'document_descr': dependency.document_description,
                             'standarts_text': dependency.standarts_text,
                             'exists': having, 'reason': reason, 'type_document': 'Документ про освіту'}
                if having is True and educ.first().is_verification is True:
                    exists_doc.append(educ.first().get_info_for_statement)
                    demand_exists_doc.append(educ.first())
                    having = False
                    number_doc = ''
                    date_issued = ''
                    not_have_educ_doc = False
                elif having is True:
                    number_doc = educ.first().number_document
                    date_issued = educ.first().date_issue_document
                    all_docs.append(educ.first())
                    exists_doc.append(educ.first().get_info_for_statement)
                    if self.perform_check:
                        educ_checked = educ.filter(
                            name_nz__is_red=True,
                            date_end_educ__lt=self.statement_creation_date - relativedelta(year=3)
                        )
                        if educ_checked.exists():
                            demand_exists_doc.append(educ_checked.first())
                        else:
                            demand_not_exists_doc.append(dependency)
                    else:
                        demand_exists_doc.append(educ.first())
                else:
                    number_doc = ''
                    date_issued = ''
                    not_exists_doc.append(resp_dict)
                    demand_not_exists_doc.append(dependency)
                    not_have_educ_doc = False
                if self.statement_qual is True:
                    resp_dict['number'] = number_doc
                    resp_dict['issued_date'] = date_issued
                    resp_dict['doc_name'] = 'Курси підвищення кваліфікації.'
                    statement_qual_doc.append(resp_dict)
                have_all_doc.append(having)

            elif dependency.type_document == 'Танкерист':
                competency = qual_doc.filter(
                    type_document_id__in=[49],
                    status_document_id__in=[
                        19, magic_numbers.VERIFICATION_STATUS,
                        magic_numbers.STATUS_CREATED_BY_AGENT]
                ).annotate(
                    status=Case(
                        When(status_document_id=2, then=Value(0)),
                        When(status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                                     magic_numbers.STATUS_CREATED_BY_AGENT],
                             then=Value(1)),
                        output_field=IntegerField(), default=Value(2)
                    )
                ).order_by('status', 'rank__priority', '-date_start').exclude(rank_id__in=[98, 99])
                proficiency = qual_doc.filter(
                    type_document_id__in=[87, 3, 4],
                    status_document_id__in=[19, magic_numbers.VERIFICATION_STATUS,
                                            magic_numbers.STATUS_CREATED_BY_AGENT]
                ).annotate(
                    status=Case(
                        When(status_document_id=2, then=Value(0)),
                        When(status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                                     magic_numbers.STATUS_CREATED_BY_AGENT],
                             then=Value(1)),
                        output_field=IntegerField(), default=Value(2)
                    )
                ).order_by('status', 'rank__priority', '-date_start')
                proficiency_check = proficiency.exists()
                competency_check = competency.exists()
                if competency_check is True:
                    reason = 'all_good'
                    if competency.filter(date_end=None).exists():
                        competency_check = True
                    else:
                        competency_check = competency.filter(date_end__gte=year_end).exists()
                    resp_dict = {'document_descr': dependency.document_description,
                                 'standarts_text': dependency.standarts_text,
                                 'exists': competency_check, 'reason': reason,
                                 'type_document': 'Кваліфікаційний документ моряка'}
                    if competency_check is True and competency.first().is_verification is True:
                        number_doc = ' '
                        date_issued = ' '
                        exists_doc.append(competency.first().get_info_for_statement)
                        demand_exists_doc.append(competency.first())
                        competency_check = False
                        not_have_educ_doc = False
                    elif competency_check is True:
                        number_doc = competency.first().get_number
                        date_issued = competency.first().date_start
                        exists_doc.append(competency.first().get_info_for_statement)
                        all_docs.append(competency.first())
                        demand_exists_doc.append(competency.first())
                    else:
                        number_doc = ' '
                        date_issued = ' '
                        not_exists_doc.append(resp_dict)
                        demand_not_exists_doc.append(dependency)
                        not_have_educ_doc = False
                    if self.statement_qual is True:
                        resp_dict['number'] = number_doc
                        resp_dict['issued_date'] = date_issued
                        resp_dict['doc_name'] = 'Оригінали і копії робочого диплому та підтвердження до нього.'
                        statement_qual_doc.append(resp_dict)
                    have_all_doc.append(competency_check)
                    if not self.statement_qual:
                        apply_competency = proof_diploma.filter(
                            diploma_id__in=competency,
                            status_document_id__in=[2, 19, magic_numbers.VERIFICATION_STATUS, 7,
                                                    magic_numbers.STATUS_CREATED_BY_AGENT]
                        ).annotate(
                            status=Case(
                                When(status_document_id=2, then=Value(0)),
                                When(status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                                             magic_numbers.STATUS_CREATED_BY_AGENT],
                                     then=Value(1)),
                                output_field=IntegerField(), default=Value(2))
                        ).order_by('status', 'diploma__rank__priority')
                        apply_competency_check = apply_competency.exists()
                        if apply_competency_check:
                            exists_doc.append(apply_competency.first().get_info_for_statement)
                            all_docs.append(apply_competency.first())
                            demand_exists_doc.append(apply_competency.first())
                        else:
                            resp_dict = {'document_descr': 'Підтвердження (Endorsement) до диплома',
                                         'standarts_text': dependency.standarts_text,
                                         'exists': False,
                                         'type_document': 'Кваліфікаційний документ моряка'}
                            not_exists_doc.append(resp_dict)
                            demand_not_exists_doc.append(DependencyDocuments.objects.get(for_what='demand'))
                        have_all_doc.append(apply_competency_check)
                elif proficiency_check is True and proficiency.first().is_verification is True:
                    exists_doc.append(proficiency.first().get_info_for_statement)
                    demand_exists_doc.append(proficiency.first())
                    not_have_educ_doc = False
                elif proficiency_check is True:
                    demand_exists_doc.append(proficiency.first())
                    number_doc = proficiency.first().get_number
                    date_issued = proficiency.first().date_start
                    all_docs.append(proficiency.first())
                    exists_doc.append(proficiency.first().get_info_for_statement)
                    reason = 'all good'
                    resp_dict = {'document_descr': dependency.document_description,
                                 'standarts_text': dependency.standarts_text,
                                 'exists': proficiency_check, 'reason': reason,
                                 'type_document': 'Кваліфікаційний документ моряка'}
                    if self.statement_qual is True:
                        resp_dict['number'] = number_doc
                        resp_dict['issued_date'] = date_issued
                        resp_dict['doc_name'] = 'Оригінали і копії робочого диплому та підтвердження до нього.'
                        statement_qual_doc.append(resp_dict)
                    have_all_doc.append(proficiency_check)
                else:
                    resp_dict = {'document_descr': dependency.document_description,
                                 'standarts_text': dependency.standarts_text,
                                 'exists': False, 'reason': '',
                                 'type_document': 'Кваліфікаційний документ моряка'}
                    not_exists_doc.append(resp_dict)
                    demand_not_exists_doc.append(dependency)
                    not_have_educ_doc = False
        _resp = {'have_all_doc': all(have_all_doc), 'descr': not_exists_doc, 'exists_doc': exists_doc,
                 'not_have_educ_doc': not_have_educ_doc}
        if self.statement_qual is True:
            _resp['statement_qual'] = statement_qual_doc
        if all(have_all_doc):
            try:
                citizen_passport = Passport.objects.filter(id__in=sailor_key.citizen_passport).latest('date')
                all_docs.append(citizen_passport)
            except (Passport.DoesNotExist, TypeError):
                pass
            try:
                sailor_passport = SailorPassport.objects.filter(id__in=sailor_key.sailor_passport).latest('date_start')
                all_docs.append(sailor_passport)
            except (SailorPassport.DoesNotExist, TypeError):
                pass
            try:
                service_record = ServiceRecord.objects.filter(
                    id__in=sailor_key.service_records,
                    status_document_id=2
                ).latest('date_issued')
                all_docs.append(service_record)
            except (ServiceRecord.DoesNotExist, TypeError):
                pass
            _resp.update({'all_docs': all_docs})
        if self.demand_position:
            _resp.update({'all_docs': demand_exists_doc, 'not_exists_docs': demand_not_exists_doc})
        # cache.set(f'check_{sailor_key.pk}_{count_doc}_{self.list_position}_{self.is_continue}', _resp, 60 * 15)
        return _resp

    @staticmethod
    def check_educ_portflot(educ_docs):
        portflot_educ = []
        portflot_filter_1 = educ_docs.filter(
            (Q(speciality__name_ukr__icontains='судновод')
             &
             (Q(speciality__name_ukr__icontains='механ') |
              Q(speciality__name_ukr__icontains='енергет') |
              Q(speciality__name_ukr__icontains='ДВЗ') |
              Q(speciality__name_ukr__icontains='ССУ') |
              Q(speciality__name_ukr__icontains='СЕУ')))
            |
            (Q(qualification__name_ukr__icontains='судновод')
             &
             (Q(qualification__name_ukr__icontains='механ') |
              Q(qualification__name_ukr__icontains='енергет') |
              Q(qualification__name_ukr__icontains='ДВЗ') |
              Q(qualification__name_ukr__icontains='ССУ') |
              Q(qualification__name_ukr__icontains='СЕУ')))
        )
        portflot_filter_2 = educ_docs.filter(
            Q(speciality__name_ukr__icontains='судновод') | Q(qualification__name_ukr__icontains='судновод'))
        portflot_filter_3 = educ_docs.filter(
            (Q(speciality__name_ukr__icontains='механ') | Q(speciality__name_ukr__icontains='енергет'))
            |
            (Q(qualification__name_ukr__icontains='механ') | Q(qualification__name_ukr__icontains='енергет')))
        if portflot_filter_1.exists():
            portflot_educ.append(portflot_filter_1.first())
        elif portflot_filter_2.exists() and portflot_filter_3.exists():
            portflot_educ.append(portflot_filter_2.first())
            portflot_educ.append(portflot_filter_3.first())
        elif portflot_filter_2.exists():
            portflot_educ.append(portflot_filter_2.first())
        elif portflot_filter_3.exists():
            portflot_educ.append(portflot_filter_3.first())
        return portflot_educ

    def check_documents_many_pos(self):
        _resp = self.get_docs_with_status()
        if _resp.get('all_docs'):
            _resp.pop('all_docs')
        return _resp

    def check_list_position_and_student_id(self, sailor_key: SailorKeys):
        """
        Checks if the seafarer has a valid student ID and is going to the following list positions:
        - GMDSS general operator (self.list_position = [123])
        """
        valid_student_ID = StudentID.objects.filter(id__in=sailor_key.students_id,
                                                    status_document_id=magic_numbers.status_student_id_valid,
                                                    date_end__gte=date.today())
        if valid_student_ID.exists() and self.list_position == [123]:
            return True
        return False

    def get_education_for_qual(self):
        key = SailorKeys.objects.get(id=self.sailor)
        if key.education is None:
            key.education = []
        education = Education.objects.filter(id__in=key.education)
        sertification_by_position = DependencyDocuments.objects.filter(
            position_id__in=self.list_position, type_document__in=['Образование', 'Диплом про вищу освіту']). \
            order_by('type_document', 'key_document').distinct('type_document', 'key_document')
        if bool(self.is_continue) is False:
            sertification_by_position = sertification_by_position.filter(Q(for_what='start') | Q(for_what='both'))
        else:
            sertification_by_position = sertification_by_position.filter(
                Q(for_what='continue') | Q(for_what='both'))
        for sert in sertification_by_position:
            if sert.type_document == 'Диплом про вищу освіту':
                educ_qs = Education.objects.none()
                is_having = []
                if any('specialization' in key for key in sert.key_document):
                    for key in sert.key_document:
                        filtering = dict()
                        filtering = self.add_param_to_dict(key, filtering, 'priority', 'extent__priority__gte')
                        filtering = self.add_param_to_dict(key, filtering, 'speciality', 'speciality')
                        filtering['type_document_id'] = 1
                        filtering['status_document_id'] = 2
                        filtering = self.add_param_to_dict(key, filtering, 'specialization', 'specialization')
                        educ_qs = education.filter(**filtering).order_by('-date_issue_document')
                        if educ_qs.exists():
                            break
                else:
                    min_prior = min([key['priority'] for key in sert.key_document])
                    all_speciality = [self.get_value_or_none(key, 'speciality') for key in sert.key_document]
                    all_speciality = list(filter(None, all_speciality))
                    filtering = {'extent__priority__gte': min_prior,
                                 'type_document_id': 1, 'status_document_id': 2}
                    if 'any' not in all_speciality:
                        filtering['speciality_id__in'] = all_speciality
                    resp_filtering = Q(**filtering)
                    all_other_specialization = [self.get_value_or_none(key, 'specializ_other') for key in
                                                sert.key_document]
                    if all_other_specialization:
                        all_other_specialization = list(filter(None, all_other_specialization))
                        or_filtering = {'extent__priority__gte': min_prior, 'type_document_id': 1,
                                        'status_document_id': 2, 'specialization': all_other_specialization}
                        resp_filtering = (Q(**filtering) | Q(**or_filtering))
                    educ_qs = education.filter(**resp_filtering).order_by('-date_issue_document')
                try:
                    text_educ_ukr = '{}, {}, {}'.format(educ_qs.first().name_nz.name_abbr,
                                                        educ_qs.first().date_end_educ.year,
                                                        educ_qs.first().qualification.name_ukr)
                    text_educ_eng = '{}, {}, {}'.format(educ_qs.first().name_nz.name_eng,
                                                        educ_qs.first().date_end_educ.year,
                                                        educ_qs.first().qualification.name_eng)
                except AttributeError:
                    text_educ_ukr = ''
                    text_educ_eng = ''
                return {'ukr': text_educ_ukr, 'eng': text_educ_eng}
            elif sert.type_document == 'Образование':
                is_having = []
                for key in sert.key_document:
                    if 'qualification' in key:
                        if key['qualification'] != 'any':
                            educ_qs = education.filter(qualification=key['qualification'],
                                                       type_document_id=key['type_doc_nz'],
                                                       status_document_id=2).order_by('-date_issue_document')
                            is_having.append(educ_qs.exists())

                        else:
                            educ_qs = education.filter(type_document_id=key['type_doc_nz'],
                                                       status_document_id=2).order_by('-date_issue_document')
                            is_having.append(educ_qs.exists())
                    else:
                        if key['speciality'] == 'any':
                            educ_qs = education.filter(type_document_id=key['type_doc_nz'],
                                                       status_document_id=2)
                            is_having.append(educ_qs.exists())
                        else:
                            is_having.append(education.filter(type_document_id=key['type_doc_nz'],
                                                              status_document_id=2,
                                                              speciality_id=key['speciality']).exists())
                    if any(is_having):
                        break
                try:
                    text_educ_ukr = '{}, {}, {}'.format(educ_qs.first().name_nz.name_abbr,
                                                        educ_qs.first().date_end_educ.year,
                                                        educ_qs.first().qualification.name_ukr)
                    text_educ_eng = '{}, {}, {}'.format(educ_qs.first().name_nz.name_eng,
                                                        educ_qs.first().date_end_educ.year,
                                                        educ_qs.first().qualification.name_eng)
                except AttributeError:
                    text_educ_ukr = ''
                    text_educ_eng = ''
                return {'ukr': text_educ_ukr, 'eng': text_educ_eng}


class CheckSailorExperience:
    """
    Проверка стажа
    """

    def __init__(self, sailor, position=None, list_position=None):
        self.sailor = sailor
        self.position = position
        self.list_position = list_position
        if self.position and not self.list_position:
            self.list_position = [self.position]

    def check_experience_many_pos(self, is_verification=False):
        key = SailorKeys.objects.get(id=self.sailor)
        if key.qualification_documents is None:
            key.qualification_documents = []
        if key.experience_docs is None:
            key.experience_docs = []
        if key.service_records is None:
            key.service_records = []
        service_record = list(
            ServiceRecord.objects.filter(id__in=key.service_records).values_list('id', flat=True))
        experince = ExperinceForDKK.objects.filter(
            position_id__in=self.list_position).select_related()  # опыт который нужен моряку на это звание
        if not experince:
            return [{"value": True}]
        response = []
        if is_verification:
            all_line_in_service_record = LineInServiceRecord.objects.filter(
                (Q(id__in=key.experience_docs) | Q(service_record__in=service_record))
                &
                Q(status_line_id__in=[9, magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT]))
        else:
            all_line_in_service_record = LineInServiceRecord.objects.filter(
                (Q(id__in=key.experience_docs) | Q(service_record__in=service_record)) & Q(status_line_id=9))
        for need_exp in experince:
            my_total_exp = []
            one_exp_response = []
            must_be_total_month_for_exp = [int(need_exp.month_required)]

            ids_used_line_in_service_record = []
            ids_used_responsibility_lines = []

            for one_exp in sorted(need_exp.experince_value, key=lambda exp: (exp['required'], -len(exp['month'])),
                                  reverse=True):
                line_in_service_record = all_line_in_service_record.exclude(id__in=ids_used_line_in_service_record)
                if one_exp['type_vessel'] != 'any':
                    if one_exp['type_vessel'] == 'MM':
                        line_in_service_record = line_in_service_record.filter(Q(gross_capacity__lte=80) | Q(
                            propulsion_power__lte=55))
                    elif one_exp['type_vessel'] == 'MT':
                        line_in_service_record = line_in_service_record.filter((Q(gross_capacity__gte=80) | Q(
                            propulsion_power__gte=55)) & (Q(gross_capacity__lte=500) | Q(propulsion_power__kte=750)))
                    elif one_exp['type_vessel'] == 'S':
                        line_in_service_record = line_in_service_record.filter(propulsion_power__isnull=False)
                    elif type(one_exp['type_vessel']) is list:
                        line_in_service_record = line_in_service_record.filter(
                            type_vessel_id__in=one_exp['type_vessel'])
                # if one_exp['function'] != 'any':
                #     line_in_service_record = line_in_service_record.filter(responsibility__overlap=one_exp['function'])

                if one_exp['position'] != 'any':
                    line_in_service_record = line_in_service_record.filter(position_id__in=one_exp['position'])

                if one_exp['practical_book'] != 'any':
                    line_in_service_record = line_in_service_record.filter(
                        book_registration_practical=one_exp['practical_book'])

                if one_exp['gross_capacity'] != 'any':
                    try:
                        line_in_service_record = line_in_service_record.filter(
                            gross_capacity__gte=float(one_exp['gross_capacity'][0]))
                    except (SyntaxError, ValueError):
                        if one_exp['gross_capacity'][:1] == '>':
                            line_in_service_record = line_in_service_record.filter(
                                gross_capacity__gte=float(one_exp['gross_capacity'][1:]))
                        elif one_exp['gross_capacity'][:1] == '<':
                            line_in_service_record = line_in_service_record.filter(
                                gross_capacity__lte=float(one_exp['gross_capacity'][1:]))

                if one_exp['propulsion_power'] != 'any':
                    try:
                        line_in_service_record = line_in_service_record.filter(
                            propulsion_power__gte=float(one_exp['propulsion_power'][0]))
                        try:
                            line_in_service_record = line_in_service_record.filter(
                                propulsion_power__lt=float(one_exp['propulsion_power'][1]))
                        except (SyntaxError, ValueError, IndexError):
                            pass
                    except (SyntaxError, ValueError):
                        if ';' in one_exp['propulsion_power']:
                            prop_power = one_exp['propulsion_power'].split(';')
                            for prop in prop_power:
                                if one_exp['propulsion_power'][:1] == '>':
                                    line_in_service_record = line_in_service_record.filter(
                                        propulsion_power__gte=float(prop[1:]))
                                elif one_exp['propulsion_power'][:1] == '<':
                                    line_in_service_record = line_in_service_record.filter(
                                        propulsion_power__lte=float(prop[1:]))
                        elif one_exp['propulsion_power'][:1] == '>':
                            line_in_service_record = line_in_service_record.filter(
                                propulsion_power__gte=float(one_exp['propulsion_power'][1:]))
                        elif one_exp['propulsion_power'][:1] == '<':
                            line_in_service_record = line_in_service_record.filter(
                                propulsion_power__lte=float(one_exp['propulsion_power'][1:]))

                if one_exp['mode_of_navigation'] != 'any':
                    line_in_service_record = line_in_service_record.filter(
                        mode_of_navigation_id__in=one_exp['mode_of_navigation'])

                if one_exp['levelRefrigerPlant'] != 'any':
                    line_in_service_record = \
                        line_in_service_record.filter(levelRefrigerPlant__in=one_exp['levelRefrigerPlant'])

                try:
                    is_gmzlb = one_exp['is_gmzlb']
                    if is_gmzlb is True:
                        line_in_service_record = line_in_service_record.filter(equipment_gmzlb=True)
                except KeyError:
                    pass

                if one_exp.get('electrical_power') and one_exp.get('electrical_power') != 'any':
                    try:
                        line_in_service_record = line_in_service_record.filter(
                            electrical_power__gte=float(one_exp.get('electrical_power')[0]))
                    except (SyntaxError, ValueError):
                        electrical_power = one_exp['electrical_power']
                        if electrical_power[:1] == '>':
                            line_in_service_record = line_in_service_record.filter(
                                electrical_power__gte=float(electrical_power[1:]))
                        elif electrical_power[:1] == '<':
                            line_in_service_record = line_in_service_record.filter(
                                electrical_power__lte=float(electrical_power[1:]))
                    except KeyError:
                        pass

                if one_exp.get('refrigerating_power') and one_exp.get('refrigerating_power') != 'any':
                    try:
                        line_in_service_record = line_in_service_record.filter(refrigerating_power__gte=float(
                            one_exp.get('refrigerating_power')[0]))
                    except (SyntaxError, ValueError):
                        refrigerating_power = one_exp['refrigerating_power']
                        if refrigerating_power[:1] == '>':
                            line_in_service_record = line_in_service_record.filter(refrigerating_power__gte=float(
                                refrigerating_power[1:]))
                        elif refrigerating_power[:1] == '<':
                            line_in_service_record = line_in_service_record.filter(refrigerating_power__lte=float(
                                refrigerating_power[1:]))
                    except KeyError:
                        pass

                if one_exp.get('function_work_book') and one_exp.get('function_work_book') != 'any':
                    line_in_service_record = line_in_service_record.filter(
                        responsibility_work_book_id__in=one_exp.get('function_work_book'))
                    month_exp = self.get_experience(line_in_service_record)

                elif one_exp.get('function') and one_exp.get('function') != 'any':
                    lines_ids = list(line_in_service_record.values_list('id', flat=True))
                    if one_exp.get('repair'):
                        responsibility_lines = ResponsibilityServiceRecord.objects.filter(
                            service_record_line_id__in=lines_ids,
                            responsibility_id__in=one_exp.get('function'),
                            is_repaired=True).exclude(id__in=ids_used_responsibility_lines)

                    elif len(one_exp['function']) == 2:
                        # для двух обязанностей моряка одновременно
                        date_from = []
                        date_to = []
                        temp = ResponsibilityServiceRecord.objects.filter(
                            service_record_line_id__in=lines_ids,
                            responsibility_id=one_exp.get('function')[0],
                            is_repaired=False).exclude(id__in=ids_used_responsibility_lines)
                        for x in temp:
                            date_from.append(x.date_from)
                            date_to.append(x.date_to)
                        responsibility_lines = ResponsibilityServiceRecord.objects.filter(
                            service_record_line_id__in=lines_ids,
                            responsibility_id=one_exp.get('function')[1],
                            is_repaired=False, date_from__in=date_from, date_to__in=date_to
                        ).exclude(id__in=ids_used_responsibility_lines)
                        responsibility_lines.values_list('date_from', flat=True)
                        if responsibility_lines.exists():
                            ids_used_responsibility_lines += list(temp.filter(date_from__in=list(
                                responsibility_lines.values_list('date_from', flat=True))).values_list('id', flat=True))
                            ids_used_responsibility_lines += list(responsibility_lines.values_list('id', flat=True))
                    else:
                        responsibility_lines = ResponsibilityServiceRecord.objects.filter(
                            service_record_line_id__in=lines_ids,
                            responsibility_id__in=one_exp.get('function'),
                            is_repaired=False).exclude(id__in=ids_used_responsibility_lines)
                    if responsibility_lines.exists():
                        ids_used_responsibility_lines += list(responsibility_lines.values_list('id', flat=True))
                        for resp in responsibility_lines:
                            if resp.date_from:
                                responsibility_date_match = ResponsibilityServiceRecord.objects.exclude(
                                    id=resp.id).filter(
                                    service_record_line=resp.service_record_line,
                                    date_from=resp.date_from,
                                    date_to=resp.date_to
                                )
                            else:
                                responsibility_date_match = ResponsibilityServiceRecord.objects.exclude(
                                    id=resp.id).filter(
                                    service_record_line=resp.service_record_line,
                                    days_work=resp.days_work,
                                    responsibility__isnull=False,
                                )
                            if responsibility_date_match.exists():
                                ids_used_responsibility_lines += list(responsibility_date_match.values_list('id',
                                                                                                            flat=True))
                    month_exp = self.get_experience(responsibility_lines)
                else:
                    lines_ids = list(line_in_service_record.values_list('id', flat=True))
                    responsibility_lines = ResponsibilityServiceRecord.objects.filter(
                        service_record_line_id__in=lines_ids, is_repaired=False)
                    responsibility_lines_ids = list(responsibility_lines.values_list('service_record_line_id',
                                                                                     flat=True))
                    # responsibility_lines = responsibility_lines.filter(responsibility__isnull=True)
                    month_cruise_exp = [0, 0]  # [месяцы и дни] из записей в ResponsibilityServiceRecord
                    if responsibility_lines.exists():
                        responsibility_lines = responsibility_lines.exclude(id__in=ids_used_responsibility_lines)
                        ids_used_responsibility_lines += list(responsibility_lines.values_list('id', flat=True))
                        # из записей в ResponsibilityServiceRecord
                        month_cruise_exp = self.get_experience(responsibility_lines)
                    line_in_service_record = line_in_service_record.exclude(id__in=responsibility_lines_ids)
                    month_line_exp = self.get_experience(line_in_service_record)  # из записей в LineInServiceRecord
                    ids_used_line_in_service_record += list(line_in_service_record.values_list('id', flat=True))
                    month_exp = list(map(sum, zip(month_cruise_exp, month_line_exp)))

                try:
                    month_exp_required = one_exp.get('month', (None, None))

                    if len(month_exp_required) > 1:
                        if month_exp[0] > month_exp_required[1]:
                            month_exp[0] = month_exp_required[1]
                            month_exp[1] = 0
                            my_total_exp.append(month_exp)
                        elif month_exp[0] >= month_exp_required[0]:
                            my_total_exp.append(month_exp)
                    elif month_exp_required[0]:
                        # if month_exp[0] < month_exp_required[0]:
                        #     one_exp_response.append({'value': False, 'required': one_exp['required'], 'month_exp': month_exp})
                        # break
                        my_total_exp.append(month_exp)
                except (SyntaxError, ValueError, TypeError):
                    # TODO: need to be deleted in a future releases
                    if one_exp['month'][:1] == '<':
                        if month_exp[0] > int(one_exp['month'][1:]):
                            month_exp[0] = int(one_exp['month'][1:])
                        my_total_exp.append(int(month_exp[0]))
                    elif one_exp['month'][:1] == '>':
                        if month_exp[0] < int(one_exp['month'][1:]):
                            one_exp_response.append({'value': False, 'required': one_exp['required']})
                            break
                        my_total_exp.append(int(month_exp[0]))

                if sum([x[0] for x in my_total_exp]) >= max(month_exp_required):
                    try:
                        one_exp_response.append({'value': True, 'required': one_exp['required'],
                                                 'month_exp': month_exp[0], 'days_exp': month_exp[1],
                                                 'need_month': one_exp['month'], 'column': one_exp['column']})
                    except KeyError:
                        one_exp_response.append({'value': True, 'required': one_exp['required'],
                                                 'month_exp': month_exp[0], 'days_exp': month_exp[1],
                                                 'need_month': one_exp['month']})
                else:
                    try:
                        one_exp_response.append({'value': False, 'required': one_exp['required'],
                                                 'month_exp': month_exp[0], 'days_exp': month_exp[1],
                                                 'need_month': one_exp['month'], 'column': one_exp['column']})
                    except KeyError:
                        one_exp_response.append({'value': False, 'required': one_exp['required'],
                                                 'month_exp': month_exp[0], 'days_exp': month_exp[1],
                                                 'need_month': one_exp['month']})

            # sum_not_required_in_line = sum([exp['month_exp'] for exp in one_exp_response if exp['required'] is False])
            # sum_required_in_line = sum([exp['month_exp'] for exp in one_exp_response if exp['required'] is True])

            if need_exp.position_id == 84:
                month_calculate = self.calculate_experience_second_mechanic(one_exp_response, need_exp.month_required)
            elif need_exp.position_id == 87:
                month_calculate = self.calculate_experience_third_mechanic(one_exp_response, need_exp.month_required)
            elif need_exp.position_id == 96:
                month_calculate = self.calculate_experience_third_electromechanic(one_exp_response,
                                                                                  need_exp.month_required)
            elif need_exp.position_id == 99:
                month_calculate = self.calculate_experience_third_refrigerator(one_exp_response,
                                                                               need_exp.month_required)
            elif need_exp.position_id == 201:
                month_calculate = self.calculate_experience_electric_first_class(one_exp_response,
                                                                                 need_exp.month_required)
            elif need_exp.position_id in [81, 221]:
                month_calculate = self.calculate_experience_third_deck_and_engineer_officer(
                    one_exp_response, need_exp.month_required, key.qualification_documents)
            elif need_exp.position_id == 90:
                month_calculate = self.calculate_experience_mechanic_light_duty_vehicles(one_exp_response,
                                                                                         need_exp.month_required)
            else:
                month_calculate = self.calculate_experience_not_more(one_exp_response)
            sum_not_required_in_line = month_calculate['sum_not_required_in_line']
            sum_required_in_line = month_calculate['sum_required_in_line']
            month_required_table = sum(
                [max(exp['month']) for exp in need_exp.experince_value if exp['required'] is True])
            # days_left = sum([exp['days_exp'] for exp in one_exp_response])

            if sum_required_in_line > need_exp.month_required:
                sum_required_in_line = need_exp.month_required
            if sum_required_in_line > month_required_table:
                month_required_table = sum_required_in_line

            convert_rest_days = self.convert_days_to_month(month_calculate['sum_work_days'])
            need_not_required = need_exp.month_required - month_required_table
            if sum_not_required_in_line >= need_not_required:
                sum_not_required_in_line = need_not_required
                convert_rest_days = self.convert_days_to_month(month_calculate.get('sum_required_days', 0))

            sailor_month = sum_not_required_in_line + sum_required_in_line + convert_rest_days['month']
            sailor_days = convert_rest_days['days']
            if sailor_days != 0:
                days_left = 30 - convert_rest_days['days']
                month_left = sum(must_be_total_month_for_exp) - sailor_month - 1
            else:
                days_left = 0
                month_left = sum(must_be_total_month_for_exp) - sailor_month

            required_resp = [val['value'] for val in one_exp_response if val['required'] is True]
            if sum(must_be_total_month_for_exp) > sailor_month:
                value = False
            elif all(required_resp) is False:
                value = False
            elif all(required_resp) is True and sum(must_be_total_month_for_exp) < sailor_month:
                value = True
            else:
                value = True
            if need_exp.experince_descr:
                experience_descr = need_exp.experince_descr
            else:
                experience_descr = need_exp.position.experience_description
            response.append({'experience_descr': experience_descr,
                             'standarts_text': need_exp.position.standarts_text,
                             'value': value,
                             # 'moths_data': sum(must_be_total_month_for_exp) - sum(my_total_exp),
                             'sailor_month': sailor_month, 'sailor_days': sailor_days, 'days_left': days_left,
                             'month_left': month_left, 'must_be_exp': sum(must_be_total_month_for_exp),
                             'position': need_exp.position_id})
        true_resp = [v for v in response if v.get('value')]
        return true_resp or response

    def get_experience(self, all_work):
        """
        Подсчет количества месяцев и дней, соответствующих определенной колонке
        """
        if not all_work:
            return [0, 0]
        full_days_all_work = int()
        full_months_all_work = int()
        for line in all_work:
            try:
                date_to = line.date_end
                date_from = line.date_start
            except AttributeError:
                date_to = line.date_to
                date_from = line.date_from
            if date_to is None or date_from is None:
                full_days_all_work += line.days_work
            else:
                date_to += timedelta(days=1)
                inspect_date_from = self.get_date_from(date_from, date_to)
                date_from = inspect_date_from['date_from']
                full_days_all_work += inspect_date_from['days']
                remain_date = relativedelta(date_to, date_from)
                full_month = remain_date.months + (remain_date.years * 12)
                remain_days = remain_date.days
                full_days_all_work += remain_days
                full_months_all_work += full_month
            if line.__class__.__name__ == 'LineInServiceRecord' and line.is_repaired:
                if line.days_repair:
                    if line.days_repair >= 30:
                        credited_days = full_days_all_work - line.days_repair % 30
                        if credited_days < 0:
                            full_months_all_work = full_months_all_work - line.days_repair // 30 - 1
                            full_days_all_work = 30 + credited_days
                        else:
                            full_months_all_work = full_months_all_work - line.days_repair // 30
                            full_days_all_work = credited_days
                else:
                    repair_date_to = line.repair_date_to + timedelta(days=1)
                    remain_date_repair = relativedelta(repair_date_to, line.repair_date_from)
                    if remain_date_repair.years == 0 and \
                            (
                                    remain_date_repair.months == 0
                                    or
                                    (remain_date_repair.months == 1 and remain_date_repair.days == 0)
                            ):
                        continue
                    inspect_repair_date_from = self.get_date_from(line.repair_date_from, line.repair_date_to)
                    repair_date_from = inspect_repair_date_from['date_from']
                    full_days_all_work -= inspect_repair_date_from['days']
                    remain_date_repair = relativedelta(repair_date_to, repair_date_from)
                    credited_days = full_days_all_work - remain_date_repair.days
                    remain_months = remain_date_repair.years * 12 + remain_date_repair.months
                    if credited_days < 0:
                        full_months_all_work = full_months_all_work - remain_months - 1 + credited_days // 30
                        full_days_all_work = 30 + credited_days % 30
                    else:
                        full_months_all_work = full_months_all_work - remain_months + credited_days // 30
                        full_days_all_work = credited_days % 30
        if full_days_all_work >= 30:
            full_months_all_work += full_days_all_work // 30
            full_days_all_work = full_days_all_work % 30
        return [full_months_all_work, full_days_all_work]

    @staticmethod
    def get_date_from(date_from, date_to):
        """
        Если интервал времени начинается не с 1го числа, тогда высчитываем количество дней до 1го числа следующего
        месяца, чтобы подсчет полных месяцев был с 1го числа (требование заказчика)
        """
        days_start_new_month = 0
        if date_from.day != 1:
            next_month = date_from.month + 1
            year = date_from.year
            if next_month == 13:
                next_month = 1
                year += 1
            start_next_month = date(year, next_month, 1)
            if start_next_month >= date_to:
                return {'date_from': date_from, 'days': days_start_new_month}
            days_start_new_month = (start_next_month - date_from).days
            date_from = start_next_month
        return {'date_from': date_from, 'days': days_start_new_month}

    @staticmethod
    def convert_days_to_month(days):
        """
        Конвертирует дни в месяцы
        """
        month = 0
        days = days
        if days >= 30:
            month = days // 30
            days %= 30
        return {'month': month, 'days': days}

    def calculate_experience_not_more(self, one_exp_response):
        """
        Если в таблице experiencefordkk в поле experience_value у month имеет вид [x1, x2], то опыт не должен превышать
        значение x2
        """
        month_not_more = []
        days_not_more = []
        month_more = []
        days_more = []
        month_required = []
        days_required = []
        for exp in one_exp_response:
            if exp['required'] is False and len(exp['need_month']) == 2:
                month_not_more.append((max(exp['need_month']), exp['month_exp']))
                days_not_more.append(exp['days_exp'])
            elif exp['required'] is False:
                month_more.append(exp['month_exp'])
                days_more.append(exp['days_exp'])
            else:
                month_required.append(exp['month_exp'])
                days_required.append(exp['days_exp'])
        convert_not_more = self.convert_days_to_month(sum(days_not_more))
        convert_more = self.convert_days_to_month(sum(days_more))
        convert_required = self.convert_days_to_month(sum(days_required))
        sum_required_in_line = sum(month_required) + convert_required['month']
        sum_month_more = sum(month_more) + convert_more['month']
        sum_month_not_more = 0
        if month_not_more:
            max_month_not_more = sorted(month_not_more, key=lambda x: x[0], reverse=True)[0][0]
            sum_month_not_more = sum([month_work[1] for month_work in month_not_more]) + convert_not_more['month']
            if sum_month_not_more >= max_month_not_more:
                sum_month_not_more = max_month_not_more
                convert_not_more['days'] = 0
        sum_work_days = convert_not_more['days'] + convert_more['days'] + convert_required['days']
        return {'sum_not_required_in_line': sum_month_not_more + sum_month_more,
                'sum_required_in_line': sum_required_in_line, 'sum_work_days': sum_work_days,
                'sum_required_days': convert_required['days']}

    def calculate_experience_second_mechanic(self, one_exp_response, month_required):
        """
        Расчет стажа для Механік другого розряду (Другий механік суден з потужністю ГЕУ 3000 кВт і більше)
        """
        month_col_1 = sum([exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X1'])
        month_col_2 = sum([exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X2'])
        month_col_3 = sum([exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X3'])
        month_col_4 = sum([exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X4'])
        days_col_1 = sum([exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X1'])
        days_col_2 = sum([exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X2'])
        days_col_3 = sum([exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X3'])
        days_col_4 = sum([exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X4'])
        convert_col_2_col_4 = self.convert_days_to_month(days_col_2 + days_col_4)
        convert_col_3_col_4 = self.convert_days_to_month(days_col_3 + days_col_4)
        month_col_2_col_4 = month_col_2 + month_col_4 + convert_col_2_col_4['month']
        month_col_3_col_4 = month_col_3 + month_col_4 + convert_col_3_col_4['month']
        sum_days = days_col_1 + days_col_2 + days_col_3 + days_col_4
        convert_sum_days = self.convert_days_to_month(sum_days)
        sum_work_days = convert_sum_days['days']
        month_have = month_col_1 + month_col_2 + month_col_3 + month_col_4 + convert_sum_days['month']
        if month_col_1 >= 12:
            month_col_1 = 12
            days_col_1 = 0
        if month_col_2_col_4 >= 6 and month_col_3_col_4 >= 6:
            if month_have >= month_required:
                sum_work_days = 0
            response = {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0,
                        'sum_work_days': sum_work_days}
        elif month_col_2_col_4 >= 6 and month_col_3_col_4 < 6:
            need_work_month = 6 - month_col_3_col_4
            if (month_col_1 + month_col_2 + self.convert_days_to_month(days_col_1 + days_col_2)['month']) >= 12:
                response = {'sum_not_required_in_line': month_required - need_work_month, 'sum_required_in_line': 0,
                            'sum_work_days': convert_col_3_col_4['days']}
            else:
                if month_have >= month_required:
                    sum_work_days = 0
                response = {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0,
                            'sum_work_days': sum_work_days}
        elif month_col_2_col_4 < 6 and month_col_3_col_4 >= 6:
            need_work_month = 6 - month_col_2_col_4
            if (month_col_1 + month_col_3 + self.convert_days_to_month(days_col_1 + days_col_3)['month']) >= 12:
                response = {'sum_not_required_in_line': month_required - need_work_month, 'sum_required_in_line': 0,
                            'sum_work_days': convert_col_2_col_4['days']}
            else:
                if month_have >= month_required:
                    sum_work_days = 0
                response = {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0,
                            'sum_work_days': sum_work_days}
        else:
            temp_have_col_24 = float('{month}.{day}'.format(month=month_col_2_col_4,
                                                            day=str(convert_col_2_col_4['days']).rjust(2, '0')))
            temp_have_col_34 = float('{month}.{day}'.format(month=month_col_3_col_4,
                                                            day=str(convert_col_3_col_4['days']).rjust(2, '0')))
            if temp_have_col_24 > temp_have_col_34:
                if month_have > (month_required - 6):
                    temp_convert = self.convert_days_to_month(convert_col_3_col_4['days'] + days_col_1)
                    month_have = month_col_1 + month_col_3_col_4 + temp_convert['month']
                    sum_work_days = temp_convert['days']
            elif month_have > (month_required - 6):
                temp_convert = self.convert_days_to_month(convert_col_2_col_4['days'] + days_col_1)
                month_have = month_col_1 + month_col_2_col_4 + temp_convert['month']
                sum_work_days = temp_convert['days']
            response = {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0,
                        'sum_work_days': sum_work_days}
        return response

    def calculate_experience_third_mechanic(self, one_exp_response, month_required):
        """
        Расчет стажа для Механік третього розряду
        (Вахтовий механік суден з машинним відділенням, що обслуговується традиційно або періодично безвахтово)
        """
        if month_required == 12:
            month_col_1 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
            month_col_2 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
            month_col_3 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X3'][0]
            month_col_4 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X4'][0]
            month_col_5 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X5'][0]
            month_col_6 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X6'][0]
            month_col_7 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X7'][0]

            days_col_1 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
            days_col_2 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
            days_col_3 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X3'][0]
            days_col_4 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X4'][0]
            days_col_5 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X5'][0]
            days_col_6 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X6'][0]
            days_col_7 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X7'][0]

            convert_month_12356 = self.convert_days_to_month(
                days_col_1 + days_col_2 + days_col_3 + days_col_5 + days_col_6)
            month_col_12356 = month_col_1 + month_col_2 + month_col_3 + month_col_5 + month_col_6 + \
                              convert_month_12356['month']
            days_col_12356 = convert_month_12356['days']
            convert_month_123 = self.convert_days_to_month(days_col_1 + days_col_2 + days_col_3)
            month_col_123 = month_col_1 + month_col_2 + month_col_3 + convert_month_123['month']
            days_col_123 = convert_month_123['days']
            convert_month_67 = self.convert_days_to_month(days_col_6 + days_col_7)
            month_col_67 = month_col_6 + month_col_7 + convert_month_67['month']
            days_col_67 = convert_month_67['days']

            if month_col_123 > 6:
                month_col_123 = 6
                days_col_123 = 0

            convert_all_days = self.convert_days_to_month(days_col_123 + days_col_4 + days_col_5 + days_col_67)
            all_exp_month = month_col_123 + month_col_4 + month_col_5 + month_col_67 + convert_all_days['month']
            all_exp_days = convert_all_days['days']
            month_have = all_exp_month
            days_have = all_exp_days
            if (month_col_12356 > 0 or days_col_12356 > 0) and month_col_67 >= 6:
                return {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0, 'sum_work_days': days_have}
            elif month_col_12356 == 0 and days_col_12356 == 0 and month_col_67 >= 6 and all_exp_month >= month_required:
                month_have = month_required - 1
                days_have = 29
            elif all_exp_month >= month_required:
                month_have = (month_required - 6) + month_col_67
                days_have = days_col_67
        else:
            month_col_1 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
            month_col_2 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]

            days_col_1 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
            days_col_2 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]

            if month_col_1 >= 30:
                month_col_1 = 30
                days_col_1 = 0

            convert_all_days = self.convert_days_to_month(days_col_1 + days_col_2)
            month_have = month_col_1 + month_col_2 + convert_all_days['month']
            days_have = convert_all_days['days']

        return {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0, 'sum_work_days': days_have}

    def calculate_experience_third_electromechanic(self, one_exp_response, month_required):
        """
        Расчет стажа для Електромеханіка третього розряду (Електромеханік)
        """
        month_col_1 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
        month_col_2 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
        month_col_3 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X3'][0]
        month_col_4 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X4'][0]
        days_col_1 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
        days_col_2 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
        days_col_3 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X3'][0]
        days_col_4 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X4'][0]

        convert_col_14 = self.convert_days_to_month(days_col_1 + days_col_4)
        month_col_14 = month_col_1 + month_col_4 + convert_col_14['month']
        days_col_14 = convert_col_14['days']
        if month_col_14 >= 6:
            month_col_14 = 6
            days_col_14 = 0

        if month_required == 12:
            convert_col_1234 = self.convert_days_to_month(days_col_14 + days_col_2 + days_col_3)
            month_have = month_col_14 + month_col_2 + month_col_3 + convert_col_1234['month']
            all_exp_days = convert_col_1234['days']
            if month_col_14 == 0 and month_col_2 == 0 and days_col_14 == 0 and days_col_2 == 0:
                if month_have > month_required:
                    month_have = month_required - 1
                    all_exp_days = 29
        else:
            if month_col_3 >= 30:
                month_col_3 = 30
                days_col_3 = 0
            month_col_5 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X5'][0]
            days_col_5 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X5'][0]
            convert_col_12345 = self.convert_days_to_month(days_col_14 + days_col_2 + days_col_3 + days_col_5)
            month_have = month_col_14 + month_col_2 + month_col_3 + month_col_5 + convert_col_12345['month']
            all_exp_days = convert_col_12345['days']
        return {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0, 'sum_work_days': all_exp_days}

    def calculate_experience_third_refrigerator(self, one_exp_response, month_required):
        """
        Расчет стажа для Рефрижераторний механік третього класу (Рефрижераторний механік)
        """
        month_col_1 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
        month_col_2 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
        month_col_3 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X3'][0]
        month_col_4 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X4'][0]
        days_col_1 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
        days_col_2 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
        days_col_3 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X3'][0]
        days_col_4 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X4'][0]

        convert_days_12 = self.convert_days_to_month(days_col_1 + days_col_2)
        month_col_12 = month_col_1 + month_col_2 + convert_days_12['month']
        days_col_12 = convert_days_12['days']

        if month_col_12 >= 6:
            month_col_12 = 6
            days_col_12 = 0

        if month_col_4 < 2 and month_col_3 >= 4:
            month_col_3 = 4
            days_col_3 = 0

        convert_days_34 = self.convert_days_to_month(days_col_3 + days_col_4)
        month_col_34 = month_col_3 + month_col_4 + convert_days_34['month']
        days_col_34 = convert_days_34['days']

        if month_col_34 >= 6:
            month_col_34 = 6
            days_col_34 = 0

        convert_days_1234 = self.convert_days_to_month(days_col_12 + days_col_34)
        month_have = month_col_12 + month_col_34 + convert_days_1234['month']
        all_exp_days = convert_days_1234['days']

        response = {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0,
                    'sum_work_days': all_exp_days}
        return response

    def calculate_experience_electric_first_class(self, one_exp_response, month_required):
        """
        Расчет стажа для Електрик судновий першого класу (Електрик судновий)
        """
        month_col_1 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
        month_col_2 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
        days_col_1 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
        days_col_2 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]

        if (month_col_1 == 0 and days_col_1 < 31) or (month_col_1 == 1 and days_col_1 == 0):
            convert_days_12 = self.convert_days_to_month(days_col_1 + days_col_2)
            month_have = month_col_1 + month_col_2 + convert_days_12['month']
            all_exp_days = convert_days_12['days']
        else:
            month_have = month_col_2
            all_exp_days = days_col_2

        response = {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0,
                    'sum_work_days': all_exp_days}
        return response

    def calculate_experience_third_deck_and_engineer_officer(self, one_exp_response, month_required, qual_documents):
        """
        Расчет стажа для Судноводій-механік третього класу (Змінний помічник капітана-механіка або
        Вахтового помічника капітана з правом управління двигунами на суднах валовою місткістю до 5000
        одиниць у прибережному плаванні)
        """
        try:
            month_col_1 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
            month_col_2 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
            month_col_3 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X3'][0]
            days_col_1 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
            days_col_2 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
            days_col_3 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X3'][0]
        except IndexError:
            month_col_1 = month_col_2 = month_col_3 = 0
            days_col_1 = days_col_2 = days_col_3 = 0
        try:
            month_col_4 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X4'][0]
            days_col_4 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X4'][0]
        except IndexError:
            month_col_4 = 0
            days_col_4 = 0
        try:
            month_col_5 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X5'][0]
            days_col_5 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X5'][0]
        except IndexError:
            month_col_5 = 0
            days_col_5 = 0
        qual_doc = QualificationDocument.objects.filter(id__in=qual_documents)
        qual_doc_officer = qual_doc.filter(rank_id__in=[21, 22, 23, 61],
                                           status_document_id=magic_numbers.status_qual_doc_valid)
        qual_doc_mechanic = qual_doc.filter(rank_id__in=[84, 85, 86],
                                            status_document_id=magic_numbers.status_qual_doc_valid)
        if qual_doc_officer.exists() and month_required == 3:
            if qual_doc_mechanic.exists():
                return {'sum_not_required_in_line': month_required, 'sum_required_in_line': 0,
                        'sum_work_days': 0}
            response = {'sum_not_required_in_line': month_col_4, 'sum_required_in_line': 0,
                        'sum_work_days': days_col_4}
        elif qual_doc_mechanic.exists() and month_required == 6:
            if qual_doc_officer.exists():
                return {'sum_not_required_in_line': month_required, 'sum_required_in_line': 0,
                        'sum_work_days': 0}
            response = {'sum_not_required_in_line': month_col_5, 'sum_required_in_line': 0,
                        'sum_work_days': days_col_5}
        elif month_required == 12:
            if month_col_1 >= 6:
                month_col_1 = 6
                days_col_1 = 0
            convert_days_23 = self.convert_days_to_month(days_col_2 + days_col_3)
            month_col_23 = month_col_2 + month_col_3 + convert_days_23['month']
            days_col_23 = convert_days_23['days']
            if month_col_23 >= 6:
                month_col_23 = 6
                days_col_23 = 0
            convert_days_123 = self.convert_days_to_month(days_col_1 + days_col_23)
            month_have = month_col_1 + month_col_23 + convert_days_123['month']
            all_exp_days = convert_days_123['days']
            response = {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0,
                        'sum_work_days': all_exp_days}
        else:
            response = {'sum_not_required_in_line': 0, 'sum_required_in_line': 0,
                        'sum_work_days': 0}
        return response

    def calculate_experience_mechanic_light_duty_vehicles(self, one_exp_response, month_required):
        """
        Расчет стажа для Механік малотоннажного судна (Змінний механік)
        """
        month_col_1 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
        month_col_2 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
        month_col_3 = [exp['month_exp'] for exp in one_exp_response if exp['column'] == 'X3'][0]
        days_col_1 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X1'][0]
        days_col_2 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X2'][0]
        days_col_3 = [exp['days_exp'] for exp in one_exp_response if exp['column'] == 'X3'][0]

        if month_col_1 >= 6:
            month_col_1 = 6
            days_col_1 = 0

        convert_days_23 = self.convert_days_to_month(days_col_2 + days_col_3)
        month_col_23 = month_col_2 + month_col_3 + convert_days_23['month']
        days_col_23 = convert_days_23['days']
        if month_col_23 >= 6:
            month_col_23 = 6
            days_col_23 = 0

        convert_days_123 = self.convert_days_to_month(days_col_1 + days_col_23)
        month_have = month_col_1 + month_col_23 + convert_days_123['month']
        all_exp_days = convert_days_123['days']

        response = {'sum_not_required_in_line': month_have, 'sum_required_in_line': 0,
                    'sum_work_days': all_exp_days}
        return response


def get_date_or_none(_date):
    try:
        date_text = _date.strftime('%d.%m.%Y')
    except AttributeError:
        date_text = None
    return date_text


def generate_number_statement_dkk():
    excl = [654369, 654354, 654385, 654374, 654381, 654391, 654390, 654392, 654393, 654397, 654399, 654398, 654394,
            654396, 654395, 654400, 654404, 654406, 654426, 654403, 654407, 654428, 654427, 654434, 654438, 654439,
            654452, 654445, 654446, 654444, 654447, 654448, 654449, 654454, 654453, 654464, 654461, 654465, 654470,
            654489, 654498, 654486, 654496, 654501, 654499, 654502, 654505, 654506, 654504, 654507, 654518, 654520,
            654522, 654521, 654532, 654525, 654530, 654531, 654533, 654534, 654544, 654547, 654548, 654549, 654543,
            654535, 654550, 654536, 654537, 654538, 654539, 654540, 654541, 654542, 654551, 654554, 654555, 654556,
            654557, 654558, 654561, 654559, 654560, 654562, 654563, 654567, 654564, 654565, 654566, 654503, 654376,
            654450, 654455, 654529, 654476, 673592, 673591, 673594, 673593, 673595, 673603]

    number = \
        StatementSQC.objects.filter(created_at__year=date.today().year).exclude(
            status_document_id=16).exclude(id__in=excl).aggregate(number=Max('number'))['number'] + 1
    if not number:
        number = 1
    return number


def check_continue_sailor(rank_id=None, list_positions=None, position_in_qual_doc=None):
    """
    Только определенные звания
    :param rank_id:
    :param list_positions:
    :param position_in_qual_doc:
    :return:
    """
    if rank_id == 101 and ({323, 47, 142, 143, 321, 134, 327} & set(position_in_qual_doc)):
        # Свідоцтво кваліфікованого моряка (матрос першого класу) -> дкк на матроса першого класу
        return True
    # elif rank_id == 106 and 134 in list_positions and ({321, 134} & set(position_in_qual_doc)):
    #     # Свідоцтво кваліфікованого моряка (боцман) -> дкк на боцман
    #     return True
    elif rank_id == 121 and 145 in list_positions and ({50, 322, 145} & set(position_in_qual_doc)):
        # Свідоцтво кваліфікованого моряка (матрос другого класу) -> дпо на матроса другого класу
        return True
    elif rank_id == 102 and ({325, 48, 146, 148} & set(position_in_qual_doc)):
        # Свідоцтво кваліфікованого моториста (моторист першого класу) -> дкк на моториста першого класу
        return True
    elif rank_id == 161 and ({151} & set(position_in_qual_doc)):
        # Свідоцтво Судновий електрик 1-го класу -> дкк на Електрик судновий першого класу
        return True
    elif rank_id == 122 and ({147, 326} & set(position_in_qual_doc)):
        # Свідоцтво Донкерман -> дкк на Донкерман
        return True
    return False


def check_continue_for_experience(list_positions=None, rank_id=None, ids_positions_in_qual_doc=None):
    check_positions = []
    for position in list_positions:
        if position in ids_positions_in_qual_doc:
            continue
        elif rank_id == 23 and 63 in ids_positions_in_qual_doc and (position in [64, 65, 66, 67]):
            check_positions.append(position)
        elif rank_id == 22 and 21 in ids_positions_in_qual_doc and (position in [62]):
            check_positions.append(position)
        elif rank_id == 21 and 22 in ids_positions_in_qual_doc and (position in [2, 41]):
            check_positions.append(position)
        elif rank_id == 86 and 87 in ids_positions_in_qual_doc and (position in [88, 89]):
            check_positions.append(position)
        elif rank_id == 85 and (84 in ids_positions_in_qual_doc or 85 in ids_positions_in_qual_doc) and \
                (position in [86]):
            check_positions.append(position)
    if check_positions:
        return {'is_check_exp': True, 'list_positions': check_positions}
    else:
        return {'is_check_exp': False, 'list_positions': []}


def generate_number_for_protocol_dkk(direction_id, branch_id):
    number = \
        ProtocolSQC.objects.filter(date_meeting__year=date.today().year,
                                   statement_dkk__rank__direction_id=direction_id,
                                   branch_create_id=branch_id).aggregate(
            number=Max('number_document'))['number']
    if not number:
        number = 0
    number += 1
    return number


def get_qual_doc(sailor_qs):
    """
    Поиск квалификационных документов моряка
    """
    if not sailor_qs.qualification_documents:
        sailor_qs.qualification_documents = []
    qual_docs = QualificationDocument.objects.filter(
        (Q(id__in=sailor_qs.qualification_documents) &
         ((
                  Q(status_document_id=magic_numbers.status_qual_doc_valid) &
                  (
                          (Q(type_document_id__in=[3, 49, 1]) & Q(proofofworkdiploma__isnull=False)) |
                          (Q(type_document_id__in=[4, 5, 6, 57, 85, 86, 87, 88, 89, 21]))
                  )
          ) | (
                  Q(status_document_id__in=[magic_numbers.status_qual_doc_valid,
                                            magic_numbers.status_qual_doc_expired]) &
                  Q(type_document_id__in=[57, 85, 86, 88, 89])
          )
          ))
    ).exclude(rank_id=103)
    return qual_docs


def check_is_continue(sailor_qs, rank_id, list_positions):
    """
    Полная проверка на подтверждение
    Взято с заявки на дкк
    :returns 0 - new position, 1 - continue with old position, 2 - continue with new position
    """
    qual_docs = get_qual_doc(sailor_qs)
    flat_list_rank = list(qual_docs.values_list('rank_id', flat=True))
    flat_list_position = set(chain.from_iterable(qual_docs.values_list('list_positions', flat=True)))
    _check_other_ranks = check_continue_sailor(rank_id=rank_id, list_positions=list(list_positions),
                                               position_in_qual_doc=flat_list_position)
    if rank_id in flat_list_rank:
        if set(list_positions).difference(flat_list_position):
            return 2  # continue with new position
        else:
            return 1  # continue with old position
    elif _check_other_ranks:
        return 1
    else:
        return 0  # new position


def check_interval_date(all_function=None, date_start=None, date_end=None, days_repair=0, repair_date_from=None,
                        repair_date_to=None):
    """
    Стаж.
    Проверка интервалов времени для рейса при выполнении моряком разных обязанностей
    Возвращает интервалы, в которые моряк не выполнял никаких обязанностей
    """
    if days_repair is None:
        days_repair = 0
    interval = []
    days_work = []
    all_intervals = []
    response = []
    for function in all_function:
        date_from = function.get('date_from')
        date_to = function.get('date_to')
        responsibility = function.get('responsibility')
        interval.append(date_from)
        interval.append(date_to)
        all_intervals.append({'date_from': date_from, 'date_to': date_to, 'responsibility': responsibility.id})
        days_work.append(function.get('days_work'))
    if any(interval + [repair_date_from, repair_date_to]) and any(days_work + [days_repair]):
        raise ValidationError('Must be only interval or days')
    remain_date_cruise = relativedelta(date_end + timedelta(days=1), date_start)
    cruise_days = (remain_date_cruise.years * 12 + remain_date_cruise.months) * 30 + remain_date_cruise.days
    if all(days_work) and (sum(days_work) + days_repair) > cruise_days:
        raise ValidationError('days longer')
    elif all(days_work):
        if days_repair >= 30:
            response.append({'days_work': cruise_days - sum(days_work) - days_repair})
        else:
            response.append({'days_work': cruise_days - sum(days_work)})
    else:
        if repair_date_from and repair_date_to:
            _all_intervals = deepcopy(all_intervals)
            for interval in _all_intervals:
                if (interval['responsibility'] == 8 or interval['responsibility'] == 9) \
                        and (repair_date_from <= interval['date_from'] <= repair_date_to
                             and repair_date_from <= interval['date_to'] <= repair_date_to):
                    # проверка, что обязанность судноремонт (8) или ремонт электрооборудования входит в период ремонта
                    # судна, и что остальные обязанности не входят в период ремонта и не пересекаются с ним
                    if interval['date_from'] == repair_date_from and interval['date_to'] == repair_date_to:
                        all_intervals.append({'date_from': repair_date_from, 'date_to': repair_date_to, 'repair': True})
                    # if repair_date_from > interval['date_from'] or repair_date_to < interval['date_to']:
                    #     raise ValidationError('wrong date intervals')
                    if interval['date_from'] > repair_date_from:
                        all_intervals.append({'date_from': repair_date_from,
                                              'date_to': interval['date_from'] - timedelta(days=1), 'repair': True})
                    if interval['date_to'] < repair_date_to:
                        all_intervals.append({'date_from': interval['date_to'] + timedelta(days=1),
                                              'date_to': repair_date_to, 'repair': True})
                elif repair_date_from <= interval['date_from'] <= repair_date_to or \
                        repair_date_from <= interval['date_to'] <= repair_date_to:
                    raise ValidationError('wrong date intervals')
                elif {'date_from': repair_date_from, 'date_to': repair_date_to, 'repair': True} not in all_intervals:
                    all_intervals.append({'date_from': repair_date_from, 'date_to': repair_date_to, 'repair': True})
        # валидация периодов времени, из которых состоит весь рейс
        all_intervals.sort(key=lambda x: x['date_to'], reverse=True)
        if all_intervals[0]['date_to'] > date_end:
            raise ValidationError('wrong date intervals')
        all_intervals.sort(key=lambda x: x['date_from'])
        if all_intervals[0]['date_from'] < date_start:
            raise ValidationError('wrong date intervals')
        if any([True if (interval['date_to'] - interval['date_from']).days < 0 else False
                for interval in all_intervals]):
            raise ValidationError('wrong date intervals')
        if repair_date_from and repair_date_to:
            _repair_date_to = repair_date_to + timedelta(days=1)
            remain_date = relativedelta(_repair_date_to, repair_date_from)
            if remain_date.years == 0 and (remain_date.months == 0 or
                                           (remain_date.months == 1 and remain_date.days == 0)):
                # не учитывать период ремонта, если он составляет меньше 1 месяца или 1 месяц
                all_intervals = [interval for interval in all_intervals if not interval.get('repair')]
            elif {'date_from': repair_date_from, 'date_to': repair_date_to, 'responsibility': 8} in all_intervals and \
                    {'date_from': repair_date_from, 'date_to': repair_date_to, 'repair': True} in all_intervals:
                # не учитывать ремонт, если он совпадает по датам с выполнением работ по судноремонту
                all_intervals.remove({'date_from': repair_date_from, 'date_to': repair_date_to, 'repair': True})
            elif {'date_from': repair_date_from, 'date_to': repair_date_to, 'responsibility': 9} in all_intervals and \
                    {'date_from': repair_date_from, 'date_to': repair_date_to, 'repair': True} in all_intervals:
                # не учитывать ремонт, если он совпадает по датам с выполнением работ по ремонту электрооборудования
                all_intervals.remove({'date_from': repair_date_from, 'date_to': repair_date_to, 'repair': True})
        for num in range(0, len(all_intervals) - 1):
            if all_intervals[num]['date_to'] >= all_intervals[num + 1]['date_from']:
                # в плавании выполнял две обязанности одновременно (судноремонт - 8 и нес вахту в маш отделении - 13)
                if (all_intervals[num].get('responsibility') == 8 and
                    all_intervals[num + 1].get('responsibility') == 13
                    or
                    all_intervals[num].get('responsibility') == 13 and
                    all_intervals[num + 1].get('responsibility') == 8) \
                        and \
                        all_intervals[num]['date_from'] == all_intervals[num + 1]['date_from'] and \
                        all_intervals[num]['date_to'] == all_intervals[num + 1]['date_to']:
                    pass
                else:
                    raise ValidationError('wrong date intervals')
            elif (all_intervals[num + 1]['date_from'] - all_intervals[num]['date_to']).days > 1:
                response.append({'date_from': all_intervals[num]['date_to'] + timedelta(days=1),
                                 'date_to': all_intervals[num + 1]['date_from'] - timedelta(days=1)})
        if all_intervals[0]['date_from'] > date_start:
            response.append({'date_from': date_start,
                             'date_to': all_intervals[0]['date_from'] - timedelta(days=1)})
        if all_intervals[-1]['date_to'] < date_end:
            response.append({'date_from': all_intervals[-1]['date_to'] + timedelta(days=1),
                             'date_to': date_end})
    return response


def get_is_repair(start_repair=None, end_repair=None, all_intervals=None):
    """
    Стаж.
    Проверка выполнения обязанности - выполнение работы по судноремонту или работ по ремонту электрооборудования,
    во время постановки судна в ремонт
    """
    if start_repair is None or end_repair is None:
        return all_intervals
    for interval in all_intervals:
        if interval.get('responsibility') and interval.get('responsibility').id == 8:
            if start_repair <= interval['date_from'] and end_repair >= interval['date_to']:
                interval.update(is_repaired=True)
        if interval.get('responsibility') and interval.get('responsibility').id == 9:
            if start_repair <= interval['date_from'] and end_repair >= interval['date_to']:
                interval.update(is_repaired=True)
    return all_intervals


def check_repair_enter_to_cruise(date_start_cruise=None, date_end_cruise=None, repair_date_from=None,
                                 repair_date_to=None, repairs_days=None):
    """
    Стаж.
    Проверка вхождения ремонта в период рейса
    """
    if repair_date_from and repair_date_to:
        if (date_start_cruise <= repair_date_from <= date_end_cruise and
            date_start_cruise <= repair_date_to <= date_end_cruise) is False:
            raise ValidationError('wrong date intervals')
    if repairs_days:
        remain_date_cruise = relativedelta(date_end_cruise + timedelta(days=1), date_start_cruise)
        cruise_days = (remain_date_cruise.years * 12 + remain_date_cruise.months) * 30 + remain_date_cruise.days
        if cruise_days < repairs_days:
            raise ValidationError('days longer')
    return True


def check_all_function(all_function):
    """
    Стаж.
    Проверка отсутствия обязанностей с отработанным количестов дней равным 0
    """
    if all_function:
        return [func for func in all_function if not (func['date_from'] is None and func['date_to'] is None and
                                                      func['days_work'] == 0)]
    return all_function


def get_sailor_by_modelname(model_name, content_obj):
    """

    :param model_name: model name by model._meta.model_name
    :param content_obj:
    :return:
    """
    sailor_key = None
    if model_name == 'servicerecord':
        sailor_key = SailorKeys.objects.filter(service_records__overlap=[content_obj.id]).first()
    elif model_name == 'education':
        sailor_key = SailorKeys.objects.filter(education__overlap=[content_obj.id]).first()
    elif model_name == 'certificateeti':
        sailor_key = SailorKeys.objects.filter(sertificate_ntz__overlap=[content_obj.id]).first()
    elif model_name == 'qualificationdocument':
        sailor_key = SailorKeys.objects.filter(qualification_documents__overlap=[content_obj.id]).first()
    elif model_name == 'medicalcertificate':
        sailor_key = SailorKeys.objects.filter(medical_sertificate__overlap=[content_obj.id]).first()
    elif model_name == 'sailorpassport':
        sailor_key = SailorKeys.objects.filter(sailor_passport__overlap=[content_obj.id]).first()
    elif model_name == 'statementsqc':
        sailor_key = SailorKeys.objects.filter(statement_dkk__overlap=[content_obj.id]).first()
    elif model_name == 'passport':
        sailor_key = SailorKeys.objects.filter(citizen_passport__overlap=[content_obj.id]).first()
    elif model_name == 'lineinservicerecord':
        if content_obj.service_record:
            sailor_key = SailorKeys.objects.filter(service_record__overlap=[content_obj.service_record_id]).first()
        else:
            sailor_key = SailorKeys.objects.filter(experience_docs__overlap=[content_obj.id]).first()
    elif model_name == 'protocoldkk':
        sailor_key = SailorKeys.objects.filter(protocol_dkk__overlap=[content_obj.id]).first()
    elif model_name == 'statementqualification':
        sailor_key = SailorKeys.objects.filter(statement_qualification__overlap=[content_obj.id]).first()
    elif model_name == 'proofofworkdiploma':
        diploma_id = content_obj.diploma_id
        sailor_key = SailorKeys.objects.filter(qualification_documents__overlap=[diploma_id]).first()
    elif model_name == 'demandpositiondkk':
        sailor_key = SailorKeys.objects.filter(demand_position__overlap=[content_obj.id]).first()
    elif model_name == 'statementservicerecord':
        sailor_key = SailorKeys.objects.filter(statement_service_records__overlap=[content_obj.id]).first()
    if not sailor_key:
        return False
    return sailor_key


def update_date_meeting_statement_dpd(date_meeting, packet, sailor_id, user_id):
    """
    Update the date_meeting DPD in packet when updating date_meeting statement SQC
    """
    from sailor.tasks import save_history
    import back_office.serializers
    date_end_meeting = workdays.workday(date_meeting, hours_to_date(8))
    _packet = deepcopy(packet)
    packet.date_end_meeting = date_end_meeting
    packet.save(update_fields=['date_end_meeting'])
    save_history.s(user_id=user_id,
                   module='PacketItem',
                   action_type='edit',
                   content_obj=_packet,
                   serializer=back_office.serializers.PacketSerializer,
                   old_obj=_packet,
                   new_obj=packet,
                   sailor_key_id=sailor_id,
                   ).apply_async(serializer='pickle')


def create_verification_status_for_document(document):
    """
    Creates all verification statuses for a document in the verification status
    """
    ct: ContentType = ContentType.objects.get_for_model(document)
    all_status = VerificationStage.objects.filter(is_disable=False, for_service=ct).order_by('order_number')
    statuses = []
    statuses += [DocumentInVerification(object_id=document.pk, content_type=ct, verification_status=all_status.first(),
                                        is_active=True)]
    statuses += [DocumentInVerification(object_id=document.pk, content_type=ct, verification_status=status)
                 for status in all_status[1:]]
    DocumentInVerification.objects.bulk_create(statuses)


def update_is_active_verification_status(document, is_active_status: int):
    """
    Changes the specified verification status to active for a document under verification,
    transfers the rest to inactive status
    """
    ct: ContentType = ContentType.objects.get_for_model(document)
    status_for_disactive = list(VerificationStage.objects.filter(
        is_disable=False, for_service=ct
    ).exclude(
        id=is_active_status
    ).values_list('id', flat=True))
    DocumentInVerification.objects.filter(
        object_id=document.pk, content_type=ct, verification_status_id__in=status_for_disactive
    ).update(
        is_active=False)
    active_doc = DocumentInVerification.objects.get(object_id=document.pk, content_type=ct,
                                                    verification_status_id=is_active_status)
    active_doc.is_active = True
    active_doc.save(update_fields=['is_active'])
    return active_doc


def verification_stages(document, context=None):
    """
    Returns the stages of document verification.
    If the document has no stages - add
    """
    from sailor.serializers import VerificationStageForDocumentSerializer
    if not document.verification_status.exists():
        create_verification_status_for_document(document)
        document.refresh_from_db()
    return VerificationStageForDocumentSerializer(document.verification_status.all(),
                                                  many=True,
                                                  context=context).data


class MergeSailor:

    def __init__(self, sailor_from, sailor_to):
        self.sailor_from = sailor_from
        self.sailor_to = sailor_to

    def delete_user(self):
        sailor_from = self.sailor_from
        sailor_to = self.sailor_to
        profile_from = Profile.objects.get(id=sailor_from.profile)
        profile_to = Profile.objects.get(id=sailor_to.profile)
        if profile_from.pk != profile_to.pk:
            profile_from.delete()
        sailor_from.delete()
        return sailor_from.pk

    @staticmethod
    def add_lists(l1, l2):
        if not l1:
            l1 = []
        if not l2:
            l2 = []
        return list(set(l1 + l2))

    def migrate_documents(self):
        sailor_from = self.sailor_from
        sailor_to = self.sailor_to
        sailor_to.sertificate_ntz = self.add_lists(sailor_to.sertificate_ntz, sailor_from.sertificate_ntz)
        sailor_to.education = self.add_lists(sailor_to.education, sailor_from.education)
        sailor_to.qualification_documents = self.add_lists(sailor_to.qualification_documents,
                                                           sailor_from.qualification_documents)
        sailor_to.service_records = self.add_lists(sailor_to.service_records, sailor_from.service_records)
        sailor_to.statement_dkk = self.add_lists(sailor_to.statement_dkk, sailor_from.statement_dkk)
        sailor_to.protocol_dkk = self.add_lists(sailor_to.protocol_dkk, sailor_from.protocol_dkk)
        sailor_to.citizen_passport = self.add_lists(sailor_to.citizen_passport, sailor_from.citizen_passport)
        sailor_to.experience_docs = self.add_lists(sailor_to.experience_docs, sailor_from.experience_docs)
        sailor_to.medical_sertificate = self.add_lists(sailor_to.medical_sertificate, sailor_from.medical_sertificate)
        sailor_to.sailor_passport = self.add_lists(sailor_to.sailor_passport, sailor_from.sailor_passport)
        sailor_to.statement_qualification = self.add_lists(sailor_to.statement_qualification,
                                                           sailor_from.statement_qualification)
        sailor_to.demand_position = self.add_lists(sailor_to.demand_position, sailor_from.demand_position)
        sailor_to.user_id = sailor_from.user_id if not sailor_to.user_id else sailor_to.user_id
        sailor_to.agent_id = sailor_from.agent_id if not sailor_to.agent_id else sailor_to.agent_id
        sailor_to.packet_item = self.add_lists(sailor_to.packet_item, sailor_from.packet_item)
        sailor_to.students_id = self.add_lists(sailor_to.students_id, sailor_from.students_id)
        sailor_to.statement_service_records = self.add_lists(sailor_to.statement_service_records,
                                                             sailor_from.statement_service_records)
        sailor_to.statement_sailor_passport = self.add_lists(sailor_to.statement_sailor_passport,
                                                             sailor_from.statement_sailor_passport)
        sailor_to.statement_eti = self.add_lists(sailor_to.statement_eti, sailor_from.statement_eti)
        sailor_to.statement_medical_certificate = self.add_lists(sailor_to.statement_medical_certificate,
                                                                 sailor_from.statement_medical_certificate)
        sailor_to.statement_advanced_training = self.add_lists(sailor_to.statement_advanced_training,
                                                               sailor_from.statement_advanced_training)
        sailor_to.save(force_update=True)
        self.delete_user()

        if sailor_to.statement_dkk:
            self.edit_statement_dkk(sailor_from.pk, sailor_to.pk)

        if sailor_to.protocol_dkk:
            self.edit_protocol_dkk(sailor_from.pk, sailor_to.pk, sailor_from.protocol_dkk)

        if sailor_to.qualification_documents:
            self.edit_statement_qual_doc(sailor_from.pk, sailor_to.pk)

        if sailor_to.statement_service_records:
            self.edit_statement_service_records(sailor_from.pk, sailor_to.pk)

        if sailor_to.agent_id:
            self.edit_agent_sailor(sailor_from.pk, sailor_to.pk)

        if sailor_to.packet_item:
            self.edit_packet_item(sailor_from.pk, sailor_to.pk)

        if sailor_to.user_id:
            self.edit_user(sailor_to.user_id, sailor_to.pk)

        return True

    def edit_statement_dkk(self, old_sailor_key, new_sailor_key):
        StatementSQC.objects.filter(sailor=old_sailor_key).update(sailor=new_sailor_key)
        return True

    def edit_protocol_dkk(self, old_sailor_key, new_sailor_key, protocol_pks):
        ProtocolSQC.objects.filter(id__in=protocol_pks, _sailor=old_sailor_key).update(_sailor=new_sailor_key)
        return True

    def edit_statement_qual_doc(self, old_sailor_key, new_sailor_key):
        StatementQualification.objects.filter(sailor=old_sailor_key).update(sailor=new_sailor_key)
        return True

    def edit_statement_service_records(self, old_sailor_key, new_sailor_key):
        StatementServiceRecord.objects.filter(sailor=old_sailor_key).update(sailor=new_sailor_key)
        return True

    def edit_agent_sailor(self, old_sailor_key, new_sailor_key):
        StatementAgentSailor.objects.filter(sailor_key=old_sailor_key).update(sailor_key=new_sailor_key)
        AgentSailor.objects.filter(sailor_key=old_sailor_key).update(sailor_key=new_sailor_key)
        return True

    def edit_packet_item(self, old_sailor_key, new_sailor_key):
        PacketItem.objects.filter(sailor_id=old_sailor_key).update(sailor_id=new_sailor_key)
        return True

    def edit_user(self, user_id, new_sailor_key):
        User.objects.filter(id=user_id).update(last_name=new_sailor_key)
        return True
