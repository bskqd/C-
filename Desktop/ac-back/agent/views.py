import base64
import json
import random
from copy import deepcopy
from datetime import datetime
from typing import Union

import pyqrcode as qr
from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Value, Q, Count, CharField
from django.db.models.functions import Concat, Cast
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

import agent.filters
from agent.models import (AgentSailor, StatementAgent, StatementAgentSailor, AgentGroup, CodeToStatementAgentSailor)
from agent.permissions import StatementForAgentPermission, IsHeadGroupsAgent, IsAgentInAgentGroup, IsSecretaryAgent
from agent.serializers import (AgentUserSerializer, StatementAgentSerializer, StatementAgentSailorSerializer,
                               AgentGroupsSerializer, AwaitingCretaeStatementAgentSailorSerializer,
                               StatementAgentSailorPhoneSerializer)
from agent.tasks import (send_email_about_new_statement, send_sms_about_new_statement, send_sms_about_wait_sailor)
from agent.utils import register_sailor_agent
from communication.models import SailorKeys
from directory.models import StatusDocument
from itcs import magic_numbers
from mixins.permission_mixins import IsAgentOrSecretaryOrHeadUser, IsPersonalCabinetUser, IsBackOfficeUser
from reports.filters import ShortLinkResultPagination
from sailor.models import Profile, PhotoProfile, Passport, ContactInfo, Rating
from sailor.tasks import save_history
from sms_auth.misc import send_message
from user_profile.models import UserProfile
from user_profile.serializer import AgentByGroupSerializer

User = get_user_model()


class ListOfMySailorViewset(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsAgentOrSecretaryOrHeadUser)
    queryset = AgentSailor.objects.filter(is_disable=False)
    pagination_class = ShortLinkResultPagination

    def get_queryset(self):
        user = self.request.user
        if user.userprofile.type_user in [user.userprofile.SECRETARY_SERVICE, user.userprofile.HEAD_AGENT]:
            return self.queryset.filter(
                agent__userprofile__agent_group__in=user.userprofile.agent_group.all()
            ).order_by('-modified_at')
        return self.queryset.filter(agent=self.request.user).order_by('-modified_at')

    def list(self, request):
        sailors = self.get_queryset()
        page = self.paginate_queryset(sailors)
        sailor_keys = [sailor.sailor_key for sailor in page]
        keys = SailorKeys.objects.only('id', 'profile', 'citizen_passport').filter(id__in=sailor_keys)
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
            response.append({'id': key_id,
                             'full_name': {'ukr': profile.get_full_name_ukr, 'eng': profile.get_full_name_eng},
                             'photo': photo, 'date_birth': profile.date_birth, 'passport': serial_passport,
                             'tax_number': inn_value,
                             'sex': {'name_ukr': profile.sex.value_ukr, 'name_eng': profile.sex.value_eng},
                             })
        return self.get_paginated_response(response)


