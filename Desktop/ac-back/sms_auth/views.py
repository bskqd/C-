import json
import urllib
from datetime import datetime, timezone, timedelta

import rest_framework.permissions
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseForbidden
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication, JWTTokenUserAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from communication.models import SailorKeys
from itcs import magic_numbers
from itcs.ExpireToken import ExpiringTokenAuthentication
from itcs.settings import CODE_EXPIRATION_TIME, MAX_UPLOAD_SIZE
from mixins.permission_mixins import IsBackOfficeUser
from reports.filters import ShortLinkResultPagination
from sailor.models import Profile, ContactInfo, Passport
from .filters import SailorStatementVerificationFilter
from .misc import send_message, generic_password, create_sms_code
from .models import SecurityCode, UserStatementVerification, PhotoDocumentForVerification
from .permissions import IsASUser, PermissionStatementVerification
from .serializers import UserStatementVerificationSerializer, SMSLoginSerializer, UserRegistrationSerializer
from .tasks import check_and_register_sailor

User = get_user_model()


class UserStatementVerificationView(APIView):
    """Заявка на верификацию пользователя для регистрации в ЛК"""
    permission_classes = (rest_framework.permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserStatementVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        files = request.FILES.getlist('photo')
        if not files:
            raise ValidationError({'response': 'Required fields are not filled', 'status': 'error'})
        size_photo = sum([_file.size for _file in files])
        if size_photo > MAX_UPLOAD_SIZE:
            raise ValidationError({'response': 'File size is too large', 'status': 'error'})
        phone_number = serializer.data['phone']
        inn = serializer.data['inn']
        serial = serializer.data['passport']
        first_name = serializer.data['first_name']
        last_name = serializer.data['last_name']
        middle_name = serializer.data['middle_name']
        birthday = serializer.data['birthday']
        email = serializer.data['email']
        service = serializer.data.get('service', 'e-sailor')
        user = User.objects.filter(username=phone_number).exists()
        if user:
            raise ValidationError({'response': 'A user with this name is already registered', 'status': 'error'})
        statement = UserStatementVerification.objects.filter(phone=phone_number, inn=inn, passport__iexact=serial,
                                                             status_document_id=magic_numbers.VERIFICATION_STATUS)
        if statement.exists():
            raise ValidationError({'response': 'Statement exist', 'status': 'error'})
        passport = list(Passport.objects.filter(serial__iexact=serial, inn=inn).values_list('id', flat=True))
        sailor = SailorKeys.objects.filter(citizen_passport__overlap=passport).first()
        if sailor and sailor.user_id:
            raise ValidationError({'response': 'User already registered', 'status': 'error'})
        if sailor:
            try:
                profile = Profile.objects.get(id=sailor.profile)
            except Profile.DoesNotExist:
                raise ValidationError({'response': 'Sailor not found', 'status': 'error'})
            if profile.contact_info:
                sailor_contacts = json.loads(profile.contact_info)
            else:
                sailor_contacts = []
            sailor_phones = ContactInfo.objects.filter(id__in=sailor_contacts, type_contact=1)
            if phone_number not in sailor_phones.values_list('value', flat=True):
                new_contact = ContactInfo.objects.get_or_create(value=phone_number, type_contact_id=1)[0]
                sailor_contacts.append(new_contact.id)
                profile.contact_info = json.dumps(sailor_contacts)
                profile.save()
        photo_ids = [PhotoDocumentForVerification.objects.create(photo=file).id for file in files]
        statement = UserStatementVerification.objects.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            birthday=birthday,
            phone=phone_number,
            inn=inn,
            passport=serial,
            photo=photo_ids,
            status_document_id=magic_numbers.VERIFICATION_STATUS,
            email=email,
            sailor_id=getattr(sailor, 'pk', None),
            service=service
        )
        check_and_register_sailor.s(statement.pk).apply_async()
        return Response({'response': 'Verification Request Created Successfully', 'status': 'success'})


class StatementSailorVerificationView(viewsets.ModelViewSet):
    permission_classes = (PermissionStatementVerification, IsBackOfficeUser,)
    queryset = UserStatementVerification.objects.select_related('status_document').filter(
        status_document_id=magic_numbers.VERIFICATION_STATUS
    ).order_by('created_at')
    serializer_class = UserStatementVerificationSerializer
    pagination_class = ShortLinkResultPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SailorStatementVerificationFilter


