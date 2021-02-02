import json
from copy import deepcopy

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Count, Subquery
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.permissions

from agent.models import StatementAgent, StatementAgentSailor
from communication.models import SailorKeys
from itcs import magic_numbers
from mixins.permission_mixins import IsBackOfficeUser
from notifications.models import UserNotification
from reports.filters import ShortLinkResultPagination
from reports.models import ProtocolFiles
from sailor.document.models import (Education, LineInServiceRecord, MedicalCertificate, QualificationDocument,
                                    ServiceRecord)
from sailor.filters import FullUserSailorHistoryFilter
from sailor.models import (Passport, PhotoProfile, Profile, SailorPassport)
from sailor.serializers import FullUserSailorHistorySerializer
from sailor.statement.models import StatementSQC, StatementServiceRecord
from sailor.tasks import save_history
from signature.models import CommissionerSignProtocol
from sms_auth.models import UserStatementVerification
from user_profile.models import (BranchOfficeRestrictionForPermission, FullUserSailorHistory, Group, MainGroups,
                                 Permission, UserSailorHistory, Version)
from user_profile.permissions import IsAdminUser
from user_profile.serializer import GroupSerializer, MainGroupSerializer, UserSerializer, IsTrainedSerializer
from . import serializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (rest_framework.permissions.IsAuthenticated, IsBackOfficeUser)  # UserPermission,)

    queryset = User.objects.filter(userprofile__isnull=False).distinct('pk')
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def upload_seaman_photo(self, request, *args, **kwargs):
        photo = request.FILES.get('photo')
        user = request.data['user']
        agent_user = User.objects.get(id=user)
        agent_user.userprofile.photo = photo
        agent_user.userprofile.save(update_fields=['photo'])
        return Response({'response': 'Photo added', 'status': 'success'})


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = (rest_framework.permissions.IsAuthenticated,
                          rest_framework.permissions.IsAdminUser)

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class MainGroupViewSet(viewsets.ModelViewSet):
    permission_classes = (rest_framework.permissions.IsAuthenticated,
                          rest_framework.permissions.IsAdminUser)

    queryset = MainGroups.objects.all()
    serializer_class = MainGroupSerializer


