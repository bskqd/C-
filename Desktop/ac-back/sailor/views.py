import json
import logging
import os
import re
from copy import deepcopy
from datetime import datetime, date
from itertools import chain

import openpyxl as xl
import xlrd
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import CharField, Q, Value, F
from django.db.models.functions import Cast, Concat
from django.forms import model_to_dict
from django.http import Http404
from django.utils import timezone
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from openpyxl.utils.exceptions import InvalidFileException
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

import sailor.document.serializers
import sailor.misc
import sailor.permissions
import sailor.serializers
import sailor.statement.tasks
import back_office.tasks
import sailor.statement.permissions
import sailor.statement.serializers
import sailor.tasks
from agent.models import AgentSailor
from agent.serializers import AgentSailorSerializer
from back_office.models import PacketItem
from cadets.models import StudentID
from communication.models import SailorKeys
from directory.models import (LevelQualification, Position, Speciality, TypeDocumentNZ, StatusDocument)
from itcs import magic_numbers
from mixins.core import FullSailorViewSet
from mixins.permission_mixins import IsBackOfficeUser
from reports.filters import ShortLinkResultPagination
from sailor.models import (DemandPositionDKK, OldName, Passport, PhotoProfile, Profile, Rating, SailorPassport,
                           CommentForVerificationDocument)
from sailor.statement.permissions import ApplicationSQCPermission
from user_profile.models import FullUserSailorHistory, UserProfile, UserSailorHistory
from user_profile.serializer import UserFullInfoSerializer
from . import serializers
from .document.models import (CertificateETI, Education, LineInServiceRecord, MedicalCertificate, ProofOfWorkDiploma,
                              ProtocolSQC, QualificationDocument, ServiceRecord)
from .filters import FullUserSailorHistoryFilter
from .serializers import FullUserSailorHistorySerializer
from .statement.models import (StatementSQC, StatementQualification, StatementAdvancedTraining,
                               StatementETI, StatementMedicalCertificate, StatementSailorPassport,
                               StatementServiceRecord)

logger = logging.getLogger('ac-back.ntz_cert')
sailor_not_exists_error = 'Sailor does not exists'

User = get_user_model()


class SailorMainInfoView(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.MainInfoTypeUserPermission,
        (sailor.permissions.MainInfoPermission | sailor.permissions.CheckHeadAgentProfile),
    )
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileMainInfoSerializer
    short_serializer = serializers.ShortMainInfoSerializer

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        try:
            key = SailorKeys.objects.get(id=filter_kwargs['pk'])
            profile = Profile.objects.get(id=key.profile)
            profile._key = key.pk
            self.check_object_permissions(self.request, profile)
        except (SailorKeys.DoesNotExist, Profile.DoesNotExist, ValueError):
            raise Http404
        UserSailorHistory.objects.create(user=self.request.user, sailor_key=key.id, date_open=timezone.now())
        return profile

    def perform_destroy(self, instance):
        _instance = deepcopy(instance)
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        sailor.tasks.save_history.s(user_id=self.request.user, sailor_key_id=self.kwargs[lookup_url_kwarg],
                                    module='Profile', action_type='delete',
                                    content_obj=_instance, serializer=serializers.ProfileMainInfoSerializer,
                                    old_obj=_instance).apply_async(serializer='pickle')
        instance.delete()

    @action(detail=True, methods=['get'])
    @swagger_auto_schema(responses={'200': serializers.ShortMainInfoSerializer})
    def short(self, request, *args, **kwargs):
        return Response(self.short_serializer(self.get_object()).data)


class SearchSailor(APIView):
    permission_classes = (IsAuthenticated, sailor.permissions.SearchSailorPermission)

    def get_number_documents(self, key: SailorKeys):

        def length(param):
            try:
                resp = len(param)
            except TypeError:
                resp = 0
            return resp

        num_documents = (length(key.qualification_documents) + length(key.service_records) + length(key.education) +
                         length(key.sertificate_ntz) + length(key.medical_sertificate) + length(key.sailor_passport) +
                         length(key.statement_dkk) + length(key.experience_docs) + length(key.protocol_dkk) +
                         length(key.statement_dkk) + length(key.statement_qualification))
        return num_documents

    def search(self, query, is_sorting=True):
        response = []

        qs = Profile.objects.annotate(fullname_ukr=Concat('last_name_ukr', Value(' '), 'first_name_ukr', Value(' '),
                                                          'middle_name_ukr'),
                                      fullname_eng=Concat('last_name_eng', Value(' '),
                                                          'first_name_eng', Value(' '), 'middle_name_eng'))
        profile = qs.filter(Q(fullname_ukr__icontains=query))[:20]
        if profile:
            for prof in profile:
                key = SailorKeys.objects.filter(profile=prof.id).first()
                if not key:
                    prof.delete()
                    continue
                try:
                    passport = Passport.by_sailor.filter_by_sailor(sailor_key=key).first()
                    serial_passport = passport.serial
                    issued_by_passport = passport.issued_by
                    date_passport = passport.date
                except (Passport.DoesNotExist, AttributeError, TypeError, IndexError):
                    serial_passport = None
                    issued_by_passport = None
                    date_passport = None
                resp_dict = {
                    'id': key.id, 'first_name_eng': prof.first_name_eng,
                    'first_name_ukr': prof.first_name_ukr, 'last_name_ukr': prof.last_name_ukr,
                    'last_name_eng': prof.last_name_eng, 'middle_name_ukr': prof.middle_name_ukr,
                    'middle_name_eng': prof.middle_name_eng, 'date_birth': prof.date_birth,
                    'passport_serial': serial_passport, 'passport_issued_by': issued_by_passport,
                    'passport_date': date_passport
                }
                if is_sorting is True:
                    num_documents = self.get_number_documents(key)
                    resp_dict['num_documents'] = num_documents
                response.append(resp_dict)
        passports = Passport.objects.filter(Q(serial__icontains=query) | Q(inn__icontains=query))[:20]
        if passports:
            passport_list_id = list(passports.values_list('id', flat=True))
            keys = SailorKeys.objects.filter(citizen_passport__overlap=passport_list_id)
            for key in keys:
                passport = [passport for passport in passports if passport.id == key.citizen_passport[0]][0]
                try:
                    profile = Profile.objects.get(id=key.profile)
                except SailorKeys.DoesNotExist:
                    continue
                resp_dict = {'id': key.id, 'first_name_eng': profile.first_name_eng,
                             'first_name_ukr': profile.first_name_ukr, 'last_name_ukr': profile.last_name_ukr,
                             'last_name_eng': profile.last_name_eng, 'middle_name_ukr': profile.middle_name_ukr,
                             'middle_name_eng': profile.middle_name_eng, 'date_birth': profile.date_birth,
                             'passport_serial': passport.serial, 'passport_issued_by': passport.issued_by,
                             'passport_date': passport.date}
                if is_sorting is True:
                    num_documents = self.get_number_documents(key)
                    resp_dict['num_documents'] = num_documents
                response.append(resp_dict)
        sailor_keys = SailorKeys.objects.annotate(id_as_char=Cast('id', CharField())).filter(id_as_char__contains=query)
        if sailor_keys:
            profile_qs = Profile.objects.filter(id__in=list(sailor_keys.values_list('profile', flat=True)))
            for key in sailor_keys:
                profile = profile_qs.get(id=key.profile)
                try:
                    passport = Passport.objects.get(id=key.citizen_passport[0])
                    serial_passport = passport.serial
                    issued_by_passport = passport.issued_by
                    date_passport = passport.date
                except (Passport.DoesNotExist, AttributeError, TypeError, IndexError):
                    serial_passport = None
                    issued_by_passport = None
                    date_passport = None
                resp_dict = {
                    'id': key.id, 'first_name_eng': profile.first_name_eng,
                    'first_name_ukr': profile.first_name_ukr, 'last_name_ukr': profile.last_name_ukr,
                    'last_name_eng': profile.last_name_eng, 'middle_name_ukr': profile.middle_name_ukr,
                    'middle_name_eng': profile.middle_name_eng, 'date_birth': profile.date_birth,
                    'passport_serial': serial_passport, 'passport_issued_by': issued_by_passport,
                    'passport_date': date_passport
                }
                if is_sorting is True:
                    num_documents = self.get_number_documents(key)
                    resp_dict['num_documents'] = num_documents
                response.append(resp_dict)
        if is_sorting is True:
            response = sorted(response, key=lambda i: i['num_documents'], reverse=True)
        return Response(response)

    def get(self, request, *args, **kwargs):
        query = kwargs['query']
        is_sorting = kwargs['is_sorting']
        if is_sorting == 'true':
            return self.search(is_sorting=True, query=query)

    def post(self, request):
        query = request.data.get('query')
        is_sorting = request.data.get('is_sorting', True)
        return self.search(query=query, is_sorting=is_sorting)


