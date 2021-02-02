from copy import deepcopy

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from rest_framework import serializers

import directory.models
from agent.models import AgentGroup
from sailor.forModelSerializer import ContactSerializator
from sailor.models import ContactInfo
from sailor.tasks import save_history
from user_profile.models import (UserProfile, BranchOffice, MainGroups, Version, BranchOfficeRestrictionForPermission,
                                 City)
from . import forModelSerialize

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    city = serializers.SlugRelatedField(
        slug_field='value',
        queryset=City.objects.all(),
    )
    branch_office = serializers.SlugRelatedField(
        slug_field='name_ukr',
        queryset=BranchOffice.objects.all(), default=BranchOffice.objects.get(id=2)
    )
    main_group = serializers.SlugRelatedField(
        slug_field='name',
        queryset=MainGroups.objects.all(),
        many=True,
    )
    contact_info = ContactSerializator(queryset=ContactInfo.objects.all(), required=False, allow_null=True)
    agent_group = serializers.PrimaryKeyRelatedField(queryset=AgentGroup.objects.all(), required=False, allow_null=True,
                                                     many=True)
    middle_name = serializers.CharField(required=False, allow_null=True, default='', allow_blank='')
    doctor_info = serializers.PrimaryKeyRelatedField(
        queryset=directory.models.DoctrorInMedicalInstitution.objects.all(),
        required=False, allow_null=True)
    eti_institution = serializers.PrimaryKeyRelatedField(queryset=directory.models.NTZ.objects.all(), required=False,
                                                         allow_null=True)
    education_institution = serializers.PrimaryKeyRelatedField(
        queryset=directory.models.NZ.objects.filter(type_nz_id=2), required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ('middle_name', 'city', 'branch_office', 'additional_data', 'language', 'main_group', 'contact_info',
                  'agent_group', 'doctor_info', 'type_user', 'eti_institution', 'education_institution')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    userprofile = UserProfileSerializer(required=True, partial=True)
    agent_group = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'is_active', 'userprofile',
                  'agent_group')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('userprofile', None)
        contact_info = profile_data.pop('contact_info', [])
        if contact_info:
            contact_info = list(contact_info.values_list('pk', flat=True))
        password = validated_data.pop('password')
        user, is_new = User.objects.get_or_create(**validated_data)
        if not is_new:
            return user
        user.set_password(password)
        user.save()
        if profile_data:
            groups = profile_data['main_group']
            type_user = {}
            groups_name = [group.name for group in groups]
            user_agent_group = profile_data.get('agent_group')
            if 'Довірена особа' in groups_name:
                type_user.update(type_user=UserProfile.AGENT)
            elif 'Керівник групи' in groups_name:
                type_user.update(type_user=UserProfile.HEAD_AGENT)
            elif 'Секретар СЦ' in groups_name:
                type_user.update(type_user=UserProfile.SECRETARY_SERVICE)
            elif 'Back office' in groups_name:
                user.is_superuser = True
                user.is_staff = True
                user.save(update_fields=['is_superuser', 'is_staff'])
                type_user.update(type_user=UserProfile.BACK_OFFICE)
            elif 'Верифікатор' in groups_name:
                type_user.update(type_user=UserProfile.VERIFIER)
            elif 'Мед. працівник' in groups_name:
                type_user.update(type_user=UserProfile.MEDICAL)
            elif 'Дипломно-паспортний' in groups_name:
                type_user.update(type_user=UserProfile.DPD)
            elif 'Представник НТЗ' in groups_name:
                type_user.update(type_user=UserProfile.ETI_EMPLOYEE)
            elif 'Секретар КПК' in groups_name:
                type_user.update(type_user=UserProfile.SECRETARY_ATC)
            userprofile = UserProfile.objects.create(user=user,
                                                     middle_name=profile_data['middle_name'],
                                                     city=profile_data['city'],
                                                     branch_office=profile_data.get('branch_office'),
                                                     additional_data=profile_data['additional_data'],
                                                     language=profile_data.get('language', 'UA'),
                                                     contact_info=contact_info,
                                                     doctor_info=profile_data.get('doctor_info'),
                                                     eti_institution=profile_data.get('eti_institution'),
                                                     education_institution=profile_data.get('education_institution'),
                                                     **type_user)
            if user_agent_group:
                [userprofile.agent_group.add(group) for group in user_agent_group]
            user_group = userprofile
            for group in groups:
                user_group.main_group.add(group)
                all_group = Group.objects.filter(maingroups=group)
                for item in all_group:
                    user.groups.add(item)
            user_group.save()
            author = getattr(self.context.get('request'), 'user', None)
            if author:
                save_history.s(user_id=author.id,
                               module='User',
                               action_type='create',
                               content_obj=user,
                               serializer=UserSerializer,
                               new_obj=user,
                               ).apply_async(serializer='pickle')

        return user

    def update(self, instance, validated_data):
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)

            elif attr == 'userprofile':
                profile_data = validated_data['userprofile']
                agent_group = profile_data.pop('agent_group', None)
                try:
                    profile = instance.userprofile
                    if agent_group:
                        instance.userprofile.agent_group.clear()
                        [instance.userprofile.agent_group.add(group) for group in agent_group]
                    old_instance.userprofile = deepcopy(instance.userprofile)
                except UserProfile.DoesNotExist:
                    UserProfile.objects.get_or_create(user=instance,
                                                      city=profile_data['city'],
                                                      branch_office=profile_data['branch_office'],
                                                      )
                    profile = instance.userprofile
                for item in profile_data:
                    if item == 'main_group':
                        groups = profile_data['main_group']
                        profile.main_group.clear()
                        instance.groups.clear()
                        for group in groups:
                            profile.main_group.add(group)
                            all_group = Group.objects.filter(maingroups=group)
                            for gr in all_group:
                                instance.groups.add(gr)
                    elif item == 'contact_info':
                        contact_info = profile_data['contact_info']
                        contact_ids = list(contact_info.values_list('pk', flat=True))
                        profile.contact_info = contact_ids
                    else:
                        setattr(profile, item, profile_data[item])
                profile.save()
            else:
                setattr(instance, attr, value)
        instance.save()

        author = self.context['request'].user
        save_history.s(user_id=author.id,
                       module='User',
                       action_type='edit',
                       content_obj=instance,
                       old_obj=old_instance,
                       serializer=UserSerializer,
                       new_obj=instance,
                       ).apply_async(serializer='pickle')
        return instance

    def get_agent_group(self, instance):
        instance: User
        if hasattr(instance.userprofile, 'agent_group'):
            return [{'id': group.pk, 'name_ukr': group.name_ukr} for group in instance.userprofile.agent_group.all()]
        return None


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Permission.objects.filter(
            Q(content_type__app_label='auth') |
            ~Q(name__startswith='Can')
        ),
        many=True,
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


class MainGroupSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Group.objects.all(),
        many=True,
    )

    class Meta:
        model = MainGroups
        fields = '__all__'


class UserFullInfoSerializer(serializers.ModelSerializer):
    userprofile = forModelSerialize.UserProfileSerializator(queryset=UserProfile.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'userprofile')


class VersionSerializer(serializers.ModelSerializer):
    full_version = serializers.ReadOnlyField(source='get_full_version')

    class Meta:
        model = Version
        fields = ('date', 'version', 'v_backend', 'v_frontend', 'full_version')


class BranchRestrictionForPermSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        return {
            'permission': instance.perm.codename.replace('sailor.', '').replace('auth.', ''),
            'branch_office': instance.branch_office.values_list('pk', flat=True) \
                if not self.root.context['request'].user.is_superuser else list(
                BranchOffice.objects.all().exclude(id__in=[2]).values_list('pk', flat=True))
        }

    class Meta:
        model = BranchOfficeRestrictionForPermission
        fields = ('id', 'perm', 'user', 'branch_office')


class PersonalAgentUserProfSerializer(UserProfileSerializer):
    contact_info = ContactSerializator(queryset=ContactInfo.objects.all(), required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ('middle_name', 'contact_info', 'photo')


class AgentByGroupSerializer(serializers.ModelSerializer):
    agents = serializers.SerializerMethodField(read_only=True, method_name='get_agents_by_group')

    class Meta:
        model = AgentGroup
        fields = ('id', 'name_ukr', 'agents')

    def get_agents_by_group(self, instance):
        instance: AgentGroup
        if hasattr(instance, 'userprofile_set'):
            user_ids = list(instance.userprofile_set.values_list('user_id', flat=True))
            return UserSerializer(User.objects.filter(id__in=user_ids), many=True).data
        return []


class IsTrainedSerializer(serializers.Serializer):
    """
    Used to update user training information on working with AS
    """
    is_trained = serializers.BooleanField()
