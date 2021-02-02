from copy import deepcopy

from django.contrib.auth import get_user_model
from django.db.models import Case, Value, When, IntegerField
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import generics
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

import agent.serializers
import personal_cabinet.e_transport.serializers
import personal_cabinet.views
from agent.models import AgentSailor, StatementAgentSailor
from agent.utils import register_sailor_agent
from communication.models import SailorKeys
from itcs import magic_numbers
from personal_cabinet.e_transport.core import ETransportSailorGetQuerySetMixin
from personal_cabinet.serializers import (PersonalAgentSerializer)
from sailor.document.models import (ServiceRecord, Education, ProtocolSQC, CertificateETI,
                                    MedicalCertificate, QualificationDocument, LineInServiceRecord)
from sailor.models import (SailorPassport, Passport, Rating)
from sailor.tasks import save_history

User = get_user_model()

sailor_not_exists_error = 'Sailor does not exists'


class PersonalSailorInfoView(personal_cabinet.views.MainSailorInfoView):
    """
    Main info about sailor (e-transport)
    """
    pass


class PersonalQualificationDocumentView(ETransportSailorGetQuerySetMixin,
                                        personal_cabinet.views.BasePersonalQualificationDocumentView):
    """
    Sailor's qualification documents (diplomas, specialist certificates) (e-transport)
    """
    permission_classes = [IsAuthenticated]
    model = QualificationDocument
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class PersonalProofOfWorkDiplomaView(personal_cabinet.views.BasePersonalProofOfWorkDiplomaView):
    """
    Sailor's qualification documents (proof of work diploma) (e-transport)
    """
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET
    exclude_status_document = (
        magic_numbers.STATUS_REMOVED_DOCUMENT,
        magic_numbers.STATUS_CREATED_BY_AGENT,
        magic_numbers.CREATED_FROM_MORRICHSERVICE,
    )

    def get_create_status_document(self):
        return self.create_status_document

    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_MORRICHSERVICE,
        )


class PersonalServiceRecordsView(ETransportSailorGetQuerySetMixin,
                                 personal_cabinet.views.BasePersonalServiceRecordsView):
    """
    Sailor's service records (e-transport)
    """
    serializer_class = personal_cabinet.e_transport.serializers.PersonalServiceRecordSailorSerializer
    model = ServiceRecord
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class PersonalEducationView(ETransportSailorGetQuerySetMixin,
                            personal_cabinet.views.BasePersonalEducationView):
    """
    Educational documents (e-transport)
    """
    model = Education
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class PersonalNTZCertificatesView(ETransportSailorGetQuerySetMixin,
                                  personal_cabinet.views.BasePersonalNTZCertificatesView):
    """
    Sailor's ETI certificates (e-transport)
    """
    model = CertificateETI
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class PersonalMedicalCertificatesView(ETransportSailorGetQuerySetMixin,
                                      personal_cabinet.views.BasePersonalMedicalCertificatesView):
    """
    Sailor's medical certificates (e-transport)
    """
    model = MedicalCertificate
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class PersonalSailorPassportView(ETransportSailorGetQuerySetMixin,
                                 personal_cabinet.views.BasePersonalSailorPassportView):
    """
    Sailor's passports (e-transport)
    """
    model = SailorPassport
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class PersonalCitizenPassportView(ETransportSailorGetQuerySetMixin,
                                  personal_cabinet.views.BasePersonalCitizenPassport):
    """
    Sailor's citizen passports (e-transport)
    """
    model = Passport


class PersonalProtocolDKKView(ETransportSailorGetQuerySetMixin,
                              personal_cabinet.views.BasePersonalProtocolDKK):
    """
    Sailor's protocols SQC (e-transport)
    """
    model = ProtocolSQC


class PersonalExperienceDocView(ETransportSailorGetQuerySetMixin,
                                personal_cabinet.views.BasePersonalExperienceDoc):
    """
    Sailor's experience documents (certificates) (e-transport)
    """
    create_status_line = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_line

    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_MORRICHSERVICE,
        )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.model.objects.none()
        try:
            sailor_key = SailorKeys.objects.get(user_id=self.request.user.id)
            qs = LineInServiceRecord.objects.filter(
                id__in=sailor_key.experience_docs
            ).exclude(
                status_line_id__in=self.get_exclude_status_document()
            )
            if hasattr(qs.first(), 'status_document'):
                qs = qs.exclude(status_document_id__in=self.get_exclude_status_document())
            elif hasattr(qs.first(), 'status'):
                qs = qs.exclude(status_id__in=self.get_exclude_status_document())
            return qs
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error, code=404)


class PersonalStatementDKKView(ETransportSailorGetQuerySetMixin, personal_cabinet.views.BasePersonalStatementDKK):
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class ETStatementQualificationView(ETransportSailorGetQuerySetMixin,
                                   personal_cabinet.views.BasePersonalStatementQualification):
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class ETCountDocsSailorView(personal_cabinet.views.BaseCountDocsSailor):
    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_MORRICHSERVICE,
            magic_numbers.status_statement_canceled,
            magic_numbers.status_state_qual_dkk_canceled
        )


