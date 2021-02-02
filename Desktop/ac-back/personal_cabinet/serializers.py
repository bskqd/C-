import json
from ipaddress import ip_address, ip_network

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from agent.serializers import AgentUserSerializer
from cadets.models import StudentID
from cadets.serializers import StudentIDSerializer
from communication.models import SailorKeys
from directory.models import StatusDocument
from directory.serializers import StatusDocumentSerializer
from itcs import magic_numbers
from personal_cabinet.models import HistoryUserInPersonalCabinet, PersonalDataProcessing
from personal_cabinet.utils import add_watermark_base64, get_client_ip
from sailor import forModelSerializer as customSerializers
from sailor.document.models import (CertificateETI, Education, LineInServiceRecord, MedicalCertificate,
                                    ProofOfWorkDiploma, ProtocolSQC, QualificationDocument, ServiceRecord)
from sailor.document.serializers import (CertificateNTZSerializer, EducationSerializer, ExperienceDocumentSerializer,
                                         LineInServiceRecordSerializer, MedicalCertificateSerializer,
                                         ProtocolDKKSerializer, QualificationDocumentSerializer,
                                         ServiceRecordSailorSerializer, ProofOfWorkDiplomaSerializer)
from sailor.models import (DependencyDocuments, Passport, PhotoProfile, Profile, SailorPassport)
from sailor.serializers import (CitizenPassportSerializer, ProfileMainInfoSerializer, SailorPassportSerializer)
from sailor.statement.models import StatementSQC, StatementQualification
from sailor.statement.serializers import StatementDKKSerializer, StatementQualificationDocumentSerializer
from training.models import AvailableExamsToday
from user_profile.serializer import PersonalAgentUserProfSerializer

User = get_user_model()


class PersonalPhotoSerializer(serializers.RelatedField):

    def to_representation(self, obj):
        if not obj or obj == '[]':
            return []
        try:
            obj = json.loads(obj)
        except TypeError:
            pass
        if isinstance(obj, list):
            qs = list(self.queryset.filter(id__in=obj, is_delete=False).exclude(
                photo__icontains='.pdf').values_list('photo', flat=True))[:3]
        else:
            try:
                qs = list(obj.values_list('photo', flat=True))
            except Exception:  # TODO исправить это говно
                return None
        qs = [{
            'base64': add_watermark_base64(photo),
            'photo_name': photo
        } for photo in qs]
        return qs


class PersonalEducationSerializer(EducationSerializer):
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Education
        fields = (
            'id', 'type_document', 'number_document', 'extent', 'name_nz', 'qualification', 'speciality',
            'date_end_educ', 'experied_date', 'date_issue_document', 'special_notes', 'status_document', 'photo',
            'specialization', 'serial', 'registry_number', 'is_duplicate')
        extra_kwargs = {'extent': {'required': False, 'allow_null': True},
                        'name_nz': {'required': False, 'allow_null': True},
                        'qualification': {'required': False, 'allow_null': True},
                        'speciality': {'required': False, 'allow_null': True},
                        'specialization': {'required': False, 'allow_null': True},
                        'status_document': {'required': False, 'allow_null': True},
                        }


class PersonalQualificationDocumentSerializer(QualificationDocumentSerializer):
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)

    class Meta:
        model = QualificationDocument
        fields = ('id', 'country', 'number_document', 'rank', 'date_start', 'date_end',
                  'type_document', 'status_document', 'new_document', 'statement', 'number', 'port',
                  'other_port', 'function_limitation', 'list_positions', 'strict_blank', 'photo', 'other_number')


class PersonalProofOfWorkDiplomaSerializer(ProofOfWorkDiplomaSerializer):
    status_document = None
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)

    class Meta:
        model = ProofOfWorkDiploma
        fields = ('id', 'city', 'diploma', 'number_document', 'date_start', 'date_end', 'status_document',
                  'list_positions', 'rank', 'type_document', 'port', 'statement', 'other_port', 'function_limitation',
                  'strict_blank', 'created_by', 'verificated_by', 'photo')
        extra_kwargs = {'status_document': {'required': False}}

    def to_representation(self, instance):
        response = super(PersonalProofOfWorkDiplomaSerializer, self).to_representation(instance)
        response['status_document'] = StatusDocumentSerializer(instance=instance.status_document).data
        return response


