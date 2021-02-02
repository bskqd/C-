import io
import itertools
import json
import os
import re
import shutil
from datetime import date, datetime

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.files import File
from django.http import HttpResponse
from docxtpl import DocxTemplate, RichText
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication, JWTTokenUserAuthentication

from communication.models import SailorKeys
from directory.models import (DocsForPosition, FunctionAndLevelForPosition, Limitations, Position, RegulatoryGround,
                              RulesForPosition)
from itcs import magic_numbers
from itcs.ExpireToken import ExpiringTokenAuthentication
from sailor.document.models import (CertificateETI, ProofOfWorkDiploma, ProtocolSQC, QualificationDocument,
                                    ServiceRecord)
from sailor.misc import CheckSailorForPositionDKK
from sailor.models import ContactInfo, DependencyDocuments, Passport, Profile
from sailor.statement.models import StatementSQC
from signature.models import CommissionerSignProtocol
from .misc import (date_to_doc_format, EducationForQual, get_function_level_limitation_by_position,
                   get_position_limitation, GetTableForStatementQual, GetTextForDocument)
from .models import (DocsForProofOfDiplomaDocuments, DocsForProtocolDKK, DocsForQualificationDocuments,
                     DocsForServiceRecord, DocsForStatementDKK, DocsForStatementQualification,
                     DocsForStatementServiceRecord,
                     TemplateDocForQualification)
# Service record start
from .tasks import docx_to_pdf


class AuthServiceRecordBook(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        service_record = data['doc_id']
        new_doc = DocsForServiceRecord.objects.create(service_record_id=service_record, author=request.user)
        return Response({'token': new_doc.token})


class GenerateServiceRecordBook(APIView):
    """
    Генерирует послужную книжку моряка
    """

    def generate_service_record_book(self, request, doc_id):

        service_record = ServiceRecord.objects.get(id=doc_id)
        key = SailorKeys.objects.filter(service_records__overlap=[service_record.id]).first()
        sailor = Profile.objects.get(id=key.profile)
        try:
            passport = Passport.objects.filter(id__in=key.citizen_passport).first()
            nationality_ukr = passport.country.value
            nationality_eng = passport.country.value_eng
        except (Passport.DoesNotExist, AttributeError, IndexError, TypeError):
            nationality_ukr = ''
            nationality_eng = ''
        # city_sailor = City.objects.get(id=sailor.city)
        doc = DocxTemplate(settings.BASE_DIR + '/docs/docs_file/service_record.docx')
        try:
            date_birth = sailor.date_birth.strftime('%d.%m.%Y')
        except AttributeError:
            date_birth = ''
        date_issued = service_record.date_issued.strftime('%d.%m.%Y')
        sailor_full_name = sailor.get_full_name_to_date(service_record.date_issued)
        split_full_ukr_name = sailor_full_name['ukr'].split(' ')
        context = {'number_service_record': service_record.get_name_book,
                   'fio_full_sailor_ukr': sailor_full_name['ukr'].upper(),
                   'last_name_ukr': split_full_ukr_name[0].upper(),
                   'first_name_ukr': split_full_ukr_name[1].upper(),
                   'middle_name_ukr': split_full_ukr_name[2].upper(),
                   'sailor_fio_eng': sailor_full_name['eng'].upper(),
                   'date_birth': date_birth, 'sex_ukr': sailor.sex.value_ukr.capitalize(),
                   'sex_eng': sailor.sex.value_eng.capitalize(), 'nationality_ukr': nationality_ukr,
                   'nationality_eng': nationality_eng,
                   'auth_agent_ukr': service_record.auth_agent_ukr, 'auth_agent_eng': service_record.auth_agent_eng,
                   'branch_ukr': service_record.branch_office.name_ukr,
                   'branch_eng': service_record.branch_office.name_eng,
                   'date_issued': date_issued}
        doc.render(context=context)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename={}-{}-{}.docx'.format(
            str(service_record.get_name_book),
            str(service_record.date_issued.year), str(service_record.branch_office.code_track_record))
        doc.save(response)
        # doc.save(settings.BASE_DIR + '/docs/docs_finish/service_record_{}'.format(doc_id))
        return response

    def get(self, request, token, *args, **kwargs):
        docs_serv_record = DocsForServiceRecord.objects.get(token=token)
        response = self.generate_service_record_book(request=request, doc_id=docs_serv_record.service_record.id)
        docs_serv_record.delete()
        return response


class GenerateStatementForServiceRecord(APIView):

    def generate_statement(self, request, service_record, num_blank, user):
        service_record_id = service_record
        try:
            service_record = ServiceRecord.objects.get(id=service_record_id)
        except ServiceRecord.DoesNotExist:
            raise ValidationError('ServiceRecord Does not exists')
        sailor = SailorKeys.objects.filter(service_records__overlap=[service_record.id]).first()
        sailor_profile = Profile.objects.get(id=sailor.profile)
        sailor_full_name = sailor_profile.get_full_name_to_date(service_record.date_issued)

        doc = DocxTemplate(settings.BASE_DIR + '/docs/docs_file/zayava_for_service_record.docx')
        context = {
            'fio_short_user': '{} {}.{}.'.format(user.last_name, user.first_name[:1], user.userprofile.middle_name[:1]),
            'fio_full_sailor_ukr': sailor_full_name['ukr'],
            'fio_full_sailor_eng': sailor_full_name['eng'],
            'date_birthday_sailor': sailor_profile.date_birth.strftime('%d.%m.%Y'),
            'date_now': date.today().strftime('%d.%m.%Y'),
            'number_boo': service_record.get_name_book,
            'date_book': service_record.date_issued.strftime('%d.%m.%Y'),
            'num_strict_blank': service_record.blank_strict_report,
            'auth_fio': service_record.auth_agent_ukr}
        doc.render(context=context)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename=strict_blank_{}.docx'.format(num_blank)
        doc.save(response)
        return response

    def get(self, request, token):
        docs = DocsForStatementServiceRecord.objects.get(token=token)
        generate_statement = self.generate_statement(service_record=docs.service_record_id, num_blank=docs.num_blank,
                                                     request=request, user=docs.author)
        docs.delete()
        return generate_statement