class ETStatementServiceRecordView(ETransportSailorGetQuerySetMixin,
                                   personal_cabinet.views.BaseStatementServiceRecordSailor):
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class ETSStudentIDPerSailor(ETransportSailorGetQuerySetMixin,
                            personal_cabinet.views.BaseStudentIDPerSailor):
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class PersonalDataProcessingView(personal_cabinet.views.BaseDataProcessingView):
    pass


class PersonalAgentView(generics.RetrieveAPIView, GenericViewSet):
    """
    Information about the sailor's personal agent, agent removal
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PersonalAgentSerializer

    def retrieve(self, request, *args, **kwargs):
        if not self.get_object():
            return Response('No such seaman')
        return super(PersonalAgentView, self).retrieve(request, *args, **kwargs)

    def get_object(self):
        try:
            sailor_key = SailorKeys.objects.get(user_id=self.request.user.pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        agent_id = sailor_key.agent_id
        if not agent_id:
            statement_agent_sailor = StatementAgentSailor.objects.filter(
                sailor_key=sailor_key.pk,
                status_document_id__in=[magic_numbers.status_statement_agent_sailor_wait_sailor,
                                        magic_numbers.status_statement_agent_sailor_in_process,
                                        magic_numbers.status_statement_agent_sailor_wait_secretary]
            ).annotate(
                status=Case(
                    When(status_document_id=magic_numbers.status_statement_agent_sailor_wait_sailor, then=Value(0)),
                    When(status_document_id=magic_numbers.status_statement_agent_sailor_wait_secretary, then=Value(1)),
                    When(status_document_id=magic_numbers.status_statement_agent_sailor_in_process, then=Value(2)),
                    output_field=IntegerField(), default=Value(2))
            ).order_by('status')
            if not statement_agent_sailor.exists():
                return None
            statement_agent: StatementAgentSailor = statement_agent_sailor.first()
            agent: User = statement_agent.agent
            agent._status_verification = statement_agent.status_document_id
            return agent
        agent: User = AgentSailor.objects.get(sailor_key=sailor_key.pk, is_disable=False).agent
        agent._status_verification = 0
        return agent

    @action(detail=False, methods=['delete'])
    def delete_agent(self, request):
        try:
            sailor_key = SailorKeys.objects.get(user_id=self.request.user.pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error)
        try:
            agent_sailor = AgentSailor.objects.get(agent_id=sailor_key.agent_id, sailor_key=sailor_key.id)
            _agent_sailor = deepcopy(agent_sailor)
            agent_sailor.delete()
        except AgentSailor.DoesNotExist:
            _agent_sailor = AgentSailor(sailor_key=sailor_key.pk, agent_id=sailor_key.agent_id)
        save_history.s(user_id=self.request.user.id,
                       module='AgentSailor',
                       action_type='delete',
                       content_obj=_agent_sailor,
                       serializer=agent.serializers.AgentSailorSerializer,
                       old_obj=_agent_sailor,
                       sailor_key_id=sailor_key.id,
                       ).apply_async(serializer='pickle')
        sailor_key.agent_id = None
        sailor_key.save(update_fields=['agent_id'])
        Rating.objects.create(sailor_key=sailor_key.pk, rating=4)
        return Response({'description': 'Seaman has been deleted', 'status': 'success'})

    @swagger_auto_schema(request_body=no_body)
    @action(detail=False, methods=['post'])
    def accept_agent(self, request):
        try:
            sailor_instance = SailorKeys.objects.get(user_id=self.request.user.pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError(sailor_not_exists_error, code=404)
        statement_agent_sailor = StatementAgentSailor.objects.filter(
            sailor_key=sailor_instance.pk,
            status_document_id=magic_numbers.status_statement_agent_sailor_wait_sailor)
        if not statement_agent_sailor.exists():
            raise ValidationError('Sailor does have a statement', code=404)
        statement_agent_inst: StatementAgentSailor = statement_agent_sailor.first()
        register_sailor_agent(sailor=sailor_instance, statement=statement_agent_inst, user_change=self.request.user)
        statement_agent_inst.status_document_id = magic_numbers.status_statement_agent_sailor_valid
        statement_agent_inst.save(update_fields=['status_document_id'])
        return Response({'status': 'success'})


class ETSStatementSailorPassport(ETransportSailorGetQuerySetMixin,
                                 personal_cabinet.views.BaseStatementSailorPassport):
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document


class OldAuthorizationPage(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer, ]

    def get(self, request):
        return Response(template_name='personal_cabinet/old_login.html')


class AuthorizationPage(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer, ]

    def get(self, request):
        return Response(template_name='personal_cabinet/login.html')