class PersonalLineInServiceRecordSerializer(LineInServiceRecordSerializer):
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    status_line = None

    class Meta:
        model = LineInServiceRecord
        fields = ('id', 'service_record', 'name_vessel', 'type_vessel', 'mode_of_navigation', 'type_geu', 'ship_owner',
                  'number_vessel', 'propulsion_power', 'electrical_power', 'all_responsibility', 'refrigerating_power',
                  'book_registration_practical', 'position', 'date_start', 'place_start', 'place_end', 'date_end',
                  'full_name_master', 'date_write', 'equipment_gmzlb', 'trading_area', 'ports_input', 'status_line',
                  'gross_capacity', 'levelRefrigerPlant', 'full_name_master_eng', 'number_page_book', 'photo',
                  'port_of_registration', 'is_repaired', 'repair_date_from', 'repair_date_to', 'days_repair',
                  'responsibility')

        extra_kwargs = {'status_line': {'required': False}}

    def to_representation(self, instance):
        response = super(PersonalLineInServiceRecordSerializer, self).to_representation(instance)
        response['status_line'] = StatusDocumentSerializer(instance=instance.status_line).data
        return response


class BasePersonalServiceRecordSailorSerializer(ServiceRecordSailorSerializer):
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    lines = PersonalLineInServiceRecordSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceRecord
        fields = ('id', 'number', 'issued_by', 'photo', 'auth_agent_ukr', 'auth_agent_eng', 'branch_office',
                  'date_issued', 'status', 'new_record', 'name_book', 'blank_strict_report', 'lines', 'photo')

    def create(self, validated_data):
        del validated_data['new_record']
        return ServiceRecord.objects.create(**validated_data)


class PersonalMedicalCertificateSerializer(MedicalCertificateSerializer):
    status_document = None
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)

    class Meta:
        model = MedicalCertificate
        fields = ('id', 'number', 'position', 'limitation', 'date_end', 'date_start', 'doctor', 'status_document',
                  'photo')
        extra_kwargs = {'status_document': {'required': False}}

    def to_representation(self, instance):
        response = super(PersonalMedicalCertificateSerializer, self).to_representation(instance)
        response['status_document'] = StatusDocumentSerializer(instance=instance.status_document).data
        return response


class PersonalSailorPassportSerializer(SailorPassportSerializer):
    status_document = None
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)

    class Meta:
        model = SailorPassport
        fields = ('id', 'country', 'number_document', 'date_start', 'date_end', 'port', 'captain',
                  'status_document', 'other_port', 'created_by', 'verificated_by', 'date_renewal', 'photo',
                  'is_new_document')
        extra_kwargs = {'status_document': {'required': False}}
        read_only_fields = ('is_new_document',)

    def to_representation(self, instance):
        response = super(PersonalSailorPassportSerializer, self).to_representation(instance)
        response['status_document'] = StatusDocumentSerializer(instance=instance.status_document).data
        return response


class PersonalCitizenPassportSerializer(CitizenPassportSerializer):
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    inn = serializers.CharField(allow_null=True, allow_blank=True)

    class Meta:
        model = Passport
        fields = ('id', 'serial', 'date', 'issued_by', 'country', 'city_registration', 'resident', 'inn',
                  'country_birth', 'sailor', 'photo')


class PersonalProtocolDKKSerializer(ProtocolDKKSerializer):
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)

    class Meta:
        model = ProtocolSQC
        fields = ('id', 'statement_dkk', 'date_meeting', 'branch_create', 'sailor', 'status_document',
                  'number_document', 'position', 'rank', 'decision',
                  'created_by', 'date_end', 'photo')
        read_only = ('branch_create',)


