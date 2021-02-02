import re
from typing import Type, Union, Dict

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from docxtpl import RichText

from communication.models import SailorKeys
from directory.models import FunctionAndLevelForPosition, Position, Limitations
from sailor.document.models import LineInServiceRecord, Education, ProtocolSQC, CertificateETI, \
    MedicalCertificate, QualificationDocument, ServiceRecord
from sailor.models import DependencyDocuments, SailorPassport


def get_function_level_limitation_by_position(positions: Union[list, Type[list]], language: str = None,
                                              sailor_key: SailorKeys = None, obj=None) -> Dict:
    if obj.function_limitation:
        resp_table_ukr = []
        resp_table_eng = []
        for func_limit in obj.function_limitation:
            func_limitation_qs = FunctionAndLevelForPosition.objects.get(id=func_limit['id_func'])
            limitation = Limitations.objects.filter(id__in=func_limit['id_limit'])
            text_limitation_ukr = '; '.join(limitation.values_list('name_ukr', flat=True))
            text_limitation_eng = '; '.join(limitation.values_list('name_eng', flat=True))
            resp_table_ukr.append({'func': func_limitation_qs.function.name_ukr,
                                   'level': func_limitation_qs.level.name_ukr, 'limitation': text_limitation_ukr,
                                   'limitation_id': list(limitation.values_list('id', flat=True))})
            resp_table_eng.append({'func': func_limitation_qs.function.name_eng,
                                   'level': func_limitation_qs.level.name_eng, 'limitation': text_limitation_eng,
                                   'limitation_id': list(limitation.values_list('id', flat=True))})
        return {'ukr': resp_table_ukr, 'eng': resp_table_eng}
    for_save = []
    resp = dict()
    resp_table_ukr = list()
    resp_table_eng = list()
    if not sailor_key.medical_sertificate:
        sailor_key.medical_sertificate = []
    if not sailor_key.experience_docs:
        sailor_key.experience_docs = []
    if not sailor_key.service_records:
        sailor_key.service_records = []
    position = Position.objects.get(id=positions[0])
    functions_and_levels_for_position = FunctionAndLevelForPosition.objects.filter(position=position, is_disable=False)
    try:
        depend = DependencyDocuments.objects.filter(position=position).first()
        in_port_pk = [depend.limitation_id.pk]
        in_port_ukr = depend.limitation_id.name_ukr
        in_port_eng = depend.limitation_id.name_eng
        if position.rank_id in [87]:
            raise AttributeError
    except AttributeError:
        in_port_pk = [153]
        in_port_ukr = 'Немає'
        in_port_eng = 'None'
    limitation_medical = MedicalCertificate.objects.filter(id__in=sailor_key.medical_sertificate,
                                                           status_document_id__in=[2, 19])
    if limitation_medical.filter(limitation_id__in=[2, 3]).exists():
        medical_limitation = limitation_medical.filter(limitation_id__in=[2, 3]).first()
        medical_limitation_to_limitation = {2: 52, 3: 51}
        medical_limitation_pk = [medical_limitation_to_limitation[medical_limitation.limitation.pk]]
        medical_limitation_ukr = medical_limitation.limitation.name_ukr
        medical_limitation_eng = medical_limitation.limitation.name_eng
    else:
        medical_limitation_pk = [153]
        medical_limitation_ukr = 'Немає'
        medical_limitation_eng = 'None'
    no_limitation_eng = 'None'
    no_limitation_ukr = 'Немає'
    if functions_and_levels_for_position.filter(function_id=21).exists():
        func_and_level = functions_and_levels_for_position.get(function_id=21)
        resp_table_ukr.append({'func': func_and_level.function.name_ukr,
                               'level': func_and_level.level.name_ukr, 'limitation': in_port_ukr,
                               'limitation_id': in_port_pk})
        resp_table_eng.append({'func': func_and_level.function.name_eng,
                               'level': func_and_level.level.name_eng, 'limitation': in_port_eng,
                               'limitation_id': in_port_pk})
        for_save.append({'id_func': func_and_level.pk, 'id_limit': in_port_pk})
    if functions_and_levels_for_position.filter(function_id=61).exists():
        func_and_level = functions_and_levels_for_position.get(function_id=61)
        resp_table_ukr.append({'func': func_and_level.function.name_ukr,
                               'level': func_and_level.level.name_ukr, 'limitation': medical_limitation_ukr,
                               'limitation_id': medical_limitation_pk})
        resp_table_eng.append({'func': func_and_level.function.name_eng,
                               'level': func_and_level.level.name_eng, 'limitation': medical_limitation_eng,
                               'limitation_id': medical_limitation_pk})
        for_save.append({'id_func': func_and_level.pk, 'id_limit': medical_limitation_pk})
    if functions_and_levels_for_position.filter(function_id__in=[62, 1, 2]).exists():
        func_and_level = functions_and_levels_for_position.filter(function_id__in=[62, 1, 2])
        for func_an_l_one in func_and_level:
            resp_table_ukr.append({'func': func_an_l_one.function.name_ukr,
                                   'level': func_an_l_one.level.name_ukr, 'limitation': no_limitation_ukr,
                                   'limitation_id': [153]})
            resp_table_eng.append({'func': func_an_l_one.function.name_eng,
                                   'level': func_an_l_one.level.name_eng, 'limitation': no_limitation_eng,
                                   'limitation_id': [153]})
            for_save.append({'id_func': func_an_l_one.pk, 'id_limit': [153]})
    if functions_and_levels_for_position.filter(function_id=133).exists():
        limitations = []
        line_record = LineInServiceRecord.objects.filter(Q(id__in=sailor_key.experience_docs) |
                                                         Q(service_record_id__in=sailor_key.service_records) & Q(
            status_line_id=9))
        if position.rank_id in [86, 85, 84]:
            limitations.append(22)
        if line_record.filter(type_geu_id=2).exists():
            limitations.append(41)
        if line_record.filter(type_geu_id=3).exists():
            limitations.append(42)
        if len(limitations) > 1:
            limitations_ukr_old = list(
                Limitations.objects.filter(id__in=limitations).values_list('name_ukr', flat=True))
            limitations_eng_old = list(
                Limitations.objects.filter(id__in=limitations).values_list('name_eng', flat=True))
            limitations_ukr = [limitation.replace('Тільки ', 'Дійсний ') for limitation in limitations_ukr_old]
            limitations_eng = [limitation.replace('Only ', 'Valid ') for limitation in limitations_eng_old]
        elif len(limitations) == 1:
            limitations_ukr = list(
                Limitations.objects.filter(id__in=limitations).values_list('name_ukr', flat=True))
            limitations_eng = list(
                Limitations.objects.filter(id__in=limitations).values_list('name_eng', flat=True))
        else:
            limitations_ukr = ['Немає']
            limitations_eng = ['None']
            limitations.append(153)
        func_and_level = functions_and_levels_for_position.get(function_id=133)
        resp_table_ukr.append({'func': func_and_level.function.name_ukr,
                               'level': func_and_level.level.name_ukr, 'limitation': '; '.join(limitations_ukr),
                               'limitation_id': limitations})
        resp_table_eng.append({'func': func_and_level.function.name_eng,
                               'level': func_and_level.level.name_eng, 'limitation': '; '.join(limitations_eng),
                               'limitation_id': limitations})
        for_save.append({'id_func': func_and_level.pk, 'id_limit': limitations})
    if functions_and_levels_for_position.filter(function_id=41):
        func_and_level = functions_and_levels_for_position.get(function_id=41)
        resp_table_ukr.append({'func': func_and_level.function.name_ukr,
                               'level': func_and_level.level.name_ukr, 'limitation': in_port_ukr,
                               'limitation_id': in_port_pk})
        resp_table_eng.append({'func': func_and_level.function.name_eng,
                               'level': func_and_level.level.name_eng, 'limitation': in_port_eng,
                               'limitation_id': in_port_pk})
        for_save.append({'id_func': func_and_level.pk, 'id_limit': in_port_pk})
    if functions_and_levels_for_position.filter(function_id=63):
        func_and_level = functions_and_levels_for_position.get(function_id=63)
        resp_table_ukr.append({'func': func_and_level.function.name_ukr,
                               'level': func_and_level.level.name_ukr, 'limitation': in_port_ukr,
                               'limitation_id': in_port_pk})
        resp_table_eng.append({'func': func_and_level.function.name_eng,
                               'level': func_and_level.level.name_eng, 'limitation': in_port_eng,
                               'limitation_id': in_port_pk})
        for_save.append({'id_func': func_and_level.pk, 'id_limit': in_port_pk})
    if not resp_table_ukr or not resp_table_eng:
        for func_and_level in functions_and_levels_for_position:
            resp_table_ukr.append({'func': func_and_level.function.name_ukr,
                                   'level': func_and_level.level.name_ukr, 'limitation': no_limitation_ukr,
                                   'limitation_id': [153]})
            resp_table_eng.append({'func': func_and_level.function.name_eng,
                                   'level': func_and_level.level.name_eng, 'limitation': no_limitation_eng,
                                   'limitation_id': [153]})
            for_save.append({'id_func': func_and_level.pk, 'id_limit': [153]})
    if not obj.function_limitation:
        obj.function_limitation = for_save
        obj.save(update_fields=['function_limitation'])
    resp['ukr'] = resp_table_ukr
    resp['eng'] = resp_table_eng
    return resp


