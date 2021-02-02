from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

import directory.serializers
import sailor.serializers
import sailor.statement.serializers
from cadets.models import StudentID
from communication.models import SailorKeys
from directory.models import (BranchOffice, StatusDocument, Decision, NZ, LevelQualification, TypeDocumentNZ,
                              ExtentDiplomaUniversity, Speciality, Specialization, Rank, Country, Port)
from payments.platon.models import PlatonPayments
from reports.models import ProtocolFiles
from sailor import forModelSerializer as custom_serializer
from sailor.document.models import Education, ProtocolSQC, CertificateETI, QualificationDocument, \
    ProofOfWorkDiploma
from sailor.document.serializers import CertificateNTZBaseSerializer
from sailor.models import (Profile, SailorPassport)
from sailor.statement.models import StatementSQC, StatementETI, StatementAdvancedTraining
from user_profile.models import FullUserSailorHistory


class ListSailorSerializer(serializers.RelatedField):
    def to_representation(self, obj):
        try:
            if type(obj) is int:
                qs = self.queryset.get(id=obj)
            else:
                qs = obj
        except ObjectDoesNotExist:
            try:
                qs = SailorKeys.objects.only('protocol_dkk', 'profile', 'pk').filter(
                    protocol_dkk__overlap=[self.parent._instance.pk]).first()
                if not qs:
                    raise AttributeError
            except AttributeError:
                return {
                    'id': None,
                    'full_name_ukr': '',
                    'full_name_eng': '',
                    'birth_date': ''
                }
        profile = Profile.objects.get(id=qs.profile)
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y')
        }


class ProfileSailorSerializer(serializers.RelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = SailorKeys.objects.get(id=obj)
            profile = Profile.objects.get(id=qs.profile)
        else:
            qs = SailorKeys.objects.get(profile=obj.id)
            profile = obj
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y')
        }


class ListNTZSailorSerializer(serializers.RelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.filter(sertificate_ntz__overlap=[obj]).first()
        else:
            qs = obj
        if not qs:
            return {
                'id': None,
                'full_name_ukr': '',
                'full_name_eng': '',
                'birth_date': ''
            }
        profile = Profile.objects.get(id=qs.profile)
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y')
        }


class BranchOfficeSerializator(serializers.RelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {
            'code_branch': qs.code_branch,
            'name_ukr': qs.name_ukr,
            'name_eng': qs.name_eng
        }


class ListProtocolDKKSerializer(serializers.ModelSerializer):
    branch_create = BranchOfficeSerializator(queryset=BranchOffice.objects.all(), required=False)
    sailor = ListSailorSerializer(queryset=SailorKeys.objects.all())
    # sailor_profile = ProfileSailorSerializer(source='profile', read_only=True)
    status_document = custom_serializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all(), required=False)
    number_document = serializers.ReadOnlyField(source='get_number')
    position = serializers.ReadOnlyField(source='get_position')
    rank = serializers.ReadOnlyField(source='get_rank')
    decision = custom_serializer.DecisionSerializer(queryset=Decision.objects.all())
    is_experience_required = serializers.ReadOnlyField(source='is_exp_required')
    statement_dkk = serializers.ReadOnlyField(source='get_full_number_statement')
    is_continue = serializers.ReadOnlyField(source='_is_continue')
    document_property = serializers.ReadOnlyField(source='_document_property')
    is_cadet = serializers.ReadOnlyField(source='get_is_cadet')
    committe_head = serializers.ReadOnlyField(source='get_committe_head_full_name')
    commissioners = serializers.ReadOnlyField(source='get_commissioners_full_name')

    class Meta:
        model = ProtocolSQC
        fields = ('id', 'statement_dkk', 'date_meeting', 'branch_create', 'sailor', 'status_document',
                  'number_document', 'position', 'rank', 'decision', 'is_experience_required', 'is_continue',
                  'document_property', 'is_cadet', 'committe_head', 'commissioners')
        read_only = fields

    def to_representation(self, instance):
        self._instance = instance
        return super(ListProtocolDKKSerializer, self).to_representation(instance=instance)