class SearchSailorByAgent(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsAgentOrSecretaryOrHeadUser)

    def get_queryset(self):
        user: User = self.request.user
        if user.userprofile.type_user in [user.userprofile.AGENT, user.userprofile.MARAD]:
            agents = list(AgentSailor.objects.filter(
                is_disable=False, agent=self.request.user).values_list('sailor_key', flat=True))
        else:
            agents = list(AgentSailor.objects.filter(
                is_disable=False, agent__userprofile__agent_group__in=user.userprofile.agent_group.all()
            ).values_list('sailor_key', flat=True))
        return SailorKeys.objects.filter(id__in=list(agents))

    def list(self, request, query):
        response = []
        qs = Profile.objects.annotate(fullname_ukr=Concat('last_name_ukr', Value(' '), 'first_name_ukr', Value(' '),
                                                          'middle_name_ukr'),
                                      fullname_eng=Concat('last_name_eng', Value(' '),
                                                          'first_name_eng', Value(' '), 'middle_name_eng'))
        profile = qs.filter(Q(fullname_ukr__icontains=query))[:20]
        if profile:
            for prof in profile:
                key = self.get_queryset().filter(profile=prof.id).first()
                if not key:
                    continue
                try:
                    passport = Passport.objects.filter(id__in=key.citizen_passport).first()
                    serial_passport = passport.serial
                    issued_by_passport = passport.issued_by
                    date_passport = passport.date
                except (Passport.DoesNotExist, AttributeError, TypeError, IndexError):
                    serial_passport = None
                    issued_by_passport = None
                    date_passport = None
                resp_dict = {'id': key.id, 'first_name_eng': prof.first_name_eng,
                             'first_name_ukr': prof.first_name_ukr, 'last_name_ukr': prof.last_name_ukr,
                             'last_name_eng': prof.last_name_eng, 'middle_name_ukr': prof.middle_name_ukr,
                             'middle_name_eng': prof.middle_name_eng, 'date_birth': prof.date_birth,
                             'passport_serial': serial_passport, 'passport_issued_by': issued_by_passport,
                             'passport_date': date_passport}
                response.append(resp_dict)
        passports = Passport.objects.filter(Q(serial__icontains=query) | Q(inn__icontains=query))[:20]
        if passports:
            passport_list_id = list(passports.values_list('id', flat=True))
            keys = self.get_queryset().filter(citizen_passport__overlap=passport_list_id)
            for key in keys:
                passport = [passport for passport in passports if passport.id == key.citizen_passport[0]][0]
                try:
                    profile = Profile.objects.get(id=key.profile)
                except Profile.DoesNotExist:
                    continue
                resp_dict = {'id': key.id, 'first_name_eng': profile.first_name_eng,
                             'first_name_ukr': profile.first_name_ukr, 'last_name_ukr': profile.last_name_ukr,
                             'last_name_eng': profile.last_name_eng, 'middle_name_ukr': profile.middle_name_ukr,
                             'middle_name_eng': profile.middle_name_eng, 'date_birth': profile.date_birth,
                             'passport_serial': passport.serial, 'passport_issued_by': passport.issued_by,
                             'passport_date': passport.date}
                response.append(resp_dict)
        sailor_keys = self.get_queryset().annotate(id_as_char=Cast('id', CharField())).filter(
            id_as_char__contains=query)
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
                resp_dict = {'id': key.id, 'first_name_eng': profile.first_name_eng,
                             'first_name_ukr': profile.first_name_ukr, 'last_name_ukr': profile.last_name_ukr,
                             'last_name_eng': profile.last_name_eng, 'middle_name_ukr': profile.middle_name_ukr,
                             'middle_name_eng': profile.middle_name_eng, 'date_birth': profile.date_birth,
                             'passport_serial': serial_passport, 'passport_issued_by': issued_by_passport,
                             'passport_date': date_passport}
                response.append(resp_dict)
        return Response(response)


class GetAgentQRCode(APIView):
    permission_classes = (IsAuthenticated, IsAgentInAgentGroup)

    def get(self, request):
        agent = self.request.user
        key = base64.b64decode(settings.CRYPTO_KEY)
        fernet_alg = Fernet(key)
        agent_pk_enc = fernet_alg.encrypt(str(agent.pk).encode()).decode()
        qrc = qr.create(f'seaman/qr_code/{agent_pk_enc}/info/')
        qr_code = qrc.png_as_base64_str(scale=10, module_color=(61, 76, 99, 255))
        url_to_apply = f'https://mdu.com.ua/seaman?{agent_pk_enc}/'
        return Response({'qr': f'data:image/png;base64,{qr_code}', 'url': url_to_apply})


class GetInfoAgentByQR(APIView):
    permission_classes = (IsAuthenticated, IsPersonalCabinetUser)

    def get(self, request, payload):
        key = base64.b64decode(settings.CRYPTO_KEY)
        fernet_alg = Fernet(key)
        try:
            payload = payload.replace('?', '').replace('%3D%2F', '=')
            sailor_data = fernet_alg.decrypt(payload.encode()).decode()
            agent_obj = User.objects.get(id=int(sailor_data))
        except AttributeError:
            raise ValidationError('Bad request. Data incomplete', code=404)
        except (InvalidToken, InvalidSignature):
            raise ValidationError('Bad request. Token is invalid or was changed', code=403)
        except User.DoesNotExist:
            raise ValidationError('Bad request. Seaman not found')
        td = datetime.now()
        # if AgentSailor.objects.filter(created_at__year=td.year, created_at_month=td.month, is_disable=False,
        #                               agent=agent_obj).count() >= 30:
        #     raise ValidationError('Agent has reached the limit for the current month')
        return Response(AgentUserSerializer(instance=agent_obj).data)