def get_position_limitation(positions: list):
    dependency = DependencyDocuments.objects.filter(position_id__in=positions).order_by('position_id'). \
        distinct('position_id')
    # positions = Position.objects.filter(id__in=positions)
    table_ukr = list()
    table_eng = list()
    for depend in dependency:
        position_ukr = depend.position.name_ukr
        if depend.position.rank_id in [89]:
            try:
                position_ukr = position_ukr.split(' (')[0]
            except:
                position_ukr = depend.position.name_ukr
        try:
            limitation_ukr = depend.limitation_id.name_ukr
            limitation_eng = depend.limitation_id.name_eng
        except AttributeError:
            limitation_ukr = 'Немає'
            limitation_eng = 'None'
        table_ukr.append({'position': position_ukr, 'limitation': limitation_ukr})
        table_eng.append({'position': depend.position.name_eng, 'limitation': limitation_eng})
    return {'table_ukr': table_ukr, 'table_eng': table_eng}


def get_ukranian_month(number_month):
    _dict = {1: 'січня', 2: 'лютого', 3: 'березня', 4: 'квітня', 5: 'травня', 6: 'червня', 7: 'липня',
             8: 'серпня', 9: 'вересня', 10: 'жовтня', 11: 'листопада', 12: 'грудня'}
    return _dict[number_month]


