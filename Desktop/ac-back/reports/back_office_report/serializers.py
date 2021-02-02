from django.contrib.auth import get_user_model
from rest_framework import serializers

import directory.serializers
from agent.models import AgentGroup
from agent.serializers import AgentGroupsSerializer
from back_office.models import PacketItem
from communication.models import SailorKeys
from directory.models import (MedicalInstitution, DoctrorInMedicalInstitution, BranchOffice, NTZ, Course,
                              LevelQualification)
from reports.serializers import ProfileSailorSerializer
from sailor.document.models import ProofOfWorkDiploma
from user_profile.serializer import UserSerializer

User = get_user_model()


class BaseGlobalPacketReportSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    form2_sum = serializers.FloatField()
    form1_sum = serializers.FloatField()


class GlobalPacketByGroupReportSerializer(BaseGlobalPacketReportSerializer):
    group = serializers.IntegerField(source='packet_item__agent__userprofile__agent_group')

    def to_representation(self, instance):
        response = super(GlobalPacketByGroupReportSerializer, self).to_representation(instance)
        try:
            group_instance = AgentGroup.objects.get(id=instance.get('packet_item__agent__userprofile__agent_group'))
            response['group'] = AgentGroupsSerializer(instance=group_instance).data
        except AgentGroup.DoesNotExist:
            pass
        return response


class GlobalPacketByAgentReportSerializer(BaseGlobalPacketReportSerializer):
    agent = serializers.IntegerField(source='packet_item__agent')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        agent_instance = User.objects.get(id=instance.get('packet_item__agent'))
        response['agent'] = UserSerializer(instance=agent_instance).data
        return response


class GlobalPacketBySailorReportSerializer(BaseGlobalPacketReportSerializer):
    sailor = ProfileSailorSerializer(source='packet_item__sailor_id', queryset=SailorKeys.objects.all())


class GlobalPacketByPacketReportSerializer(BaseGlobalPacketReportSerializer):
    packet = serializers.IntegerField(source='packet_item')
    sailor = ProfileSailorSerializer(source='packet_item__sailor_id', queryset=SailorKeys.objects.all())

    def to_representation(self, instance):
        packet_item_instance = PacketItem.objects.get(id=instance.get('packet_item'))
        response = super(GlobalPacketByPacketReportSerializer, self).to_representation(instance)
        response['number'] = packet_item_instance.number
        response['payment_date'] = packet_item_instance.payment_date
        response['rank'] = packet_item_instance.rank
        return response


class GlobalPacketByDocumentReportSerializer(BaseGlobalPacketReportSerializer):
    id = serializers.IntegerField()
    type_document = directory.serializers.TypeOfAccrualRulesSerializer()
    number_document = serializers.SerializerMethodField()

    def get_number_document(self, instance):
        try:
            return instance.item.get_number
        except AttributeError:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sailor'] = ProfileSailorSerializer(
            source=instance.packet_item.sailor_id, queryset=SailorKeys.objects.all()
        ).to_representation(instance.packet_item.sailor_id)
        return response


class BaseDistributionSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    count = serializers.IntegerField()
    form2_sum = serializers.FloatField()


class DistributionDPDSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    form2_sum = serializers.FloatField()

    def to_representation(self, instance):
        response = super().to_representation(instance)
        branch_office = BranchOffice.objects.get(id=instance['packet_item__service_center'])
        response['branch_office'] = directory.serializers.BranchOfficeSerializer(branch_office).data
        return response


class DistributionDPDDocumentSerializer(serializers.Serializer):

    def to_representation(self, instance):
        response = [{'name': 'Посвідчення особи моряка (роздача)',
                     'distribution_sum': instance['distribution_sum_sailor_pasport'],
                     'profit_sum': instance['profit_sum_sailor_pasport'],
                     'form2_sum': instance['form2_sum_sailor_pasport'],
                     'type': 'passport'},
                    {'name': 'Кваліфікаційні документи (роздача)',
                     'distribution_sum': instance['distribution_sum_qual_doc'],
                     'profit_sum': instance['profit_sum_qual_doc'],
                     'form2_sum': instance['form2_sum_qual_doc'],
                     'type': 'qualification'}]
        return response


class DistributionDPDSailorPassportSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    number_document = serializers.SerializerMethodField()
    date_create = serializers.SerializerMethodField()
    is_continue = serializers.SerializerMethodField()
    form2_sum = serializers.FloatField()

    def get_number_document(self, instance):
        try:
            return instance.item.number
        except AttributeError:
            return None

    def get_date_create(self, instance):
        try:
            date_create = instance.item.statement.created_at
            return date_create.strftime('%d-%m-%Y')
        except AttributeError:
            return None

    def get_is_continue(self, instance):
        try:
            return instance.item.is_continue
        except AttributeError:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sailor'] = ProfileSailorSerializer(queryset=SailorKeys.objects.all()
                                                     ).to_representation(instance.packet_item.sailor_id)
        return response


class DistributionDPDQualDocSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    number_document = serializers.SerializerMethodField()
    date_create = serializers.SerializerMethodField()
    date_start = serializers.SerializerMethodField()
    form2_sum = serializers.FloatField()

    def get_number_document(self, instance):
        try:
            return instance.item.get_number
        except AttributeError:
            return None

    def get_date_start(self, instance):
        try:
            return instance.item.date_start
        except AttributeError:
            return None

    def get_date_create(self, instance):
        try:
            date_create = instance.item.statement.created_at
            return date_create.strftime('%d-%m-%Y')
        except AttributeError:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sailor'] = ProfileSailorSerializer(queryset=SailorKeys.objects.all()
                                                     ).to_representation(instance.packet_item.sailor_id)
        response['rank'] = instance.packet_item.rank
        response['list_positions'] = directory.serializers.PositionSerializer(
            instance.packet_item.position, many=True).data
        if hasattr(instance.item, 'type_document'):
            response['type_document'] = directory.serializers.TypeDocumentQualSerializer(
                instance.item.type_document).data
        elif isinstance(instance.item, ProofOfWorkDiploma):
            response['type_document'] = 'Підтвердження робочого диплому'
        else:
            response['type_document'] = None
        return response