class PersonalExperienceDocumentSerializer(ExperienceDocumentSerializer):
    status_line = None
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)

    class Meta:
        model = LineInServiceRecord
        fields = ('id', 'name_vessel', 'type_vessel', 'mode_of_navigation', 'type_geu', 'ship_owner',
                  'number_vessel', 'propulsion_power', 'electrical_power', 'all_responsibility', 'refrigerating_power',
                  'book_registration_practical', 'position', 'date_start', 'place_start', 'place_end', 'date_end',
                  'full_name_master', 'date_write', 'equipment_gmzlb', 'trading_area', 'ports_input', 'status_line',
                  'gross_capacity', 'levelRefrigerPlant', 'full_name_master_eng', 'photo', 'record_type',
                  'responsibility_work_book', 'place_work', 'days_work', 'is_repaired', 'repair_date_from',
                  'repair_date_to', 'days_repair', 'responsibility', 'port_of_registration')
        extra_kwargs = {'status_line': {'required': False}}

    def create(self, validated_data):
        return LineInServiceRecord.objects.create(**validated_data)

    def to_representation(self, instance):
        response = super(PersonalExperienceDocumentSerializer, self).to_representation(instance)
        response['status_line'] = StatusDocumentSerializer(instance=instance.status_line).data
        return response


class PersonalSailorStatementDKKSerialize(StatementDKKSerializer):
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)
    status_sqc = serializers.ReadOnlyField(source='get_status_position', read_only=True)
    date_create = serializers.DateTimeField(format='%m-%d-%Y', read_only=True, source='created_at')
    can_create_exam = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StatementSQC
        fields = ('id', 'sailor', 'is_payed', 'status_sqc', 'can_create_exam',
                  'number', 'status_document', 'rank', 'list_positions', 'rank', 'date_create', 'photo')

    def get_can_create_exam(self, instance: StatementSQC):
        request = self.context.get('request')
        if not request:
            return False
        client_ip = get_client_ip(request=request)
        if not hasattr(instance, 'protocolsqc') and \
                instance.status_document.pk == magic_numbers.status_state_qual_dkk_approv:
            now = timezone.now()
            exam = AvailableExamsToday.objects.filter(datetime_meeting__lte=now,
                                                      datetime_end_meeting__gte=now,
                                                      list_positions=sorted(instance.list_positions))
            sailor = SailorKeys.objects.filter(id=instance.sailor).first()
            if not sailor:
                return None
            proofs = QualificationDocument.objects.filter(
                id__in=sailor.qualification_documents,
                list_positions=instance.list_positions,
                date_start__gte=instance.created_at
            )
            return exam.exists() and not proofs.exists() and ip_address(client_ip) in ip_network('212.8.50.254/32')
        return False


class PersonalInfoSailorStatementDKKSerialize(StatementDKKSerializer):
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    sailor = serializers.IntegerField(write_only=True, required=False)
    date_create = serializers.DateTimeField(format='%m-%d-%Y', required=False, source='created_at')

    class Meta:
        model = StatementSQC
        fields = ('id', 'sailor', 'is_payed', 'status_dkk',
                  'number', 'status_document', 'rank', 'list_positions', 'rank', 'date_create', 'photo')


class PersonalStatementQualificationDocumentSerializer(StatementQualificationDocumentSerializer):
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)
    sailor = serializers.IntegerField(write_only=True, required=False)
    date_create = serializers.DateTimeField(format='%m-%d-%Y', required=False, source='created_at')
    status_document = customSerializers.StatusDocumentSerializer(queryset=StatusDocument.objects.all(),
                                                                 required=False, allow_null=True, allow_empty=True)

    class Meta:
        model = StatementQualification
        fields = ('id', 'status_dkk', 'number', 'status_document', 'protocol_dkk',
                  'port', 'type_document', 'rank', 'list_positions', 'is_payed', 'date_create', 'photo')
        read_only = ('photo',)


class PersonalProfileMainInfoSerializer(ProfileMainInfoSerializer):
    sailor_key = serializers.SerializerMethodField()
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), allow_null=True, required=False)
    is_approved_personal_data_processing = serializers.SerializerMethodField()
    is_main_phone = serializers.SerializerMethodField()

    def get_sailor_key(self, *args, **kwargs):
        return self.sailor_key_val

    def get_is_approved_personal_data_processing(self, *args, **kwargs):
        return PersonalDataProcessing.objects.filter(sailor=self.sailor_key_val, is_accepted=True).exists()

    def get_is_main_phone(self, *args, **kwargs):
        sailor = SailorKeys.objects.get(id=self.sailor_key_val)
        user = User.objects.get(id=sailor.user_id)
        return user.username.startswith('+')

    class Meta:
        fields = ('first_name_ukr', 'first_name_eng', 'last_name_ukr', 'last_name_eng', 'middle_name_ukr',
                  'middle_name_eng', 'sex', 'contact_info', 'position', 'rank', 'is_approved_personal_data_processing',
                  'date_birth', 'photo', 'passport', 'created_by', 'is_dkk', 'sailor_key', 'is_main_phone')
        model = Profile