class GetInfoByMyUser(generics.RetrieveAPIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)
    serializer_class = serializer.UserFullInfoSerializer

    def get_object(self):
        user = self.request.user
        return user

    @method_decorator(vary_on_headers('Authorization'))
    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class GetLanguageUser(APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if hasattr(self.request.user, 'userprofile'):
            return Response({'language': user.userprofile.language})
        return Response({'language': 'UA'})

    @method_decorator(vary_on_headers('Authorization'))
    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class GetUserPermissions(APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        all_permissions = self.request.user.get_all_permissions()
        permissions = [perm.split('.')[1] for perm in all_permissions if
                       not perm.startswith('Can ')]
        return Response(
            {'permissions': permissions,
             'groups': list(self.request.user.userprofile.main_group.all().order_by('-id').values())})

    @method_decorator(vary_on_headers('Authorization'))
    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super(GetUserPermissions, self).dispatch(request, *args, **kwargs)


class HistorySailorByUser(APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,
                          rest_framework.permissions.IsAdminUser)

    def get(self, request) -> Response:
        history = UserSailorHistory.objects.filter(
            pk__in=Subquery(
                UserSailorHistory.objects.filter(user_id=self.request.user).
                    distinct('sailor_key').order_by('sailor_key', '-date_open').values('pk')
            )
        ).order_by('-date_open')[:20]
        keys = SailorKeys.objects.filter(id__in=list(history.values_list('sailor_key', flat=True)))
        profiles = Profile.objects.filter(id__in=list(keys.values_list('profile', flat=True)))
        response = []
        for profile in profiles:
            try:
                photos = json.loads(profile.photo)
                photo_qs = PhotoProfile.objects.get(id=photos[0])
                photo = photo_qs.photo.name
            except (PhotoProfile.DoesNotExist, IndexError, TypeError):
                photo = 'default_profile.png'
            try:
                passport = Passport.objects.filter(id__in=keys.get(profile=profile.id).citizen_passport).first()
                serial_passport = passport.serial or ''
                inn_value = passport.inn
            except (Passport.DoesNotExist, AttributeError, TypeError, IndexError):
                serial_passport = ''
                inn_value = ''
            key_id = keys.get(profile=profile.id).id
            datetime = [hist.date_open for hist in history if key_id == hist.sailor_key][0]
            response.append({'id': key_id,
                             'FIO_sailor': {'fio_ukr': profile.get_full_name_ukr, 'fio_eng': profile.get_full_name_eng},
                             'photo': photo, 'date_birth': profile.date_birth, 'passport': serial_passport,
                             'tax_number': inn_value,
                             'sex': {'name_ukr': profile.sex.value_ukr, 'name_eng': profile.sex.value_eng},
                             'date_time': datetime})
        response.sort(key=lambda item: item['date_time'], reverse=True)
        return Response(response)


class SomeDataAPI(APIView):
    permission_classes = (IsAdminUser,)

    def remove_duplicates(self):
        duplicates = Permission.objects.values('name', 'codename').annotate(Count('id')).order_by().filter(
            id__count__gt=1)
        names_of_duplicate = [d['name'] for d in duplicates]
        for name in names_of_duplicate:
            if name.startswith('Can '):
                continue
            permissions = Permission.objects.filter(name=name, codename=name)
            first_permission = permissions.first()
            for perm in permissions[1:]:
                if Group.objects.filter(permissions=perm, user__isnull=True).exists() and \
                        Permission.objects.filter(user__isnull=True, id=perm.pk).exists():
                    perm.delete()
                first_permission.user_set.set(perm.user_set.all())
                first_permission.group_set.set(perm.group_set.all())
                perm.delete()

    def load_perms(self):
        response = []
        self.remove_duplicates()
        registry, _ = MainGroups.objects.get_or_create(name='Реєстр')
        verification, _ = MainGroups.objects.get_or_create(name='Верифікатор')
        secretary_sqc, _ = MainGroups.objects.get_or_create(name='Секретар ДКК')
        secretary_service, _ = MainGroups.objects.get_or_create(name='Секретар СЦ')
        diploma_passport, _ = MainGroups.objects.get_or_create(name='Дипломно-паспортний')
        secretary_university, _ = MainGroups.objects.get_or_create(name='Секретар вищого навчального закладу (ВНЗ)')
        agent, _ = MainGroups.objects.get_or_create(name='Довірена особа')
        head_agent_group, _ = MainGroups.objects.get_or_create(name='Керівник групи')
        back_office, _ = MainGroups.objects.get_or_create(name='Back office')
        medical, _ = MainGroups.objects.get_or_create(name='Мед. працівник')
        eti_employee, _ = MainGroups.objects.get_or_create(name='Представник НТЗ')
        secretary_atc, _ = MainGroups.objects.get_or_create(name='Секретар КПК')

        print('----------------------------------------------------------------------------------------')

        group, _ = Group.objects.get_or_create(name='верификация рабочих документов ДПО (изменение статусов)')
        verification.group.add(group)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='writeQualificationStatus',
                                                            name='writeQualificationStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='изменение статуса медицинских свидетельств')
        verification.group.add(group)
        diploma_passport.group.add(group)
        medical.group.add(group)
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='writeMedicalStatus',
                                                            name='writeMedicalStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        # TODO добавить верификатора мед свидоцтв

        group, _ = Group.objects.get_or_create(name='проверка документов для отдела Верификации')
        verification.group.add(group)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='writeCheckDocuments',
                                                            name='writeCheckDocuments',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='верификация внесенных записей по стажу с ПКМ'
                                                    ' (“потребує підтвердження”“схвалено” “відхиллено”)')
        verification.group.add(group)
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeRecordBookEntryStatus',
                                                            name='writeRecordBookEntryStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='верификация добавления существующих ПКМ (изменение статусов)')
        verification.group.add(group)
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeRecordBookStatus',
                                                            name='writeRecordBookStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='верификация документов об образовании')
        verification.group.add(group)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='writeGraduationStatus',
                                                            name='writeGraduationStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='верификация иностранного рабочего документа (или СССР)')
        verification.group.add(group)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='writeQualificationStatus',
                                                            name='writeQualificationStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='верификация (подтверждение) изменений смены статусов по ДПО')
        verification.group.add(group)

        group, _ = Group.objects.get_or_create(name='верификация заявлений на прохождение ДКК')
        verification.group.add(group)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='writeApplicationSQCStatus',
                                                            name='writeApplicationSQCStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readApplicationSQCApproved',
                                                            name='readApplicationSQCApproved',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='верификация гражданских документов (паспорт, ИНН) и ПМ')
        verification.group.add(group)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='writeSeafarerPassportStatus',
                                                            name='writeSeafarerPassportStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр всех документов, заявлений, протоколов и разделов')
        verification.group.add(group)
        agent.group.add(group)
        head_agent_group.group.add(group)
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='profile')
        permission, _ = Permission.objects.update_or_create(codename='readMainInfo',
                                                            name='readMainInfo',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='readSeafarerPassport',
                                                            name='readSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='passport')
        permission, _ = Permission.objects.update_or_create(codename='readCitizenPassport',
                                                            name='readCitizenPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='readGraduation',
                                                            name='readGraduation',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='readQualification',
                                                            name='readQualification',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementqualification')
        permission, _ = Permission.objects.update_or_create(codename='readQualificationApplication',
                                                            name='readQualificationApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='certificateeti')
        permission, _ = Permission.objects.update_or_create(codename='readCertificates',
                                                            name='readCertificates',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='readRecordBook',
                                                            name='readRecordBook',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='readExperience',
                                                            name='readExperience',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readApplicationSQC',
                                                            name='readApplicationSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='readProtocolSQC',
                                                            name='readProtocolSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='readMedical',
                                                            name='readMedical',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='get_full_statement_dkk',
                                                            name='get_full_statement_dkk',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='get_full_protocol_dkk',
                                                            name='get_full_protocol_dkk',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        # group[3].permissions.add(permission)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='get_full_service_record',
                                                            name='get_full_service_record',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        print('----------------------------------------------------------------------------------------')

        group, _ = Group.objects.get_or_create(name='подача заявления на ГКК')
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readApplicationSQC',
                                                            name='readApplicationSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='createApplicationSQC',
                                                            name='createApplicationSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='печать заявления на ГКК')
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readApplicationSQC',
                                                            name='readApplicationSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='внесение документов моряка, учебных документов, рабочих дипломов'
                                                    ' (в тч иностранных),'
                                                    'медицинские справки')
        secretary_sqc.group.add(group)
        diploma_passport.group.add(group)
        # TODO добавить 4 группу
        ct = ContentType.objects.get(model='profile')
        permission, _ = Permission.objects.update_or_create(codename='readMainInfo',
                                                            name='readMainInfo',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='profile')
        permission, _ = Permission.objects.update_or_create(codename='writeMainInfo',
                                                            name='writeMainInfo',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='readSeafarerPassport',
                                                            name='readSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='createSeafarerPassport',
                                                            name='createSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='passport')
        permission, _ = Permission.objects.update_or_create(codename='readCitizenPassport',
                                                            name='readCitizenPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='passport')
        permission, _ = Permission.objects.update_or_create(codename='writeCitizenPassportInfo',
                                                            name='writeCitizenPassportInfo',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        # ct = ContentType.objects.get(model='servicerecord')
        # permission, _ = Permission.objects.update_or_create(codename='readRecordBook',
        #                                               name='readRecordBook',
        #                                               defaults={'content_type': ct})
        # group.permissions.add(permission)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='readGraduation',
                                                            name='readGraduation',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='createGraduation',
                                                            name='createGraduation',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='readQualification',
                                                            name='readQualification',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='createQualification',
                                                            name='createQualification',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        # ct = ContentType.objects.get(model='lineinservicerecord')
        # permission, _ = Permission.objects.update_or_create(codename='readExperience',
        #                                               name='readExperience',
        #                                               defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='servicerecord')
        # permission, _ = Permission.objects.update_or_create(codename='createExistRecordBook',
        #                                               name='createExistRecordBook',
        #                                               defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='servicerecord')
        # permission, _ = Permission.objects.update_or_create(codename='createRecordBookEntry',
        #                                               name='createRecordBookEntry',
        #                                               defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='lineinservicerecord')
        # permission, _ = Permission.objects.update_or_create(codename='readExperience',
        #                                               name='readExperience',
        #                                               defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='sailorpassport')
        # permission, _ = Permission.objects.update_or_create(codename='createExperience',
        #                                               name='createExperience',
        #                                               defaults={'content_type': ct})
        # group.permissions.add(permission)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='readMedical',
                                                            name='readMedical',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='createMedical',
                                                            name='createMedical',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='создание в базе учетной записи моряка')
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model='profile')
        permission, _ = Permission.objects.update_or_create(codename='createSeafarer',
                                                            name='createSeafarer',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_university.group.add(group)

        group, _ = Group.objects.get_or_create(name='оформление ПКМ (создание новой и распечатка бланка ПКМ)')
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='createNewRecordBook',
                                                            name='createNewRecordBook',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_university.group.add(group)
        group, _ = Group.objects.get_or_create(name='внесение информации по существующей ПОМ со статусом “Верификация”')
        secretary_sqc.group.add(group)
        secretary_university.group.add(group)
        agent.group.add(group)
        diploma_passport.group.add(group)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='readSeafarerPassport',
                                                            name='readSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='createSeafarerPassport',
                                                            name='createSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='внесение информации по ПГУ со статусом “Верификация”')
        secretary_sqc.group.add(group)
        secretary_university.group.add(group)
        ct = ContentType.objects.get(model='passport')
        permission, _ = Permission.objects.update_or_create(codename='readCitizenPassport',
                                                            name='readCitizenPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='passport')
        permission, _ = Permission.objects.update_or_create(codename='writeCitizenPassportInfo',
                                                            name='writeCitizenPassportInfo',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(
            name='внесение информации по мед. свидетельствам со статусом “Верификация”')
        secretary_sqc.group.add(group)
        secretary_service.group.add(group)
        secretary_university.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='readMedical',
                                                            name='readMedical',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='createMedical',
                                                            name='createMedical',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='внесение информации по ПМ со статусом “Верификация”')
        secretary_sqc.group.add(group)
        secretary_university.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='readSeafarerPassport',
                                                            name='readSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='createSeafarerPassport',
                                                            name='createSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='внесение информации по учебным документам '
                                                    '(дипломы, СПК и уч.свидетельства) со статусом “Верификация”')
        secretary_sqc.group.add(group)
        secretary_university.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='readGraduation',
                                                            name='readGraduation',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='createGraduation',
                                                            name='createGraduation',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        group, _ = Group.objects.get_or_create(name='внесение в базу иностранного рабочего документа (или СССР)'
                                                    ' со статусом “Верификация”')
        secretary_sqc.group.add(group)
        agent.group.add(group)

        group, _ = Group.objects.get_or_create(name='создание Ведомости и Протокола ГКК')
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='createProtocolSQC',
                                                            name='createProtocolSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='writeApplicationSQCPayment',
                                                            name='writeApplicationSQCPayment',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр заяв на прохождение ГКК')
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readApplicationSQC',
                                                            name='readApplicationSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='get_full_statement_dkk',
                                                            name='get_full_statement_dkk',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр протоколов и ведомостей ГКК')
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='readProtocolSQC',
                                                            name='readProtocolSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='get_full_protocol_dkk',
                                                            name='get_full_protocol_dkk',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр ПКМ и стаж')
        secretary_sqc.group.add(group)
        secretary_university.group.add(group)
        secretary_service.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='readRecordBook',
                                                            name='readRecordBook',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='get_full_service_record',
                                                            name='get_full_service_record',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        print('----------------------------------------------------------------------------------------')

        group, _ = Group.objects.get_or_create(name='создание учетной записи моряка')
        diploma_passport.group.add(group)
        secretary_university.group.add(group)
        ct = ContentType.objects.get(model='profile')
        permission, _ = Permission.objects.update_or_create(codename='createSeafarer',
                                                            name='createSeafarer',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='profile')
        permission, _ = Permission.objects.update_or_create(codename='readMainInfo',
                                                            name='readMainInfo',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        group, _ = Group.objects.get_or_create(name='внесение информации по существующей ПКМ')
        secretary_university.group.add(group)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='readRecordBook',
                                                            name='readRecordBook',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='createExistRecordBook',
                                                            name='createExistRecordBook',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='внесение записей с ПКМ по стажу плавания')
        secretary_university.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='createRecordBookEntry',
                                                            name='createRecordBookEntry',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='верификация внесенных записей по стажу с ПКМ')

        group, _ = Group.objects.get_or_create(name='внесение информации по ПГУ')
        diploma_passport.group.add(group)
        secretary_university.group.add(group)
        ct = ContentType.objects.get(model='passport')
        permission, _ = Permission.objects.update_or_create(codename='readCitizenPassport',
                                                            name='readCitizenPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='passport')
        permission, _ = Permission.objects.update_or_create(codename='writeCitizenPassportInfo',
                                                            name='writeCitizenPassportInfo',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='внесение информации по мед. свидетельствам')
        diploma_passport.group.add(group)
        secretary_university.group.add(group)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='readMedical',
                                                            name='readMedical',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='createMedical',
                                                            name='createMedical',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='внесение информации по ПМ')
        diploma_passport.group.add(group)
        secretary_service.group.add(group)
        secretary_university.group.add(group)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='readSeafarerPassport',
                                                            name='readSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='createSeafarerPassport',
                                                            name='createSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='внесение информации по учебным документам '
                                                    '(дипломы и уч.свидетельства)')
        diploma_passport.group.add(group)
        secretary_university.group.add(group)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='readGraduation',
                                                            name='readGraduation',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='createGraduation',
                                                            name='createGraduation',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='подача заявления на смену статуса рабочих документов')
        diploma_passport.group.add(group)
        ct = ContentType.objects.get(model='statementqualification')
        permission, _ = Permission.objects.update_or_create(codename='createQualificationApplication',
                                                            name='createQualificationApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='смена статуса рабочих документов «Дія призупинена»')
        diploma_passport.group.add(group)

        group, _ = Group.objects.get_or_create(name='просмотр ДПО “Кваліфікаційні документи” и “Заяви”')
        medical.group.add(group)
        diploma_passport.group.add(group)
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='statementqualification')
        permission, _ = Permission.objects.update_or_create(codename='readQualificationApplication',
                                                            name='readQualificationApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='readQualification',
                                                            name='readQualification',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр ДКК “Протоколы ДКК”')
        diploma_passport.group.add(group)
        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='readProtocolSQC',
                                                            name='readProtocolSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        print('----------------------------------------------------------------------------------------')

        group, _ = Group.objects.get_or_create(name='просмотр всех документов за исключением '
                                                    'статусов “Верификация” и “В обработке”;')
        registry.group.add(group)
        ct = ContentType.objects.get(model='profile')
        permission, _ = Permission.objects.update_or_create(codename='readMainInfo',
                                                            name='readMainInfo',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='readSeafarerPassport',
                                                            name='readSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='passport')
        permission, _ = Permission.objects.update_or_create(codename='readCitizenPassport',
                                                            name='readCitizenPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='readGraduation',
                                                            name='readGraduation',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='readQualification',
                                                            name='readQualification',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementqualification')
        permission, _ = Permission.objects.update_or_create(codename='readQualificationApplication',
                                                            name='readQualificationApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='certificateeti')
        permission, _ = Permission.objects.update_or_create(codename='readCertificates',
                                                            name='readCertificates',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='readRecordBook',
                                                            name='readRecordBook',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='readExperience',
                                                            name='readExperience',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readApplicationSQC',
                                                            name='readApplicationSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='readProtocolSQC',
                                                            name='readProtocolSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='readMedical',
                                                            name='readMedical',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='writeQualificationStatus',
                                                            name='writeQualificationStatus',
                                                            defaults={'content_type': ct})
        group, _ = Group.objects.get_or_create(name='смена статуса квалификационного документа')
        secretary_service.group.add(group)
        group.permissions.add(permission)
        diploma_passport.group.add(group)

        # TODO
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeExperienceStatus',
                                                            name='writeExperienceStatus', defaults={'content_type': ct})
        group, _ = Group.objects.get_or_create(name='смена статуса довидки про стаж')
        group.permissions.add(permission)
        verification.group.add(group)

        ct = ContentType.objects.get(model='statementqualification')
        permission, _ = Permission.objects.update_or_create(codename='writeQualificationApplicationStatus',
                                                            name='writeQualificationApplicationStatus',
                                                            defaults={'content_type': ct})
        # TODO добавить для ДПО
        group, _ = Group.objects.get_or_create(name='изменение статуса заявок на ДПО')
        group.permissions.add(permission)
        diploma_passport.group.add(group)

        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='deleteSeafarerPassport',
                                                            name='deleteSeafarerPassport',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='deleteGraduation',
                                                            name='deleteGraduation',
                                                            defaults={'content_type': ct})
        group, _ = Group.objects.update_or_create(name='Удаление квалификационных документов')
        agent.group.add(group)
        back_office.group.add(group)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='deleteQualification',
                                                            name='deleteQualification',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementqualification')
        permission, _ = Permission.objects.update_or_create(codename='deleteQualificationApplication',
                                                            name='deleteQualificationApplication',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='deleteRecordBook',
                                                            name='deleteRecordBook',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='deleteExperience',
                                                            name='deleteExperience',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='writeApplicationSQCStatus',
                                                            name='writeApplicationSQCStatus',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='deleteApplicationSQC',
                                                            name='deleteApplicationSQC',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='writeProtocolSQCStatus',
                                                            name='writeProtocolSQCStatus',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='deleteProtocolSQC',
                                                            name='deleteProtocolSQC',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='deleteMedical',
                                                            name='deleteMedical',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='get_statement_dkk_by_branch',
                                                            name='get_statement_dkk_by_branch',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='get_protocol_dkk_by_branch',
                                                            name='get_protocol_dkk_by_branch',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='get_service_record_by_branch',
                                                            name='get_service_record_by_branch',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readApplicationSQCProccess',
                                                            name='readApplicationSQCProccess',
                                                            defaults={'content_type': ct})

        group, _ = Group.objects.get_or_create(name='работа с пользователями и группами пользователей')
        ct = ContentType.objects.get(model='group')
        permission, _ = Permission.objects.update_or_create(codename='createUsers',
                                                            name='createUsers',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр отчета по ДКК по ')
        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='reportSqcProtocol',
                                                            name='reportSqcProtocol',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='редактирование ПКМ со статусом “Верификация”')
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeRecordBook',
                                                            name='writeRecordBook',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_sqc.group.add(group)
        secretary_university.group.add(group)
        agent.group.add(group)

        group, _ = Group.objects.get_or_create(name='редактирование записей про стаж в пкм со статусом “Верификация”')
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeRecordBookEntry',
                                                            name='writeRecordBookEntry',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_sqc.group.add(group)
        secretary_university.group.add(group)
        agent.group.add(group)

        group, _ = Group.objects.get_or_create(name='редактирование справки по стажу со статусом “Верификация”')
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeExperience',
                                                            name='writeExperience',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_sqc.group.add(group)
        agent.group.add(group)

        group, _ = Group.objects.get_or_create(name='редактирование мед. свидетельствам со статусом “Верификация“')
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='writeMedical',
                                                            name='writeMedical',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_sqc.group.add(group)
        diploma_passport.group.add(group)
        agent.group.add(group)
        medical.group.add(group)

        group, _ = Group.objects.get_or_create(name='редактирование существующего квалификационного документа')
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='writeQualification',
                                                            name='writeQualification',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_service.group.add(group)
        secretary_sqc.group.add(group)
        diploma_passport.group.add(group)

        group, _ = Group.objects.get_or_create(
            name='редактировать учебные доки (если моряк не дкк) со статусом Верификация')
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='writeGraduation',
                                                            name='writeGraduation',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_sqc.group.add(group)
        secretary_service.group.add(group)
        diploma_passport.group.add(group)
        agent.group.add(group)

        group, _ = Group.objects.get_or_create(name='просмотр верификаторов которые верифицировали документ')
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='readAuthorApprov',
                                                            name='readAuthorApprov',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        verification.group.add(group)

        group, _ = Group.objects.get_or_create(
            name='редактирование ПМ со статусом “Верификация”')
        ct = ContentType.objects.get(model='sailorpassport')
        secretary_service.group.add(group)

        permission, _ = Permission.objects.update_or_create(codename='writeSeafarerPassport',
                                                            name='writeSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_sqc.group.add(group)
        agent.group.add(group)

        permission = Permission.objects.get(codename='createNewSailorPassport')
        group, _ = Group.objects.get_or_create(name='Создание новых ПОМ')
        group.permissions.add(permission)
        diploma_passport.group.add(group)


        # Регистрация новых пользователей
        # group, _ = Group.objects.get_or_create(name='работа с пользователями и группами пользователей')
        # ct = ContentType.objects.get(model='group')
        # permission, _ = Permission.objects.get(codename='add_group',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='group')
        # permission, _ = Permission.objects.get(codename='delete_group',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='group')
        # permission, _ = Permission.objects.get(codename='change_group',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='group')
        # permission, _ = Permission.objects.get(codename='view_group',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        #
        # ct = ContentType.objects.get(model='user')
        # permission, _ = Permission.objects.get(codename='add_user',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='user')
        # permission, _ = Permission.objects.get(codename='view_user',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='user')
        # permission, _ = Permission.objects.get(codename='delete_user',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='user')
        # permission, _ = Permission.objects.get(codename='change_user',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        #
        # ct = ContentType.objects.get(model='permission')
        # permission, _ = Permission.objects.get(codename='add_permission',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='permission')
        # permission, _ = Permission.objects.get(codename='view_permission',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='permission')
        # permission, _ = Permission.objects.get(codename='delete_permission',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)
        # ct = ContentType.objects.get(model='permission')
        # permission, _ = Permission.objects.get(codename='change_permission',
        #                                     defaults={'content_type': ct})
        # group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='создание и просмотр стажа')
        secretary_sqc.group.add(group)
        agent.group.add(group)
        secretary_university.group.add(group)

        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='readRecordBook',
                                                            name='readRecordBook',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='readExperience',
                                                            name='readExperience',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='createExistRecordBook',
                                                            name='createExistRecordBook',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='createRecordBookEntry',
                                                            name='createRecordBookEntry',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='readExperience',
                                                            name='readExperience',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='createExperience',
                                                            name='createExperience',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='statementservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeApplicationRecordBook',
                                                            name='writeApplicationRecordBook',
                                                            defaults={'content_type': ct})
        group, _ = Group.objects.get_or_create(name='просмотр и обработка заявок на пкм')
        group.permissions.add(permission)

        ct = ContentType.objects.get(model='certificateeti')
        permission, _ = Permission.objects.update_or_create(codename='addCertificatesETI',
                                                            name='addCertificatesETI',
                                                            defaults={'content_type': ct})
        group, _ = Group.objects.get_or_create(name='добавление нтз сертификатов для ДПВ')
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр отчета по ДКК по ')
        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='reportProtocolSQC',
                                                            name='reportProtocolSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр отчета по заявлениям ДКК')
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readReportApplicationSQC',
                                                            name='readReportApplicationSQC',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр отчета по НТЗ')
        ct = ContentType.objects.get(model='certificateeti')
        permission, _ = Permission.objects.update_or_create(codename='readCertificatesReport',
                                                            name='readCertificatesReport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр отчета по заявлениям НТЗ')
        ct = ContentType.objects.get(model='statementeti')
        permission, _ = Permission.objects.update_or_create(codename='readReportApplicationETI',
                                                            defaults={'content_type': ct,
                                                                      'name': 'readReportApplicationETI'})
        group.permissions.add(permission)
        back_office.group.add(group)
        eti_employee.group.add(group)

        group, _ = Group.objects.get_or_create(name='Просмотр информации по оплате заявлениий НТЗ')
        ct = ContentType.objects.get(model='statementeti')
        permission, _ = Permission.objects.update_or_create(codename='readPaymentsETI',
                                                            defaults={'content_type': ct,
                                                                      'name': 'readPaymentsETI'})
        group.permissions.add(permission)
        back_office.group.add(group)
        eti_employee.group.add(group)

        group, _ = Group.objects.get_or_create(name='Просмотр информации по оплате сервисным центрам')
        ct = ContentType.objects.get(model='dependencyitem')
        permission, _ = Permission.objects.update_or_create(codename='readPaymentsSC',
                                                            defaults={'content_type': ct,
                                                                      'name': 'readPaymentsSC'})
        group.permissions.add(permission)
        back_office.group.add(group)

        group, _ = Group.objects.get_or_create(name='просмотр отчета по квалификационным документам')
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='readReportQualificationDocument',
                                                            name='readReportQualificationDocument',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр отчета по образовательным документам')
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='readGraduationReport',
                                                            name='readGraduationReport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр списка отчетов сформированных в xlsx файлы')
        ct = ContentType.objects.get(model='protocolfiles', app_label='reports')
        permission, _ = Permission.objects.update_or_create(codename='readReportListOfFiles',
                                                            name='readReportListOfFiles',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр заявлений на доступ в личный кабинет')
        ct = ContentType.objects.get(model='userstatementverification')
        permission, _ = Permission.objects.update_or_create(codename='writeCheckDocuments',
                                                            name='writeCheckDocuments',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        ct = ContentType.objects.get(model='protocolsqc')
        permission, _ = Permission.objects.update_or_create(codename='createProtocolSQCTraining',
                                                            name='createProtocolSQCTraining',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readApplicationSQCTraining',
                                                            name='readApplicationSQCTraining',
                                                            defaults={'content_type': ct})

        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='writeApplicationSQCTraining',
                                                            name='writeApplicationSQCTraining',
                                                            defaults={'content_type': ct})

        group, _ = Group.objects.get_or_create(name='просмотр студентческого билета кадета')
        ct = ContentType.objects.get(model='studentid')
        permission, _ = Permission.objects.update_or_create(codename='readStudentsID',
                                                            name='readStudentsID',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_service.group.add(group)
        secretary_university.group.add(group)
        agent.group.add(group)
        head_agent_group.group.add(group)
        eti_employee.group.add(group)

        group, _ = Group.objects.get_or_create(name='создание студентческого билета кадета')
        ct = ContentType.objects.get(model='studentid')
        permission, _ = Permission.objects.update_or_create(codename='createStudentsID',
                                                            name='createStudentsID',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_university.group.add(group)

        group, _ = Group.objects.get_or_create(name='обновление студентческого билета кадета')
        ct = ContentType.objects.get(model='studentid')
        permission, _ = Permission.objects.update_or_create(codename='writeStudentsID',
                                                            name='writeStudentsID',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        secretary_university.group.add(group)
        group, _ = Group.objects.get_or_create(name='обновление статуса студентческого билета кадета')
        permission, _ = Permission.objects.update_or_create(codename='writeStudentsIDStatus',
                                                            name='writeStudentsIDStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='удаление студентческого билета кадета')
        ct = ContentType.objects.get(model='studentid')
        permission, _ = Permission.objects.update_or_create(codename='deleteStudentsID',
                                                            name='deleteStudentsID',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(
            name='создание, редактирование в статусе "Верификация", просмотр стажа для '
                 'неконвенционных профессий')
        diploma_passport.group.add(group)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='readExperienceNotConventional',
                                                            name='readExperienceNotConventional',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='createExperienceNotConventional',
                                                            name='createExperienceNotConventional',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeExperienceNotConventional',
                                                            name='writeExperienceNotConventional',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='смена статуса стажа для неконвенционных профессий')
        diploma_passport.group.add(group)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeExperienceNotConventionalStatus',
                                                            name='writeExperienceNotConventionalStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        group, _ = Group.objects.get_or_create(name='просмотрв списка заявок дкк с статусом "створено з лк"')
        diploma_passport.group.add(group)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readApplicationSQCCreatedFromPA',
                                                            name='readApplicationSQCCreatedFromPA',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='readPostVerification',
                                                            name='readPostVerification',
                                                            defaults={'content_type': ct})

        group, _ = Group.objects.get_or_create(name='работа с изменением ФИО')
        ct = ContentType.objects.get(model='oldname')
        permission, _ = Permission.objects.update_or_create(codename='readSurnameChanges',
                                                            name='readSurnameChanges', defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='createSurnameChanges',
                                                            name='createSurnameChanges', defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='writeSurnameChanges',
                                                            name='writeSurnameChanges', defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='deleteSurnameChanges',
                                                            name='deleteSurnameChanges', defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр заявления на пакет услуг')
        head_agent_group.group.add(group)
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='packetitem')
        permission, _ = Permission.objects.update_or_create(codename='readPacketService',
                                                            name='readPacketService', defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр превью пакета')
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='packetitem')
        permission, _ = Permission.objects.update_or_create(codename='readPacketPreview',
                                                            name='readPacketPreview', defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр заявлений на пакеты услуг')
        head_agent_group.group.add(group)
        ct = ContentType.objects.get(model='packetitem')
        permission, _ = Permission.objects.get_or_create(codename='readPacketService',
                                                         name='readPacketService', content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='заявление на пакет услуг')
        agent.group.add(group)
        ct = ContentType.objects.get(model='packetitem')
        permission, _ = Permission.objects.update_or_create(codename='readPacketService',
                                                            name='readPacketService', defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='createPacketService',
                                                            name='createPacketService', defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='writePacketService',
                                                            name='writePacketService', defaults={'content_type': ct})

        group, _ = Group.objects.get_or_create(name='Просмотр и обработка агентом заявок на становление агентом')
        agent.group.add(group)
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='statementagentsailor')
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='writeAgentApplicationFromSailor',
                                                            name='writeAgentApplicationFromSailor',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр и обработка секретарем заявок на становление агентом')
        secretary_service.group.add(group)

        ct = ContentType.objects.get(model='statementagentsailor')
        permission, _ = Permission.objects.get_or_create(codename='applyAgentApplicationFromSailor',
                                                         name='applyAgentApplicationFromSailor',
                                                         content_type=ct)
        group.permissions.add(permission)
        permission, _ = Permission.objects.get_or_create(codename='readAgentApplicationFromSailor',
                                                         name='readAgentApplicationFromSailor',
                                                         content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр и обработка заявок на агентов')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='statementagent')
        permission, _ = Permission.objects.update_or_create(codename='readAgentApplication',
                                                            name='readAgentApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='writeAgentApplication',
                                                            name='writeAgentApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Создание заявки на НТЗ')
        ct = ContentType.objects.get(model='statementeti')
        permission, _ = Permission.objects.update_or_create(codename='readCertificateApplication',
                                                            name='readCertificateApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='createCertificationApplication',
                                                            name='createCertificationApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Редактирование заявки на НТЗ')
        agent.group.add(group)
        ct = ContentType.objects.get(model='statementeti')
        permission, _ = Permission.objects.update_or_create(codename='readCertificateApplication',
                                                            name='readCertificateApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='writeCertificationApplication',
                                                            name='writeCertificationApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Смена статуса заявки на НТЗ')
        agent.group.add(group)
        ct = ContentType.objects.get(model='statementeti')
        permission, _ = Permission.objects.update_or_create(codename='readCertificateApplication',
                                                            name='readCertificateApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='writeCertificationApplicationStatus',
                                                            name='writeCertificationApplicationStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр заявок на НТЗ')
        agent.group.add(group)
        head_agent_group.group.add(group)
        eti_employee.group.add(group)
        ct = ContentType.objects.get(model='statementeti')
        permission, _ = Permission.objects.update_or_create(codename='readCertificateApplication',
                                                            name='readCertificateApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        # удаление заявок на НТЗ
        Permission.objects.update_or_create(codename='deleteCertificationApplication',
                                            name='deleteCertificationApplication',
                                            defaults={'content_type': ct})

        group, _ = Group.objects.get_or_create(name='Просмотр цен на должности')
        ct = ContentType.objects.get(model='priceforposition')
        permission, _ = Permission.objects.update_or_create(codename='readPriceForPosition',
                                                            name='readPriceForPosition',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        back_office.group.add(group)

        group, _ = Group.objects.get_or_create(name='Редактирование цен на должности')
        ct = ContentType.objects.get(model='priceforposition')
        permission, _ = Permission.objects.update_or_create(codename='readPriceForPosition',
                                                            name='readPriceForPosition',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        back_office.group.add(group)
        permission, _ = Permission.objects.update_or_create(codename='writePriceForPosition',
                                                            name='writePriceForPosition',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        back_office.group.add(group)

        group, _ = Group.objects.get_or_create(name='Редактирование цен на курсы')
        ct = ContentType.objects.get(model='courseprice')
        permission, _ = Permission.objects.update_or_create(codename='readCoursePrice',
                                                            name='readCoursePrice',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        back_office.group.add(group)
        permission, _ = Permission.objects.update_or_create(codename='writeCoursePrice',
                                                            name='writeCoursePrice',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        back_office.group.add(group)

        group, _ = Group.objects.get_or_create(name='Просмотр цен на курсы')
        ct = ContentType.objects.get(model='courseprice')
        permission, _ = Permission.objects.update_or_create(codename='readCoursePrice',
                                                            name='readCoursePrice',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        back_office.group.add(group)

        group, _ = Group.objects.get_or_create(name='Редактирование процентной части прибыли и НТЗ')
        ct = ContentType.objects.get(model='etiprofitpart')
        permission, _ = Permission.objects.update_or_create(codename='readETIProfitPart',
                                                            name='readETIProfitPart',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        back_office.group.add(group)
        permission, _ = Permission.objects.update_or_create(codename='writeETIProfitPart',
                                                            name='writeETIProfitPart',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        back_office.group.add(group)

        group, _ = Group.objects.get_or_create(name='Просмотр процентной части прибыли и НТЗ')
        ct = ContentType.objects.get(model='courseprice')
        permission, _ = Permission.objects.update_or_create(codename='readETIProfitPart',
                                                            name='readETIProfitPart',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        back_office.group.add(group)

        # Заявки на ПОМ

        group, _ = Group.objects.get_or_create(name='Просмотр заявки на ПОМ')
        agent.group.add(group)
        head_agent_group.group.add(group)
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='statementsailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='readSeafarerPassportApplication',
                                                            name='readSeafarerPassportApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Создание заявки на ПОМ')
        permission, _ = Permission.objects.update_or_create(codename='createSeafarerPassportApplication',
                                                            name='createSeafarerPassportApplication',
                                                            defaults={'content_type': ct})
        diploma_passport.group.add(group)
        group, _ = Group.objects.get_or_create(name='Редактирование заявки на ПОМ')
        agent.group.add(group)
        secretary_service.group.add(group)
        diploma_passport.group.add(group)
        ct = ContentType.objects.get(model='statementsailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='writeSeafarerPassportApplication',
                                                            name='writeSeafarerPassportApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='readSeafarerPassportApplication',
                                                            name='readSeafarerPassportApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Смена статуса заявки на ПОМ')
        diploma_passport.group.add(group)
        ct = ContentType.objects.get(model='statementsailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='writeSeafarerPassportApplicationStatus',
                                                            name='writeSeafarerPassportApplicationStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        permission, _ = Permission.objects.update_or_create(codename='readSeafarerPassportApplication',
                                                            name='readSeafarerPassportApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр списка НТЗ БО')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='ntz')
        permission, _ = Permission.objects.update_or_create(codename='readInstitutionListETI',
                                                            name='readInstitutionListETI',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Редактирование списка НТЗ БО')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='ntz')
        permission, _ = Permission.objects.update_or_create(codename='readInstitutionListETI',
                                                            name='readInstitutionListETI',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='writeInstitutionListETI',
                                                            name='writeInstitutionListETI',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Добавление списка НТЗ БО')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='ntz')
        permission, _ = Permission.objects.update_or_create(codename='readInstitutionListETI',
                                                            name='readInstitutionListETI',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='createInstitutionListETI',
                                                            name='createInstitutionListETI',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Добавление протокола НТЗ')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='ntz')
        permission, _ = Permission.objects.update_or_create(codename='readInstitutionListETI',
                                                            name='readInstitutionListETI',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='createInstitutionListETI',
                                                            name='createInstitutionListETI',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Создание направлений в НТЗ')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='ntz')
        permission, _ = Permission.objects.update_or_create(codename='readETIRegistry',
                                                            name='readETIRegistry',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='createETIRegistry',
                                                            name='createETIRegistry',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр направлений в НТЗ')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='ntz')
        permission, _ = Permission.objects.update_or_create(codename='readETIRegistry',
                                                            name='readETIRegistry',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Редактирование направлений в НТЗ')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='ntz')
        permission, _ = Permission.objects.update_or_create(codename='readETIRegistry',
                                                            name='readETIRegistry',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='writeETIRegistry',
                                                            name='writeETIRegistry',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Редактирования рейтинга НТЗ')
        back_office.group.add(group)
        ct = ContentType.objects.get(model__iexact='ETIMonthRatio')
        permission, _ = Permission.objects.update_or_create(codename='readDealingETI',
                                                            name='readDealingETI',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='writeDealingETI',
                                                            name='writeDealingETI',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Проставление рейтинга моряка')
        back_office.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model__iexact='rating')
        permission, _ = Permission.objects.update_or_create(codename='ratingSailor',
                                                            name='ratingSailor',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Изменение рейтинга моряка')
        back_office.group.add(group)
        ct = ContentType.objects.get(model__iexact='rating')
        permission, _ = Permission.objects.update_or_create(codename='changeRating',
                                                            name='changeRating',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Список документов на верификацию агента')
        verification.group.add(group)
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model__iexact='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='readAgentVerificationDocs',
                                                            name='readAgentVerificationDocs',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр заявок на мед сертификат')
        agent.group.add(group)
        secretary_sqc.group.add(group)
        medical.group.add(group)
        ct = ContentType.objects.get(model__iexact='StatementMedicalCertificate')
        permission, _ = Permission.objects.get_or_create(codename='readStatementMedicalCertificate',
                                                         name='readStatementMedicalCertificate',
                                                         content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Редактирование заявок на мед сертификат')
        agent.group.add(group)
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model__iexact='StatementMedicalCertificate')
        permission, _ = Permission.objects.update_or_create(codename='readStatementMedicalCertificate',
                                                            name='readStatementMedicalCertificate',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='writeStatementMedicalCertificate',
                                                            name='writeStatementMedicalCertificate',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Смена статуса заявок на мед сертификаты')
        verification.group.add(group)
        back_office.group.add(group)
        medical.group.add(group)
        ct = ContentType.objects.get(model__iexact='StatementMedicalCertificate')
        permission, _ = Permission.objects.update_or_create(codename='readStatementMedicalCertificate',
                                                            name='readStatementMedicalCertificate',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='writeStatementMedicalCertificateStatus',
                                                            name='writeStatementMedicalCertificateStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр заявок на мед сертификаты')
        agent.group.add(group)
        head_agent_group.group.add(group)
        secretary_sqc.group.add(group)
        medical.group.add(group)
        ct = ContentType.objects.get(model__iexact='StatementMedicalCertificate')
        permission, _ = Permission.objects.update_or_create(codename='readStatementMedicalCertificate',
                                                            name='readStatementMedicalCertificate',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Добавление заявок на мед сертификаты')
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model__iexact='StatementMedicalCertificate')
        permission, _ = Permission.objects.update_or_create(codename='readStatementMedicalCertificate',
                                                            name='readStatementMedicalCertificate',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='createStatementMedicalCertificate',
                                                            name='createStatementMedicalCertificate',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)
        group, _ = Group.objects.get_or_create(name='Редактирование заявок на свидетельсто повышения квалификации')
        agent.group.add(group)
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model__iexact='StatementAdvancedTraining')
        permission, _ = Permission.objects.update_or_create(codename='readStatementAdvancedTraining',
                                                            name='readStatementAdvancedTraining',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='writeStatementAdvancedTraining',
                                                            name='writeStatementAdvancedTraining',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Смена статуса заявок на свидетельсто повышения квалификации')
        verification.group.add(group)
        back_office.group.add(group)
        ct = ContentType.objects.get(model__iexact='StatementAdvancedTraining')
        permission, _ = Permission.objects.update_or_create(codename='readStatementAdvancedTraining',
                                                            name='readStatementAdvancedTraining',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='writeStatementAdvancedTrainingStatus',
                                                            name='writeStatementAdvancedTrainingStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр заявок на свидетельсто повышения квалификации')
        agent.group.add(group)
        head_agent_group.group.add(group)
        secretary_sqc.group.add(group)
        eti_employee.group.add(group)
        secretary_atc.group.add(group)
        ct = ContentType.objects.get(model__iexact='StatementAdvancedTraining')
        permission, _ = Permission.objects.update_or_create(codename='readStatementAdvancedTraining',
                                                            name='readStatementAdvancedTraining',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Добавление заявок на свидетельсто повышения квалификации')
        secretary_sqc.group.add(group)
        ct = ContentType.objects.get(model__iexact='StatementAdvancedTraining')
        permission, _ = Permission.objects.update_or_create(codename='readStatementAdvancedTraining',
                                                            name='readStatementAdvancedTraining',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        permission, _ = Permission.objects.update_or_create(codename='createStatementAdvancedTraining',
                                                            name='createStatementAdvancedTraining',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        ct = ContentType.objects.get(model__iexact='ntz')
        permission, _ = Permission.objects.update_or_create(codename='ETICertificationIntegration',
                                                            name='ETICertificationIntegration',
                                                            defaults={'content_type': ct})
        permission, _ = Permission.objects.update_or_create(codename='ETICertificationIntegration',
                                                            name='ETICertificationIntegration',
                                                            defaults={'content_type': ct})

        group, _ = Group.objects.get_or_create(name='Просмотр своих подчиненных агентов')
        head_agent_group.group.add(group)
        ct = ContentType.objects.get(model__iexact='user')
        permission, _ = Permission.objects.update_or_create(codename='readAgentGroups',
                                                            name='readAgentGroups',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр гражданского паспорта')
        medical.group.add(group)
        eti_employee.group.add(group)
        secretary_atc.group.add(group)
        ct = ContentType.objects.get(model__iexact='passport')
        permission, _ = Permission.objects.update_or_create(codename='readCitizenPassport',
                                                            name='readCitizenPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр паспорта моряка')
        medical.group.add(group)
        eti_employee.group.add(group)
        secretary_atc.group.add(group)
        ct = ContentType.objects.get(model__iexact='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='readSeafarerPassport',
                                                            name='readSeafarerPassport',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Создание мед справки с заявки')
        medical.group.add(group)
        ct = ContentType.objects.get(model__iexact='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='writeStatementMedicalToDocument',
                                                            name='writeStatementMedicalToDocument',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр страницы моряка')
        medical.group.add(group)
        eti_employee.group.add(group)
        secretary_atc.group.add(group)
        ct = ContentType.objects.get(model='profile')
        permission, _ = Permission.objects.update_or_create(codename='readMainInfo',
                                                            name='readMainInfo',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='просмотр агента моряка')
        head_agent_group.group.add(group)
        ct = ContentType.objects.get(model='user')
        permission, _ = Permission.objects.update_or_create(codename='readAgentInfo',
                                                            name='readAgentInfo',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Редактирование квал документов в любом статусе')
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='writeQualificationInAnyStatus',
                                                            name='writeQualificationInAnyStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Редактирование заявок квал документов в любом статусе')
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='writeQualificationApplicationInAnyStatus',
                                                            name='writeQualificationApplicationInAnyStatus',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Редактирование заявок квал документов')
        agent.group.add(group)
        ct = ContentType.objects.get(model='statementqualification')
        permission, _ = Permission.objects.update_or_create(codename='writeQualificationApplication',
                                                            name='writeQualificationApplication',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        # Change status for preverification documents

        group, _ = Group.objects.update_or_create(name='Преверификация мед справки')
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='writeMedicalPreVerificationStatus',
                                                            name='writeMedicalPreVerificationStatus',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Редактирование мед справки на преверификации')
        secretary_service.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='writeMedicalPreVerification',
                                                            name='writeMedicalPreVerification',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Преверификация мед справки')
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='writeMedicalPreVerificationStatus',
                                                            name='writeMedicalPreVerificationStatus',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Преверификация ПКМ')
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeRecordBookPreVerificationStatus',
                                                            name='writeRecordBookPreVerificationStatus',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Редактирование ПКМ на преверификации')
        secretary_service.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeRecordBookPreVerification',
                                                            name='writeRecordBookPreVerification',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Преверификация стажа')
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeExperiencePreVerificationStatus',
                                                            name='writeExperiencePreVerificationStatus',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Редактирование стажа в преверификации')
        secretary_service.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='writeExperiencePreVerification',
                                                            name='writeExperiencePreVerification',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Преверификация квал документов(ДПО, ДПВ)')
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='writeQualificationPreVerificationStatus',
                                                            name='writeQualificationPreVerificationStatus',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Редактирование квал доков в преверификации')
        secretary_service.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='writeQualificationPreVerification',
                                                            name='writeQualificationPreVerification',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Преверификация образовательных документов')
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='writeGraduationPreVerificationStatus',
                                                            name='writeGraduationPreVerificationStatus',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Редактирование образовательных доков в преверификации')
        secretary_service.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='writeGraduationPreVerification',
                                                            name='writeGraduationPreVerification',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Преверификация ПОМ(паспорт моряка)')
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='writeSeafarerPassportPreVerificationStatus',
                                                            name='writeSeafarerPassportPreVerificationStatus',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Редактирование ПОМ')
        secretary_service.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='writeSeafarerPassportPreVerification',
                                                            name='writeSeafarerPassportPreVerification',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Создание существующих квал документов')
        agent.group.add(group)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='createExistsQualification',
                                                            name='createExistsQualification',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Преверификация заявки на ДКК')
        secretary_service.group.add(group)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='writeApplicationSQCPreVerificationStatus',
                                                            name='writeApplicationSQCPreVerificationStatus',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Редактирование заявки на дкк на преверификации')
        secretary_service.group.add(group)
        agent.group.add(group)
        ct = ContentType.objects.get(model='statementsqc')
        permission, _ = Permission.objects.update_or_create(codename='writeApplicationSQCPreVerification',
                                                            name='writeApplicationSQCPreVerification',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Удаление ПОМ')
        agent.group.add(group)
        back_office.group.add(group)
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='deleteSeafarerPassport',
                                                            name='deleteSeafarerPassport',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Удаление образовательного документа')
        agent.group.add(group)
        back_office.group.add(group)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='deleteGraduation',
                                                            name='deleteGraduation',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Удаление заявления СПК')
        agent.group.add(group)
        back_office.group.add(group)
        ct = ContentType.objects.get(model='statementadvancedtraining')
        permission, _ = Permission.objects.update_or_create(codename='deleteStatementAdvancedTraining',
                                                            name='deleteStatementAdvancedTraining',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Удаление ПКМ')
        agent.group.add(group)
        back_office.group.add(group)
        ct = ContentType.objects.get(model='servicerecord')
        permission, _ = Permission.objects.update_or_create(codename='deleteRecordBook',
                                                            name='deleteRecordBook',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Удаление записи в ПКМ')
        agent.group.add(group)
        back_office.group.add(group)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='deleteRecordBookEntry',
                                                            name='deleteRecordBookEntry',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Удаление стажа')
        agent.group.add(group)
        back_office.group.add(group)
        ct = ContentType.objects.get(model='lineinservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='deleteExperience',
                                                            name='deleteExperience',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Удаление заявления ПКМ')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='statementservicerecord')
        permission, _ = Permission.objects.update_or_create(codename='deleteApplicationRecordBook',
                                                            name='deleteApplicationRecordBook',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Удаление мед сертификата')
        agent.group.add(group)
        back_office.group.add(group)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='deleteMedical',
                                                            name='deleteMedical',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Удаление заявления на мед сертификат')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='statementmedicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='deleteStatementMedicalCertificate',
                                                            name='deleteStatementMedicalCertificate',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Просмотр списка заявлений ДПО созданных из пакета')
        back_office.group.add(group)
        diploma_passport.group.add(group)
        ct = ContentType.objects.get(model='statementqualification')
        permission, _ = Permission.objects.update_or_create(codename='readListApplicationFromPacket',
                                                            name='readListApplicationFromPacket',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Удаление комментариев к статусу документа на верификации')
        back_office.group.add(group)
        ct = ContentType.objects.get(model='commentforverificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='writeCommentForVerification',
                                                            name='writeCommentForVerification',
                                                            content_type=ct)
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Просмотр образовательных документов')
        eti_employee.group.add(group)
        secretary_atc.group.add(group)
        ct = ContentType.objects.get(model='education')
        permission, _ = Permission.objects.update_or_create(codename='readGraduation',
                                                            name='readGraduation',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.update_or_create(name='Просмотр квалификационных документов')
        eti_employee.group.add(group)
        secretary_atc.group.add(group)
        ct = ContentType.objects.get(model='qualificationdocument')
        permission, _ = Permission.objects.update_or_create(codename='readQualification',
                                                            name='readQualification',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр информации по мед. свидетельствам')
        eti_employee.group.add(group)
        ct = ContentType.objects.get(model='medicalcertificate')
        permission, _ = Permission.objects.update_or_create(codename='readMedical',
                                                            name='readMedical',
                                                            defaults={'content_type': ct})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Создание документа СПК из заявления СПК')
        back_office.group.add(group)
        secretary_atc.group.add(group)
        ct = ContentType.objects.get(model='statementadvancedtraining')
        permission, _ = Permission.objects.update_or_create(codename='createAdvancedTraining',
                                                            defaults={'content_type': ct,
                                                                      'name': 'createAdvancedTraining'})
        group.permissions.add(permission)

        group, _ = Group.objects.get_or_create(name='Просмотр отчета по заявлениям КПК')
        ct = ContentType.objects.get(model='statementadvancedtraining')
        permission, _ = Permission.objects.update_or_create(codename='readReportApplicationATC',
                                                            defaults={'content_type': ct,
                                                                      'name': 'readReportApplicationATC'})
        group.permissions.add(permission)
        back_office.group.add(group)
        secretary_atc.group.add(group)

        group, _ = Group.objects.get_or_create(name='Просмотр отчета по ПОМ')
        ct = ContentType.objects.get(model='sailorpassport')
        permission, _ = Permission.objects.update_or_create(codename='readReportSailorPassport',
                                                            defaults={'content_type': ct,
                                                                      'name': 'readReportSailorPassport'})
        group.permissions.add(permission)
        back_office.group.add(group)

        group, _ = Group.objects.update_or_create(name='Объединение моряков')
        ct = ContentType.objects.get(model='profile')
        permission, _ = Permission.objects.update_or_create(codename='mergeSeafarer',
                                                            defaults={'content_type': ct,
                                                                      'name': 'mergeSeafarer'})
        group.permissions.add(permission)
        back_office.group.add(group)

        return response

    def get(self, request, *args, **kwargs):
        response = self.load_perms()

        return Response({'res': response})

    def delete(self, instance):
        Group.objects.all().delete()
        MainGroups.objects.all().delete()
        return Response({'res': 'ok'})


class VersionViewset(viewsets.ModelViewSet):
    queryset = Version.objects.order_by('-date')[:1]
    serializer_class = serializer.VersionSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class BranchOfficeRestriction(viewsets.ModelViewSet):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)
    serializer_class = serializer.BranchRestrictionForPermSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BranchOfficeRestrictionForPermission.objects.none()
        return BranchOfficeRestrictionForPermission.objects.filter(user=self.request.user)

    @method_decorator(vary_on_headers('Authorization'))
    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class UserNotificationCounter(APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        document_to_sign = CommissionerSignProtocol.objects.filter(signer__user=user, is_signatured=False).count()
        statement_service_record = StatementServiceRecord.objects.exclude(
            status_id__in=(magic_numbers.status_statement_serv_rec_created,
                           magic_numbers.STATUS_REMOVED_DOCUMENT)
        ).count()
        reports_files = ProtocolFiles.objects.filter(user=self.request.user).count()
        user_verification = UserStatementVerification.objects.filter(
            status_document_id=magic_numbers.VERIFICATION_STATUS).count()
        statement_dkk = StatementSQC.objects.only('pk', 'status_documents').filter(
            status_document_id__in=[magic_numbers.status_state_qual_dkk_in_process,
                                    magic_numbers.CREATED_FROM_PERSONAL_CABINET]). \
            values('status_document_id').order_by('status_document_id').annotate(count=Count('status_document_id'))
        statement_dkk_processing = statement_dkk[0]['count']
        statement_dkk_from_personal_cabinet = statement_dkk[1]['count']
        statement_dkk_aproved = StatementSQC.objects.filter(
            protocolsqc__isnull=True, created_at__gte='2020-02-07',
            status_document_id=magic_numbers.status_state_qual_dkk_approv).count()
        unchecked_notification = UserNotification.objects.filter(recipient=self.request.user, is_hidden=False).count()
        if self.request.user.has_perm('sailor.writePostVerificationDocuments'):
            with transaction.atomic():
                sailor_passport = SailorPassport.objects.filter(
                    status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION).count()
                education_doc = Education.objects.filter(
                    status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION).count()
                qual_doc = QualificationDocument.objects.filter(
                    status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION).count()
                service_record = ServiceRecord.objects.filter(
                    status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION).count()
                line_in_serv = LineInServiceRecord.objects.filter(
                    status_line_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION).count()
                medical_cert = MedicalCertificate.objects.filter(
                    status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION).count()
            post_verification = sailor_passport + education_doc + qual_doc + service_record + line_in_serv + medical_cert
        else:
            post_verification = 0
        statement_agent = StatementAgent.objects.filter(
            status_document_id=magic_numbers.status_statement_agent_in_process).count()
        statement_agent_sailor = StatementAgentSailor.objects.filter(agent_id=self.request.user.id).count()
        amount = document_to_sign + statement_service_record + reports_files + user_verification + \
                 statement_dkk_processing + statement_dkk_aproved + statement_dkk_from_personal_cabinet + \
                 post_verification + statement_agent + statement_agent_sailor + unchecked_notification
        resp = {'document_to_sign': document_to_sign, 'statement_service_record': statement_service_record,
                'report_to_download': reports_files, 'user_to_verificate': user_verification,
                'statement_dkk_processing': statement_dkk_processing, 'statement_dkk_aproved': statement_dkk_aproved,
                'statement_dkk_from_personal_cabinet': statement_dkk_from_personal_cabinet,
                'post_verification': post_verification, 'statement_agent': statement_agent,
                'statement_agent_sailor': statement_agent_sailor, 'summ': amount,
                'unchecked_notification': unchecked_notification}
        return Response(resp)


class HistoryByUser(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = FullUserSailorHistory.objects.exclude(user_id=magic_numbers.celery_user_id).order_by('-datetime')
    serializer_class = FullUserSailorHistorySerializer
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = FullUserSailorHistoryFilter
    pagination_class = ShortLinkResultPagination
    permission_classes = (rest_framework.permissions.IsAuthenticated,
                          rest_framework.permissions.IsAdminUser)


class UserIsTrainedView(APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if hasattr(self.request.user, 'userprofile'):
            return Response({'is_trained': user.userprofile.is_trained})
        return Response({'is_trained': False})

    @swagger_auto_schema(request_body=IsTrainedSerializer)
    def patch(self, request, *args, **kwargs):
        serializer = IsTrainedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        if not hasattr(user, 'userprofile'):
            raise NotFound('User has no user_profile')
        old_user = deepcopy(user)
        user.userprofile.is_trained = serializer.validated_data.get('is_trained', False)
        user.userprofile.save(update_fields=['is_trained'])
        save_history.s(user_id=user.id,
                       module='User',
                       action_type='edit',
                       content_obj=user,
                       old_obj=old_user,
                       serializer=UserSerializer,
                       new_obj=user,
                       ).apply_async(serializer='pickle')
        return Response({'response': 'User is trained', 'status': 'success'})