def date_to_doc_format(date):
    return '«{}» {} {}'.format(str(date.day).zfill(2), get_ukranian_month(date.month), date.year)


class GetTextForDocument:
    def __init__(self, list_positions=None, sailor_key=None, protocol: ProtocolSQC = None):
        self.list_positions = list_positions
        self.sailor_key = sailor_key
        self.protocol = protocol

    def _get_education_for_protocol(self):
        ct = ContentType.objects.get(model__iexact='education')
        documents = self.protocol.related_docs.filter(gm2m_ct=ct)
        _resp = []
        for education in documents:
            if education.type_document_id != 3:
                if not education.date_end_educ:
                    education.date_end_educ = education.date_issue_document
                if not education.speciality:
                    speciality = 'Немає'
                else:
                    speciality = education.speciality.name_ukr
                _resp.append({'type_doc': 'other', 'text': 'У {} році закінчив {}\nза спеціальністю {}\nта здобув'
                                                           ' кваліфікацію {}\n'.format(education.date_end_educ.year,
                                                                                       education.name_nz.name_ukr,
                                                                                       speciality,
                                                                                       education.qualification.name_ukr)})
            else:
                date_issued_educ = education.date_end_educ.strftime('%Y')
                name_qual = education.qualification.name_ukr
                name_educ = education.name_nz.name_ukr
                _resp.append({'type_doc': 'upper_qual',
                              'text': 'У {} році закінчив курси {} в {}\n'.format(date_issued_educ, name_qual,
                                                                                  name_educ)})
        return _resp

    def _get_qual_for_protocol(self):
        ct = ContentType.objects.get(model__iexact='QualificationDocument')
        documents = self.protocol.related_docs.filter(gm2m_ct=ct)
        _resp = []
        for qual_doc in documents:
            if qual_doc.port:
                captain = qual_doc.port.position_capitan_ukr
                captain = captain.replace('Капітан', '')
            else:
                captain = '____________________________'
            if qual_doc.rank.type_rank_id == 3:
                type_r_text = 'кваліфікацію'
            else:
                type_r_text = 'звання'
            date_issued = qual_doc.date_start.strftime('%d.%m.%Y')
            _resp.append('{} № {} на {} {} виданий / видане {} року '
                         'капітаном {}\n'.format(qual_doc.type_document.name_ukr, qual_doc.get_number,
                                                 type_r_text, qual_doc.rank.name_ukr, date_issued,
                                                 captain))
        return RichText('\n'.join(_resp), font='Times New Roman')

    def _get_ntz(self):
        _resp = []
        documents = self.protocol.related_docs.filter(Model=CertificateETI)
        documents = CertificateETI.objects.filter(id__in=list(documents.values_list('gm2m_pk', flat=True)),
                                                  course_training_id__in=[219, 27, 104, 485, 488])
        for document in documents:
            date_issued_ntz = document.date_start.year
            name_course = document.course_training.name_ukr
            number_doc = document.ntz_number
            name_ntz = document.ntz.name_ukr
            date_issued_full = document.date_start.strftime('%d.%m.%Y')
            _resp.append(
                'У {} році закінчив {} в {}. \nСвідоцтво №{} видано {}\n'.format(date_issued_ntz, name_course,
                                                                                 name_ntz, number_doc,
                                                                                 date_issued_full))
        return RichText('\n'.join(_resp), font='Times New Roman')

    def get_response(self):
        ntz = self._get_ntz()
        qual_doc = self._get_qual_for_protocol()
        education = self._get_education_for_protocol()
        text_education = ''
        resp_education = []
        resp_ntz = []
        for educ in education:
            if educ['type_doc'] == 'upper_qual':
                resp_ntz.append(educ['text'])
            else:
                resp_education.append(educ['text'])
        if resp_education:
            text_education = RichText('\n'.join(resp_education), font='Times New Roman')
        if resp_ntz:
            ntz = RichText('\n'.join(resp_ntz), font='Times New Roman')
        return {'text_education': text_education, 'text_qual_doc': qual_doc, 'text_ntz': ntz}


