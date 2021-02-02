from copy import deepcopy

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from sailor.tasks import save_history
from .models import (AuthorizatedUsers, BranchOffice, City, Commisioner, Country, Course, Decision,
                     Direction, DoctrorInMedicalInstitution, EducationForm, ExtentDiplomaUniversity, Faculty,
                     FIOCapitanOfPort, FunctionAndLevelForPosition, FunctionForPosition, LevelQualification,
                     Limitations, MedicalInstitution, ModeOfNavigation, NTZ, NZ, Port, Position, PositionForExperience,
                     PositionForMedical, Rank, Region, Responsibility, ResponsibilityWorkBook, Sex, Speciality,
                     Specialization, StatusDocument, TypeContact, TypeDocument, TypeDocumentNZ, TypeGeu,
                     TypeOfAccrualRules, TypeRank, TypeVessel, VerificationStage)


class NTZSerializer(serializers.ModelSerializer):
    class Meta:
        model = NTZ
        exclude = ('ntz_integration_id',)


class SmallETISerializer(serializers.ModelSerializer):
    """
    Small  ETI serializer
    """

    class Meta:
        model = NTZ
        fields = ('id', 'name_ukr', 'name_abbr', 'name_eng', 'can_pay_platon')


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

    def create(self, validated_data):
        try:
            queryset = City.objects.get(**validated_data)
            if queryset:
                raise ValidationError("City exist")
        except City.DoesNotExist:
            user = getattr(self.context.get('request'), 'user', None)
            user_id = None
            if user:
                user_id = user.id
            try:
                instance = City.objects.get(region=validated_data['region'], value=validated_data['value'])
                if instance:
                    old_instance = deepcopy(instance)
                    new_instance = super().update(instance, validated_data)
                    if user_id:
                        save_history.s(user_id=user_id,
                                       module='City',
                                       action_type='edit',
                                       content_obj=instance,
                                       serializer=CitySerializer,
                                       new_obj=new_instance,
                                       old_obj=old_instance,
                                       ).apply_async(serializer='pickle')
                    return instance

            except City.DoesNotExist:
                try:
                    instance = City.objects.get(region=validated_data['region'], value_eng=validated_data['value_eng'])
                    if instance:
                        old_instance = deepcopy(instance)
                        new_instance = super().update(instance, validated_data)
                        if user_id:
                            save_history.s(user_id=user_id,
                                           module='City',
                                           action_type='edit',
                                           content_obj=instance,
                                           serializer=CitySerializer,
                                           new_obj=new_instance,
                                           old_obj=old_instance,
                                           ).apply_async(serializer='pickle')
                        return instance
                except City.DoesNotExist:
                    instance, _ = City.objects.get_or_create(**validated_data)
                    if user_id:
                        save_history.s(user_id=user_id,
                                       module='City',
                                       action_type='create',
                                       content_obj=instance,
                                       serializer=CitySerializer,
                                       new_obj=instance,
                                       ).apply_async(serializer='pickle')
                    return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['region'] = RegionSerializer(instance=instance.region).data
        response['country'] = CountrySerializer(instance=instance.region.country).data
        return response


class RankSerializer(serializers.ModelSerializer):
    is_dkk = serializers.ReadOnlyField(source='get_is_dkk')
    summ = serializers.FloatField(source='price')

    class Meta:
        model = Rank
        fields = ('id', 'name_ukr', 'is_dkk', 'name_eng', 'type_rank', 'type_document', 'direction', 'is_disable',
                  'summ')


class FunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsibility
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    name_with_rank_ukr = serializers.ReadOnlyField(source='position_with_rank_ukr')
    name_with_rank_eng = serializers.ReadOnlyField(source='position_with_rank_eng')

    class Meta:
        model = Position
        fields = ('id', 'name_ukr', 'name_eng', 'rank', 'is_dkk', 'team', 'is_disable', 'name_with_rank_ukr',
                  'name_with_rank_eng')


class StatusDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusDocument
        fields = '__all__'


class PortCaptainSerializer(serializers.ModelSerializer):
    class Meta:
        model = FIOCapitanOfPort
        fields = '__all__'


class PortSerializer(serializers.ModelSerializer):
    # captain = PortCaptainSerializer()
    # captain_eng = PortCaptainSerializer(source='name_eng')

    class Meta:
        model = Port
        # fields = ('code_port', 'name_ukr', 'name_eng', 'position_capitan_ukr', 'position_capitan_eng', 'phone', 'email',
        #           'captain_eng', 'is_disable')
        fields = '__all__'


class BranchOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchOffice
        fields = '__all__'


class MedicalInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalInstitution
        fields = '__all__'


class DoctrorInMedicalInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctrorInMedicalInstitution
        fields = '__all__'


class PositionForMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionForMedical
        fields = '__all__'


class PositionForExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionForExperience
        fields = '__all__'


class TypeDocumentNZSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeDocumentNZ
        fields = '__all__'


class ExtentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtentDiplomaUniversity
        fields = '__all__'


class NZSerializer(serializers.ModelSerializer):
    class Meta:
        model = NZ
        fields = '__all__'


class NZNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = NZ
        fields = ('id', 'name_ukr', 'name_eng')


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = '__all__'


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'


class LevelQualitifcationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelQualification
        fields = '__all__'


class LimitationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Limitations
        fields = '__all__'


class AuthUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizatedUsers
        fields = '__all__'


class TypeDocumentQualSerializer(serializers.ModelSerializer):
    summ = serializers.FloatField(source='price')

    class Meta:
        model = TypeDocument
        fields = '__all__'


# class CommitteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Committe
#         fields = '__all__'


class CommisionerForCommitteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commisioner
        fields = '__all__'


class CourseForNTZSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class DecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decision
        fields = '__all__'


class FunctionForPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionForPosition
        fields = '__all__'


class FunctionAndLevelForPositionSerializer(serializers.ModelSerializer):
    function = FunctionForPositionSerializer()

    class Meta:
        model = FunctionAndLevelForPosition
        fields = ('function', 'id', 'position', 'level')


class TypeRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeRank
        fields = '__all__'


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = '__all__'


class EducationFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationForm
        fields = ('id', 'name_ukr', 'name_eng')


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ('id', 'name_ukr', 'name_eng')


class SexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sex
        fields = '__all__'


class TypeContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeContact
        fields = '__all__'


class TypeVesselSailorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeVessel
        fields = '__all__'


class ModeOfNavigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeOfNavigation
        fields = '__all__'


class TypeGeuSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeGeu
        fields = '__all__'


class ResponsibilityWorkBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponsibilityWorkBook
        fields = '__all__'


class TypeOfAccrualRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOfAccrualRules
        exclude = ('document_type',)


class VerificationStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationStage
        fields = ('id', 'name_ukr', 'name_eng', 'order_number')
