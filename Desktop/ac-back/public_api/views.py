import base64
import itertools
import operator
import re

from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone as tz, timezone
from django.utils.timezone import localtime
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from communication.models import SailorKeys
from directory.models import RulesForPosition, StatusDocument, Rank
from docs.misc import get_function_level_limitation_by_position
from itcs import magic_numbers
from sailor.document.models import CertificateETI, MedicalCertificate, QualificationDocument, ProofOfWorkDiploma
from sailor.models import (Profile, Position, PhotoProfile, Passport)
from user_profile.models import FullUserSailorHistory


class AbstractView(APIView):

    def get_history(self, qual_doc, model_name):
        ct = ContentType.objects.get(model=model_name)
        history = FullUserSailorHistory.objects.filter(content_type=ct, object_id=qual_doc.id, action_type='edit')
        resp_history_ukr = []
        resp_history_eng = []
        for hist in history:
            try:
                old_obj_status = hist.old_obj_json['status_document']
                new_obj_status = hist.new_obj_json['status_document']
            except (TypeError, KeyError):
                continue
            if isinstance(old_obj_status, int):
                old_obj_status = StatusDocument.objects.get(id=old_obj_status).__dict__
            if isinstance(new_obj_status, int):
                new_obj_status = StatusDocument.objects.get(id=new_obj_status).__dict__
            if operator.eq(old_obj_status, new_obj_status) is False:
                try:
                    old_status_ukr = old_obj_status['name_ukr']
                    old_status_eng = old_obj_status['name_eng']
                except TypeError:
                    old_status_ukr = ''
                    old_status_eng = ''
                resp_history_ukr.append({'old_status': old_status_ukr,
                                         'new_status': new_obj_status['name_ukr'],
                                         'date_change': hist.datetime})
                resp_history_eng.append({'old_status': old_status_eng,
                                         'new_status': new_obj_status['name_eng'],
                                         'date_change': hist.datetime})
        return {'ukr': resp_history_ukr, 'eng': resp_history_eng}

    def get_citizen_country(self, passport_ids):
        try:
            citizen_passport = Passport.objects.filter(id__in=passport_ids).first()
            citizen_country = {'ukr': citizen_passport.country.value, 'eng': citizen_passport.country.value_eng}
        except (AttributeError, Passport.DoesNotExist, TypeError):
            citizen_country = {}
        return citizen_country