class ListStatementDKKSerializer(serializers.ModelSerializer):
    branch_office = BranchOfficeSerializator(queryset=BranchOffice.objects.all(), required=False)
    sailor = ListSailorSerializer(queryset=SailorKeys.objects.all())
    status_document = custom_serializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all(), required=False)
    protocol_number = serializers.ReadOnlyField()
    number_document = serializers.ReadOnlyField(source='get_number')
    position = serializers.ReadOnlyField(source='get_position')
    rank = custom_serializer.RankSerializer(queryset=Rank.objects.all())
    is_experience_required = serializers.ReadOnlyField(source='is_exp_required')
    date_create = serializers.DateTimeField(source='created_at')

    class Meta:
        model = StatementSQC
        fields = ('id', 'number', 'date_create', 'branch_office', 'sailor', 'status_document', 'protocol_number',
                  'number_document', 'position', 'rank', 'is_experience_required', 'is_cadet', 'date_meeting')
        read_only = fields


class CertificateNTZListSerializer(CertificateNTZBaseSerializer):
    sailor = ListNTZSailorSerializer(source='id', queryset=SailorKeys.objects.all())

    class Meta:
        model = CertificateETI
        read_only_fields = ['date_create']
        fields = ('id', 'sailor', 'ntz', 'ntz_number', 'course_traning', 'date_create', 'date_start', 'date_end',
                  'status_document')


class ListQualificationDocumentSailorSerializer(serializers.RelatedField):
    """
    Данные о моряке при фильтрации квалификационных документов
    (диплом, свидетельство фахивця, квалификационный документ, свидетельства танкеристов и офицер охраны судна)
    """

    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.filter(qualification_documents__overlap=[obj]).first()
        else:
            qs = obj
        if qs:
            profile = Profile.objects.get(id=qs.profile)
            return {
                'id': qs.id,
                'full_name_ukr': profile.get_full_name_ukr,
                'full_name_eng': profile.get_full_name_eng,
                'birth_date': profile.date_birth.strftime('%d.%m.%Y')
            }
        else:
            return {
                'id': None,
                'full_name_ukr': None,
                'full_name_eng': None,
                'birth_date': None
            }


class ListQualificationDocumentProofSailorSerializer(serializers.RelatedField):
    """Данные о моряке при фильтрации квалификационных документов (подтвержедния дипломов)"""

    def to_representation(self, obj):
        if type(obj) is int:
            proof_diploma = ProofOfWorkDiploma.objects.get(id=obj)
            qs = self.queryset.filter(qualification_documents__overlap=[proof_diploma.diploma_id]).first()
        else:
            qs = obj
        if not qs:
            return {
                'id': None,
                'full_name_ukr': None,
                'full_name_eng': None,
                'birth_date': None
            }
        profile = Profile.objects.get(id=qs.profile)
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y')
        }


class PortSerializator(serializers.RelatedField):
    """Данные о портах при фильтрации квалификационных документов"""

    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {
            'code_port': qs.code_port,
            'name_ukr': qs.name_ukr,
            'name_eng': qs.name_eng
        }


class ListQualificationDocumentBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для фильтра квалификационных документов"""

    sailor = ListQualificationDocumentSailorSerializer(source='id', queryset=SailorKeys.objects.all())
    status_document = custom_serializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all(), required=False)
    number_document = serializers.ReadOnlyField(source='get_number')
    port = PortSerializator(queryset=Port.objects.all())
    type_document = serializers.ReadOnlyField(source='get_type_document')


class ListQualificationDocumentAllSerializer(ListQualificationDocumentBaseSerializer):
    """
    Сериализатор для фильтра квалификационных документов (диплом, свидетельство фахивця, квалификационный документ)
    """
    position = serializers.ReadOnlyField(source='get_position')
    rank = serializers.ReadOnlyField(source='get_rank')
    country = custom_serializer.CountrySeriallizer(queryset=Country.objects.all())

    class Meta:
        model = QualificationDocument
        fields = ('id', 'sailor', 'status_document', 'port', 'date_start', 'date_end', 'number_document',
                  'position', 'rank', 'other_port', 'type_document', 'country', 'other_number')
        read_only = fields


class ListQualificationDocumentProofDiplomaSerializer(ListQualificationDocumentBaseSerializer):
    """Сериализатор для фильтра квалификационных документов (подтвержедния дипломов)"""

    position = serializers.ReadOnlyField(source='get_position')
    rank = serializers.ReadOnlyField(source='get_rank')
    sailor = ListQualificationDocumentProofSailorSerializer(source='id', queryset=SailorKeys.objects.all())

    class Meta:
        model = ProofOfWorkDiploma
        fields = ('id', 'sailor', 'status_document', 'port', 'date_start', 'date_end', 'number_document',
                  'position', 'rank', 'other_port', 'type_document')
        read_only = fields


class ListQualificationDocumentCertificatesSerializer(ListQualificationDocumentBaseSerializer):
    """Сериализатор для фильтра квалификационных документов (свидетельства танкеристов и офицер охраны судна)"""

    certificate_name = serializers.ReadOnlyField(source='get_type_document')

    class Meta:
        model = QualificationDocument
        fields = ('id', 'sailor', 'status_document', 'port', 'date_start', 'date_end', 'number_document',
                  'certificate_name', 'other_port')
        read_only = fields


class ListEducationDocumentSailorSerializer(serializers.RelatedField):
    """Данные о моряке при фильтрации образовательных документов"""

    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.filter(education__overlap=[obj]).first()
        else:
            qs = obj
        if qs is None:
            return {}
        profile = Profile.objects.get(id=qs.profile)
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y')
        }


class EducationDocumentBaseSerializer(serializers.ModelSerializer):
    sailor = ListEducationDocumentSailorSerializer(source='id', queryset=SailorKeys.objects.all())
    name_nz = custom_serializer.NameNZSerializer(queryset=NZ.objects.all())
    qualification = custom_serializer.QualificationSerializer(queryset=LevelQualification.objects.all())
    status_document = custom_serializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all(), required=False)
    type_document = custom_serializer.TypeDocumentNZSerializer(queryset=TypeDocumentNZ.objects.all())
    extent = custom_serializer.ExtentSerializer(queryset=ExtentDiplomaUniversity.objects.all(), required=False)
    speciality = custom_serializer.SpecialitySerializer(queryset=Speciality.objects.all(), required=False)
    specialization = custom_serializer.SpecializationSerializer(queryset=Specialization.objects.all(), required=False)
    date_start = serializers.DateField(source='date_issue_document')
    experied_date = serializers.DateField(required=False, allow_null=True, source='expired_date')

    class Meta:
        model = Education
        fields = ('id', 'sailor', 'registry_number', 'serial', 'number_document', 'name_nz', 'qualification',
                  'date_start', 'experied_date', 'status_document', 'type_document', 'extent', 'speciality',
                  'specialization')
        read_only = fields


class ListOfFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtocolFiles
        fields = ('token', 'created_at', 'user', 'file_name')


class ListStudentIDSailorSerializer(serializers.RelatedField):
    """Данные о моряке при фильтрации образовательных документов"""

    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.filter(students_id__overlap=[obj]).first()
            self.root._sailor_key = qs
        else:
            qs = obj
            self.root._sailor_key = qs
        if qs is None:
            return {}
        profile = Profile.objects.get(id=qs.profile)
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y')
        }


class StudentIDReportSerializer(serializers.ModelSerializer):
    sailor = ListStudentIDSailorSerializer(source='id', queryset=SailorKeys.objects.all())
    name_nz = custom_serializer.NameNZSerializer(queryset=NZ.objects.all())
    author_name = serializers.SerializerMethodField()
    is_have_documents = serializers.SerializerMethodField()

    class Meta:
        model = StudentID
        fields = ('id', 'sailor', 'serial', 'number', 'name_nz', 'date_start', 'date_end', 'faculty',
                  'educ_with_dkk', 'passed_educ_exam', 'is_have_documents', 'author_name')
        read_only = fields
        read_only_fields = fields

    def get_is_have_documents(self, instance):
        if self.root._sailor_key is None or not self.root._sailor_key.statement_dkk:
            statement = []
        else:
            statement = self.root._sailor_key.statement_dkk
        protocol_exists = False
        statement = StatementSQC.objects.filter(id__in=statement, is_cadet=True)
        statement_exists = statement.exists()
        if statement_exists:
            protocol_exists = ProtocolSQC.objects.filter(statement_dkk__in=statement).exists()
        return {'statement': statement_exists, 'protocol': protocol_exists}

    def get_author_name(self, instance):
        if instance.author:
            return f'{instance.author.last_name} {instance.author.first_name} {instance.author.userprofile.middle_name}'
        else:
            hist = FullUserSailorHistory.objects.filter(content_type__model='StudentID', object_id=instance.pk,
                                                        action_type='create').first()
            if hist:
                return f'{hist.user.last_name} {hist.user.first_name} {hist.user.userprofile.middle_name}'
            else:
                return ''


class StatementETISailorSerializer(serializers.RelatedField):
    """
    Information about the sailor in the report on the statements of ETI
    """

    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.filter(statement_eti__overlap=[obj]).first()
        else:
            qs = obj
        if qs is None:
            return {}
        profile = Profile.objects.get(id=qs.profile)
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y')
        }


class StatementETIListSerializer(sailor.statement.serializers.StatementETISerializer):
    sailor = StatementETISailorSerializer(source='id', queryset=SailorKeys.objects.all())

    class Meta:
        model = StatementETI
        fields = ('id', 'number', 'date_create', 'date_meeting', 'date_end_meeting', 'course', 'status_document',
                  'institution', 'sailor', 'is_payed')
        read_only_fields = fields


class PaymentStatementETISerializer(serializers.ModelSerializer):

    class Meta:
        model = PlatonPayments
        fields = ('pay_time', 'amount', 'platon_id')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        statement_eti = instance.content_object
        sailor = SailorKeys.objects.get(statement_eti__overlap=[statement_eti.pk])
        profile = Profile.objects.filter(id=sailor.profile).first()
        response['full_name'] = profile.get_full_name_ukr
        response['sailor'] = sailor.pk
        response['course'] = directory.serializers.CourseForNTZSerializer(instance.content_object.course).data
        response['institution'] = directory.serializers.SmallETISerializer(instance.content_object.institution).data
        return response


class PaymentBranchOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatonPayments
        fields = ('pay_time', 'amount', 'platon_id')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        packet_item = instance.content_object.packet_item
        sailor = SailorKeys.objects.get(packet_item__overlap=[packet_item.pk])
        profile = Profile.objects.filter(id=sailor.profile).first()
        response['full_name'] = profile.get_full_name_ukr
        response['sailor'] = sailor.pk
        response['branch_office'] = directory.serializers.BranchOfficeSerializer(instance.content_object.item).data
        return response


class StatementAdvTrainingSailorSerializer(serializers.RelatedField):
    """
    Information about the sailor in the report on the statements of advanced training
    """

    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.filter(statement_advanced_training__overlap=[obj]).first()
        else:
            qs = obj
        if qs is None:
            return {}
        profile = Profile.objects.get(id=qs.profile)
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y')
        }


class StatementAdvancedTrainingListSerializer(sailor.statement.serializers.StatementAdvancedTrainingSerializer):
    sailor = StatementAdvTrainingSailorSerializer(source='id', queryset=SailorKeys.objects.all())

    class Meta:
        model = StatementAdvancedTraining
        fields = ('id', 'number', 'is_payed', 'date_create', 'date_meeting', 'date_end_meeting', 'sailor',
                  'status_document', 'level_qualification', 'educational_institution')
        read_only_fields = fields


class SailorPassportSailorSerializer(serializers.RelatedField):
    """
    Information about the sailor in the report on the sailor passport
    """

    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.filter(sailor_passport__overlap=[obj]).first()
        else:
            qs = obj
        if qs is None:
            return {}
        profile = Profile.objects.get(id=qs.profile)
        return {
            'id': qs.id,
            'full_name_ukr': profile.get_full_name_ukr,
            'full_name_eng': profile.get_full_name_eng,
            'birth_date': profile.date_birth.strftime('%d.%m.%Y')
        }


class SailorPassportListSerializer(sailor.serializers.SailorPassportSerializer):
    sailor = SailorPassportSailorSerializer(source='id', queryset=SailorKeys.objects.all())

    class Meta:
        model = SailorPassport
        fields = ('id', 'country', 'number_document', 'date_start', 'date_end', 'port', 'status_document',
                  'other_port', 'date_renewal', 'created_at', 'sailor')