class DistributionAdvTrainingSerializer(BaseDistributionSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        level = LevelQualification.objects.get(id=instance['adv_training_item__level_qualification'])
        response['level_qualification'] = directory.serializers.LevelQualitifcationSerializer(level).data
        return response


class DistributionAdvTrainingSailorSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    date_create = serializers.SerializerMethodField()
    form2_sum = serializers.FloatField()

    def get_date_create(self, instance):
        try:
            date_create = instance.item.created_at
            return date_create.strftime('%d-%m-%Y')
        except AttributeError:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sailor'] = ProfileSailorSerializer(queryset=SailorKeys.objects.all()
                                                     ).to_representation(instance.packet_item.sailor_id)
        response['level_qualification'] = directory.serializers.LevelQualitifcationSerializer(
            instance.item.level_qualification).data
        return response


class DistributionMedicalInstitutionSerializer(BaseDistributionSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        medical = MedicalInstitution.objects.get(id=instance['medical'])
        response['medical_institution'] = directory.serializers.MedicalInstitutionSerializer(medical).data
        return response


class DistributionDoctorSerializer(BaseDistributionSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance['doctor']:
            doctor = DoctrorInMedicalInstitution.objects.get(id=instance['doctor'])
            response['doctor'] = directory.serializers.DoctrorInMedicalInstitutionSerializer(doctor).data
        else:
            response['doctor'] = None
        return response


class DistributionMedicalSailorSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    number_document = serializers.SerializerMethodField()
    date_create = serializers.SerializerMethodField()
    form2_sum = serializers.FloatField()

    def get_number_document(self, instance):
        try:
            return instance.item.get_number
        except AttributeError:
            return None

    def get_date_create(self, instance):
        try:
            date_create = instance.item.medical_statement.created_at
            return date_create.strftime('%d-%m-%Y')
        except AttributeError:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sailor'] = ProfileSailorSerializer(queryset=SailorKeys.objects.all()
                                                     ).to_representation(instance.packet_item.sailor_id)
        response['position'] = directory.serializers.PositionForMedicalSerializer(instance.item.position).data
        return response


class DistributionSQCSerializer(BaseDistributionSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        try:
            group_instance = AgentGroup.objects.get(id=instance.get('packet_item__agent__userprofile__agent_group'))
            response['group'] = AgentGroupsSerializer(instance=group_instance).data
        except AgentGroup.DoesNotExist:
            response['group'] = None
        return response


class DistributionSQCGroupSerializer(BaseDistributionSerializer):
    agent = serializers.IntegerField(source='packet_item__agent')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        agent_instance = User.objects.get(id=instance.get('packet_item__agent'))
        response['agent'] = UserSerializer(instance=agent_instance).data
        return response


class DistributionSQCSailorSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    date_create = serializers.SerializerMethodField()
    form2_sum = serializers.FloatField()

    def get_date_create(self, instance):
        try:
            date_create = instance.item.created_at
            return date_create.strftime('%d-%m-%Y')
        except AttributeError:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sailor'] = ProfileSailorSerializer(queryset=SailorKeys.objects.all()
                                                     ).to_representation(instance.packet_item.sailor_id)
        response['rank'] = instance.packet_item.rank
        return response


class DistributionServiceCenterSerializer(BaseDistributionSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        branch_office = BranchOffice.objects.get(id=instance.get('packet_item__service_center'))
        response['branch_office'] = directory.serializers.BranchOfficeSerializer(branch_office).data
        return response


class DistributionServiceCenterSailorSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    date_create = serializers.SerializerMethodField()
    form2_sum = serializers.FloatField()

    def get_date_create(self, instance):
        try:
            date_create = instance.packet_item.created_at
            return date_create.strftime('%d-%m-%Y')
        except AttributeError:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sailor'] = ProfileSailorSerializer(queryset=SailorKeys.objects.all()
                                                     ).to_representation(instance.packet_item.sailor_id)
        response['rank'] = instance.packet_item.rank
        return response


class NameETISerializer(serializers.ModelSerializer):
    """
    Only name ETI
    """

    class Meta:
        model = NTZ
        fields = ('id', 'name_ukr', 'name_eng')


class DistributionETISerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    count = serializers.IntegerField()
    form2_sum = serializers.FloatField()

    def to_representation(self, instance):
        response = super().to_representation(instance)
        eti = NTZ.objects.get(id=instance['eti'])
        response['eti'] = NameETISerializer(eti).data
        return response


class DistributionETICoursesSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    count = serializers.IntegerField()
    form2_sum = serializers.FloatField()

    def to_representation(self, instance):
        response = super().to_representation(instance)
        course = Course.objects.get(id=instance['course'])
        response['course'] = directory.serializers.CourseForNTZSerializer(course).data
        return response


class DistributionETISailorSerializer(serializers.Serializer):
    distribution_sum = serializers.FloatField()
    profit_sum = serializers.FloatField()
    date_create = serializers.SerializerMethodField()
    form2_sum = serializers.FloatField()

    def get_date_create(self, instance):
        try:
            date_create = instance.packet_item.created_at
            return date_create.strftime('%d-%m-%Y')
        except AttributeError:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sailor'] = ProfileSailorSerializer(queryset=SailorKeys.objects.all()
                                                     ).to_representation(instance.packet_item.sailor_id)
        return response
