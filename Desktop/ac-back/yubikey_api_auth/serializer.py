from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from directory.models import BranchOffice, City
from user_profile.models import UserProfile
from yubikey_api_auth.models import AuthorizationLog

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    group_permissions = serializers.IntegerField(write_only=True)
    branch_office = serializers.PrimaryKeyRelatedField(queryset=BranchOffice.objects.all(), write_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), write_only=True)
    middle_name = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = UserModel.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        profile = UserProfile.objects.create(user=user, branch_office=validated_data['branch_office'],
                                             city=validated_data['city'],
                                             middle_name=validated_data['middle_name'], language='UA')
        profile.main_group.add(validated_data['group_permissions'])
        profile.save()
        return user

    class Meta:
        model = UserModel
        ref_name = 'YubiUserSerializer'
        # Tuple of serialized model fields (see link [2])
        fields = ("id", "username", "password", 'first_name', 'last_name', 'group_permissions',
                  'branch_office', 'city', 'middle_name')


class CheckPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all())


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_old_password(self, value):
        old_password = value
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise ValidationError('Old password does not correct')
        return value


class AuthorizationLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthorizationLog
        fields = '__all__'
        read_only_fields = ('user', )