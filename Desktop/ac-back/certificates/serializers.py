from copy import deepcopy
from datetime import date

from rest_framework import serializers

from back_office.models import ETIMonthRatio
from certificates.models import ETIRegistry, CertificateRedHistory
from directory.models import NTZ, Course
from directory.serializers import NTZSerializer, CourseForNTZSerializer, SmallETISerializer
from sailor.document.models import CertificateETI
from sailor.tasks import save_history


class ETIRegistrySerializer(serializers.ModelSerializer):
    full_number_protocol = serializers.ReadOnlyField(source='get_full_number_protocol')
    date_create = serializers.DateTimeField(source='created_at', read_only=True)
    date_modified = serializers.DateTimeField(source='modified_at', read_only=True)

    class Meta:
        fields = ('id', 'date_create', 'date_modified', 'institution', 'course', 'date_start', 'date_end',
                  'number_protocol', 'full_number_protocol', 'is_disable')
        read_only_fields = ('date_create', 'date_modified')
        extra_kwargs = {'number_protocol': {'write_only': True}}
        model = ETIRegistry

    def to_representation(self, instance):
        response = super(ETIRegistrySerializer, self).to_representation(instance)
        response['institution'] = SmallETISerializer(instance.institution).data
        response['course'] = CourseForNTZSerializer(instance.course).data
        return response

    def update(self, instance, validated_data):
        old_instance = deepcopy(instance)
        new_instance = super().update(instance, validated_data)
        save_history.s(user_id=self.context['request'].user.id,
                       module='ETIRegistry',
                       action_type='edit',
                       content_obj=instance,
                       serializer=ETIRegistrySerializer,
                       new_obj=new_instance,
                       old_obj=old_instance,
                       ).apply_async(serializer='pickle')
        return instance


class ETIWithoutInstitution(serializers.ModelSerializer):
    full_number_protocol = serializers.ReadOnlyField(source='get_full_number_protocol')
    date_create = serializers.DateTimeField(source='created_at')
    date_modified = serializers.DateTimeField(source='modified_at')

    class Meta:
        fields = ('id', 'date_create', 'date_modified', 'course', 'date_start', 'date_end', 'full_number_protocol',
                  'number_protocol', 'is_disable')
        read_only_fields = ('date_create', 'date_modified')
        extra_kwargs = {'number_protocol': {'write_only': True}}
        model = ETIRegistry

    def to_representation(self, instance):
        response = super(ETIWithoutInstitution, self).to_representation(instance)
        response['course'] = CourseForNTZSerializer(instance.course).data
        return response


class ETIByInstitutionSerializer(SmallETISerializer):
    eti_registry = ETIWithoutInstitution(many=True)

    class Meta:
        model = NTZ
        fields = ('id', 'name_ukr', 'name_eng', 'name_abbr', 'eti_registry')


class ETIMonthRatioSerializer(serializers.ModelSerializer):
    ntz = NTZSerializer(read_only=True, source='institution')
    order = serializers.SerializerMethodField()

    class Meta:
        model = ETIRegistry
        fields = ('ntz', 'order')
        read_only_fields = ('ntz', 'order')

    def get_order(self, instance):
        return 1


class FullInfoETIMonthRatioSerializer(serializers.ModelSerializer):
    ntz = NTZSerializer(read_only=True)
    order = serializers.ReadOnlyField()
    course = CourseForNTZSerializer(read_only=True)

    class Meta:
        model = ETIMonthRatio
        fields = ('id', 'ntz', 'order', 'ratio', 'month_amount', 'course')
        read_only_fields = fields


class CertificateRedHistorySerializer(serializers.ModelSerializer):
    date_create = serializers.DateTimeField(source='created_at')
    date_modified = serializers.DateTimeField(source='modified_at')

    class Meta:
        model = CertificateRedHistory
        fields = '__all__'
        read_only_fields = ('date_end', 'date_create', 'date_modified')


