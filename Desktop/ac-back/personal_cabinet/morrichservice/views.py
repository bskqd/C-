from rest_framework.exceptions import ValidationError

import personal_cabinet.morrichservice.serializers
import personal_cabinet.views
from communication.models import SailorKeys
from itcs import magic_numbers
from personal_cabinet.morrichservice.core import MorrichSailorGetQuerySetMixin
from sailor.document.models import (MedicalCertificate, Education, CertificateETI, QualificationDocument,
                                    ServiceRecord, ProtocolSQC, LineInServiceRecord)
from sailor.models import (SailorPassport, Passport)


class MRSPersonalSailorInfoView(personal_cabinet.views.MainSailorInfoView):
    """
    Main info about sailor (morrichservice)
    """
    pass


class MRSPersonalQualificationDocumentView(MorrichSailorGetQuerySetMixin,
                                           personal_cabinet.views.BasePersonalQualificationDocumentView):
    """
    Sailor's qualification documents (diplomas, specialist certificates) (morrichservice)
    """
    model = QualificationDocument
    create_status_document = magic_numbers.CREATED_FROM_MORRICHSERVICE

    def get_create_status_document(self):
        return self.create_status_document


class MRSPersonalProofOfWorkDiplomaView(personal_cabinet.views.BasePersonalProofOfWorkDiplomaView):
    """
    Sailor's qualification documents (proof of work diploma) (morrichservice)
    """
    create_status_document = magic_numbers.CREATED_FROM_MORRICHSERVICE
    exclude_status_document = (
        magic_numbers.STATUS_REMOVED_DOCUMENT,
        magic_numbers.STATUS_CREATED_BY_AGENT,
        magic_numbers.CREATED_FROM_PERSONAL_CABINET,
    )

    def get_create_status_document(self):
        return self.create_status_document

    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_PERSONAL_CABINET,
        )


class MRSPersonalServiceRecordsView(MorrichSailorGetQuerySetMixin,
                                    personal_cabinet.views.BasePersonalServiceRecordsView):
    """
    Sailor's service records (morrichservice)
    """
    serializer_class = personal_cabinet.morrichservice.serializers.MRSPersonalServiceRecordSailorSerializer
    model = ServiceRecord
    create_status_document = magic_numbers.CREATED_FROM_MORRICHSERVICE

    def get_create_status_document(self):
        return self.create_status_document


class MRSPersonalEducationView(MorrichSailorGetQuerySetMixin,
                               personal_cabinet.views.BasePersonalEducationView):
    """
    Educational documents (morrichservice)
    """
    model = Education
    create_status_document = magic_numbers.CREATED_FROM_MORRICHSERVICE

    def get_create_status_document(self):
        return self.create_status_document


class MRSPersonalETICertificatesView(MorrichSailorGetQuerySetMixin,
                                     personal_cabinet.views.BasePersonalNTZCertificatesView):
    """
    Sailor's ETI certificates (morrichservice)
    """
    model = CertificateETI
    create_status_document = magic_numbers.CREATED_FROM_MORRICHSERVICE

    def get_create_status_document(self):
        return self.create_status_document


class MRSPersonalMedicalCertificatesView(MorrichSailorGetQuerySetMixin,
                                         personal_cabinet.views.BasePersonalMedicalCertificatesView):
    """
    Sailor's medical certificates (morrichservice)
    """
    model = MedicalCertificate
    create_status_document = magic_numbers.CREATED_FROM_MORRICHSERVICE

    def get_create_status_document(self):
        return self.create_status_document


class MRSPersonalSailorPassportView(MorrichSailorGetQuerySetMixin,
                                    personal_cabinet.views.BasePersonalSailorPassportView):
    """
    Sailor's passports (morrichservice)
    """
    model = SailorPassport
    create_status_document = magic_numbers.CREATED_FROM_MORRICHSERVICE

    def get_create_status_document(self):
        return self.create_status_document


class MRSPersonalCitizenPassportView(MorrichSailorGetQuerySetMixin,
                                     personal_cabinet.views.BasePersonalCitizenPassport):
    """
    Sailor's citizen passports (morrichservice)
    """
    model = Passport


class MRSPersonalProtocolDKKView(MorrichSailorGetQuerySetMixin,
                                 personal_cabinet.views.BasePersonalProtocolDKK):
    """
    Sailor's protocols SQC (morrichservice)
    """
    model = ProtocolSQC


class MRSPersonalExperienceDocView(MorrichSailorGetQuerySetMixin,
                                   personal_cabinet.views.BasePersonalExperienceDoc):
    """
    Sailor's experience documents (certificates) (morrichservice)
    """
    create_status_line = magic_numbers.CREATED_FROM_MORRICHSERVICE

    def get_create_status_document(self):
        return self.create_status_line

    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_PERSONAL_CABINET
        )

    def get_queryset(self):
        try:
            sailor = SailorKeys.objects.get(user_id=self.request.user.id)
        except SailorKeys.DoesNotExist:
            raise ValidationError(personal_cabinet.views.sailor_not_exists_error)
        return LineInServiceRecord.objects.filter(id__in=sailor.experience_docs).exclude(
            status_line_id__in=self.get_exclude_status_document()).order_by('-id')


class MRSPersonalDataProcessingView(personal_cabinet.views.BaseDataProcessingView):
    pass


class MRSPersonalStatementDKKView(MorrichSailorGetQuerySetMixin, personal_cabinet.views.BasePersonalStatementDKK
                                  ):
    create_status_document = magic_numbers.CREATED_FROM_MORRICHSERVICE
    serializer_class = personal_cabinet.morrichservice.serializers.MRSPersonalSailorStatementDKKSerialize

    def get_create_status_document(self):
        return self.create_status_document


class MRSStatementQualificationView(MorrichSailorGetQuerySetMixin,
                                    personal_cabinet.views.BasePersonalStatementQualification,
                                    ):
    create_status_document = magic_numbers.CREATED_FROM_MORRICHSERVICE
    serializer_class = personal_cabinet.morrichservice.serializers.MRSStatementQualificationDocumentSerializer

    def get_create_status_document(self):
        return self.create_status_document


class MRSCountDocsSailorView(personal_cabinet.views.BaseCountDocsSailor):
    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_PERSONAL_CABINET,
            magic_numbers.status_statement_canceled,
            magic_numbers.status_state_qual_dkk_canceled
        )


class MRSStatementServiceRecordView(MorrichSailorGetQuerySetMixin,
                                    personal_cabinet.views.BaseStatementServiceRecordSailor):
    create_status_document = magic_numbers.CREATED_FROM_MORRICHSERVICE
    serializer_class = personal_cabinet.morrichservice.serializers.MRSStatementServiceRecord

    def get_create_status_document(self):
        return self.create_status_document


class MRSStatementSailorPassport(MorrichSailorGetQuerySetMixin,
                                 personal_cabinet.views.BaseStatementSailorPassport):
    create_status_document = magic_numbers.CREATED_FROM_PERSONAL_CABINET

    def get_create_status_document(self):
        return self.create_status_document