class ListOfAgent(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = User.objects.filter(userprofile__type_user__in=[UserProfile.AGENT, UserProfile.MARAD], is_active=True)
    serializer_class = AgentUserSerializer
    pagination_class = ShortLinkResultPagination
    permission_classes = (IsAuthenticated, IsAdminUser)
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = agent.filters.AgentListFilter

    def get_queryset(self):
        return self.queryset.all()


class StatementAgentView(viewsets.ModelViewSet):
    queryset = StatementAgent.objects.all()
    serializer_class = StatementAgentSerializer
    permission_classes = (IsAuthenticated, (IsAdminUser | StatementForAgentPermission),)
    permission_classes_by_action = {'create': [AllowAny]}

    def get_parsers(self):
        if self.get_view_name() == 'Upload file':
            self.parser_classes = (MultiPartParser, FormParser)
        return super(StatementAgentView, self).get_parsers()

    @action(methods=['post'], detail=True)
    def upload_file(self, request, *args, **kwargs):
        obj = self.get_object()
        files = request.FILES.getlist('photo')
        files = [PhotoProfile.objects.create(photo=file).pk for file in files]
        obj.photo += files
        obj.save(update_fields=['photo'])
        return Response({'status': 'success'})

    def get_permissions(self):
        if self.get_view_name() in ['Upload file', 'Statement Agent List']:
            return [permission() for permission in (AllowAny,)]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        data = serializer.validated_data

        # TODO Move to serializer validate function
        statements = self.queryset.filter(first_name__iexact=data['first_name'],
                                          last_name__iexact=data['last_name'],
                                          middle_name__iexact=data.get('middle_name', ''),
                                          status_document_id=magic_numbers.status_statement_agent_in_process)
        if statements.exists():
            raise ValidationError('Statement exists')
        serializer.save(status_document_id=magic_numbers.status_statement_agent_in_process)

    def perform_destroy(self, instance):
        _instance = deepcopy(instance)
        instance.delete()

        save_history.s(user_id=self.request.user.id, module='StatementAgent', action_type='delete',
                       content_obj=_instance, serializer=StatementAgentSerializer, old_obj=_instance
                       ).apply_async(serializer='pickle')


class StatementAgentSailorViewset(viewsets.ModelViewSet):
    """
    Sailor's statement to agent
    """
    queryset = StatementAgentSailor.objects.all()
    serializer_class = StatementAgentSailorSerializer
    permission_classes = (IsAuthenticated, (IsPersonalCabinetUser | IsAgentOrSecretaryOrHeadUser | IsBackOfficeUser))
    pagination_class = ShortLinkResultPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = agent.filters.StatementAgentSailorFilter

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return StatementAgentSailor.objects.none()
        user: User = self.request.user
        if hasattr(user, 'userprofile'):
            type_user = user.userprofile.type_user
            if type_user in [user.userprofile.AGENT, user.userprofile.MARAD]:
                return self.queryset.filter(agent_id=user.id).order_by('id')
            elif type_user == user.userprofile.SECRETARY_SERVICE:
                return self.queryset.filter(
                    (Q(status_document_id__in=[magic_numbers.status_statement_agent_sailor_wait_secretary,
                                               magic_numbers.status_statement_agent_sailor_wait_sailor])
                     |
                     (Q(status_document_id=magic_numbers.status_statement_agent_sailor_valid) &
                      Q(date_end_proxy__isnull=True)))
                    &
                    Q(agent__userprofile__agent_group__in=user.userprofile.agent_group.all())
                ).order_by('-modified_at')
            elif type_user == user.userprofile.BACK_OFFICE or user.is_superuser:
                return self.queryset.all().order_by('id')
        try:
            sailor_qs = SailorKeys.objects.only('id').get(user_id=user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        return self.queryset.filter(sailor_key=sailor_qs.id).order_by('id')

    def perform_create(self, serializer):
        user_id = self.request.user.id
        try:
            if not hasattr(self.request.user, 'userprofile'):
                sailor_qs = SailorKeys.objects.only('id', 'agent_id', 'profile').get(user_id=user_id)
            else:
                sailor_qs = serializer.validated_data.get('sailor_key')
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        if sailor_qs.agent_id:
            raise ValidationError('Sailor has seaman')
        agent_id = serializer.initial_data['agent']
        statement = self.queryset.filter(agent_id=agent_id, sailor_key=sailor_qs.id,
                                         status_document_id=magic_numbers.status_statement_agent_sailor_in_process)
        if statement.exists():
            raise ValidationError('Statement exists')
        # td = datetime.now()
        # if AgentSailor.objects.filter(created_at__year=td.year, created_at__month=td.month, is_disable=False,
        #                               agent_id=agent_id).count() >= 30:
        #     raise ValidationError('Agent has reached the limit for the current month')
        ser = serializer.save(status_document_id=magic_numbers.status_statement_agent_sailor_in_process,
                              sailor_key=sailor_qs.id, agent_id=agent_id)
        save_history.s(user_id=user_id, module='StatementAgentSailor', action_type='create', content_obj=ser,
                       serializer=StatementAgentSailorSerializer, new_obj=ser, sailor_key_id=sailor_qs.id
                       ).apply_async(serializer='pickle')
        if self.request.user.userprofile.type_user == self.request.user.userprofile.MARAD:
            return
        profile = Profile.objects.filter(id=sailor_qs.profile).first()
        sailor_full_name = profile.get_full_name_ukr
        agent = User.objects.get(id=agent_id)
        try:
            sailor_contacts_list = json.loads(profile.contact_info)
            sailor_contacts = ContactInfo.objects.filter(id__in=sailor_contacts_list)
            sailor_phone = sailor_contacts.filter(type_contact_id=1).first().value
        except (AttributeError, TypeError):
            sailor_phone = ''
        try:
            agent_contacts = ContactInfo.objects.filter(id__in=agent.userprofile.contact_info)
            email = agent_contacts.filter(type_contact_id=2).first().value
            phone = agent_contacts.filter(type_contact_id=1).first().value
            agent_full_name = f'{agent.last_name} {agent.first_name} {agent.userprofile.middle_name}'
            send_email_about_new_statement.s(email=email, sailor_full_name=sailor_full_name,
                                             sailor_phone=sailor_phone).apply_async()
            send_sms_about_new_statement.s(phone=phone, sailor_full_name=sailor_full_name,
                                           agent_full_name=agent_full_name).apply_async()
        except AttributeError:
            pass

    def perform_destroy(self, instance):
        _instance = deepcopy(instance)
        instance.delete()

        save_history.s(user_id=self.request.user.id, module='StatementAgentSailor', action_type='delete',
                       content_obj=_instance, serializer=StatementAgentSailorSerializer, old_obj=_instance
                       ).apply_async(serializer='pickle')

    def perform_update(self, serializer):
        statement: StatementAgentSailor = self.get_object()
        is_agent = False
        userprofile: UserProfile = self.request.user.userprofile
        if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.type_user == 'agent':
            is_agent = True
        status_document: Union[StatusDocument, None] = serializer.validated_data.get('status_document')
        if (status_document and status_document.pk in [magic_numbers.status_statement_agent_sailor_valid] and
                self.request.user.is_superuser and statement.agent.userprofile.type_user == UserProfile.MARAD):
            register_sailor_agent(sailor=SailorKeys.objects.get(id=statement.sailor_key), statement=statement,
                                  user_change=self.request.user)
            Rating.objects.create(rating=4, sailor_key=statement.sailor_key)
        elif (status_document and status_document.pk in [magic_numbers.status_statement_agent_sailor_valid,
                                                         magic_numbers.status_statement_agent_sailor_wait_sailor] and
              is_agent and not self.request.user.is_superuser):
            status_document = StatusDocument.objects.get(
                id=magic_numbers.status_statement_agent_sailor_wait_secretary)
        elif (status_document and status_document.pk in [magic_numbers.status_statement_agent_sailor_valid,
                                                         magic_numbers.status_statement_agent_sailor_wait_sailor] and
              userprofile.type_user in [userprofile.SECRETARY_SERVICE, userprofile.BACK_OFFICE]):
            status_document = StatusDocument.objects.get(id=magic_numbers.status_statement_agent_sailor_wait_sailor)
            send_sms_about_wait_sailor.s(statement_id=statement.pk).apply_async()
        serializer.save(status_document=status_document, is_agent=is_agent)

    @action(methods=['post'], detail=True)
    def upload_file(self, request, *args, **kwargs):
        obj = self.get_object()
        files = request.FILES.getlist('photo')
        files = [PhotoProfile.objects.create(photo=file).pk for file in files]
        obj.photo += files
        obj.save(update_fields=['photo'])
        return Response({'status': 'success'})


class StatementSailorToAgentView(APIView):
    """
    Send statement from personal cabinet to agent with qr code
    """
    permission_classes = (IsAuthenticated, IsPersonalCabinetUser)

    def get(self, request, payload):
        key = base64.b64decode(settings.CRYPTO_KEY)
        fernet_alg = Fernet(key)
        try:
            sailor_data = fernet_alg.decrypt(payload.encode()).decode()
            agent_obj = User.objects.get(id=int(sailor_data))
        except AttributeError:
            raise ValidationError('Bad request. Data incomplete', code=404)
        except (InvalidToken, InvalidSignature):
            raise ValidationError('Bad request. Token is invalid or was changed', code=403)
        except User.DoesNotExist:
            raise ValidationError('Bad request. Seaman not found')
        sailor_user = self.request.user
        sailor_key = SailorKeys.objects.filter(user_id=sailor_user.pk).first()
        if not sailor_key:
            raise ValidationError('Please use account with personal cabinet')
        if sailor_key.agent_id:
            raise ValidationError('Sailor has a seaman')
        td = datetime.now()
        # if AgentSailor.objects.filter(created_at__year=td.year, created_at__month=td.month, is_disable=False,
        #                               agent=agent_obj).count() >= 30:
        #     raise ValidationError('Agent has reached the limit for the current month')
        has_statement = StatementAgentSailor.objects.filter(sailor_key=sailor_key.id, agent=agent_obj).exclude(
            status_document_id__in=[magic_numbers.status_statement_agent_sailor_invalid,
                                    magic_numbers.status_statement_agent_sailor_valid])
        if has_statement.exists():
            raise ValidationError('Sailor has statement to this seaman')
        statement = StatementAgentSailor.objects.create(
            status_document_id=magic_numbers.status_statement_agent_sailor_in_process,
            sailor_key=sailor_key.id, agent_id=agent_obj.id)
        profile = Profile.objects.filter(id=sailor_key.profile).first()
        sailor_full_name = profile.get_full_name_ukr

        agent_contacts = ContactInfo.objects.filter(id__in=agent_obj.userprofile.contact_info)
        try:
            email = agent_contacts.filter(type_contact_id=2).first().value
            phone = agent_contacts.filter(type_contact_id=1).first().value
            agent_full_name = f'{agent_obj.last_name} {agent_obj.first_name} {agent_obj.userprofile.middle_name}'
            try:
                sailor_contacts_list = json.loads(profile.contact_info)
                sailor_contacts = ContactInfo.objects.filter(id__in=sailor_contacts_list)
                sailor_phone = sailor_contacts.filter(type_contact_id=1).first().value
            except (AttributeError, TypeError):
                sailor_phone = ''
            send_email_about_new_statement.s(email=email, sailor_full_name=sailor_full_name,
                                             sailor_phone=sailor_phone).apply_async()
            send_sms_about_new_statement.s(phone=phone, sailor_full_name=sailor_full_name,
                                           agent_full_name=agent_full_name).apply_async()
        except AttributeError:
            pass
        save_history.s(user_id=sailor_user.id, module='StatementAgentSailor', action_type='create',
                       content_obj=statement, serializer=StatementAgentSailorSerializer, new_obj=statement,
                       sailor_key_id=sailor_key.id).apply_async(serializer='pickle')

        return Response({'status': 'success'}, status=201)


class AgentGroupsViewset(viewsets.ModelViewSet):
    permission_classes = ((IsAdminUser | IsHeadGroupsAgent | IsSecretaryAgent),)
    queryset = AgentGroup.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = AgentGroupsSerializer


class AgentsByGroupViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Informations about agents by group
    """
    permission_classes = (IsAuthenticated, (IsAgentOrSecretaryOrHeadUser | IsHeadGroupsAgent),)
    queryset = AgentGroup.objects.all()
    serializer_class = AgentByGroupSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        user = self.request.user
        if self.request.user.is_superuser:
            return self.queryset.all()
        return user.userprofile.agent_group.all()


class CheckAgentStatementView(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsPersonalCabinetUser)
    queryset = StatementAgentSailor.objects.all()

    def get(self, request, *args, **kwargs):
        sailor = kwargs.get('sailor_id')
        statement = self.queryset.filter(
            agent_id=self.request.user, sailor_key=sailor,
            status_document_id__in=[magic_numbers.status_statement_agent_sailor_in_process,
                                    magic_numbers.status_statement_agent_sailor_wait_secretary])
        return Response({'has_statement': statement.exists()})


class PhoneCodeToStatementAgentSailor(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsPersonalCabinetUser)

    def list(self, request, *args, **kwargs):
        awaiting_confirmation = CodeToStatementAgentSailor.objects.filter(agent=request.user)
        awaiting = AwaitingCretaeStatementAgentSailorSerializer(awaiting_confirmation, many=True).data
        return Response({'awaiting_confirmation': awaiting})

    @swagger_auto_schema(request_body=StatementAgentSailorPhoneSerializer)
    def post(self, request, *args, **kwargs):
        serializer = StatementAgentSailorPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        phone = data.get('phone')
        security_code = data.get('security_code')
        agent = request.user
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            raise ValidationError('Sailor does not found')
        if not security_code:
            self.check_and_send_security_code(phone=phone, user=user, agent=agent)
            return Response({'status': 'success', 'description': 'Sent SMS to the sailor'})
        else:
            try:
                code = CodeToStatementAgentSailor.objects.get(phone=phone, security_code=security_code)
            except CodeToStatementAgentSailor.DoesNotExist:
                raise ValidationError('Invalid security code')
            code.delete()
            self.create_statement_agent_sailor(phone=phone,
                                               sailor_id=code.sailor_key,
                                               user=user,
                                               agent=agent)
            return Response({'status': 'success', 'description': 'Statement create'})

    def check_and_send_security_code(self, phone=None, user=None, agent=None):
        code = CodeToStatementAgentSailor.objects.filter(phone=phone)
        if code.exists():
            raise ValidationError('Code has been sent to this phone')
        sailor_key = SailorKeys.objects.filter(user_id=user.id).first()
        if sailor_key.agent_id or sailor_key.pk != int(user.last_name):
            raise ValidationError('You cannot interact with this sailor')
        self.check_exists_staement_agent_sailor(agent=agent, sailor_id=sailor_key.pk)
        self.send_sms_with_security_code(phone=phone, sailor_key=sailor_key.pk, agent_id=agent.id)
        return True

    def create_statement_agent_sailor(self, phone=None, sailor_id=None, user=None, agent=None):
        self.check_exists_staement_agent_sailor(agent=agent, sailor_id=sailor_id)
        statement = StatementAgentSailor.objects.create(
            agent=agent,
            sailor_key=int(user.last_name),
            status_document_id=magic_numbers.status_statement_agent_sailor_in_process)
        save_history.s(user_id=agent.id,
                       module='StatementAgentSailor',
                       action_type='create',
                       content_obj=statement,
                       serializer=StatementAgentSailorSerializer,
                       new_obj=statement,
                       sailor_key_id=int(user.last_name),
                       ).apply_async(serializer='pickle')
        return True

    @staticmethod
    def create_security_code(phone=None, agent_id=None, sailor_key=None):
        not_exist_code = True
        security_code = random.randint(1000, 9999)
        while not_exist_code:
            exists_code = CodeToStatementAgentSailor.objects.filter(security_code=security_code)
            if exists_code.exists():
                security_code = random.randint(1000, 9999)
                continue
            not_exist_code = False
        CodeToStatementAgentSailor.objects.create(security_code=security_code,
                                                  phone=phone,
                                                  agent_id=agent_id,
                                                  sailor_key=sailor_key)
        return security_code

    def send_sms_with_security_code(self, phone=None, agent_id=None, sailor_key=None):
        security_code = self.create_security_code(phone=phone, agent_id=agent_id, sailor_key=sailor_key)
        text = f'{security_code} - код для створення заяви з довіренною особою. Передайте цей код Вашій' \
               f' довіренній особі.'
        send_message(phone=phone, message=text, service='sms-fly', alpha_name='AirXpress')
        return True

    @staticmethod
    def check_exists_staement_agent_sailor(agent=None, sailor_id=None):
        today = datetime.today().date()
        statement = StatementAgentSailor.objects.filter(
            Q(agent=agent) & Q(sailor_key=sailor_id) &
            (Q(date_end_proxy__isnull=True) | Q(date_end_proxy__gte=today)))
        if statement.exists():
            raise ValidationError('You have statement with this sailor')