class AuthStatementForServiceRecord(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        service_record = data['service_record']
        service_record = ServiceRecord.objects.get(id=service_record)
        if not service_record.blank_strict_report:
            num_blank = data['num_blank']
            service_record.blank_strict_report = num_blank
            service_record.save()
        else:
            num_blank = service_record.blank_strict_report
        new_doc = DocsForStatementServiceRecord.objects.create(service_record_id=service_record.id, num_blank=num_blank,
                                                               author=request.user)
        return Response({'token': new_doc.token})


# service record end

# DKK start

class GenerateDocForStatementDKK(APIView):

    @staticmethod
    def get_rank(sailor: SailorKeys, statement: StatementSQC):
        position_to = statement.list_positions[0]
        if statement.on_create_rank.exists():
            return ';'.join(
                list(statement.on_create_rank.all()
                     .distinct('name_ukr').values_list('name_ukr', flat=True)))
        if not sailor.qualification_documents:
            sailor.qualification_documents = []

        sailor_qualification_document = QualificationDocument.objects.filter(id__in=sailor.qualification_documents)
        list_key_document = DependencyDocuments.objects.filter(
            position_id=position_to, type_document__in=['Диплом', 'Свідоцтво фахівця']). \
            values_list('key_document', flat=True)
        position_diploma = [key['position'] for key_document in list_key_document for key in key_document]
        sailor_diploma_in_qual_doc = sailor_qualification_document.filter(list_positions__overlap=position_diploma)
        if sailor_diploma_in_qual_doc.exists():
            statement.on_create_rank.set(
                sailor_diploma_in_qual_doc.order_by('rank').distinct('rank').values_list('rank', flat=True)
            )
            return ';'.join(
                list(sailor_diploma_in_qual_doc.order_by('rank').distinct('rank').values_list('rank__name_ukr',
                                                                                              flat=True)))
        else:
            return 'Відсутній'

    def generate_doc_for_statement_dkk(self, statement_id):
        try:
            statement = StatementSQC.objects.get(id=statement_id)
            doc_key = DocsForPosition.objects.get(position=statement.list_positions[0],
                                                  is_continue=bool(statement.is_continue))
            key = SailorKeys.objects.filter(statement_dkk__overlap=[statement.id]).first()
            profile = Profile.objects.get(id=key.profile)
        except StatementSQC.DoesNotExist:
            raise ValueError('StatementDKK not found')
        except DocsForPosition.DoesNotExist:
            raise ValueError('Doc not found')
        doc = DocxTemplate(settings.DOCS_ROOT + doc_key.file.name)
        if statement.author:
            author = statement.author
        else:
            author = self.user
        author_fio = '{} {} {}'.format(author.last_name, author.first_name,
                                       author.userprofile.middle_name)
        try:
            rank_ukr = self.get_rank(sailor=key, statement=statement)
        except IndexError:
            rank_ukr = 'Відсутній'
        try:
            contact = ContactInfo.objects.filter(id__in=json.loads(profile.contact_info),
                                                 type_contact_id=1).first().value
        except Exception:
            contact = ''

        number_doc = statement.get_number
        positions_text = ';'.join(
            list(Position.objects.filter(id__in=statement.list_positions).values_list('name_ukr', flat=True)))
        sailor_full_name = profile.get_full_name_to_date(statement.created_at.date())
        context = {
            'number_doc': number_doc, 'fio_sailor_ukr': sailor_full_name['ukr'],
            'fio_sailor_eng': sailor_full_name['eng'], 'old_rank_sailor': rank_ukr, 'contact_sailor': contact,
            'date_now': date.today().strftime('%d.%m.%Y'), 'new_rank_sailor': statement.rank.name_ukr,
            'date_create': statement.created_at.strftime('%d.%m.%Y'), 'author_fio': author_fio,
            'new_position_sailor': positions_text
        }
        doc.render(context=context)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        if not number_doc:
            number_doc = datetime.now().strftime('%d_%m_%Y__%H-%M')
        response['Content-Disposition'] = 'attachment; filename={}.docx'.format(number_doc)
        doc.save(response)
        return response

    def get(self, request, token, *args, **kwargs):
        doc = DocsForStatementDKK.objects.get(token=token)
        self.user = doc.user
        document = self.generate_doc_for_statement_dkk(statement_id=doc.statement_id)
        doc.delete()
        return document


class AuthDocForStatementDKK(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        statement_id = data['statement_id']
        new_doc = DocsForStatementDKK.objects.create(statement_id=statement_id, user=request.user)
        return Response({'token': new_doc.token})


class AuthDocForProtocolDKK(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        protocol_id = data['doc_id']
        if data.get('action') == 'update':
            protocol = ProtocolSQC.objects.get(id=protocol_id)
            if protocol.document_file_docx and os.path.exists(protocol.document_file_docx.path):
                dir_name = os.path.split(protocol.document_file_docx.path)[0]
                shutil.rmtree(dir_name)
                protocol.document_file_docx = None
                protocol.document_file_pdf = None
                protocol.save(update_fields=['document_file_docx', 'document_file_pdf'])
        new_doc = DocsForProtocolDKK.objects.create(protocol_id=protocol_id)
        return Response({'token': new_doc.token})


class GenerateDocForProtocolDKK(APIView):

    def generate_doc(self, protocol_id):
        try:
            protocol_dkk = ProtocolSQC.objects.get(id=protocol_id)
        except ProtocolSQC.DoesNotExist:
            raise ValidationError('ProtocolDKK not found')
        if protocol_dkk.document_file_docx:
            data = open(protocol_dkk.document_file_docx.path, 'rb').read()
            response = HttpResponse(data)
            response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            response['Content-Disposition'] = 'attachment; filename=protocol_{}.docx'.format(
                protocol_dkk.number_document)
            return response
        key = SailorKeys.objects.filter(protocol_dkk__overlap=[protocol_dkk.id]).first()
        if key is None:
            raise ValidationError('Sailor not found')
        profile = Profile.objects.get(id=key.profile)
        sign_commissioners = protocol_dkk.commissioner_sign
        if not sign_commissioners.exists():
            raise ValidationError('Protocol has no signers')
        commissioners = list(sign_commissioners.filter(commissioner_type='CH').values_list(
            'signer__name'
        ))
        secretary = sign_commissioners.filter(commissioner_type='SC').first().signer.name
        committe_head = sign_commissioners.filter(commissioner_type='HD').first().signer.name

        statement_dkk = protocol_dkk.statement_dkk
        if bool(statement_dkk.is_continue) is True or \
                (bool(statement_dkk.is_continue) is False and
                 statement_dkk.rank.is_dkk is True and statement_dkk.rank.type_rank_id == 3):
            text_is_continue = 'підтвердження звання(кваліфікації) '
        else:
            text_is_continue = 'присвоєння звання(кваліфікації) '
        commissioners_fio = RichText('\n{}'.format(' ' * 52).join(commissioners))
        try:
            date_birth = profile.date_birth.strftime('%d.%m.%Y')
        except AttributeError:
            date_birth = ''
        number_of_protocol = protocol_dkk.get_number
        sailor_full_name = profile.get_full_name_to_date(protocol_dkk.date_meeting)
        context = {
            'protocol_number': number_of_protocol, 'date_meeting': protocol_dkk.date_meeting.strftime('%d.%m.%Y'),
            'branch_name_ukr': protocol_dkk.branch_create.name_ukr, 'branch_phone': protocol_dkk.branch_create.phone,
            'committee_head': committe_head,
            'committee_secretary': secretary,
            'commissioners': commissioners_fio, 'fio_sailor_ukr': sailor_full_name['ukr'].upper(),
            'fio_sailor_eng': sailor_full_name['eng'].upper(), 'text_is_continue': text_is_continue,
            'new_sailor_rank': statement_dkk.rank.name_ukr, 'date_birth_sailor': date_birth,
        }

        if protocol_dkk.related_docs.all().exists():
            documents_info = GetTextForDocument(statement_dkk.list_positions, key, protocol_dkk)
            context.update(documents_info.get_response())
        elif protocol_dkk.related_docs.all().exists() is False and protocol_dkk.statement_dkk.related_docs.all().exists() is True:
            protocol_dkk.related_docs = list(protocol_dkk.statement_dkk.related_docs.all())
            documents_info = GetTextForDocument(statement_dkk.list_positions, key, protocol_dkk)
            context.update(documents_info.get_response())
        else:
            check_sailor = CheckSailorForPositionDKK(sailor=key.id,
                                                     is_continue=statement_dkk.is_continue,
                                                     list_position=statement_dkk.list_positions)
            documents_info = check_sailor.check_documents_for_protocol_dkk_list_pos()
            [context.update(doc) for doc in documents_info]

        if protocol_dkk.statement_dkk.position_id in magic_numbers.tankers_position:
            file = {185: '/p_19.2.docx', 184: '/p_19.1.docx', 181: '/p_20.1.docx', 182: '/p_20.2.docx',
                    183: '/p_20.3.docx'}
            end_file = '/protocol_dkk' + file[protocol_dkk.statement_dkk.list_positions[0]]
        else:
            end_file = '/protocol_dkk/p_13.docx'
        doc = DocxTemplate(settings.DOCS_ROOT + end_file)
        doc.render(context=context)
        doc_io = io.BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)
        protocol_dkk.document_file_docx.save(f'protocol_{protocol_dkk.number_document}.docx', File(doc_io))
        doc_io.seek(0)
        response = HttpResponse(doc_io.read())
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        response['Content-Disposition'] = 'attachment; filename=protocol_{}.docx'.format(
            protocol_dkk.number_document)
        return response

    def generate_tanker_doc(self, protocol_dkk: ProtocolSQC):
        key = SailorKeys.objects.filter(protocol_dkk__overlap=[protocol_dkk.id]).first()
        if key is None:
            raise ValidationError('Sailor not found')
        profile = Profile.objects.get(id=key.profile)
        sign_commissioners = protocol_dkk.commissioner_sign
        if not sign_commissioners.exists():
            raise ValidationError('Protocol has no signers')
        commissioners = list(sign_commissioners.filter(commissioner_type='CH').values_list('signer__name'))
        secretary = sign_commissioners.filter(commissioner_type='SC').first().signer.name
        committe_head = sign_commissioners.filter(commissioner_type='HD').first().signer.name

        statement_dkk = protocol_dkk.statement_dkk
        if bool(statement_dkk.is_continue) is True or (
                bool(statement_dkk.is_continue) is False and
                statement_dkk.rank.is_dkk is True and statement_dkk.rank.type_rank_id == 3):
            text_is_continue = 'підтвердження звання(кваліфікації) '
        else:
            text_is_continue = 'присвоєння звання(кваліфікації) '
        commissioners_fio = RichText('\n{}'.format(' ' * 52).join(commissioners))
        try:
            date_birth = date_to_doc_format(profile.date_birth)
        except AttributeError:
            date_birth = ''
        number_of_protocol = protocol_dkk.get_number
        if statement_dkk.rank_id == 144:
            course_training_id = [98]
        elif statement_dkk.rank_id == 145:
            course_training_id = [99]
        elif statement_dkk.rank_id == 143:
            course_training_id = [99, 102]
        elif statement_dkk.rank_id == 142:
            course_training_id = [98, 100]
        elif statement_dkk.rank_id == 141:
            course_training_id = [98, 101]
        else:
            course_training_id = [0]
        ntz_name = ntz_2_name = '           '
        number_ntz = number_ntz_2 = '           '
        date_start = date_start_ntz_2 = '           '
        ntz_2 = None
        if protocol_dkk.related_docs.all().exists():
            ntz_related = list(protocol_dkk.related_docs.filter(Model=CertificateETI).values_list('gm2m_pk', flat=True))
            ntz_certs = CertificateETI.objects.filter(id__in=ntz_related, course_training_id__in=course_training_id
                                                      ).order_by('pk')
            ntz = ntz_certs.first()
            if len(course_training_id) == 2:
                ntz_2 = ntz_certs.last()
        elif not protocol_dkk.related_docs.all().exists() and protocol_dkk.statement_dkk.related_docs.all().exists():
            ntz_related = list(statement_dkk.list_positions.filter(Model=CertificateETI).values_list(
                'gm2m_pk',
                flat=True
            ))
            ntz_certs = CertificateETI.objects.filter(id__in=ntz_related, course_training_id__in=course_training_id
                                                      ).order_by('pk')
            ntz = ntz_certs.first()
            if len(course_training_id) == 2:
                ntz_2 = ntz_certs.last()
        else:
            ntz = CertificateETI.objects.filter(id__in=key.sertificate_ntz,
                                                course_training_id=course_training_id[0]).exclude(
                date_start__isnull=True).order_by('-date_start')
            if ntz.exists():
                ntz = ntz.first()
            if len(course_training_id) == 2:
                ntz_2 = CertificateETI.objects.filter(id__in=key.sertificate_ntz,
                                                      course_training_id=course_training_id[1]).exclude(
                    date_start__isnull=True).order_by('-date_start')
                if ntz_2.exists():
                    ntz_2 = ntz_2.first()
        if ntz:
            ntz_name = ntz.ntz.name_ukr
            number_ntz = ntz.ntz_number
            date_start = ntz.date_start.strftime('%d.%m.%Y')
        if ntz_2:
            ntz_2_name = ntz_2.ntz.name_ukr
            number_ntz_2 = ntz_2.ntz_number
            date_start_ntz_2 = ntz_2.date_start.strftime('%d.%m.%Y')
        date_meeting = date_to_doc_format(protocol_dkk.date_meeting)
        sailor_full_name = profile.get_full_name_to_date(protocol_dkk.date_meeting)
        context = {
            'protocol_number': number_of_protocol, 'date_meeting': date_meeting,
            'branch_name_ukr': protocol_dkk.branch_create.name_ukr, 'branch_phone': protocol_dkk.branch_create.phone,
            'committee_head': committe_head,
            'committee_secretary': secretary,
            'commissioners': commissioners_fio, 'fio_sailor_ukr': sailor_full_name['ukr'].upper(),
            'fio_sailor_eng': sailor_full_name['eng'].upper(), 'text_is_continue': text_is_continue,
            'new_sailor_rank': statement_dkk.rank.name_ukr, 'date_birth_sailor': date_birth, 'ntz_name': ntz_name,
            'number_ntz': number_ntz, 'date_start_ntz': date_start, 'ntz_2_name': ntz_2_name,
            'number_ntz_2': number_ntz_2, 'date_start_ntz_2': date_start_ntz_2
        }

        if protocol_dkk.statement_dkk.list_positions[0] in magic_numbers.tankers_position:
            file = {185: '/p_19.2.docx', 184: '/p_19.1.docx', 181: '/p_20.1.docx', 182: '/p_20.2.docx',
                    183: '/p_20.3.docx'}
            end_file = '/protocol_dkk' + file[protocol_dkk.statement_dkk.list_positions[0]]
        else:
            end_file = '/protocol_dkk/p_13.docx'
        doc = DocxTemplate(settings.DOCS_ROOT + end_file)
        doc.render(context=context)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename=protocol_{}.docx'.format(protocol_dkk.number_document)
        doc.save(response)
        return response

    def get(self, request, token, *args, **kwargs):
        doc = DocsForProtocolDKK.objects.get(token=token)
        document = self.generate_doc_main(doc.protocol)
        doc.delete()
        return document

    def generate_doc_main(self, protocol_obj):
        if protocol_obj.statement_dkk.list_positions[0] in magic_numbers.tankers_position:
            document = self.generate_tanker_doc(protocol_obj)
        else:
            document = self.generate_doc(protocol_id=protocol_obj.pk)
        return document


class GenerateProtocolWithConcusionDKK(APIView):

    @staticmethod
    def get_decision(protocol_dkk):
        if protocol_dkk.decision_id == 1 and (
                (bool(protocol_dkk.statement_dkk.is_continue) is True) or
                (
                        not bool(protocol_dkk.statement_dkk.is_continue) and
                        protocol_dkk.statement_dkk.rank.is_dkk and
                        protocol_dkk.statement_dkk.rank.type_rank_id == 3
                )
        ):
            status_doc = 'підтвердити'
        elif protocol_dkk.decision_id == 2 and (
                (bool(protocol_dkk.statement_dkk.is_continue)) or
                (
                        not bool(protocol_dkk.statement_dkk.is_continue) and
                        protocol_dkk.statement_dkk.rank.is_dkk and
                        protocol_dkk.statement_dkk.rank.type_rank_id == 3
                )
        ):
            status_doc = 'не підтвердити'
        elif protocol_dkk.decision_id == 1 and not bool(protocol_dkk.statement_dkk.is_continue):
            status_doc = 'присвоїти'
        elif protocol_dkk.decision_id == 2 and not bool(protocol_dkk.statement_dkk.is_continue):
            status_doc = 'не присвоїти'
        else:
            status_doc = ''
        return status_doc

    @staticmethod
    def get_tables(protocol_dkk, key):
        resp_table1 = get_function_level_limitation_by_position(positions=protocol_dkk.statement_dkk.list_positions,
                                                                sailor_key=key, obj=protocol_dkk)['ukr']
        all_limitation_ukr = [item['limitation'] for item in resp_table1 if item['limitation'] != 'Немає']
        if protocol_dkk.statement_dkk.rank_id in [1, 87, 81, 82, 83, 24]:
            dependency = DependencyDocuments.objects.filter(
                position_id=protocol_dkk.statement_dkk.list_positions[0]).distinct(
                'limitation_id')
            all_limitation_ukr = all_limitation_ukr + list(dependency.values_list('limitation_id__name_ukr', flat=True))
            seen_ukr = set()
            result_ukr = []
            for item in all_limitation_ukr:
                if item not in seen_ukr:
                    seen_ukr.add(item)
                    result_ukr.append(item)
            all_limitation_ukr = result_ukr
        all_limitation_text_ukr = RichText('\n'.join(all_limitation_ukr), font='Times New Roman')
        if not str(all_limitation_text_ukr):
            all_limitation_text_ukr = RichText('Немає', font='Times New Roman')
        return {'table': resp_table1, 'all_limitation': all_limitation_text_ukr}

    def generate_doc(self, protocol_id):
        try:
            protocol_dkk = ProtocolSQC.objects.get(id=protocol_id)
        except ProtocolSQC.DoesNotExist:
            raise ValidationError('ProtocolDKK not found')
        if not protocol_dkk.is_printeble:
            return Response({'error': 'ProtocolDKK not printeble'})
        key = SailorKeys.objects.filter(protocol_dkk__overlap=[protocol_dkk.id]).first()
        if key is None:
            raise ValidationError('Sailor not found')
        profile = Profile.objects.get(id=key.profile)
        sign_commissioners = protocol_dkk.commissioner_sign
        if not sign_commissioners.exists():
            raise ValidationError('Protocol has no signers')
        commissioners = list(sign_commissioners.filter(commissioner_type='CH').values_list('signer__name', flat=True))
        secretary = sign_commissioners.filter(commissioner_type='SC').first().signer.name
        committe_head = sign_commissioners.filter(commissioner_type='HD').first().signer.name

        statement_dkk = protocol_dkk.statement_dkk
        if bool(statement_dkk.is_continue) is True or (
                bool(statement_dkk.is_continue) is False and
                statement_dkk.rank.is_dkk is True and statement_dkk.rank.type_rank_id == 3):
            text_is_continue = 'підтвердження звання(кваліфікації) '
        else:
            text_is_continue = 'присвоєння звання(кваліфікації) '
        status_doc = self.get_decision(protocol_dkk)
        commissioners_fio = RichText('\n{}'.format(' ' * 52).join(commissioners), bold=True, font='Times New Roman')
        try:
            date_birth = profile.date_birth.strftime('%d.%m.%Y')
        except AttributeError:
            date_birth = ''
        regulatory = RegulatoryGround.objects.filter(position__in=protocol_dkk.statement_dkk.list_positions). \
            distinct('rule')
        split_regulatory_text = re.split(r'[IІV]+\/\d', regulatory[0].text_regulatory)
        try:
            rules = ', '.join(list(regulatory.values_list('rule__value', flat=True)))
        except TypeError:
            rules = ''
        if len(split_regulatory_text) == 1:
            regulatory_text = split_regulatory_text[0]
        else:
            regulatory_text = split_regulatory_text[0] + rules + split_regulatory_text[1]
        if protocol_dkk.statement_dkk.rank.type_rank_id == 21:
            valid_date = 'до ' + (protocol_dkk.date_meeting + relativedelta(years=5)).strftime('%d.%m.%Y')
        else:
            valid_date = 'до "необмежений"'
        if protocol_dkk.statement_dkk.rank.type_rank_id == 3:
            type_doc = 'свідоцтво фахівця'
        elif bool(protocol_dkk.statement_dkk.is_continue) is True:
            type_doc = 'підтвердження до диплому'
        elif protocol_dkk.statement_dkk.rank.type_document_id == 49:
            type_doc = 'диплом з підтвердженням до диплому'
        else:
            type_doc = 'свідоцтво фахівця'
        number_of_protocol = protocol_dkk.get_number
        table_limitation_position = get_position_limitation(positions=protocol_dkk.statement_dkk.list_positions)[
            'table_ukr']
        tables = self.get_tables(protocol_dkk, key)
        if protocol_dkk.statement_dkk.rank.type_rank_id == 3:
            type_rank_text = 'кваліфікацію'
        else:
            type_rank_text = 'звання'
        sailor_full_name = profile.get_full_name_to_date(protocol_dkk.date_meeting)
        context = {
            'protocol_number': number_of_protocol, 'date_meeting': protocol_dkk.date_meeting.strftime('%d.%m.%Y'),
            'branch_name_ukr': protocol_dkk.branch_create.name_ukr, 'branch_phone': protocol_dkk.branch_create.phone,
            'committee_head': committe_head,
            'committee_secretary': secretary,
            'commissioners': commissioners_fio, 'fio_sailor_ukr': sailor_full_name['ukr'].upper(),
            'fio_sailor_eng': sailor_full_name['eng'].upper(), 'text_is_continue': text_is_continue,
            'new_sailor_rank': statement_dkk.rank.name_ukr, 'date_birth_sailor': date_birth, 'rules': rules,
            'text_regulatory': regulatory_text, 'status_document_ukr': status_doc, 'valid_date': valid_date,
            'commissioner_1': commissioners[0], 'commissioner_2': commissioners[1], 'type_document': type_doc,
            'status_doc_lower': protocol_dkk.decision.name_ukr.lower(), 'positions_table': table_limitation_position,
            'table1': tables['table'], 'all_limitation_text_ukr': tables['all_limitation'],
            'type_rank_text': type_rank_text
        }
        if protocol_dkk.related_docs.all().exists():
            documents_info = GetTextForDocument(statement_dkk.list_positions, key, protocol_dkk)
            context.update(documents_info.get_response())
        elif protocol_dkk.statement_dkk.related_docs.all().exists() is True:
            protocol_dkk.related_docs = list(protocol_dkk.statement_dkk.related_docs.all())
            documents_info = GetTextForDocument(statement_dkk.list_positions, key, protocol_dkk)
            context.update(documents_info.get_response())
        else:
            pr = protocol_dkk.statement_dkk.get_status_position
            if protocol_dkk.statement_dkk.related_docs.all().exists() is True:
                protocol_dkk.related_docs = list(protocol_dkk.statement_dkk.related_docs.all())
                documents_info = GetTextForDocument(statement_dkk.list_positions, key, protocol_dkk)
                context.update(documents_info.get_response())
            else:
                check_sailor = CheckSailorForPositionDKK(sailor=key.id,
                                                         is_continue=statement_dkk.is_continue,
                                                         list_position=statement_dkk.list_positions)

                documents_info = check_sailor.check_documents_for_protocol_dkk_list_pos()
                [context.update(doc) for doc in documents_info]

        if protocol_dkk.statement_dkk.position_id in magic_numbers.tankers_position:
            file = {185: '/pv_19.2.docx', 184: '/pv_19.1.docx', 181: '/pv_20.1.docx', 182: '/pv_20.2.docx',
                    183: '/pv_20.3.docx'}
            end_file = '/protocol_dkk' + file[protocol_dkk.statement_dkk.list_positions[0]]
        else:
            end_file = '/protocol_dkk/pv_13.docx' if protocol_dkk.date_meeting >= date(2020, 11, 23)\
                else '/protocol_dkk/inspection_pv_13.docx'
        doc = DocxTemplate(settings.DOCS_ROOT + end_file)
        doc.render(context=context)
        doc_io = io.BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)
        protocol_dkk.document_file_docx.save(f'protocol_{protocol_dkk.number_document}.docx', File(doc_io))
        generate_pdf = False
        if not protocol_dkk.document_file_pdf:
            task = docx_to_pdf.delay(protocol_id)
            generate_pdf = task.get()
        protocol_dkk.refresh_from_db(fields=['document_file_pdf'])
        if protocol_dkk.document_file_pdf or generate_pdf is True:
            with open(protocol_dkk.document_file_pdf.path, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline;filename=some_file.pdf'
                return response
        raise ValidationError('Cant create pdf file')

    def generate_tanker_doc(self, protocol_dkk: ProtocolSQC):
        key = SailorKeys.objects.filter(protocol_dkk__overlap=[protocol_dkk.id]).first()
        if key is None:
            raise ValidationError('Sailor not found')
        profile = Profile.objects.get(id=key.profile)
        sign_commissioners = protocol_dkk.commissioner_sign
        if not sign_commissioners.exists():
            raise ValidationError('Protocol has no signers')
        commissioners = list(sign_commissioners.filter(commissioner_type='CH').values_list('signer__name', flat=True))
        secretary = sign_commissioners.filter(commissioner_type='SC').first().signer.name
        committe_head = sign_commissioners.filter(commissioner_type='HD').first().signer.name
        for num_comm in range(3):
            try:
                commissioners[num_comm]
            except IndexError:
                commissioners.append('')
        statement_dkk = protocol_dkk.statement_dkk
        if bool(statement_dkk.is_continue) is True or (
                bool(statement_dkk.is_continue) is False and
                statement_dkk.rank.is_dkk is True and statement_dkk.rank.type_rank_id == 3):
            text_is_continue = 'підтвердження звання(кваліфікації) '
        else:
            text_is_continue = 'присвоєння звання(кваліфікації) '
        if protocol_dkk.decision_id == 1:
            condition_doc = 'може бути'
            decision = 'видати'
        else:
            condition_doc = 'не може бути'
            decision = 'не видати'
        commissioners_fio = RichText('\n{}'.format(' ' * 52).join(commissioners), bold=True, font='Times New Roman')
        try:
            date_birth = date_to_doc_format(profile.date_birth)
        except AttributeError:
            date_birth = ''
        number_of_protocol = protocol_dkk.get_number
        if statement_dkk.rank_id == 144:
            course_training_id = [98]
        elif statement_dkk.rank_id == 145:
            course_training_id = [99]
        elif statement_dkk.rank_id == 143:
            course_training_id = [99, 102]
        elif statement_dkk.rank_id == 142:
            course_training_id = [98, 100]
        elif statement_dkk.rank_id == 141:
            course_training_id = [98, 101]
        else:
            course_training_id = [0]
        ntz_name = ntz_2_name = '           '
        number_ntz = number_ntz_2 = '           '
        date_start = date_start_ntz_2 = '           '
        ntz_2 = None
        if protocol_dkk.related_docs.all().exists():
            ntz_related = list(protocol_dkk.related_docs.filter(Model=CertificateETI).values_list('gm2m_pk', flat=True))
            ntz_certs = CertificateETI.objects.filter(id__in=ntz_related, course_training_id__in=course_training_id
                                                      ).order_by('pk')
            ntz = ntz_certs.first()
            if len(course_training_id) == 2:
                ntz_2 = ntz_certs.last()
        elif protocol_dkk.related_docs.all().exists() is False and protocol_dkk.statement_dkk.related_docs.all().exists() is True:
            protocol_dkk.related_docs = list(protocol_dkk.statement_dkk.related_docs.all())
            ntz_related = list(statement_dkk.list_positions.filter(Model=CertificateETI).values_list('gm2m_pk',
                                                                                                     flat=True))
            ntz_certs = CertificateETI.objects.filter(id__in=ntz_related, course_training_id__in=course_training_id
                                                      ).order_by('pk')
            ntz = ntz_certs.first()
            if len(course_training_id) == 2:
                ntz_2 = ntz_certs.last()
        else:
            ntz = CertificateETI.objects.filter(id__in=key.sertificate_ntz,
                                                course_training_id=course_training_id[0]).exclude(
                date_start__isnull=True).order_by('-date_start')
            if ntz.exists():
                ntz = ntz.first()
            if len(course_training_id) == 2:
                ntz_2 = CertificateETI.objects.filter(id__in=key.sertificate_ntz,
                                                      course_training_id=course_training_id[1]).exclude(
                    date_start__isnull=True).order_by('-date_start')
                if ntz_2.exists():
                    ntz_2 = ntz_2.first()
        if ntz:
            ntz_name = ntz.ntz.name_ukr
            number_ntz = ntz.ntz_number
            date_start = ntz.date_start.strftime('%d.%m.%Y')
        if ntz_2:
            ntz_2_name = ntz_2.ntz.name_ukr
            number_ntz_2 = ntz_2.ntz_number
            date_start_ntz_2 = ntz_2.date_start.strftime('%d.%m.%Y')
        date_meeting = date_to_doc_format(protocol_dkk.date_meeting)
        valid_date = date_to_doc_format(protocol_dkk.date_meeting + relativedelta(years=5))
        sailor_full_name = profile.get_full_name_to_date(protocol_dkk.date_meeting)
        context = {
            'protocol_number': number_of_protocol, 'date_meeting': date_meeting,
            'branch_name_ukr': protocol_dkk.branch_create.name_ukr, 'branch_phone': protocol_dkk.branch_create.phone,
            'commission_head': committe_head,
            'commission_secretary': secretary,
            'commissioners': commissioners_fio, 'fio_sailor_ukr': sailor_full_name['ukr'].upper(),
            'fio_sailor_eng': sailor_full_name['eng'].upper(), 'text_is_continue': text_is_continue,
            'new_sailor_rank': statement_dkk.rank.name_ukr, 'date_birth_sailor': date_birth, 'ntz_name': ntz_name,
            'number_ntz': number_ntz, 'date_start_ntz': date_start, 'ntz_2_name': ntz_2_name,
            'number_ntz_2': number_ntz_2, 'date_start_ntz_2': date_start_ntz_2,
            'status_doc': protocol_dkk.decision.name_ukr, 'condition_doc': condition_doc, 'decision': decision,
            'valid_date': valid_date, 'commissioner_1': commissioners[0],
            'commissioner_2': commissioners[1], 'commissioner_3': commissioners[2],
        }

        if protocol_dkk.statement_dkk.list_positions[0] in magic_numbers.tankers_position:
            file = {185: '/pv_19.2.docx', 184: '/pv_19.1.docx', 181: '/pv_20.1.docx', 182: '/pv_20.2.docx',
                    183: '/pv_20.3.docx'}
            end_file = '/protocol_dkk' + file[protocol_dkk.statement_dkk.list_positions[0]]
        else:
            end_file = '/protocol_dkk/pv_13.docx'
        doc = DocxTemplate(settings.DOCS_ROOT + end_file)
        doc.render(context=context)
        doc_io = io.BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)
        protocol_dkk.document_file_docx.save(f'protocol_{protocol_dkk.number_document}.docx', File(doc_io))
        if not protocol_dkk.document_file_pdf:
            result = docx_to_pdf.apply_async([protocol_dkk.pk])
            result.wait(timeout=6, interval=0.5)
        protocol_dkk.refresh_from_db(fields=['document_file_pdf'])
        if protocol_dkk.document_file_pdf:
            with open(protocol_dkk.document_file_pdf.path, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline;filename=some_file.pdf'
                return response
        raise ValidationError('Cant create pdf file')

    def get(self, request, token, *args, **kwargs):
        doc = DocsForProtocolDKK.objects.get(token=token)
        document = self.generate_doc_main(doc.protocol)
        doc.delete()
        return document

    def generate_doc_main(self, protocol_obj):
        if protocol_obj.document_file_pdf:
            if str(protocol_obj.number_document) not in protocol_obj.document_file_pdf.name:
                shutil.rmtree(os.path.dirname(protocol_obj.document_file_pdf.path))
                protocol_obj.document_file_pdf = None
                protocol_obj.document_file_docx = None
                protocol_obj.save(update_fields=['document_file_pdf', 'document_file_docx'])
                return self.generate_doc_main(protocol_obj=protocol_obj)
            with open(protocol_obj.document_file_pdf.path, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline;filename=some_file.pdf'
                return response
        elif not protocol_obj.document_file_pdf and protocol_obj.document_file_docx:
            if not protocol_obj.document_file_pdf:
                result = docx_to_pdf.apply_async([protocol_obj.pk])
                result.wait(timeout=None, interval=0.5)
            if protocol_obj.document_file_pdf:
                with open(protocol_obj.document_file_pdf.path, 'rb') as pdf:
                    response = HttpResponse(pdf.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'inline;filename=some_file.pdf'
                    return response
        if protocol_obj.statement_dkk.list_positions[0] in magic_numbers.tankers_position:
            document = self.generate_tanker_doc(protocol_obj)
        else:
            document = self.generate_doc(protocol_id=protocol_obj.pk)
        return document


class GenerateProtocolForAST(GenerateProtocolWithConcusionDKK):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTTokenUserAuthentication, JWTAuthentication, ExpiringTokenAuthentication)

    def get(self, request, protocol_id):
        protocol = ProtocolSQC.objects.get(id=protocol_id)
        document = self.generate_doc_main(protocol)
        return document

    def generate_doc_main(self, protocol_obj):
        if protocol_obj.document_file_pdf:
            if str(protocol_obj.number_document) not in protocol_obj.document_file_pdf.name:
                shutil.rmtree(os.path.dirname(protocol_obj.document_file_pdf.path))
                protocol_obj.document_file_pdf = None
                protocol_obj.document_file_docx = None
                protocol_obj.save(update_fields=['document_file_pdf', 'document_file_docx'])
                return self.generate_doc_main(protocol_obj=protocol_obj)
            return Response({'url': protocol_obj.document_file_pdf.url, 'name': protocol_obj.document_file_pdf.name})
        elif not protocol_obj.document_file_pdf and protocol_obj.document_file_docx:
            if not protocol_obj.document_file_pdf:
                result = docx_to_pdf.apply_async([protocol_obj.pk])
                result.wait(timeout=None, interval=0.5)
            if protocol_obj.document_file_pdf:
                return Response({'url': protocol_obj.document_file_pdf.url,
                                 'name': protocol_obj.document_file_pdf.name})
        if protocol_obj.statement_dkk.list_positions[0] in magic_numbers.tankers_position:
            self.generate_tanker_doc(protocol_obj)
            protocol_obj.refresh_from_db()
        else:
            self.generate_doc(protocol_id=protocol_obj.pk)
            protocol_obj.refresh_from_db()
        return Response({'url': protocol_obj.document_file_pdf.url, 'name': protocol_obj.document_file_pdf.name})



class AuthStatementQualification(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        statement_id = data['statement_id']
        new_doc = DocsForStatementQualification.objects.create(statement_id=statement_id, user=request.user)
        return Response({'token': new_doc.token})


class GenerateDocForStatementQualification(APIView):

    def generate_document(self, statement, user):

        def uniq(lst):
            for _, grp in itertools.groupby(lst, lambda d: (d['issued_date'], d['number'], d['doc_name'])):
                yield list(grp)[0]

        key = SailorKeys.objects.filter(statement_qualification__overlap=[statement.id]).first()
        if key is None:
            raise ValidationError('Sailor not found')
        if not key.sailor_passport:
            key.sailor_passport = []
        profile = Profile.objects.get(id=key.profile)
        port_ukr = statement.port.name_ukr[:-2] + 'ого'
        try:
            captain_port = statement.port.fiocapitanofport_set.first().name_ukr
        except AttributeError:
            captain_port = ''
        if statement.related_docs.exists():
            try:
                passport = statement.related_docs.filter(Model=Passport)[0]
                serial = passport.serial
                passport_date_iss = passport.date
            except (AttributeError, IndexError):
                serial = ''
                passport_date_iss = ''
        else:
            try:
                passport = Passport.objects.filter(id__in=key.citizen_passport).first()
                serial = passport.serial
                passport_date_iss = passport.date
            except (Passport.DoesNotExist, KeyError, AttributeError):
                serial = ''
                passport_date_iss = ''
        try:
            contact = ';'.join(list(ContactInfo.objects.filter(id__in=json.loads(profile.contact_info),
                                                               ).values_list('value', flat=True)))
        except Exception:
            contact = ''
        documents = []
        if statement.protocol_dkk:
            name_rank = statement.rank.name_ukr
            documents.append({'id': (len(documents) + 1), 'doc_name': 'Протокол засідання ДКК (оригінал)',
                              'number': statement.protocol_dkk.get_number,
                              'issued_date': statement.protocol_dkk.date_meeting})
        else:
            name_rank = statement.rank.name_ukr
        if statement.type_document_id == 49:
            type_doc = 'диплом, підтвердження до диплома'
        elif statement.type_document_id == 16:
            type_doc = 'підтвердження до диплома'
        else:
            type_doc = statement.type_document.name_ukr.lower()
        if statement.related_docs.exists() is False:
            checking_doc = CheckSailorForPositionDKK(sailor=key.id,
                                                     is_continue=statement.is_continue,
                                                     list_position=statement.list_positions, statement_qual=True)
            checking_doc = checking_doc.check_documents_many_pos()
            _checking_doc = list(uniq(checking_doc['statement_qual']))

        else:
            get_table = GetTableForStatementQual(statement_qual=statement, sailor_key=key)
            checking_doc = get_table.get_resp()
            _checking_doc = list(uniq(checking_doc))

        documents = documents + _checking_doc
        if bool(statement.is_continue) is True:
            decision = 'підтвердження звання'
        else:
            decision = 'присвоєння звання'
            sailor_date_start = ''
        documents.append({'id': (len(documents) + 1),
                          'doc_name': 'Копія паспорту громадянина України.', 'number': serial,
                          'issued_date': passport_date_iss})
        for index, value in enumerate(documents):
            value['id'] = index + 1
        sailor_full_name_ukr = profile.get_full_name_to_date(statement.created_at.date())['ukr']
        context = {
            'documents': documents, 'captain_city': port_ukr, 'fio_captain_port': captain_port,
            'fio_sailor_ukr': sailor_full_name_ukr, 'contact_sailor_ukr': contact,
            'type_document': type_doc, 'type_position': decision, 'name_rank': name_rank
        }
        doc = DocxTemplate(settings.DOCS_ROOT + '/statement_qual.docx')
        doc.render(context=context)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename={}.docx'.format(statement.get_number or 'notn')
        doc.save(response)
        return response

    def get(self, *args, **kwargs):
        token = kwargs['token']
        doc = DocsForStatementQualification.objects.get(token=token)
        document = self.generate_document(statement=doc.statement, user=doc.user)
        doc.delete()
        return document


class AuthDiplomaDocuments(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        qual_id = data['doc_id']
        num_blank = data['num_blank']
        new_doc = DocsForQualificationDocuments.objects.create(qualification_id=qual_id)
        diploma = QualificationDocument.objects.get(id=qual_id)
        if not diploma.strict_blank:
            diploma.strict_blank = num_blank
            diploma.save(update_fields=['strict_blank'])
        return Response({'token': new_doc.token})


class GenerateDiplomaDocuments(APIView):

    def limitation_text_ukr(self, _dict):
        _dict['limitation'] = 'Як зазначено у підтвердженні'
        return _dict

    def limitation_text_eng(self, _dict):
        _dict['limitation'] = 'As indicated in the endorsement'
        return _dict

    def generate_doc(self, qual_doc: QualificationDocument) -> HttpResponse:
        key = SailorKeys.objects.filter(qualification_documents__overlap=[qual_doc.id]).first()
        if key is None:
            raise ValidationError('Sailor not found')
        profile = Profile.objects.get(id=key.profile)
        tables = get_function_level_limitation_by_position(positions=qual_doc.list_positions, language='ukr',
                                                           sailor_key=key, obj=qual_doc)
        table_ukr = tables['ukr']
        table_eng = tables['eng']
        table_ukr = list(map(self.limitation_text_ukr, table_ukr))
        table_eng = list(map(self.limitation_text_eng, table_eng))
        positions = Position.objects.filter(id__in=qual_doc.list_positions)
        positions_ukr = list(positions.values_list('name_ukr', flat=True))
        positions_eng = list(positions.values_list('name_eng', flat=True))
        if qual_doc.rank_id in [89]:
            positions_ukr = [pos.split(' (')[0] for pos in positions_ukr]
        positions_text_ukr = ', '.join(list(positions_ukr))
        positions_text_eng = ', '.join(list(positions_eng))
        is_continue = False
        if qual_doc.related_docs.exists() is True:
            education = EducationForQual(sailor_key=key, qual_doc=qual_doc)
            educ_response = education.get_education()
            educ_ukr = educ_response['ukr']
            educ_eng = educ_response['eng']
        else:
            try:
                if qual_doc.statement:
                    is_continue = qual_doc.statement.is_continue
                check_doc = CheckSailorForPositionDKK(sailor=key.pk, is_continue=is_continue,
                                                      list_position=qual_doc.list_positions)
                education = check_doc.get_education_for_qual()
                educ_ukr = education['ukr']
                educ_eng = education['eng']
            except Exception:
                educ_ukr = ''
                educ_eng = ''
        rule = ', '.join(list(RulesForPosition.objects.filter(
            position_id__in=qual_doc.list_positions).distinct('rule').values_list('rule__value', flat=True)))
        try:
            pos_cap_ukr = qual_doc.port.position_capitan_ukr
            pos_cap_eng = qual_doc.port.position_capitan_eng
        except AttributeError:
            pos_cap_ukr = ''
            pos_cap_eng = ''
        sailor_full_name = profile.get_full_name_to_date(qual_doc.date_start)
        context = {
            'sailor_rank_ukr': qual_doc.rank.name_ukr, 'number_doc': qual_doc.get_number,
            'full_name_ukr': sailor_full_name['ukr'].upper(), 'date_birth': profile.date_birth.strftime('%d.%m.%Y'),
            'sailor_position_ukr': positions_text_ukr, 'date_issued': qual_doc.date_start.strftime('%d.%m.%Y'),
            'captain_port_position_ukr': pos_cap_ukr,
            'captain_port_name_ukr': qual_doc.fio_captain_ukr or '', 'sailor_rank_eng': qual_doc.rank.name_eng,
            'full_name_eng': sailor_full_name['eng'].upper(), 'sailor_position_eng': positions_text_eng,
            'captain_port_position_eng': pos_cap_eng,
            'captain_port_name_eng': qual_doc.fio_captain_eng or '', 'table_ukr': table_ukr, 'table_eng': table_eng,
            'rule_position': rule, 'education_sailor_ukr': educ_ukr, 'education_sailor_eng': educ_eng
        }
        # if qual_doc.related_docs.all().exists():
        #     documents_info = qual_doc.related_docs.all()
        #     infos_ukr = [info.dkk_protocol_record for info in documents_info]
        #     infos_eng = [info.dkk_protocol_record_eng for info in documents_info]
        #     additional = {'sailor_docs_ukr': {}, 'sailor_docs_eng': {}}
        #     for info in infos_ukr:
        #         info = list(info.items())[0]
        #         if info[0] in additional:
        #             additional['sailor_docs_ukr'][info[0]] += '\n{}'.format(info[1])
        #         else:
        #             additional['sailor_docs_ukr'][info[0]] = info[1]
        #     for info in infos_eng:
        #         info = list(info.items())[0]
        #         if info[0] in additional:
        #             additional['sailor_docs_eng'][info[0]] += '\n{}'.format(info[1])
        #         else:
        #             additional['sailor_docs_eng'][info[0]] = info[1]
        #     context.update(additional)
        file = TemplateDocForQualification.objects.get(rank=qual_doc.rank_id, is_proof_diploma=False).file
        doc = DocxTemplate(settings.DOCS_ROOT + file.name)
        doc.render(context=context)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename={}.docx'.format(qual_doc.get_number)
        doc.save(response)
        return response

    def get(self, *args, **kwargs) -> HttpResponse:
        token = kwargs['token']
        key = DocsForQualificationDocuments.objects.get(token=token)
        document = self.generate_doc(qual_doc=key.qualification)
        key.delete()
        return document


class AuthProofOfDiplomaDocuments(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request) -> Response:
        data = request.data
        proof_id = data['doc_id']
        num_blank = data['num_blank']
        new_doc = DocsForProofOfDiplomaDocuments.objects.create(proof_id=proof_id)
        proof = ProofOfWorkDiploma.objects.get(id=proof_id)
        if not proof.strict_blank:
            proof.strict_blank = num_blank
            proof.save(update_fields=['strict_blank'])
        return Response({'token': new_doc.token})


class GenerateProofOfDiplomaDocuments(APIView):

    def generate_doc(self, proof_diploma: ProofOfWorkDiploma) -> HttpResponse:
        diploma = proof_diploma.diploma
        key = SailorKeys.objects.filter(qualification_documents__overlap=[diploma.id]).first()
        if key is None:
            raise ValidationError('Sailor not found')
        profile = Profile.objects.get(id=key.profile)
        list_positions = proof_diploma.get_list_positions
        tables = get_function_level_limitation_by_position(positions=list_positions, language='ukr',
                                                           sailor_key=key, obj=proof_diploma)
        table_eng = tables['eng']
        table_ukr = tables['ukr']
        all_limitation_ukr = [item['limitation'] for item in table_ukr if item['limitation'] != 'Немає']
        all_limitation_eng = [item['limitation'] for item in table_eng if item['limitation'] != 'None']
        if diploma.rank_id in [1, 87, 81, 82, 83, 24] or list_positions[0] == 44:
            dependency = DependencyDocuments.objects.filter(position_id=list_positions[0]).distinct(
                'limitation_id')
            all_limitation_ukr = all_limitation_ukr + list(dependency.values_list('limitation_id__name_ukr', flat=True))
            all_limitation_eng = all_limitation_eng + list(dependency.values_list('limitation_id__name_eng', flat=True))
            seen_ukr = set()
            result_ukr = []
            seen_eng = set()
            result_eng = []
            for item in all_limitation_ukr:
                if item not in seen_ukr:
                    seen_ukr.add(item)
                    result_ukr.append(item)
            for item in all_limitation_eng:
                if item not in seen_eng:
                    seen_eng.add(item)
                    result_eng.append(item)
            all_limitation_ukr = result_ukr
            all_limitation_eng = result_eng

        all_limitation_text_ukr = RichText('\n'.join(all_limitation_ukr))
        all_limitation_text_eng = RichText('\n'.join(all_limitation_eng))
        if not str(all_limitation_text_ukr) and not str(all_limitation_text_eng):
            all_limitation_text_ukr = 'Немає'
            all_limitation_text_eng = 'None'
        rule = ', '.join(list(RulesForPosition.objects.filter(
            position_id__in=list_positions).distinct('rule').values_list('rule__value', flat=True)))
        position_table = get_position_limitation(positions=list_positions)
        position_table_ukr = position_table['table_ukr']
        position_table_eng = position_table['table_eng']
        sailor_position_ukr = ', '.join(list(Position.objects.filter(id__in=list_positions).
                                             values_list('name_ukr', flat=True)))
        sailor_position_eng = ', '.join(list(Position.objects.filter(id__in=list_positions).
                                             values_list('name_eng', flat=True)))
        try:
            pos_cap_ukr = proof_diploma.port.position_capitan_ukr
            pos_cap_eng = proof_diploma.port.position_capitan_eng
        except AttributeError:
            pos_cap_ukr = ''
            pos_cap_eng = ''
        sailor_full_name = profile.get_full_name_to_date(proof_diploma.date_start)
        context = {
            'number_diploma_doc': proof_diploma.get_number, 'full_name_ukr': sailor_full_name['ukr'].upper(),
            'date_birth': profile.date_birth.strftime('%d.%m.%Y'),
            'date_end_proof': proof_diploma.date_end.strftime('%d.%m.%Y'), 'table_ukr': table_ukr,
            'position_limit_ukr': position_table_ukr, 'position_limit_eng': position_table_eng,
            'date_issued': proof_diploma.date_start.strftime('%d.%m.%Y'),
            'captain_port_position_ukr': pos_cap_ukr,
            'captain_port_name_ukr': proof_diploma.fio_captain_ukr or '',
            'full_name_eng': sailor_full_name['eng'].upper(),
            'table_eng': table_eng,
            'captain_port_name_eng': proof_diploma.fio_captain_eng or '',
            'captain_port_position_eng': pos_cap_eng, 'position_rule': rule, 'sailor_position_ukr': sailor_position_ukr,
            'sailor_position_eng': sailor_position_eng, 'all_limitation_text_ukr': all_limitation_text_ukr,
            'all_limitation_text_eng': all_limitation_text_eng

        }
        file = TemplateDocForQualification.objects.get(rank=diploma.rank_id, is_proof_diploma=True).file
        doc = DocxTemplate(settings.DOCS_ROOT + file.name)
        doc.render(context=context)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename={}.docx'.format(proof_diploma.get_number)
        doc.save(response)
        return response

    def get(self, *args, **kwargs) -> HttpResponse:
        token = kwargs['token']
        key = DocsForProofOfDiplomaDocuments.objects.get(token=token)
        document = self.generate_doc(proof_diploma=key.proof)
        key.delete()
        return document


class AuthCertificateSpecialist(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request) -> Response:
        data = request.data
        qual_doc_id = data['doc_id']
        num_blank = data['num_blank']
        new_doc = DocsForQualificationDocuments.objects.create(qualification_id=qual_doc_id)
        diploma = QualificationDocument.objects.get(id=qual_doc_id)
        if not diploma.strict_blank:
            diploma.strict_blank = num_blank
            diploma.save(update_fields=['strict_blank'])
        return Response({'token': new_doc.token})


class GenerateCertificateSpecialist(APIView):

    def generate_doc(self, qual_document: QualificationDocument) -> HttpResponse:
        key = SailorKeys.objects.filter(qualification_documents__overlap=[qual_document.id]).first()
        if key is None:
            raise ValidationError('Sailor not found')
        profile = Profile.objects.get(id=key.profile)
        if qual_document.new_document is False and qual_document.function_limitation:
            table_ukr = list()
            table_eng = list()
            for func_limit in qual_document.function_limitation:
                func_level = FunctionAndLevelForPosition.objects.get(id=func_limit['id_func'])
                limitation = Limitations.objects.filter(id__in=func_limit['id_limit'])
                limitation_ukr = '; '.join(limitation.values_list('name_ukr', flat=True))
                limitation_eng = '; '.join(limitation.values_list('name_eng', flat=True))
                table_ukr.append({'func': func_level.function.name_ukr, 'level': func_level.level.name_ukr,
                                  'limitation': limitation_ukr})
                table_eng.append({'func': func_level.function.name_eng, 'level': func_level.level.name_eng,
                                  'limitation': limitation_eng})
        else:
            tables = get_function_level_limitation_by_position(positions=qual_document.list_positions, language='ukr',
                                                               sailor_key=key, obj=qual_document)
            table_eng = tables['eng']
            table_ukr = tables['ukr']
        all_limitation_text_ukr = RichText(
            '\n'.join([item['limitation'] for item in table_ukr if item['limitation'] != 'Немає']))
        all_limitation_text_eng = RichText(
            '\n'.join([item['limitation'] for item in table_eng if item['limitation'] != 'None']))
        if not str(all_limitation_text_ukr) and not str(all_limitation_text_eng):
            all_limitation_text_eng = 'None'
            all_limitation_text_ukr = 'Немає'
        try:
            rule = RulesForPosition.objects.filter(position_id=qual_document.list_positions[0])
            if not rule:
                rule = RulesForPosition.objects.filter(rank_id=qual_document.rank_id)
            rule = rule.first().rule.value
        except AttributeError:
            rule = ''
        position_table = get_position_limitation(positions=qual_document.list_positions)
        position_table_ukr = position_table['table_ukr']
        position_table_eng = position_table['table_eng']
        sailor_position_ukr = ', '.join(list(Position.objects.filter(id__in=qual_document.list_positions).
                                             values_list('name_ukr', flat=True)))
        sailor_position_eng = ', '.join(list(Position.objects.filter(id__in=qual_document.list_positions).
                                             values_list('name_eng', flat=True)))
        try:
            date_end = qual_document.date_end.strftime('%d.%m.%Y')
        except AttributeError:
            date_end = ''
        try:
            pos_cap_ukr = qual_document.port.position_capitan_ukr
            pos_cap_eng = qual_document.port.position_capitan_eng
        except AttributeError:
            pos_cap_ukr = ''
            pos_cap_eng = ''
        sailor_full_name = profile.get_full_name_to_date(qual_document.date_start)
        context = {
            'number_doc': qual_document.get_number, 'full_name_ukr': sailor_full_name['ukr'].upper(),
            'date_birth': profile.date_birth.strftime('%d.%m.%Y'),
            'date_end': date_end, 'table_ukr': table_ukr,
            'sailor_position_ukr': sailor_position_ukr,
            'position_limit_ukr': position_table_ukr, 'position_limit_eng': position_table_eng,
            'date_issued': qual_document.date_start.strftime('%d.%m.%Y'),
            'captain_port_position_ukr': pos_cap_ukr,
            'captain_port_name_ukr': qual_document.fio_captain_ukr or '',
            'full_name_eng': sailor_full_name['eng'].upper(),
            'table_eng': table_eng, 'sailor_position_eng': sailor_position_eng,
            'captain_port_name_eng': qual_document.fio_captain_eng or '',
            'captain_port_position_eng': pos_cap_eng, 'rule_position': rule,
            'all_limitation_text_ukr': all_limitation_text_ukr,
            'all_limitation_text_eng': all_limitation_text_eng, 'sailor_rank_ukr': qual_document.rank.name_ukr,
            'sailor_rank_eng': qual_document.rank.name_eng

        }
        file = TemplateDocForQualification.objects.get(rank=qual_document.rank_id).file
        doc = DocxTemplate(settings.DOCS_ROOT + file.name)
        doc.render(context=context)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename={}.docx'.format(qual_document.get_number)
        doc.save(response)
        return response

    def get(self, *args, **kwargs) -> HttpResponse:
        token = kwargs['token']
        key = DocsForQualificationDocuments.objects.get(token=token)
        document = self.generate_doc(qual_document=key.qualification)
        key.delete()
        return document


class SignedProtocolDKK(APIView):

    def get(self, request, token, *args, **kwargs):
        doc = DocsForProtocolDKK.objects.get(token=token)
        protocol = doc.protocol
        if protocol.vchasno_id and CommissionerSignProtocol.objects.filter(protocol_dkk=protocol,
                                                                           is_signatured=True).exists():
            req = requests.get(url=f'https://vchasno.ua/api/v2/documents/{protocol.vchasno_id}/pdf/print',
                               headers={'Authorization': settings.VCHASHO_MAIN_TOKEN})
            return HttpResponse(
                content=req.content,
                status=req.status_code,
                content_type=req.headers['Content-Type']
            )
        raise ValidationError({'status': 'error', 'detail': 'document not has signs'})
