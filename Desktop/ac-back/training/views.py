import json
from datetime import date

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Max
from django.forms import model_to_dict
from rest_framework import mixins
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
import rest_framework.permissions
import training.permissions

from communication.models import SailorKeys
from itcs.ExpireToken import ExpiringTokenAuthentication
from reports.filters import ShortLinkResultPagination
from reports.views import StatementDkkList
from sailor.document.models import ProtocolSQC
from sailor.document.serializers import ProtocolDKKSerializer
from sailor.models import Profile, ContactInfo
from sailor.statement.models import StatementSQC
from sailor.tasks import save_history
from .serializers import StatementDKKTrainingSerializer, ProtocolDKKTrainingSerializer, RequestTokenSerializer, \
    SearchSailorSerializer
from .tasks import update_token_user

User = get_user_model()


class StatementDKKList(StatementDkkList, GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    permission_classes = (rest_framework.permissions.IsAuthenticated,
                          training.permissions.CheckIPAddressAST)
    pagination_class = ShortLinkResultPagination
    queryset = StatementSQC.objects.filter(
        status_document_id=24, protocolsqc__isnull=True
    ).order_by('-date_meeting', '-id')
    serializer_class = StatementDKKTrainingSerializer
    authentication_classes = (JWTTokenUserAuthentication, ExpiringTokenAuthentication)

    def get_queryset(self):
        return StatementSQC.objects.filter(
            status_document_id=24, protocolsqc__isnull=True
        ).order_by('-date_meeting', '-id')


class CreateProtocolDKK(mixins.CreateModelMixin, GenericViewSet, mixins.UpdateModelMixin):
    permission_classes = (rest_framework.permissions.IsAuthenticated,
                          training.permissions.CheckIPAddressAST)
    queryset = ProtocolSQC.objects.all()
    serializer_class = ProtocolDKKTrainingSerializer
    authentication_classes = (JWTTokenUserAuthentication,)

    def perform_create(self, serializer):
        sailor_id = serializer.initial_data['sailor']
        try:
            sailor_qs = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        statement = StatementSQC.objects.get(id=serializer.initial_data['statement_dkk'])
        direction_id = statement.rank.direction_id
        branch = statement.branch_office
        number = \
            ProtocolSQC.objects.filter(date_meeting__year=date.today().year,
                                       statement_dkk__rank__direction_id=direction_id,
                                       branch_create=branch).aggregate(
                number=Max('number_document'))['number']
        if not number:
            number = 0
        number = number + 1
        if ProtocolSQC.objects.filter(statement_dkk_id=serializer.initial_data['statement_dkk']).exists():
            raise ValidationError('Qualification document with this statement exists')
        status_document = serializer.initial_data.get('status_document', 29)
        ser = serializer.save(number_document=number, status_document_id=status_document, _sailor=sailor_id,
                              branch_create=branch)
        if ser.statement_dkk.related_docs.exists():
            ser.related_docs = list(ser.statement_dkk.related_docs.all())
        else:
            docs_set = ser.statement_dkk.get_status_position
            all_docs = docs_set.get('all_docs', [])
            ser.related_docs = all_docs
        if sailor_qs.protocol_dkk:
            sailor_qs.protocol_dkk.append(ser.id)
            sailor_qs.save(update_fields=['protocol_dkk'])
        else:
            sailor_qs.protocol_dkk = [ser.id]
            sailor_qs.save(update_fields=['protocol_dkk'])
        save_history.s(user_id=self.request.user.id, module='ProtocolSQC', action_type='create',
                       content_obj=ser, serializer=ProtocolDKKSerializer, new_obj=ser,
                       sailor_key_id=sailor_id).apply_async(serializer='pickle')


class SearchSailor(GenericAPIView):
    serializer_class = SearchSailorSerializer
    authentication_classes = (JWTTokenUserAuthentication, ExpiringTokenAuthentication)
    permission_classes = (rest_framework.permissions.IsAuthenticated,
                          training.permissions.CheckIPAddressAST)

    def post(self, request, *args, **kwargs):
        contact_not_found = {'detail': 'error', 'error': 'Contact not found'}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        phone = data.get('phone')
        sailor_id = data.get('sailor_id')
        phone = phone[1:] if phone.startswith('+') else phone
        try:
            sailor_key = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise NotFound({'detail': 'error', 'error': 'Sailor does not exists'})
        profile = Profile.objects.get(id=sailor_key.profile)
        user_by_phone = User.objects.filter(username__contains=phone)
        if not profile.contact_info:
            raise NotFound(contact_not_found)
        contact_json = json.loads(profile.contact_info)
        contact_qs = ContactInfo.objects.filter(id__in=contact_json)
        if contact_qs.filter(value__contains=phone).exists() is False and user_by_phone.exists() is False:
            raise NotFound(contact_not_found)
        return Response({'sailor_key': sailor_key.pk, 'phone': phone, 'first_name': profile.first_name_ukr,
                         'last_name': profile.last_name_ukr, 'middle_name': profile.middle_name_ukr,
                         'birth_date': profile.date_birth
                         })


class CreateUserExamOnStatementSQC(APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,
                          training.permissions.CheckIPAddressAST)

    def validate_statement(self, statement):
        if statement.have_protocol:
            raise ValidationError('This statement have protocol')
        if statement.status_document_id != 24:
            raise ValidationError('You can\'t start exam in this status')

    def get(self, request, statement_id):
        statement = StatementSQC.objects.get(id=statement_id)

        self.validate_statement(statement=statement)
        statement_data = model_to_dict(
            statement,
            exclude=(
                'date_meeting', 'created_at', 'modified_at', 'on_create_rank', 'related_docs'
            )
        )
        statement_data.update(number_document=statement.get_number)
        sailor = SailorKeys.objects.get(user_id=self.request.user.pk)
        profile = Profile.objects.get(id=sailor.profile)
        request_data = {'statement': statement_data,
                        'username': self.request.user.username,
                        'sailor_id': sailor.pk,
                        'first_name': profile.first_name_ukr,
                        'last_name': profile.last_name_ukr,
                        'middle_name': profile.middle_name_ukr,
                        'birth_date': str(profile.date_birth)
                        }
        endpoint = settings.AST_URL + '/examination/registration_exam_by_statement/'
        ast_response = requests.post(endpoint, json=request_data, headers={'Authorization': f'Bearer {request.auth}'})
        json_response = ast_response.json()
        if ast_response.status_code == 200:
            statement.userexam_id = json_response.get('userexam_id')
            statement.save(update_fields=['userexam_id'])
            return Response(json_response)
        return Response(json_response, status=ast_response.status_code)
