from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, mixins, viewsets, permissions, generics
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

import authorization.mail.filters
import authorization.mail.permissions
import authorization.mail.serializers
import authorization.mail.tasks
from authorization.mail.models import UserInvitation
from core.models import User, Agent
from directory.models import Contacts


class InvitationAgentView(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = UserInvitation.objects.all()
    serializer_class = authorization.mail.serializers.InvitationSerializer
    permission_classes = (permissions.IsAuthenticated, authorization.mail.permissions.SentInvitePermissions)
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = authorization.mail.filters.InvitationFilters

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserInvitation.objects.none()
        if self.request.user.type_user == User.HEAD_AGENCY_CH:
            return UserInvitation.objects.filter(agency=self.request.user.get_agency)
        return UserInvitation.objects.all()

    @swagger_auto_schema(method='post', request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email')
    }))
    @action(methods=['post'], detail=False)
    def refresh_invite(self, request):
        email = request.data['email']
        try:
            invite = UserInvitation.objects.get(email=email)
        except UserInvitation.DoesNotExist:
            raise ValidationError('The invitation for this user does not exist')
        if invite.accepted:
            raise ValidationError('User was registered')
        invite.sent = None
        invite.save(update_fields=['sent'])
        authorization.mail.tasks.send_mail_to_agent.s(invite.pk).apply_async()
        return Response({'status': 'success', 'detail': 'The invitation has been sent again'}, status=201)


class RegistrationByToken(generics.GenericAPIView):
    serializer_class = authorization.mail.serializers.UserAgentMailSerializer

    def post(self, request, key=None):
        if not key:
            raise ValidationError('Please write correct invite token')
        try:
            invite = UserInvitation.objects.get(key=key)
        except UserInvitation.DoesNotExist:
            raise ValidationError('Key does not exist')
        if invite.accepted:
            raise ValidationError('User was registered')
        if invite.sent + timedelta(hours=settings.TIME_TO_ACTIVATE_HRS) < timezone.now():
            raise ValidationError('Confirmation was expired')
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        agent_data = data.pop('agent', None)
        password = data.pop('password', None)
        contacts = data.pop('contacts', [])
        agent_user = User.objects.create_user(email=invite.email,
                                              password=password,
                                              type_user=User.AGENT_CH,
                                              type_authorization=User.get_type_authorization(User.AGENT_CH),
                                              **data)
        Agent.objects.create(user=agent_user,
                             agency=invite.agency,
                             **agent_data)
        agent_user.set_default_permission()
        if contacts:
            Contacts.objects.bulk_create([Contacts(user=agent_user, **contact) for contact in contacts])
        invite.created_user = agent_user
        invite.accepted = True
        invite.save(update_fields=['accepted', 'created_user'])
        if agent_user.type_authorization == agent_user.TOTP:
            refresh_token = RefreshToken.for_user(user=agent_user)
            access_token = refresh_token.access_token
            access_token.set_exp(lifetime=timedelta(minutes=10))
            return Response({'status': 'success', 'id': agent_user.id,
                             'type_authorization': agent_user.type_authorization,
                             'token': str(refresh_token.access_token)}, status=status.HTTP_201_CREATED)
        elif agent_user.type_authorization == agent_user.BASIC:
            token, _ = Token.objects.get_or_create(user=agent_user)
            return Response({'status': 'success', 'id': agent_user.id,
                             'type_authorization': agent_user.type_authorization,
                             'token': str(token.key)}, status=status.HTTP_201_CREATED)


    def get(self, request, key=None):
        if not key:
            raise ValidationError('Please write correct invite token')
        try:
            invite = UserInvitation.objects.get(key=key)
        except UserInvitation.DoesNotExist:
            raise ValidationError('Key does not exist')
        if invite.accepted:
            raise ValidationError('User was registered')
        if invite.sent + timedelta(hours=settings.TIME_TO_ACTIVATE_HRS) < timezone.now():
            raise ValidationError('Confirmation was expired')
        return Response({'status': 'success', 'detail': 'Can be register'}, status=200)
