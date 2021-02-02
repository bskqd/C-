from rest_framework import serializers

import authorization.mail.utils
import core.serializers
import directory.serializers
from authorization.mail.models import UserInvitation
from core.models import User


class InvitationSerializer(serializers.ModelSerializer):
    created_user = core.serializers.UserSerializer(allow_null=True, read_only=True)

    class Meta:
        model = UserInvitation
        fields = ('created_user', 'accepted', 'email', 'sent', 'created_at', 'agency')
        read_only_fields = ('created_user', 'accepted', 'sent', 'created_at')
        extra_kwargs = {'agency': {'required': False, 'write_only': True}}

    def create(self, validated_data):
        user = self.context['request'].user
        email = validated_data['email']
        if user.type_user in [User.HEAD_AGENCY_CH, User.AGENT_CH]:
            invite = authorization.mail.utils.create_invite_for_agent(inviter=user, email=email,
                                                                      agency=user.get_agency)
        elif user.type_user == User.ADMIN_CH:
            agency = validated_data.get('agency')
            invite = authorization.mail.utils.create_invite_for_agent(inviter=user, email=email, agency=agency)
        return invite


class UserAgentMailSerializer(serializers.ModelSerializer):
    agent = core.serializers.AgentSerializer()
    contacts = directory.serializers.ContactsSerializer(write_only=True, required=False, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name', 'password', 'agent', 'contacts')
        extra_kwargs = {'password': {'write_only': True}}