class CheckDocumentsStatementDKKSerializer(serializers.ModelSerializer):
    type_document = serializers.ReadOnlyField(source='get_name_type_document', read_only=True)

    class Meta:
        model = DependencyDocuments
        fields = ('document_description', 'type_document')


class CheckDocumentParamsSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    list_positions = serializers.ListField(child=serializers.IntegerField())


class PersonalDataProcessingSerializer(serializers.ModelSerializer):
    sailor = serializers.IntegerField(required=False, allow_null=True, read_only=True)
    date_create = serializers.DateTimeField(read_only=True)

    class Meta:
        model = PersonalDataProcessing
        fields = ('id', 'sailor', 'date_create', 'is_accepted')


class HistoryUserInPersonalCabinetSerializer(serializers.ModelSerializer):
    sailor = serializers.IntegerField(required=False, allow_null=True, read_only=True)
    date_create = serializers.DateTimeField(read_only=True)
    document_type = serializers.CharField(allow_null=True, required=False, write_only=True)

    class Meta:
        model = HistoryUserInPersonalCabinet
        fields = ('id', 'sailor', 'date_create', 'longitude', 'latitude', 'action', 'document_type', 'object_id')
        extra_kwargs = {'object_id': {'write_only': True}}

    def create(self, validated_data):
        user = self.context['request'].user
        try:
            sailor_key = SailorKeys.objects.get(user_id=user.pk)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        document_type = validated_data.pop('document_type', None)
        if document_type:
            ct = ContentType.objects.get(model__iexact=document_type)
            history = HistoryUserInPersonalCabinet.objects.create(sailor=sailor_key.pk, user_id=user.pk,
                                                                  document_type_id=ct.id, **validated_data)
        else:
            history = HistoryUserInPersonalCabinet.objects.create(sailor=sailor_key.pk, user_id=user.pk,
                                                                  **validated_data)
        return history


class PersonalAgentSerializer(AgentUserSerializer):
    userprofile = PersonalAgentUserProfSerializer(read_only=True)
    status_seaman = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'userprofile', 'status_seaman')

    def get_status_seaman(self, instance):
        status_by_code = {0: 'have_seaman',
                          magic_numbers.status_statement_agent_sailor_wait_sailor: 'wait_sailor',
                          magic_numbers.status_statement_agent_sailor_wait_secretary: 'in_progress',
                          magic_numbers.status_statement_agent_sailor_in_process: 'in_progress'}
        return status_by_code[instance._status_verification]


class CurrentAppVersionSerializer(serializers.Serializer):
    version = serializers.CharField(max_length=50)


class ChangeMainPhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=30)
    security_code = serializers.IntegerField(required=False, allow_null=True)


class PersonalCertificateNTZSerializer(CertificateNTZSerializer):
    status_document = None
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    date_create = serializers.DateTimeField(source='created_at')

    class Meta:
        model = CertificateETI
        read_only_fields = ['date_create']
        fields = ('id', 'ntz', 'ntz_number', 'course_traning', 'date_create', 'date_start', 'date_end', 'photo',
                  'status_document')
        extra_kwargs = {'status_document': {'required': False}}

    def to_representation(self, instance):
        response = super(PersonalCertificateNTZSerializer, self).to_representation(instance)
        response['status_document'] = StatusDocumentSerializer(instance=instance.status_document).data
        return response


class PersonalStudentsIDSerializer(StudentIDSerializer):
    photo = PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    status_document = None

    class Meta:
        model = StudentID
        fields = ('id', 'serial', 'number', 'name_nz', 'group', 'education_form', 'faculty', 'date_start', 'date_end',
                  'educ_with_dkk', 'passed_educ_exam', 'status_document', 'photo')
        extra_kwargs = {'status_document': {'required': False}}