class DocumentWihUser(AbstractView):
    """Информация об одном документе для public_api"""

    def post(self, request):
        resp = self.search_sailors_and_document()
        return Response(resp)

    def search_sailors_and_document(self):
        data = self.request.data
        last_name_sailor = data.get('last_name')
        number_document = data.get('number_document')
        type_document = data.get('type_document')
        profile = Profile.objects.filter(Q(last_name_eng__iexact=last_name_sailor) |
                                         Q(old_name__old_last_name_eng__iexact=last_name_sailor))
        keys = SailorKeys.objects.filter(profile__in=list(profile.values_list('id', flat=True)))
        if type_document == 'ntz':
            return self.get_data_ntz_certificate(profile=profile, keys=keys, number_document=number_document)
        elif type_document == 'medical':
            return self.get_data_medical_certificate(profile=profile, keys=keys, number_document=number_document)
        elif type_document == 'qual_document':
            return self.get_data_qual_document(profile=profile, keys=keys, number_document=number_document)
        else:
            raise NotFound('Wrong document type')

    def get_data_qual_document(self, profile=None, keys=None, number_document=None):
        filtering = {'type_document_id__in': [1, 3, 4, 5, 6, 49, 87, 21, 57, 85, 86, 88, 89]}
        if '/' in number_document:
            number_document = number_document.split('/')
            if len(number_document) == 3:
                filtering.update({'number_document': number_document[0], 'date_start__year': number_document[1],
                                  'port__code_port': number_document[2]})
            else:
                raise NotFound('Document not found')
        else:
            filtering.update({'other_number': number_document})
        try:
            all_quals = list(keys.values_list('qualification_documents', flat=True))
            all_quals = filter(None, all_quals)
            all_quals = list(itertools.chain.from_iterable(all_quals))
            qual_diplomas = QualificationDocument.objects.filter(
                id__in=all_quals, **filtering).exclude(
                status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                        magic_numbers.STATUS_CREATED_BY_AGENT,
                                        magic_numbers.STATUS_REMOVED_DOCUMENT]
            ).first()
            if not qual_diplomas:
                raise NotFound('Document not found')
        except (QualificationDocument.DoesNotExist, ValueError, TypeError, AttributeError):
            raise NotFound('Document not found')
        positions = Position.objects.filter(id__in=qual_diplomas.list_positions)
        sailor = keys.filter(qualification_documents__overlap=[qual_diplomas.id]).first()
        proof = None
        date_start_proof = ''
        date_end_proof = ''
        if qual_diplomas.type_document_id in [49, 1, 3, 4, 5]:
            try:
                proof = ProofOfWorkDiploma.objects.filter(
                    diploma=qual_diplomas).exclude(
                    status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                            magic_numbers.STATUS_CREATED_BY_AGENT,
                                            magic_numbers.STATUS_REMOVED_DOCUMENT]
                ).order_by('-date_start')[0]
                date_start_proof = proof.date_start
                date_end_proof = proof.date_end
            except (IndexError, AttributeError):
                pass
        if proof is not None:
            table = get_function_level_limitation_by_position(positions=qual_diplomas.list_positions,
                                                              language='ukr', sailor_key=sailor, obj=proof)
        else:
            table = get_function_level_limitation_by_position(positions=qual_diplomas.list_positions,
                                                              language='ukr', sailor_key=sailor, obj=qual_diplomas)
        profile = profile.get(id=sailor.profile)
        citizen_country = ''
        if sailor.citizen_passport:
            citizen_country = self.get_citizen_country(passport_ids=sailor.citizen_passport)
        try:
            photo = PhotoProfile.objects.get(id=qual_diplomas.photo)
            photo_name = photo.photo.name
        except (AttributeError, PhotoProfile.DoesNotExist, ValueError):
            photo_name = 'no_media.png'
        rule = ', '.join(list(RulesForPosition.objects.filter(
            position_id__in=qual_diplomas.list_positions).distinct('rule').values_list('rule__value', flat=True)))
        try:
            rank = Rank.objects.get(id=qual_diplomas.rank_id)
            rank = {'ukr': rank.name_ukr, 'eng': rank.name_eng}
        except Rank.DoesNotExist:
            rank = {}
        position = {'ukr': list(positions.values_list('name_ukr', flat=True)),
                    'eng': list(positions.values_list('name_eng', flat=True))}
        try:
            status = {'ukr': proof.status_document.name_ukr, 'eng': proof.status_document.name_eng}
        except AttributeError:
            status = {'ukr': qual_diplomas.status_document.name_ukr, 'eng': qual_diplomas.status_document.name_eng}
        sex = {'ukr': profile.sex.value_ukr, 'eng': profile.sex.value_eng}
        datetime = localtime(timezone.now()).strftime('%d.%m.%Y %H:%M:%S')
        sailor_full_name = profile.get_full_name_to_date(qual_diplomas.date_start)
        response = {'number_document': qual_diplomas.get_number, 'status': status,
                    'name_ukr': sailor_full_name['ukr'], 'name_eng': sailor_full_name['eng'],
                    'date_birth': profile.date_birth, 'citizenship': citizen_country,
                    'sex': sex, 'photo': photo_name, 'date_issued': qual_diplomas.date_start,
                    'date_terminate': date_end_proof or qual_diplomas.date_end or '',
                    'date_start_proof': date_start_proof,
                    'date_end_proof': date_end_proof, 'rank': rank, 'position': position,
                    'func_level_limit': table, 'rule': rule,
                    'history': self.get_history(qual_diplomas, 'qualificationdocument'),
                    'type_document': {'eng': qual_diplomas.type_document.name_eng,
                                      'ukr': qual_diplomas.type_document.name_ukr},
                    'time_check': datetime}
        return response

    def get_data_ntz_certificate(self, profile=None, keys=None, number_document=None):
        try:
            ntz_filtering = {'ntz_number': number_document}
            all_ntz = list(keys.values_list('sertificate_ntz', flat=True))
            all_ntz = filter(None, all_ntz)
            all_ntz = list(itertools.chain.from_iterable(all_ntz))
            found_ntz = CertificateETI.objects.filter(id__in=all_ntz, **ntz_filtering).exclude(
                status_document__for_service='ETI').exclude(
                status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                        magic_numbers.STATUS_CREATED_BY_AGENT,
                                        magic_numbers.STATUS_REMOVED_DOCUMENT]
            )
            if found_ntz.exists():
                ntz_certificate = found_ntz.first()
                sailor = keys.get(sertificate_ntz__overlap=[ntz_certificate.id])
            else:
                raise NotFound('Document not found')
        except (ValueError, TypeError, AttributeError):
            raise NotFound('Document not found')
        profile = profile.get(id=sailor.profile)
        citizen_country = ''
        if sailor.citizen_passport:
            citizen_country = self.get_citizen_country(passport_ids=sailor.citizen_passport)
        status = {'ukr': ntz_certificate.status_document.name_ukr, 'eng': ntz_certificate.status_document.name_eng}
        course = {'ukr': ntz_certificate.course_training.name_ukr, 'eng': ntz_certificate.course_training.name_eng}
        ntz_name = {'ukr': ntz_certificate.ntz.name_ukr, 'eng': ntz_certificate.ntz.name_eng}
        sex = {'ukr': profile.sex.value_ukr, 'eng': profile.sex.value_eng}
        datetime = localtime(timezone.now()).strftime('%d.%m.%Y %H:%M:%S')
        sailor_full_name = profile.get_full_name_to_date(ntz_certificate.date_start)
        return {
            'number_document': ntz_certificate.ntz_number,
            'name_ukr': sailor_full_name['ukr'], 'name_eng': sailor_full_name['eng'],
            'date_birth': profile.date_birth, 'citizenship': citizen_country, 'date_issued': ntz_certificate.date_start,
            'date_end': ntz_certificate.date_end, 'course': course, 'ntz_name': ntz_name, 'sex': sex, 'status': status,
            'history': self.get_history(ntz_certificate, 'certificateeti'), 'type_document': {'eng': 'Certificate',
                                                                                              'ukr': 'Сертифікат'},
            'time_check': datetime
        }

    def get_data_medical_certificate(self, profile=None, keys=None, number_document=None):
        try:
            med_filtering = {'number': number_document}
            all_medical = list(keys.values_list('medical_sertificate', flat=True))
            all_medical = filter(None, all_medical)
            all_medical = list(itertools.chain.from_iterable(all_medical))
            found_medical = MedicalCertificate.objects.filter(id__in=all_medical, **med_filtering).exclude(
                status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                        magic_numbers.STATUS_CREATED_BY_AGENT,
                                        magic_numbers.STATUS_REMOVED_DOCUMENT]
            )
            if found_medical.exists():
                medical_certificate = found_medical.first()
                sailor = keys.get(medical_sertificate__overlap=[medical_certificate.id])
            else:
                raise NotFound('Document not found')
        except (ValueError, TypeError, AttributeError):
            raise NotFound('Document not found')
        profile = profile.get(id=sailor.profile)
        citizen_country = ''
        if sailor.citizen_passport:
            citizen_country = self.get_citizen_country(passport_ids=sailor.citizen_passport)
        status = {'ukr': medical_certificate.status_document.name_ukr,
                  'eng': medical_certificate.status_document.name_eng}
        position = {'ukr': medical_certificate.position.name_ukr, 'eng': medical_certificate.position.name_eng}
        limitation = {'ukr': medical_certificate.limitation.name_ukr, 'eng': medical_certificate.limitation.name_eng}
        sex = {'ukr': profile.sex.value_ukr, 'eng': profile.sex.value_eng}
        datetime = localtime(timezone.now()).strftime('%d.%m.%Y %H:%M:%S')
        sailor_full_name = profile.get_full_name_to_date(medical_certificate.date_start)
        return {
            'number_document': medical_certificate.number, 'name_ukr': sailor_full_name['ukr'],
            'name_eng': sailor_full_name['eng'], 'date_birth': profile.date_birth,
            'date_start': medical_certificate.date_start, 'date_end': medical_certificate.date_end,
            'citizenship': citizen_country, 'position': position, 'limitation': limitation, 'sex': sex,
            'status': status, 'history': self.get_history(medical_certificate, 'medicalcertificate'),
            'type_document': {'eng': 'Medical certificate', 'ukr': 'Медичне свідоцтво'},
            'time_check': datetime
        }


