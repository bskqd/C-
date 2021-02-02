import itertools

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.models import AgentSailor
from communication.models import SailorKeys
from itcs import magic_numbers
from sailor.document.models import ServiceRecord, LineInServiceRecord, Education, MedicalCertificate, \
    QualificationDocument, ProofOfWorkDiploma
from sailor.misc import get_sailor_by_modelname
from sailor.models import (Profile, SailorPassport)
from sailor.statement.models import StatementSQC
from sms_auth.models import UserStatementVerification
from sms_auth.serializers import UserStatementVerificationSerializer
from user_profile.models import UserProfile
from .models import DocumentsToVerification
from .permissions import AgentVerifierPermission
import rest_framework.permissions

User = get_user_model()


class PostVerifyDocsList(APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,
                          rest_framework.permissions.IsAdminUser)

    def get(self, request):
        response = []
        sailor_passport = SailorPassport.objects.filter(
            status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION)
        education_doc = Education.objects.filter(
            status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION)
        qual_doc = QualificationDocument.objects.filter(
            status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION)
        service_record = ServiceRecord.objects.filter(
            status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION)
        line_in_serv = LineInServiceRecord.objects.filter(
            status_line_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION,
            service_record__isnull=False)
        exp_doc = LineInServiceRecord.objects.filter(status_line_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION,
                                                     service_record__isnull=True)
        medical_cert = MedicalCertificate.objects.filter(
            status_document_id=magic_numbers.STATUS_TO_ADDITIONAL_VERIFICATION)

        list_of_qs_docs = [sailor_passport, education_doc, qual_doc, service_record, line_in_serv, exp_doc,
                           medical_cert]
        status_attrs = ['status_line_id', 'status_document_id']
        for qs in list_of_qs_docs:
            for document in qs:
                sailor_key = get_sailor_by_modelname(document._meta.model_name, document)
                if sailor_key is False:
                    for attr in status_attrs:
                        try:
                            setattr(document, attr, 34)
                            document.save(update_fields=[attr])
                            continue
                        except (AttributeError, ValueError):
                            pass
                    continue
                else:
                    profile = Profile.objects.get(id=sailor_key.profile)
                response.append(
                    {'number': document.get_number, 'sailor_key': sailor_key.pk, 'full_name': profile.get_full_name_ukr,
                     'type_document': document._meta.verbose_name})
        return Response(response)


class NumOfVerifyDocuments(APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request):
        count_verify_doc = DocumentsToVerification.objects.all().count()
        return Response({'num_docs': count_verify_doc})


class UserVerifyForPersonalCabinetView(APIView):
    permission_classes = (IsAdminUser,)
    """Заявления на верификацию пользователей в ЛК"""

    def get(self, request):
        user_statement = UserStatementVerification.objects.filter(status_document_id=magic_numbers.VERIFICATION_STATUS
                                                                  ).order_by('created_at')
        serializer = UserStatementVerificationSerializer(user_statement, many=True)
        return Response({'statements': serializer.data})


class AgentVerificationView(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = (IsAuthenticated, AgentVerifierPermission)

    def get_list_of_docs(self, attr) -> list:
        documents_id = self.sailors.values_list(attr, flat=True)
        merged = list(itertools.chain.from_iterable(documents_id))
        return merged

    def get_queryset_for_secretary(self):
        user: User = self.request.user
        if user.is_superuser:
            agent_sailor = AgentSailor.objects.all()
        else:
            agent_sailor = AgentSailor.objects.filter(
                agent__userprofile__agent_group__in=user.userprofile.agent_group.all())
        self.sailors = SailorKeys.objects.filter(id__in=list(agent_sailor.values_list('sailor_key', flat=True)))
        service_records_id = self.get_list_of_docs('service_records')
        service_record_qs = ServiceRecord.objects.filter(
            status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT, id__in=service_records_id).order_by('-pk')
        qualification_documents_ids = self.get_list_of_docs('qualification_documents')
        qual_document_qs = QualificationDocument.objects.filter(
            status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT,
            id__in=qualification_documents_ids).order_by('-pk')
        educ_docs = Education.objects.filter(
            status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT,
            id__in=self.get_list_of_docs('education')).order_by('-pk')
        experience_docs = self.get_list_of_docs('experience_docs')
        line_in_service = LineInServiceRecord.objects.filter(
            Q(status_line_id=magic_numbers.STATUS_CREATED_BY_AGENT) & Q(
                Q(id__in=experience_docs) | Q(service_record_id__in=service_records_id))).order_by('-pk')
        medical = MedicalCertificate.objects.filter(
            status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT,
            id__in=self.get_list_of_docs('medical_sertificate')).order_by('-pk')
        proof_of_work_diploma = ProofOfWorkDiploma.objects.filter(
            status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT,
            diploma_id__in=qualification_documents_ids).order_by('-pk')
        statement_sqc = StatementSQC.objects.filter(status_document_id=magic_numbers.STATUS_CREATED_BY_AGENT,
                                                    id__in=self.get_list_of_docs('statement_dkk'))
        return list(itertools.chain(service_record_qs, qual_document_qs, educ_docs, line_in_service, medical,
                                    proof_of_work_diploma, statement_sqc))

    def get_queryset_for_verifier(self):
        service_record_qs = ServiceRecord.objects.filter(
            status_document_id=magic_numbers.VERIFICATION_STATUS).order_by('-pk')[:50]
        qual_document_qs = QualificationDocument.objects.filter(
            status_document_id=magic_numbers.VERIFICATION_STATUS).order_by('-pk')[:50]
        educ_docs = Education.objects.filter(
            status_document_id=magic_numbers.VERIFICATION_STATUS).order_by('-pk')[:50]
        line_in_service = LineInServiceRecord.objects.filter(
            status_line_id=magic_numbers.VERIFICATION_STATUS).order_by('-pk')[:50]
        medical = MedicalCertificate.objects.filter(
            status_document_id=magic_numbers.VERIFICATION_STATUS).order_by('-pk')[:50]
        proof_of_work_diploma = ProofOfWorkDiploma.objects.filter(
            status_document_id=magic_numbers.VERIFICATION_STATUS).order_by('-pk')[:50]
        return list(itertools.chain(service_record_qs, qual_document_qs, educ_docs, line_in_service, medical,
                                    proof_of_work_diploma))

    def list(self, request, *args, **kwargs):
        user: User = self.request.user
        userprofile: UserProfile = user.userprofile
        if userprofile.type_user in [userprofile.VERIFIER, userprofile.BACK_OFFICE]:
            queryset = self.get_queryset_for_verifier()
        else:
            queryset = self.get_queryset_for_secretary()
        response = [instance.verification_info for instance in queryset if instance.verification_info]
        return Response(response)