class InstituteETISerializer(NTZSerializer):
    red_history = CertificateRedHistorySerializer(many=True, read_only=True)

    class Meta:
        model = NTZ
        exclude = ('ntz_integration_id',)
        extra_kwargs = {'check_number': {'allow_blank': True},
                        'mfo': {'allow_blank': True},
                        'nds_number': {'allow_blank': True}}

    def update(self, instance: NTZ, validated_data):
        old_instance = deepcopy(instance)
        is_red = validated_data.get('is_red')
        if is_red is not None and is_red != instance.is_red:
            if is_red is False:
                current_history, _ = CertificateRedHistory.objects.get_or_create(
                    institute=instance,
                    date_end=None,
                    defaults={'date_start': date.today()}
                )
                current_history.date_end = date.today()
                current_history.save(update_fields=['date_end'])
            else:
                CertificateRedHistory.objects.create(
                    institute=instance,
                    date_start=date.today(),
                )
        new_instance = super().update(instance, validated_data)
        save_history.s(user_id=self.context['request'].user.id,
                       module='ETIInstitution',
                       action_type='edit',
                       content_obj=instance,
                       serializer=InstituteETISerializer,
                       new_obj=new_instance,
                       old_obj=old_instance,
                       ).apply_async(serializer='pickle')
        return instance


class PublicInstituteETISerializer(InstituteETISerializer):
    red_history = None
    organisation_name = serializers.CharField(source='name_ukr')
    organisation_name_eng = serializers.CharField(source='name_eng', allow_blank=True)
    mail_adress_ukr = serializers.CharField(source='address', allow_blank=True)
    phone1 = serializers.CharField(source='phone', allow_blank=True)
    orgnisation_email = serializers.EmailField(source='email', allow_blank=True)
    checking_number = serializers.CharField(source='check_number', allow_blank=True)
    head_full_name = serializers.CharField(source='director_name', allow_blank=True)
    head_position = serializers.CharField(source='director_position', allow_blank=True)
    activated = serializers.DateField(source='date_start', allow_null=True)
    active_till = serializers.DateField(source='date_end', allow_null=True)
    guid = serializers.UUIDField(source='uuid')

    class Meta:
        model = NTZ
        fields = ('organisation_name', 'organisation_name_eng', 'mail_adress_ukr', 'phone1', 'phone2',
                  'orgnisation_email', 'contract_number', 'contract_number_date', 'checking_number',
                  'bank_name', 'mfo', 'okpo', 'inn', 'nds_number', 'head_full_name', 'head_position',
                  'accountant_full_name', 'activated', 'active_till', 'is_disable', 'name_abbr', 'guid')


class ETIRegistryCourseSerializer(serializers.ModelSerializer):
    full_number_protocol = serializers.ReadOnlyField(source='get_full_number_protocol')
    date_create = serializers.DateTimeField(source='created_at')
    date_modified = serializers.DateTimeField(source='modified_at')

    class Meta:
        fields = ('id', 'date_create', 'date_modified', 'institution', 'course', 'date_start', 'date_end',
                  'number_protocol', 'full_number_protocol', 'is_disable')
        read_only_fields = ('date_create', 'date_modified')
        extra_kwargs = {'number_protocol': {'write_only': True}}
        model = ETIRegistry

    def to_representation(self, instance):
        response = super(ETIRegistryCourseSerializer, self).to_representation(instance)
        response['institution'] = SmallETISerializer(instance.institution).data
        return response

    def get_queryset(self):
        today = date.today()
        return ETIRegistry.objects.filter(is_disable=False, date_start__gte=today, date_end__lte=today)


class RelatedETIMonthRatioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETIMonthRatio
        fields = ('id', 'ntz', 'ratio')

    def to_representation(self, instance):
        response = super(RelatedETIMonthRatioSerializer, self).to_representation(instance)
        response['ntz'] = SmallETISerializer(instance.ntz).data
        return response


class ListMonthRatioByCourse(serializers.ModelSerializer):
    ntz_ratio = RelatedETIMonthRatioSerializer(many=True)

    class Meta:
        model = Course
        fields = ('id', 'name_ukr', 'name_eng', 'code_for_parsing', 'ntz_ratio')


class UpdateEtiRatioSerializer(serializers.Serializer):
    eti_id = serializers.PrimaryKeyRelatedField(queryset=NTZ.objects.all())
    eti_ratio = serializers.FloatField()


class UpdateMonthRatioByCourse(serializers.Serializer):
    eti_ratio = UpdateEtiRatioSerializer(many=True)


class PublicCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ('code_for_parsing', 'api_ntz_id')


class PublicUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateETI
        fields = ('id', 'status_document')