class DocumentsQRPublic(AbstractView):
    """Документы отдаваемые при запросе через QR код"""

    def get_public_documents(self, sailor_id):
        response = {}
        documents = {}
        try:
            sailor = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        profile = Profile.objects.get(id=sailor.profile)
        citizen_country = ''
        if sailor.citizen_passport:
            citizen_country = self.get_citizen_country(passport_ids=sailor.citizen_passport)
        response.update({'name_ukr': profile.get_full_name_ukr, 'name_eng': profile.get_full_name_eng,
                         'date_birth': profile.date_birth, 'citizen_country': citizen_country})
        response['sex'] = {'ukr': profile.sex.value_ukr, 'eng': profile.sex.value_eng}
        documents.update({'qual_documents': self.qual_documents(sailor)})
        documents.update({'ntz': self.ntz_documents(sailor)})
        documents.update({'medical': self.medical_documents(sailor)})
        response['documents'] = documents
        return response

    def qual_documents(self, sailor):
        qual_doc = []
        if sailor.qualification_documents is None:
            return qual_doc
        for qual_diplomas in QualificationDocument.objects.filter(id__in=sailor.qualification_documents).exclude(
                type_document_id=16).exclude(
            status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                    magic_numbers.STATUS_CREATED_BY_AGENT,
                                    magic_numbers.STATUS_REMOVED_DOCUMENT]
        ):
            positions = Position.objects.filter(id__in=qual_diplomas.list_positions)
            proof = None
            date_start_proof = ''
            date_end_proof = ''
            if qual_diplomas.type_document_id in [49, 1, 3, 4, 5]:
                try:
                    proof = ProofOfWorkDiploma.objects.filter(diploma=qual_diplomas).exclude(
                        status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                                magic_numbers.STATUS_CREATED_BY_AGENT]
                    ).order_by('-date_start')[0]
                    date_start_proof = proof.date_start
                    date_end_proof = proof.date_end
                except (IndexError, AttributeError):
                    pass
            if proof is not None:
                table = get_function_level_limitation_by_position(positions=qual_diplomas.list_positions,
                                                                  language='ukr', sailor_key=sailor, obj=proof)
            else:
                table = get_function_level_limitation_by_position(positions=qual_diplomas.list_positions,
                                                                  language='ukr', sailor_key=sailor, obj=qual_diplomas)
            try:
                photo = PhotoProfile.objects.get(id=qual_diplomas.photo)
                photo_name = photo.photo.name
            except (AttributeError, PhotoProfile.DoesNotExist, ValueError):
                photo_name = 'no_media.png'
            rule = ', '.join(list(RulesForPosition.objects.filter(
                position_id__in=qual_diplomas.list_positions).distinct('rule').values_list('rule__value', flat=True)))
            try:
                rank = Rank.objects.get(id=qual_diplomas.rank_id)
                rank = {'ukr': rank.name_ukr, 'eng': rank.name_eng}
            except Rank.DoesNotExist:
                rank = {}
            position = {'ukr': list(positions.values_list('name_ukr', flat=True)),
                        'eng': list(positions.values_list('name_eng', flat=True))}
            try:
                status = {'ukr': proof.status_document.name_ukr, 'eng': proof.status_document.name_eng}
            except AttributeError:
                status = {'ukr': qual_diplomas.status_document.name_ukr, 'eng': qual_diplomas.status_document.name_eng}
            qual_doc.append({'number_document': qual_diplomas.get_number, 'status': status,
                             'photo': photo_name, 'date_issued': qual_diplomas.date_start,
                             'date_terminate': date_end_proof or qual_diplomas.date_end or '',
                             'date_start_proof': date_start_proof, 'date_end_proof': date_end_proof,
                             'rank': rank, 'position': position, 'func_level_limit': table, 'rule': rule,
                             'history': self.get_history(qual_diplomas, 'qualificationdocument'),
                             'type_document': {'eng': qual_diplomas.type_document.name_eng,
                                               'ukr': qual_diplomas.type_document.name_ukr}
                             })
        return qual_doc

    def ntz_documents(self, sailor):
        ntz = []
        if sailor.sertificate_ntz is None:
            return ntz
        found_ntz = CertificateETI.objects.filter(id__in=sailor.sertificate_ntz).exclude(
            status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                    magic_numbers.STATUS_CREATED_BY_AGENT,
                                    magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        for ntz_certificate in found_ntz:
            status = {'ukr': ntz_certificate.status_document.name_ukr, 'eng': ntz_certificate.status_document.name_eng}
            course = {'ukr': ntz_certificate.course_training.name_ukr, 'eng': ntz_certificate.course_training.name_eng}
            ntz_name = {'ukr': ntz_certificate.ntz.name_ukr, 'eng': ntz_certificate.ntz.name_eng}
            ntz.append({
                'number_document': ntz_certificate.ntz_number, 'date_issued': ntz_certificate.date_start,
                'date_end': ntz_certificate.date_end, 'course': course, 'ntz_name': ntz_name, 'status': status,
                'type_document': {'eng': 'Certificate', 'ukr': 'Сертифікат'},
                'history': self.get_history(ntz_certificate, 'certificateeti')
            })
        return ntz

    def medical_documents(self, sailor):
        medical = []
        if sailor.medical_sertificate is None:
            return medical
        found_medical = MedicalCertificate.objects.filter(id__in=sailor.medical_sertificate).exclude(
            status_document_id__in=[magic_numbers.VERIFICATION_STATUS,
                                    magic_numbers.STATUS_CREATED_BY_AGENT,
                                    magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        for medical_certificate in found_medical:
            status = {'ukr': medical_certificate.status_document.name_ukr,
                      'eng': medical_certificate.status_document.name_eng}
            position = {'ukr': medical_certificate.position.name_ukr, 'eng': medical_certificate.position.name_eng}
            limitation = {'ukr': medical_certificate.limitation.name_ukr,
                          'eng': medical_certificate.limitation.name_eng}
            medical.append({
                'number_document': medical_certificate.number,
                'date_start': medical_certificate.date_start, 'date_end': medical_certificate.date_end,
                'position': position, 'limitation': limitation, 'status': status,
                'type_document': {'eng': 'Medical certificate', 'ukr': 'Медичне свідоцтво'},
                'history': self.get_history(medical_certificate, 'medicalcertificate'),
            })
        return medical


class CheckQr(APIView):
    """Проверка QR кода"""

    def get(self, request, *args, **kwargs):
        payload = kwargs.get('payload')
        if not payload:
            return Response(status=404)

        key = base64.b64decode(settings.CRYPTO_KEY)
        fernet_alg = Fernet(key)

        try:
            sailor_data = fernet_alg.decrypt(payload.encode()).decode()
            sailor_id, creation_date = re.search(r'^id=(\d+)&date=([\d-]+)$', sailor_data).groups()
            current_date = tz.now().date().isoformat()
            if current_date != creation_date:
                return Response({'msg': 'Bad request. Token\'s TTL is expired'}, status=403)
            return Response(DocumentsQRPublic().get_public_documents(sailor_id))
        except AttributeError:
            return Response({'msg': 'Bad request. Data incomplete'}, status=404)
        except (InvalidToken, InvalidSignature):
            return Response({'msg': 'Bad request. Token is invalid or was changed'}, status=403)