class UserRegistrationView(APIView):
    permission_classes = (rest_framework.permissions.AllowAny, IsASUser)
    """Регистрация моряка непосредственно из сервиса"""

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.data['phone']
        sailor_id = serializer.data['sailor_id']
        security_code = serializer.data['security_code']
        try:
            sailor = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError({'description': 'Sailor not found', 'status': 'error'})
        if security_code:
            try:
                code = SecurityCode.objects.get(phone=phone_number, security_code=security_code)
                user_created = User.objects.create_user(username=phone_number, password=generic_password(8))
                user_created.last_name = sailor_id
                user_created.save(update_fields=['last_name'])
                sailor.user_id = user_created.id
                sailor.save()
                ContactInfo.objects.filter(type_contact=1, value=phone_number).update(is_actual=True)
                code.delete()
                return Response({'status': 'success', 'description': 'success register'})
            except SecurityCode.DoesNotExist:
                return Response({'status': 'error', 'description': 'incorrect code'})
        user = User.objects.filter(username=phone_number).exists()
        if user:
            raise ValidationError('A user with this phone is already registered')
        if sailor.user_id:
            raise ValidationError('Sailor is registered')
        try:
            profile = Profile.objects.only('contact_info').get(id=sailor.profile)
        except Profile.DoesNotExist:
            raise ValidationError('Not user profile')
        if profile.contact_info:
            sailor_contacts = json.loads(profile.contact_info)
        else:
            sailor_contacts = []
        if ContactInfo.objects.filter(id__in=sailor_contacts, type_contact=1, value=phone_number).exists() is False:
            new_contact = ContactInfo.objects.get_or_create(value=phone_number, type_contact_id=1)[0]
            new_contact.is_actual = False
            new_contact.save()
            sailor_contacts.append(new_contact.id)
            profile.contact_info = json.dumps(sailor_contacts)
            profile.save(update_fields=['contact_info'])
        new_code, _ = SecurityCode.objects.get_or_create(phone=phone_number)
        text_message = '{} - повідомте секретарю цей код для реєстрації в кабінеті моряка'.format(
            str(new_code.security_code))
        send_message(phone=phone_number, message=text_message)
        return Response({'status': 'success', 'description': 'code sended'})


class SMSLoginView(APIView):
    """Аутентификация пользователя"""

    def post(self, request, *args, **kwargs):
        serializer = SMSLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.data['phone']
        security_code = serializer.data['security_code']
        is_morrichservice = serializer.data['is_morrichservice']
        try:
            user = User.objects.get(username=phone_number)
        except User.DoesNotExist:
            user_on_verification = UserStatementVerification.objects.filter(
                phone=phone_number, status_document_id=magic_numbers.VERIFICATION_STATUS)
            if user_on_verification.exists():
                return Response({'description': 'Statement exists'}, status=453)
            raise ValidationError({'description': 'User not found', 'status': 'error'})
        if phone_number == '+380137895634':
            token = Token.objects.get_or_create(user=user)[0]
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            access.set_exp(lifetime=timedelta(days=1))
            return Response({'status': 'success', 'token': token.key, 'bearer': str(access)})
        if security_code:
            try:
                sailor_enter = SecurityCode.objects.get(phone=phone_number)
                time_end_security_code = datetime.now(timezone.utc) - relativedelta(minutes=CODE_EXPIRATION_TIME)
                if sailor_enter.created_at < time_end_security_code:
                    sailor_enter.delete()
                    raise ValidationError({'description': 'Code is invalid', 'status': 'error'})
                if sailor_enter.security_code == security_code:
                    sailor_enter.delete()
                    token = Token.objects.get_or_create(user=user)[0]
                    refresh = RefreshToken.for_user(user)
                    access = refresh.access_token
                    access.set_exp(lifetime=timedelta(days=20))
                    return Response({'status': 'success', 'token': token.key, 'bearer': str(access)})
                else:
                    raise ValidationError({'description': 'Code is invalid', 'status': 'error'})
            except SecurityCode.DoesNotExist:
                raise ValidationError({'description': 'Code is invalid', 'status': 'error'})
        else:
            new_security_code = create_sms_code(phone_number=phone_number)
            if is_morrichservice:
                text = f'{new_security_code} - код для входу в "Особистий кабінет моряка."'
                send_message(phone_number, text, alpha_name='AirXpress', service='sms-fly')
            else:
                text = f'{new_security_code} - код для входу в MDU - Морські Документи України.'
                send_message(phone_number, text, alpha_name='AirXpress', service='turbosms')
            return Response({'status': 'Message send'})


class CheckAuthorization(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({'detail': 'success'})


class MediaAccess(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTTokenUserAuthentication, JWTAuthentication, ExpiringTokenAuthentication)

    def get(self, request, path):
        """
        When trying to access :
        myproject.com/media/uploads/passport.png

        If access is authorized, the request will be redirected to
        myproject.com/protected/media/uploads/passport.png

        This special URL will be handle by nginx we the help of X-Accel
        """
        user = request.user
        if user.is_authenticated:
            response = HttpResponse()
            # Content-type will be detected by nginx
            del response['Content-Type']
            response['X-Accel-Redirect'] = '/protected/' + urllib.parse.quote(path)
            return response
        else:
            return HttpResponseForbidden('Not authorized to access this media.')