class SailorPhotoView(APIView):
    permission_classes = ((sailor.permissions.MainInfoPermission | sailor.permissions.CheckHeadAgentGroup),
                          IsAuthenticated)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = serializers.PhotoProfileSerializer(data=request.data)
        try:
            sailor_id = request.data['sailor_id']
        except KeyError:
            sailor_id = request.POST.get('sailor_id')

        if file_serializer.is_valid():
            file_serializer.save()
            sailor_instance = Profile.objects.get(id=sailor_id)
            sailor_instance.photo = file_serializer.data['id']
            sailor_instance.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SailorPassportView(FullSailorViewSet):
    """Паспорт моряка"""
    permission_classes = (IsAuthenticated,
                          (sailor.permissions.SailorPassportPermission |
                           sailor.permissions.PostVerificationChangeStatusPermission),
                          (sailor.permissions.CheckHeadAgentGroup |
                           sailor.permissions.CheckAgentPermission))
    queryset = SailorPassport.objects.select_related(
        'country', 'port', 'status_document'
    ).prefetch_related().all()
    serializer_class = serializers.SailorPassportSerializer
    model = SailorPassport

    def get_permissions(self):
        print(self.name)
        if self.get_view_name() == 'Issue document':
            return [sailor.permissions.CreateNewSailorPassportPermission()]
        return super().get_permissions()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SailorPassport.objects.none()

        sailor_pk = self.kwargs.get('sailor_pk') or self.kwargs.get('pk')
        try:
            keys = SailorKeys.objects.get(id=sailor_pk)
        except (SailorKeys.DoesNotExist, ValueError):
            raise ValidationError(sailor_not_exists_error)
        qs = self.queryset.filter(
            id__in=keys.sailor_passport
        ).order_by('-id')
        userprofile: UserProfile = self.request.user.userprofile
        if userprofile.type_user in [userprofile.MEDICAL]:
            return qs.filter(status_document_id=2)
        elif userprofile.type_user in [userprofile.VERIFIER, userprofile.SECRETARY_SQC, userprofile.DPD,
                                       userprofile.MARAD, userprofile.ETI_EMPLOYEE, userprofile.SECRETARY_ATC]:
            qs = qs.exclude(status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT,
                                                    magic_numbers.STATUS_REMOVED_DOCUMENT])
        elif userprofile.type_user in [UserProfile.BACK_OFFICE] or self.request.user.is_superuser:
            return qs
        return qs.exclude(status_document_id=magic_numbers.STATUS_REMOVED_DOCUMENT)

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        status_document_id = self.request.user.userprofile.verification_status_by_user
        ser = serializer.save(status_document_id=status_document_id, is_new_document=False)
        sailor_qs.sailor_passport.append(ser.id)
        sailor_qs.save(update_fields=['sailor_passport'])
        if ser.status_document.pk == magic_numbers.VERIFICATION_STATUS:
            sailor.misc.create_verification_status_for_document(ser)
        sailor.tasks.save_history.s(user_id=self.request.user.id, module='SailorPassport', action_type='create',
                                    content_obj=ser, serializer=serializers.SailorPassportSerializer, new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')

    @action(methods=['get'], detail=False, url_name='choice_sailor_passport', url_path='choice')
    def choice_sailor_passport(self, request, *args, **kwargs):
        """
        Returns a dictionary for choosing whether a sailor passport is required
        """
        response = [
            {'id': 0, 'name_ukr': 'Не потрібна', 'name_eng': 'Do not need'},
            # {'id': 1, 'name_ukr': 'Потрібна за 20 днів', 'name_eng': 'Needed in 20 days'},
            {'id': 2, 'name_ukr': 'Потрібна за 7 днів', 'name_eng': 'Needed in 7 days'}
        ]
        sailor_pk = self.kwargs.get('sailor_pk')
        sailor_qs = get_object_or_404(SailorKeys, id=sailor_pk)
        sailor_passport = SailorPassport.objects.filter(
            id__in=sailor_qs.sailor_passport
        ).order_by('-date_end')
        not_renewal_sailor_passport = sailor_passport.order_by('-date_start')
        last_passport: SailorPassport = not_renewal_sailor_passport.first()
        can_renewal = (last_passport and
                       last_passport.status_document_id in [magic_numbers.status_qual_doc_expired,
                                                            magic_numbers.status_qual_doc_valid]
                       and not last_passport.date_renewal)
        if can_renewal:
            response += [
                # {'id': 3, 'name_ukr': 'Подовження за 20 днів', 'name_eng': 'Continue in 20 days'},
                {'id': 4, 'name_ukr': 'Подовження за 7 днів', 'name_eng': 'Continue in 7 days'}
            ]
        return Response(response)

    @action(methods=['post'], detail=False, )
    @swagger_auto_schema(request_body=sailor.serializers.CreateNewServiceRecordSerializer)
    def issue_document(self, request, sailor_pk):
        serializer = sailor.serializers.CreateNewServiceRecordSerializer(data=request.data,
                                                                         context={'request': request,
                                                                                  'view': self})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        statement: StatementSailorPassport = validated_data.get('statement')
        passport: SailorPassport = validated_data.pop('passport', None)
        user = self.request.user
        if statement.type_receipt in [1, 2]:
            date_start = date.today()
            date_end = date_start + relativedelta(years=5)
            captain = statement.port.fiocapitanofport_set.first().name_ukr
            instance = serializer.save(date_start=date_start,
                                       date_end=date_end,
                                       port_id=statement.port.pk,
                                       status_document_id=SailorPassport.StatusDocument.VALID,
                                       photo=statement.photo,
                                       captain=captain,
                                       country_id=2)
            sailor.statement.tasks.disable_old_sailor_passport.s(
                sailor_id=sailor_pk,
                exclude_id=instance.pk).apply_async()
        else:
            old_instance = deepcopy(passport)
            validated_data['status_document'] = StatusDocument.objects.get(pk=SailorPassport.StatusDocument.VALID)
            validated_data['date_renewal'] = passport.date_start + relativedelta(year=5)
            instance = serializer.update(instance=passport, validated_data=validated_data)
            sailor.tasks.save_history.s(user_id=user.pk,
                                        module='SailorPassport',
                                        action_type='edit',
                                        content_obj=instance,
                                        serializer=self.serializer_class,
                                        new_obj=instance,
                                        old_obj=old_instance,
                                        get_sailor=True).apply_async(serializer='pickle')
        back_office.tasks.update_sailor_passport_in_packet.s(sailor_passport_id=instance.pk,
                                                             sailor_id=sailor_pk).apply_async()
        sailor.tasks.save_history.s(user_id=user.pk,
                                    module='SailorPassport',
                                    action_type='create',
                                    content_obj=instance,
                                    serializer=self.serializer_class,
                                    new_obj=instance,
                                    get_sailor=True).apply_async(serializer='pickle')
        return Response(self.serializer_class(instance=instance).data)

    @action(methods=['get'], detail=False)
    def allowed_to_continue(self, request, sailor_pk):
        queryset = self.get_queryset().filter(Q(status_document_id__in=[SailorPassport.StatusDocument.VALID,
                                                                        SailorPassport.StatusDocument.EXPIRED]) &
                                              Q(Q(date_renewal__isnull=True) | Q(date_renewal=F('date_end'))))
        return Response(self.serializer_class(instance=queryset, many=True).data)


class CountDocSailor(APIView):
    permission_classes = (IsAuthenticated,)
    """
    Count all docs for sailor
    """
    type_user = None
    userprofile = None

    def get(self, request, sailor_pk):
        self.userprofile = self.request.user.userprofile
        self.type_user = self.userprofile.type_user
        try:
            keys = SailorKeys.objects.get(id=sailor_pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        keys.save(force_update=True)
        response = {
            'passports': self.count_passports(keys),
            'education': self.count_education(keys),
            'ntz': self.count_ntz(keys),
            'dpo_documents': self.count_dpd_documents(keys),
            'experience': self.count_experience_document(keys),
            'medical_sertificate': self.count_medical_documents(keys),
            'dkk': self.count_documents_sqc(keys),
            'packet_item': self.count_packet_item(keys),
        }
        return Response(response)

    def count_passports(self, sailor_qs):
        sailor_passport_count = self.count_sailor_passport(sailor_qs)
        statement_sailor_passport_count = self.count_statement_sailor_passport(sailor_qs)
        return {'sum': sailor_passport_count + statement_sailor_passport_count + 1,
                'passport_sailor': sailor_passport_count, 'passport': 1,
                'statement_sailor_passport': statement_sailor_passport_count}

    def count_education(self, sailor_qs):
        document_about_education_count = self.count_document_about_education(sailor_qs)
        student_id_count = self.count_student_id(sailor_qs)
        statement_adv_training_count = self.count_statement_adv_training(sailor_qs)
        return {'main': document_about_education_count, 'student': student_id_count,
                'statement_adv_training': statement_adv_training_count,
                'sum': document_about_education_count + student_id_count + statement_adv_training_count}

    def count_dpd_documents(self, sailor_qs):
        qualification_document_count = self.count_qualification_documents(sailor_qs)
        statement_qualification = self.count_statement_qualification(sailor_qs)
        return {'qual_doc': qualification_document_count, 'statement_qual_doc': statement_qualification}

    def count_ntz(self, sailor_qs):
        certificate_eti_count = self.count_certificate_eti(sailor_qs)
        statement_eti_count = self.count_statement_eti(sailor_qs)
        return {'certificate': certificate_eti_count, 'statement_eti': statement_eti_count,
                'sum': certificate_eti_count + statement_eti_count}

    def count_experience_document(self, sailor_qs):
        service_record_count = self.count_service_record(sailor_qs)
        statement_serv_rec_count = self.count_statement_service_record(sailor_qs)
        experience_doc_count = self.count_experience_doc(sailor_qs)
        return {'service_record': service_record_count, 'experience_doc': experience_doc_count,
                'statement_service_record': statement_serv_rec_count,
                'sum': service_record_count + experience_doc_count + statement_serv_rec_count}

    def count_documents_sqc(self, sailor_qs):
        statement_sqc_count = self.count_statement_sqc(sailor_qs)
        protocol_sqc_count = self.count_protocol_sqc(sailor_qs)
        demand_position_count = self.count_demand_position(sailor_qs)
        return {'statement_dkk': statement_sqc_count,
                'protocol_dkk': protocol_sqc_count, 'demand_position': demand_position_count,
                'sum': statement_sqc_count + protocol_sqc_count + demand_position_count}

    def count_medical_documents(self, sailor_qs):
        medical_certificate = self.count_medical_certificate(sailor_qs)
        statement_med_cert_count = self.count_statement_med_cert(sailor_qs)
        return {'medical_sertificate': medical_certificate, 'statement_med_cert': statement_med_cert_count,
                'sum': medical_certificate + statement_med_cert_count}

    def count_packet_item(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.MEDICAL, UserProfile.SECRETARY_EDUCATION,
                              UserProfile.REGISTRY, UserProfile.VERIFIER, UserProfile.MARAD, UserProfile.SECRETARY_ATC]:
            return 0
        return len(sailor_qs.packet_item)

    def count_sailor_passport(self, sailor_qs):
        sailor_passport = SailorPassport.objects.filter(
            id__in=sailor_qs.sailor_passport
        ).exclude(
            status_document_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        if self.type_user in [UserProfile.VERIFIER, UserProfile.SECRETARY_SQC, UserProfile.DPD,
                              UserProfile.MARAD, UserProfile.ETI_EMPLOYEE, UserProfile.SECRETARY_ATC]:
            sailor_passport = sailor_passport.exclude(
                status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT]
            )
        return sailor_passport.count()

    def count_statement_sailor_passport(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.SECRETARY_EDUCATION, UserProfile.REGISTRY,
                              UserProfile.MEDICAL, UserProfile.VERIFIER, UserProfile.DPD, UserProfile.SECRETARY_ATC]:
            return 0
        else:
            statement_sailor_passport = StatementSailorPassport.objects.filter(
                id__in=sailor_qs.statement_sailor_passport
            ).exclude(
                status_document_id__in=[magic_numbers.status_statement_canceled, magic_numbers.STATUS_REMOVED_DOCUMENT]
            )
        return statement_sailor_passport.count()

    def count_document_about_education(self, sailor_qs):
        if self.type_user in [UserProfile.MEDICAL]:
            return 0
        document_about_education = Education.objects.filter(id__in=sailor_qs.education).exclude(
            status_document_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        if self.type_user in [UserProfile.VERIFIER, UserProfile.SECRETARY_SQC, UserProfile.DPD,
                              UserProfile.MEDICAL, UserProfile.MARAD, UserProfile.ETI_EMPLOYEE,
                              UserProfile.SECRETARY_ATC]:
            document_about_education = document_about_education.exclude(
                status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT]
            )
        return document_about_education.count()

    def count_student_id(self, sailor_qs):
        if self.type_user in [UserProfile.MEDICAL, UserProfile.REGISTRY, UserProfile.VERIFIER, UserProfile.DPD,
                              UserProfile.SECRETARY_SQC, UserProfile.SECRETARY_ATC]:
            return 0
        return len(sailor_qs.students_id)

    def count_statement_adv_training(self, sailor_qs):
        if self.type_user in [UserProfile.MEDICAL, UserProfile.REGISTRY, UserProfile.VERIFIER, UserProfile.DPD]:
            return 0
        statement_adv_training = StatementAdvancedTraining.objects.filter(
            id__in=sailor_qs.statement_advanced_training
        ).exclude(
            status_document_id__in=[magic_numbers.status_statement_canceled, magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        if self.type_user == UserProfile.SECRETARY_ATC:
            statement_adv_training = statement_adv_training.filter(
                educational_institution=self.userprofile.education_institution
            )
        return statement_adv_training.count()

    def count_qualification_documents(self, sailor_qs):
        if self.type_user in [UserProfile.SECRETARY_EDUCATION]:
            return 0
        qualification_document = QualificationDocument.objects.filter(
            id__in=sailor_qs.qualification_documents
        ).exclude(
            status_document_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT])
        qualification_document_qs = qualification_document.filter(type_document_id__in=[3, 49])
        proof_of_diplomas = ProofOfWorkDiploma.objects.filter(
            diploma__in=qualification_document_qs
        ).exclude(
            status_document_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        if self.type_user in [UserProfile.VERIFIER, UserProfile.SECRETARY_SQC, UserProfile.DPD,
                              UserProfile.MEDICAL, UserProfile.MARAD, UserProfile.ETI_EMPLOYEE,
                              UserProfile.SECRETARY_ATC]:
            qualification_document = qualification_document.exclude(
                status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT]
            )
            proof_of_diplomas = proof_of_diplomas.exclude(
                status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT]
            )
        return qualification_document.count() + proof_of_diplomas.count()

    def count_statement_qualification(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.SECRETARY_EDUCATION, UserProfile.SECRETARY_ATC]:
            return 0
        statement_qualification = StatementQualification.objects.filter(
            id__in=sailor_qs.statement_qualification
        ).exclude(
            status_document_id__in=[magic_numbers.status_statement_canceled, magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        return statement_qualification.count()

    def count_certificate_eti(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.MEDICAL, UserProfile.SECRETARY_EDUCATION,
                              UserProfile.DPD, UserProfile.SECRETARY_ATC]:
            return 0
        certificate_eti = CertificateETI.objects.filter(
            id__in=sailor_qs.sertificate_ntz
        ).exclude(
            Q(status_document_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT]) | Q(ntz_number=-1)
        )
        return certificate_eti.count()

    def count_statement_eti(self, sailor_qs):
        if self.type_user in [UserProfile.MEDICAL, UserProfile.SECRETARY_EDUCATION, UserProfile.VERIFIER,
                              UserProfile.DPD, UserProfile.SECRETARY_ATC]:
            return 0
        statement_eti = StatementETI.objects.filter(
            id__in=sailor_qs.statement_eti
        ).exclude(
            status_document_id__in=[magic_numbers.status_statement_canceled, magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        if self.type_user == UserProfile.ETI_EMPLOYEE:
            statement_eti = statement_eti.filter(institution=self.userprofile.eti_institution)
        return statement_eti.count()

    def count_service_record(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.MEDICAL, UserProfile.DPD,
                              UserProfile.SECRETARY_ATC]:
            return 0
        service_record = ServiceRecord.objects.filter(
            id__in=sailor_qs.service_records
        ).exclude(
            status_document_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        if self.type_user in [UserProfile.VERIFIER, UserProfile.SECRETARY_SQC, UserProfile.DPD,
                              UserProfile.MEDICAL, UserProfile.MARAD]:
            service_record = service_record.exclude(status_document_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT])
        elif self.type_user in [UserProfile.DPD]:
            service_record = service_record.filter(status_document_id__in=[magic_numbers.status_qual_doc_valid,
                                                                           magic_numbers.VERIFICATION_STATUS])
        return service_record.count()

    def count_statement_service_record(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.MEDICAL, UserProfile.DPD,
                              UserProfile.SECRETARY_ATC]:
            return 0
        statement_serv_rec_count = StatementServiceRecord.objects.filter(
            id__in=sailor_qs.statement_service_records
        ).exclude(
            status_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        return statement_serv_rec_count.count()

    def count_experience_doc(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.MEDICAL, UserProfile.DPD,
                              UserProfile.SECRETARY_ATC]:
            return 0
        experience_doc = LineInServiceRecord.objects.filter(
            id__in=sailor_qs.experience_docs
        ).exclude(
            status_line_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        if self.type_user in [UserProfile.DPD, UserProfile.MEDICAL]:
            experience_doc = experience_doc.filter(status_line_id__in=[9, magic_numbers.VERIFICATION_STATUS])
        elif self.type_user in [UserProfile.VERIFIER, UserProfile.SECRETARY_SQC, UserProfile.DPD, UserProfile.MARAD]:
            experience_doc = experience_doc.exclude(status_line_id__in=[magic_numbers.STATUS_CREATED_BY_AGENT])
        return experience_doc.count()

    def count_statement_sqc(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.SECRETARY_EDUCATION, UserProfile.MEDICAL,
                              UserProfile.DPD, UserProfile.SECRETARY_ATC]:
            return 0
        statement_sqc = StatementSQC.objects.filter(
            id__in=sailor_qs.statement_dkk
        ).exclude(
            status_document_id__in=[magic_numbers.status_statement_canceled]
        )
        return statement_sqc.count()

    def count_protocol_sqc(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.SECRETARY_EDUCATION, UserProfile.MEDICAL,
                              UserProfile.SECRETARY_ATC]:
            return 0
        protocol_sqc = ProtocolSQC.objects.filter(
            id__in=sailor_qs.protocol_dkk
        ).exclude(
            status_document_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        return protocol_sqc.count()

    def count_demand_position(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.SECRETARY_EDUCATION, UserProfile.MEDICAL,
                              UserProfile.VERIFIER, UserProfile.DPD, UserProfile.SECRETARY_SQC]:
            return 0
        demand_position = DemandPositionDKK.objects.filter(
            id__in=sailor_qs.demand_position
        ).exclude(
            status_document_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        return demand_position.count()

    def count_medical_certificate(self, sailor_qs):
        if self.type_user in [UserProfile.SECRETARY_ATC]:
            return 0
        medical_certificate = MedicalCertificate.objects.filter(
            id__in=sailor_qs.medical_sertificate
        ).exclude(
            status_document_id__in=[magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        if self.type_user in [UserProfile.VERIFIER, UserProfile.SECRETARY_SQC, UserProfile.MARAD,
                              UserProfile.ETI_EMPLOYEE]:
            medical_certificate = medical_certificate.exclude(status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT)
        elif self.type_user in [UserProfile.MEDICAL]:
            medical_certificate = medical_certificate.filter(status_document_id=magic_numbers.status_qual_doc_valid)
        return medical_certificate.count()

    def count_statement_med_cert(self, sailor_qs):
        if self.type_user in [UserProfile.ETI_EMPLOYEE, UserProfile.SECRETARY_EDUCATION, UserProfile.REGISTRY,
                              UserProfile.VERIFIER, UserProfile.DPD, UserProfile.SECRETARY_ATC]:
            return 0
        statement_med_cert = StatementMedicalCertificate.objects.filter(
            id__in=sailor_qs.statement_medical_certificate
        ).exclude(
            status_document_id__in=[magic_numbers.status_statement_canceled, magic_numbers.STATUS_REMOVED_DOCUMENT]
        )
        return statement_med_cert.count()


class DemandPositionDKKView(FullSailorViewSet):
    permission_classes = (
        IsAuthenticated,
        ApplicationSQCPermission,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
    )
    queryset = DemandPositionDKK.objects.all()
    serializer_class = serializers.DemandPositionDKKSerializer
    model = DemandPositionDKK

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=int(sailor_id))
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        rank_id = serializer.initial_data['rank']
        list_positions = serializer.initial_data['list_positions']
        is_continue = sailor.misc.check_is_continue(sailor_qs=sailor_qs, list_positions=list_positions, rank_id=rank_id)
        status_document = magic_numbers.status_demand_pos_all_enough
        checking = sailor.misc.CheckSailorForPositionDKK(sailor=sailor_id, is_continue=is_continue,
                                                         list_position=list_positions, demand_position=True)
        documents = checking.get_docs_with_status()
        if bool(is_continue) is False:
            checking_exp = sailor.misc.CheckSailorExperience(sailor=sailor_id, list_position=list_positions)
            experience = checking_exp.check_experience_many_pos()
            if experience:
                is_experience = any(exp['value'] for exp in experience)
            else:
                is_experience = False
        else:
            from sailor.misc import check_continue_for_experience
            qual_docs = sailor.misc.get_qual_doc(sailor_qs)
            flat_list_position = list(chain.from_iterable(qual_docs.values_list('list_positions', flat=True)))
            check_exp = check_continue_for_experience(list_positions=list_positions, rank_id=rank_id,
                                                      ids_positions_in_qual_doc=flat_list_position)
            if check_exp['is_check_exp']:
                checking_exp = sailor.misc.CheckSailorExperience(sailor=sailor_id,
                                                                 list_position=check_exp['list_positions'])
                experience = checking_exp.check_experience_many_pos()
                if experience:
                    is_experience = any(exp['value'] for exp in experience)
                else:
                    is_experience = False
            else:
                is_experience = True
        if documents['not_exists_docs'] and is_experience is False:
            status_document = magic_numbers.status_demand_pos_all_not_enough
        elif documents['not_exists_docs']:
            status_document = magic_numbers.status_demand_pos_not_documents
        elif is_experience is False:
            status_document = magic_numbers.status_demand_pos_not_experience
        ser = serializer.save(status_document_id=status_document, is_continue=is_continue, is_experience=is_experience,
                              )
        all_docs = documents.get('all_docs', [])
        ser.related_docs = all_docs
        [ser.dependency_docs.add(doc) for doc in documents['not_exists_docs']]
        if sailor_qs.demand_position:
            sailor_qs.demand_position.append(ser.id)
            sailor_qs.save(update_fields=['demand_position'])
        else:
            sailor_qs.demand_position = [ser.id]
            sailor_qs.save(update_fields=['demand_position'])

        sailor.tasks.save_history.s(user_id=self.request.user.id, module='DemandPositionDKK', action_type='create',
                                    content_obj=ser, serializer=serializers.DemandPositionDKKSerializer, new_obj=ser,
                                    sailor_key_id=sailor_id).apply_async(serializer='pickle')

    @action(methods=['post'], detail=True)
    @swagger_auto_schema(operation_description='Work only with V2 version API',
                         operation_summary='Work only with V2 version API')
    def create_statement(self, request, *args, **kwargs):
        sailor_id = self.kwargs.get('sailor_pk')
        try:
            sailor_qs = SailorKeys.objects.get(id=self.kwargs.get('sailor_pk'))
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        demand_position = self.get_object()
        if demand_position.status_document_id != magic_numbers.status_demand_pos_all_enough:
            raise ValidationError('Not enough documents and/or experience')

        number = StatementSQC.generate_number()

        status_document = 25
        is_continue = demand_position.is_continue
        list_positions = demand_position.list_positions
        rank_id = demand_position.rank_id
        user = self.request.user
        branch_office = user.userprofile.branch_office
        statement_dkk = StatementSQC.objects.create(number=number, sailor=sailor_id, rank_id=rank_id,
                                                    list_positions=list_positions, is_continue=is_continue,
                                                    status_document_id=status_document,
                                                    branch_office=branch_office)
        _demand_position = deepcopy(demand_position)
        demand_position.delete()
        if sailor_qs.statement_dkk:
            sailor_qs.statement_dkk.append(statement_dkk.id)
            sailor_qs.demand_position.remove(_demand_position.id)
            sailor_qs.save(update_fields=['statement_dkk', 'demand_position'])
        else:
            sailor_qs.statement_dkk = [statement_dkk.id]
            sailor_qs.demand_position.remove(_demand_position.id)
            sailor_qs.save(update_fields=['statement_dkk', 'demand_position'])

        sailor.tasks.save_history.s(user_id=self.request.user.id, module='StatementDKK', action_type='create',
                                    content_obj=statement_dkk,
                                    serializer=sailor.statement.serializers.StatementDKKSerializer,
                                    new_obj=statement_dkk, sailor_key_id=sailor_id).apply_async(serializer='pickle')

        sailor.tasks.save_history.s(user_id=self.request.user.id, module='DemandPositionDKK', action_type='delete',
                                    content_obj=_demand_position, serializer=serializers.DemandPositionDKKSerializer,
                                    old_obj=_demand_position, sailor_key_id=sailor_id).apply_async(serializer='pickle')

        return Response({'status': 'success', 'description': 'statement_dkk is created'})


class CitizenPassportView(FullSailorViewSet):
    """
    Вывод только гражданского паспорта моряка
    """
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CitizenPassportPermission,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
    )
    serializer_class = serializers.CitizenPassportSerializer
    queryset = Passport.objects.all()
    model = Passport

    def perform_create(self, serializer):
        ser = serializer.save()
        try:
            sailor_pk = serializer.initial_data['sailor']
            sailor_qs = SailorKeys.objects.get(id=sailor_pk)
        except (KeyError, SailorKeys.DoesNotExist):
            raise ValidationError(sailor_not_exists_error)
        sailor_qs.citizen_passport.append(ser.id)
        sailor_qs.save(update_fields=['citizen_passport'])


class PhotoUploader(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (FormParser, MultiPartParser,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.list_files = list()

    def save_document_photo(self, obj, id_document, **kwargs):
        if isinstance(id_document, list):
            get_obj = obj.objects.only('id', 'photo').filter(id__in=id_document).first()
        else:
            get_obj = obj.objects.only('id', 'photo').get(id=id_document)
        try:
            photos_list = json.loads(get_obj.photo)
            photos_list += self.list_files
        except TypeError:
            photos_list = self.list_files
        get_obj.photo = json.dumps(photos_list)
        get_obj.save(update_fields=['photo'])
        photo_info = {
            'action': 'added photo',
            'photo_id': self.list_files,
            'module': get_obj.__class__.__name__,
            'object_id': get_obj.id,
            'date_added': datetime.now(),
        }
        sailor.tasks.save_history.s(user_id=self.request.user.id,
                                    module=get_obj.__class__.__name__,
                                    action_type='edit',
                                    content_obj=get_obj,
                                    old_obj=photo_info,
                                    get_sailor=True,
                                    ).apply_async(serializer='pickle')

    def delete_document_photo(self, obj, id_document, id_photo):
        photo = get_object_or_404(PhotoProfile, id=id_photo)
        photo_id = photo.id
        if isinstance(id_document, list):
            get_obj = obj.objects.only('id', 'photo').filter(id__in=id_document).first()
        else:
            get_obj = obj.objects.only('id', 'photo').get(id=id_document)
        if photo.is_delete:
            try:
                photos_list = json.loads(get_obj.photo)
                photos_list.remove(int(id_photo))
                get_obj.photo = json.dumps(photos_list)
                get_obj.save(update_fields=['photo'])
            except (TypeError, ValueError) as e:
                pass
            finally:
                photo.delete()
        else:
            photo.is_delete = True
            photo.save(update_fields=['is_delete'])
        photo_info = {
            'action': 'delete photo',
            'photo_id': photo_id,
            'module': get_obj.__class__.__name__,
            'object_id': get_obj.id,
            'date_delete': datetime.now(),
        }
        sailor.tasks.save_history.s(user_id=self.request.user.id,
                                    module=get_obj.__class__.__name__,
                                    action_type='edit',
                                    content_obj=get_obj,
                                    old_obj=photo_info,
                                    get_sailor=True,
                                    ).apply_async(serializer='pickle')

    def get_method(self):
        if self.request.method == 'POST':
            return self.save_document_photo
        else:
            return self.delete_document_photo

    def save_or_delete_in_model(self, type_document, id_document, id_photo=None):
        save_or_delete = self.get_method()
        if type_document == 'profile':
            key_prof = SailorKeys.objects.only('id', 'profile').get(id=id_document)
            save_or_delete(obj=Profile, id_document=key_prof.profile, id_photo=id_photo)
        elif type_document == 'passport':
            key_prof = SailorKeys.objects.only('id', 'profile', 'citizen_passport').get(id=id_document)
            save_or_delete(obj=Passport, id_document=key_prof.citizen_passport, id_photo=id_photo)
        elif type_document == 'GraduationDoc':
            save_or_delete(obj=Education, id_document=id_document, id_photo=id_photo)
        elif type_document == 'StatementSqp':
            save_or_delete(obj=StatementSQC, id_document=id_document, id_photo=id_photo)
        elif type_document == 'ExperienceDoc':
            save_or_delete(obj=LineInServiceRecord, id_document=id_document, id_photo=id_photo)
        elif type_document == 'SeafarerPassDoc':
            save_or_delete(obj=SailorPassport, id_document=id_document, id_photo=id_photo)
        elif type_document == 'MedicalDoc':
            save_or_delete(obj=MedicalCertificate, id_document=id_document, id_photo=id_photo)
        elif type_document == 'QualificationDoc':
            save_or_delete(obj=QualificationDocument, id_document=id_document, id_photo=id_photo)
        elif type_document == 'ProofOfWorkDiploma':
            save_or_delete(obj=ProofOfWorkDiploma, id_document=id_document, id_photo=id_photo)
        elif type_document == 'RecordBookDoc':
            save_or_delete(obj=ServiceRecord, id_document=id_document, id_photo=id_photo)
        elif type_document == 'ProtoclsSQCDoc':
            save_or_delete(obj=ProtocolSQC, id_document=id_document, id_photo=id_photo)
        elif type_document == 'StatementServiceRecord':
            save_or_delete(obj=StatementServiceRecord, id_document=id_document, id_photo=id_photo)
        elif type_document == 'StatementQualificationDoc':
            save_or_delete(obj=StatementQualification, id_document=id_document, id_photo=id_photo)
        elif type_document == 'StudentCard':
            save_or_delete(obj=StudentID, id_document=id_document, id_photo=id_photo)
        elif type_document == 'OldName':
            save_or_delete(obj=OldName, id_document=id_document, id_photo=id_photo)
        elif type_document == 'StatementSailorPassport':
            save_or_delete(obj=StatementSailorPassport, id_document=id_document, id_photo=id_photo)
        elif type_document == 'StatementMedicalCertificate':
            save_or_delete(obj=StatementMedicalCertificate, id_document=id_document, id_photo=id_photo)
        elif type_document == 'StatementAdvancedTraining':
            save_or_delete(obj=StatementAdvancedTraining, id_document=id_document, id_photo=id_photo)
        elif type_document == 'PacketItem':
            save_or_delete(obj=PacketItem, id_document=id_document, id_photo=id_photo)

    def post(self, request) -> Response:
        files = self.request.FILES.getlist('photo')
        data = self.request.data
        type_document = data['type_document']
        id_document = data['id_document']
        if not data:
            raise ValidationError('Please send body with data')
        self.list_files = [PhotoProfile.objects.create(photo=file).id for file in files]
        self.save_or_delete_in_model(type_document=type_document, id_document=id_document)
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=sailor.serializers.DeletePhotoSerializer)
    def delete(self, request, pk) -> Response:
        data = request.data
        type_document = data['type_document']
        id_document = data['id_document']
        if not data:
            raise ValidationError('Please send body with data')
        self.save_or_delete_in_model(type_document=type_document, id_document=id_document, id_photo=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FullUserSailorHistoryView(mixins.ListModelMixin, GenericViewSet):
    queryset = FullUserSailorHistory.objects.select_related('content_type').exclude(
        user_id=magic_numbers.celery_user_id)
    serializer_class = FullUserSailorHistorySerializer
    permission_classes = (IsAdminUser,)
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = FullUserSailorHistoryFilter
    pagination_class = ShortLinkResultPagination

    def get_queryset(self):
        return self.queryset.filter(sailor_key=self.kwargs['sailor_pk'])


class OldNameView(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = OldName.objects.all()
    serializer_class = serializers.OldNameSerializer
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
    )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return OldName.objects.none()
        sailor_pk = self.kwargs['sailor_pk']
        try:
            keys = SailorKeys.objects.get(id=sailor_pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        try:
            return self.queryset.filter(profile_id=keys.profile).order_by('-change_date')
        except TypeError:
            return []

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data.pop('sailor', None)
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        profile = Profile.objects.get(id=sailor_qs.profile)
        _profile = deepcopy(profile)
        change_date = serializer.initial_data.pop('change_date', None)
        if not change_date or not serializer.initial_data:
            raise ValidationError('not data')
        old_names = self.queryset.filter(profile_id=profile.id, change_date__gte=change_date)
        if old_names.exists():
            raise ValidationError('change date is incorrect')
        for attr, value in serializer.initial_data.items():
            setattr(profile, attr, value)
        profile.save()
        ser = serializer.save(old_first_name_ukr=_profile.first_name_ukr, old_first_name_eng=_profile.first_name_eng,
                              old_last_name_ukr=_profile.last_name_ukr, old_last_name_eng=_profile.last_name_eng,
                              old_middle_name_ukr=_profile.middle_name_ukr,
                              old_middle_name_eng=_profile.middle_name_eng,
                              new_first_name_ukr=profile.first_name_ukr, new_first_name_eng=profile.first_name_eng,
                              new_last_name_ukr=profile.last_name_ukr, new_last_name_eng=profile.last_name_eng,
                              new_middle_name_ukr=profile.middle_name_ukr, new_middle_name_eng=profile.middle_name_eng,
                              profile_id=profile.id)

        sailor.tasks.save_history.s(user_id=self.request.user.id, module='Profile', action_type='edit',
                                    content_obj=profile, serializer=serializers.ProfileMainInfoSerializer,
                                    new_obj=profile,
                                    old_obj=_profile, sailor_key_id=sailor_qs.pk).apply_async(serializer='pickle')

        sailor.tasks.save_history.s(user_id=self.request.user.id, module='SailorOldName', action_type='create',
                                    content_obj=ser, serializer=serializers.OldNameSerializer, new_obj=ser,
                                    sailor_key_id=sailor_qs.pk).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        profile = instance.profile
        sailor_qs = SailorKeys.objects.filter(profile=profile.id).first()
        if not sailor_qs:
            raise ValidationError(sailor_not_exists_error)
        _profile = deepcopy(profile)
        last_change = self.queryset.filter(profile_id=profile.id).order_by('-change_date')
        if instance.change_date != last_change.first().change_date:
            raise ValidationError('Сannot delete record')
        old_full_name = {'first_name_ukr': instance.old_first_name_ukr, 'first_name_eng': instance.old_first_name_eng,
                         'last_name_ukr': instance.old_last_name_ukr, 'last_name_eng': instance.old_last_name_eng,
                         'middle_name_ukr': instance.old_middle_name_ukr,
                         'middle_name_eng': instance.old_middle_name_eng}
        for attr, value in old_full_name.items():
            setattr(profile, attr, value)
        profile.save()

        _instance = deepcopy(instance)
        instance.delete()

        sailor.tasks.save_history.s(user_id=self.request.user.id, module='Profile', action_type='edit',
                                    content_obj=profile, serializer=serializers.ProfileMainInfoSerializer,
                                    new_obj=profile,
                                    old_obj=_profile, sailor_key_id=sailor_qs.pk).apply_async(serializer='pickle')

        sailor.tasks.save_history.s(user_id=self.request.user.id, module='SailorOldName', action_type='delete',
                                    content_obj=_instance, serializer=serializers.OldNameSerializer,
                                    old_obj=_instance, sailor_key_id=sailor_qs.pk).apply_async(serializer='pickle')


class AvailablePositionForSailor(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = SailorKeys.objects.all()
    permission_classes = (
        IsAuthenticated,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
    )

    def get_object(self):
        sailor_pk = self.kwargs['sailor_pk']
        try:
            return SailorKeys.objects.get(id=sailor_pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)

    def retrieve(self, request, *args, **kwargs):
        positions = list(QualificationDocument.by_sailor.filter_by_sailor(sailor_key=self.get_object()).filter(
            status_document_id__in=[19, 18, 7]).values_list('list_positions', flat=True))
        ranks_response = set()
        positions_response = set()
        if positions:
            positions = list(chain.from_iterable(positions))
            positions_to_allow = list(Position.objects.filter(
                id__in=positions
            ).values_list('allowed_to_get', 'allowed_to_get__rank_id'))
            for rank_position in positions_to_allow:
                if rank_position and rank_position[0]:
                    positions_response.add(rank_position[0])
                    ranks_response.add(rank_position[1])
        ranks_response = ranks_response.union({98, 23, 83, 87, 86, 90, 95, 97, 99, 100, 144, 145, 103, 123, 121, 104,
                                               127, 124})
        positions_response = positions_response.union(
            {123, 63, 81, 221, 87, 96, 101, 103, 105, 106, 184, 185, 151, 150, 149, 145, 144, 152, 133, 90, 154})
        return Response({'rank': list(ranks_response), 'position': list(positions_response)})


class SailorAgentView(APIView):
    permission_classes = (IsAdminUser,)

    @swagger_auto_schema(method='post', request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'agent_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Integer'),
        'date_end_proxy': openapi.Schema(type=openapi.FORMAT_DATE, description='Date', example='2020-01-01'),
    }))
    @action(detail=True, methods=['post'])
    def post(self, request, *args, **kwargs):
        sailor_pk = kwargs['sailor_pk']
        agent_id = request.data['agent_id']
        date_end_proxy = request.data['date_end_proxy']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        if sailor_qs.agent_id:
            raise ValidationError('Sailor has seaman')
        agent_sailor = AgentSailor.objects.create(sailor_key=sailor_pk,
                                                  agent_id=agent_id,
                                                  date_end_proxy=date_end_proxy)

        sailor.tasks.save_history.s(user_id=request.user.id, module='AgentSailor', action_type='create',
                                    content_obj=agent_sailor, serializer=AgentSailorSerializer, new_obj=agent_sailor,
                                    sailor_key_id=sailor_pk).apply_async(serializer='pickle')

        sailor_qs.agent_id = agent_id
        sailor_qs.save(update_fields=['agent_id'])
        return Response({'status': 'success'}, status=201)

    @action(detail=True, methods=['delete'], permission_classes=[IsBackOfficeUser])
    def delete(self, request, *args, **kwargs):
        sailor_pk = kwargs['sailor_pk']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        if not sailor_qs.agent_id:
            raise ValidationError('Sailor does not seaman')
        agent_sailor = AgentSailor.objects.get(sailor_key=sailor_qs.id)
        _agent_sailor = deepcopy(agent_sailor)
        agent_sailor.delete()
        sailor_qs.agent_id = None
        sailor_qs.save(update_fields=['agent_id'])
        sailor.tasks.save_history.s(user_id=request.user.id,
                                    module='AgentSailor',
                                    action_type='delete',
                                    content_obj=_agent_sailor,
                                    serializer=AgentSailorSerializer,
                                    old_obj=_agent_sailor,
                                    sailor_key_id=sailor_qs.pk,
                                    ).apply_async(serializer='pickle')
        return Response(status=204)


class AgentInfoView(APIView):
    permission_classes = (IsAuthenticated, (sailor.permissions.AgentInfoViewPermission | IsAdminUser))

    def get(self, request, *args, **kwargs):
        sailor_pk = int(kwargs['sailor_pk'])
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        if not sailor_qs.agent_id:
            return Response({}, status=200)
        agent = User.objects.get(id=sailor_qs.agent_id)
        return Response(UserFullInfoSerializer(agent).data, status=200)


class RatingView(GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    queryset = Rating.objects.all()
    serializer_class = serializers.RatingSerializer
    lookup_url_kwarg = None
    lookup_field = None
    permission_classes = (IsAuthenticated, sailor.permissions.RatingPermission)

    def get_rating(self, sailor_key):
        rating = Rating.objects.filter(sailor_key=sailor_key.pk).order_by('pk')
        my_rating = rating.filter(author=self.request.user).last()
        my_rating_float = my_rating.rating if my_rating else None
        if rating.filter(rating=4).exists():
            return {'rating': 4, 'my_rating': my_rating_float}
        if rating.exists():
            return {'rating': rating.last().rating, 'my_rating': my_rating_float}
        else:
            return {'rating': None, 'my_rating': my_rating_float}

    def retrieve(self, request, *args, **kwargs):
        sailor_pk = self.kwargs.get('sailor_pk')
        try:
            sailor_key = SailorKeys.objects.get(id=sailor_pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor key does not exists')
        rating_response = self.get_rating(sailor_key)
        return Response(rating_response)

    def perform_create(self, serializer):
        serializer.save(sailor_key=self.kwargs.get('sailor_pk'))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sailor_pk = self.kwargs.get('sailor_pk')
        sailor_key = SailorKeys.objects.get(id=sailor_pk)
        bad_rating = Rating.objects.filter(sailor_key=sailor_key.pk, rating=4)
        statement = serializer.validated_data.pop('statement', None)
        if self.request.user.has_perms('sailor.changeRating') and bad_rating.exists():
            bad_rating.delete()
        self.perform_create(serializer)
        if statement:
            statement.is_rated = True
            statement.save(update_fields=['is_rated'])
        headers = self.get_success_headers(serializer.data)
        rating_response = self.get_rating(sailor_key=sailor_key)
        return Response(rating_response, status=status.HTTP_201_CREATED, headers=headers)


class CheckContinueView(GenericAPIView):
    """
    Checks whether a sailor is going to continue the rank or to a new rank
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = sailor.serializers.CheckContinueSerializer

    def post(self, request, *args, **kwargs):
        sailor_pk = self.kwargs.get('sailor_pk')
        sailor_qs = SailorKeys.objects.get(id=sailor_pk)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        positions = data['position']
        rank_id = positions[0].rank.pk
        list_positions = [position.pk for position in positions]
        is_continue = sailor.misc.check_is_continue(sailor_qs, rank_id, list_positions)
        return Response({'is_continue': is_continue})


class CommentForVerificationDocViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, sailor.permissions.CommentForVerificationDocPermission)
    serializer_class = sailor.serializers.CommentForVerificationSerializer
    queryset = CommentForVerificationDocument.objects.all()

    def perform_create(self, serializer):
        author = self.request.user
        document = serializer.validated_data['document_id']
        ser = serializer.save(document_id=document.pk, author_id=author.pk)


class MergeSailorView(GenericAPIView):
    """
    Merge the current sailor (specified in url) with the specified in the request parameters
    """
    permission_classes = (IsAuthenticated, sailor.permissions.MergeSailorPermission)
    serializer_class = sailor.serializers.MergeSailorSerializer

    def get(self, request, *args, **kwargs):
        sailor_pk = self.kwargs.get('sailor_pk')
        try:
            sailor_key = SailorKeys.objects.get(id=sailor_pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        profile = Profile.objects.filter(id=sailor_key.profile).first()
        other_profile = Profile.objects.exclude(
            id=profile.id
        ).annotate(
            fullname_ukr=Concat('last_name_ukr', Value(' '), 'first_name_ukr', Value(' '), 'middle_name_ukr')
        ).filter(
            fullname_ukr__icontains=profile.get_full_name_ukr
        )
        response = [{'full_name_ukr': prof.fullname_ukr,
                     'date_birth': prof.date_birth,
                     'sailor_id': SailorKeys.objects.filter(profile=prof.id).first().pk}
                    for prof in other_profile if prof.date_birth == profile.date_birth]
        return Response(response)

    def post(self, request, *args, **kwargs):
        sailor_pk = self.kwargs.get('sailor_pk')
        current_sailor = SailorKeys.objects.get(id=sailor_pk)
        current_sailor_dict = model_to_dict(current_sailor)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        old_sailor = data['old_sailor']
        merge_info = {'merge_info': {'sailor_from': old_sailor.pk, 'sailor_to': current_sailor.pk}}
        old_sailor_dict = model_to_dict(old_sailor)
        old_sailor_dict.update(**merge_info)
        current_sailor_dict.update(**merge_info)
        old_sailor_id = old_sailor.pk
        sailor.misc.MergeSailor(sailor_from=old_sailor, sailor_to=current_sailor).migrate_documents()
        current_sailor.refresh_from_db()
        new_sailor_dict = model_to_dict(current_sailor)
        sailor.tasks.save_history.s(user_id=request.user.id,
                                    module='MergeSailor',
                                    action_type='edit',
                                    old_obj=current_sailor_dict,
                                    new_obj=new_sailor_dict,
                                    sailor_key_id=current_sailor.pk,
                                    ).apply_async(serializer='pickle')
        sailor.tasks.save_history.s(user_id=request.user.id,
                                    module='MergeSailor',
                                    action_type='delete',
                                    old_obj=old_sailor_dict,
                                    sailor_key_id=old_sailor_id,
                                    ).apply_async(serializer='pickle')
        return Response({'status': 'success'})