class GetTableForStatementQual:
    def __init__(self, statement_qual=None, sailor_key=None):
        self.statement = statement_qual
        self.sailor_key = sailor_key

    def get_resp(self):
        resp = list()
        for documents in self.statement.related_docs.all():
            if isinstance(documents, QualificationDocument):
                if 123 in documents.list_positions or 105 in documents.list_positions:
                    doc_name = 'Копія диплома оператора ГМЗЛБ та підтвердження до нього'
                else:
                    doc_name = 'Оригінали і копії робочого диплому та підтвердження до нього.'
                resp.append({'number': documents.get_number, 'issued_date': documents.date_start,
                             'doc_name': doc_name})
            elif isinstance(documents, MedicalCertificate):
                doc_name = 'Копія медичної довідки. '
                resp.append({'number': documents.number, 'issued_date': documents.date_start,
                             'doc_name': doc_name})
            elif isinstance(documents, CertificateETI):
                dependency_ntz = DependencyDocuments.objects.filter(type_document='NTZ',
                                                                    key_document__contained_by=[
                                                                        documents.course_training_id])
                try:
                    result = re.findall(r'[cсС]відоцтво "(.+)"', dependency_ntz.first().document_description)[0]
                except (IndexError, AttributeError):
                    result = ''
                resp.append({'number': documents.ntz_number, 'issued_date': documents.date_start,
                             'doc_name': result})
            elif isinstance(documents, Education):
                if documents.type_document_id != 3:
                    doc_name = 'Копія Учбового диплому з додатком.'
                else:
                    doc_name = 'Курси підвищення кваліфікації.'
                resp.append({'number': documents.number_document, 'issued_date': documents.date_issue_document,
                             'doc_name': doc_name})
            elif isinstance(documents, SailorPassport):
                doc_name = 'Копія Посвідчення особи моряка, або паспорту для виїзду за кордон'
                resp.append({'number': documents.number_document,
                             'issued_date': documents.date_start.strftime('%d.%m.%Y'),
                             'doc_name': doc_name})
            elif isinstance(documents, ServiceRecord):
                resp.append({'doc_name': 'Копія Послужної  книжка моряка.', 'number': documents.number,
                             'issued_date': documents.date_issued})
        resp.append({'doc_name': 'Документ про сплату', 'issued_date': '', 'number': ''})
        resp.append({'doc_name': 'Три кольорові фотокартки.', 'issued_date': '', 'number': ''})
        return resp


class EducationForQual:
    def __init__(self, sailor_key=None, qual_doc: QualificationDocument = None):
        self.sailor_key = sailor_key
        self.qual_doc = qual_doc

    def get_education(self):
        text_educ_ukr = []
        text_educ_eng = []
        educations = self.qual_doc.related_docs.filter(Model=Education)
        for educ in educations:
            if educ.type_document_id == 1:
                try:
                    date_end_educ = educ.date_end_educ.year
                except AttributeError:
                    date_end_educ = educ.date_issue_document.year
                text_educ_ukr.append('{}, {}, {}'.format(educ.name_nz.name_abbr,
                                                         date_end_educ,
                                                         educ.qualification.name_ukr))
                text_educ_eng.append('{}, {}, {}'.format(educ.name_nz.name_eng,
                                                         date_end_educ,
                                                         educ.qualification.name_eng))

        return {'ukr': '; '.join(text_educ_ukr), 'eng': '; '.join(text_educ_eng)}
