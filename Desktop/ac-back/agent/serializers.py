import base64
from copy import deepcopy

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from agent.forModelSerializer import SailorKeySerializer
from agent.models import StatementAgent, StatementAgentSailor, AgentSailor, AgentGroup, CodeToStatementAgentSailor
from communication.models import SailorKeys
from directory.models import StatusDocument, City, TypeContact
from itcs import magic_numbers
from reports.serializers import ProfileSailorSerializer
from sailor.forModelSerializer import ContactSerializator, StatusDocumentSerializer, PhotoSerializer
from sailor.models import ContactInfo, PhotoProfile
from sailor.tasks import save_history
from user_profile.models import UserProfile
from user_profile.serializer import UserSerializer, UserProfileSerializer, UserFullInfoSerializer

User = get_user_model()


class AgentUserProfileSerializer(UserProfileSerializer):
    photo = serializers.ReadOnlyField(source='short_photo_url')

    class Meta:
        model = UserProfile
        fields = ('middle_name', 'city', 'additional_data', 'photo')


class AgentSailorSerializer(serializers.ModelSerializer):
    agent = UserFullInfoSerializer()
    date_create = serializers.DateTimeField(source='created_at')
    date_modified = serializers.DateTimeField(source='modified_at')

    class Meta:
        model = AgentSailor
        fields = ('id', 'sailor_key', 'agent', 'is_disable', 'date_create', 'date_modified', 'date_end_proxy')


class AgentUserSerializer(UserSerializer):
    apply_url = serializers.SerializerMethodField()
    info_url = serializers.SerializerMethodField()
    statement_url = serializers.SerializerMethodField()
    userprofile = AgentUserProfileSerializer()

    def get_apply_url(self, obj):  # TODO убрать когда уберут в моб версии
        key = base64.b64decode(settings.CRYPTO_KEY)
        fernet_alg = Fernet(key)
        agent_pk_enc = fernet_alg.encrypt(str(obj.pk).encode()).decode()
        url_to_apply = f'seaman/qr_code/{agent_pk_enc}/statement/'
        return url_to_apply

    def get_statement_url(self, obj):
        key = base64.b64decode(settings.CRYPTO_KEY)
        fernet_alg = Fernet(key)
        agent_pk_enc = fernet_alg.encrypt(str(obj.pk).encode()).decode()
        url_to_apply = f'seaman/qr_code/{agent_pk_enc}/statement/'
        return url_to_apply

    def get_info_url(self, obj):
        key = base64.b64decode(settings.CRYPTO_KEY)
        fernet_alg = Fernet(key)
        agent_pk_enc = fernet_alg.encrypt(str(obj.pk).encode()).decode()
        url_to_apply = f'seaman/qr_code/{agent_pk_enc}/info/'
        return url_to_apply

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'userprofile',
                  'apply_url', 'info_url', 'statement_url')


class AgentContactInfoSerializer(ContactSerializator):

    def to_internal_value(self, data):
        response = []
        from sailor.models import ContactInfo
        if not data:
            return ContactInfo.objects.none()
        if type(data) is not list:
            raise serializers.ValidationError('Data error')
        else:
            for val in data:
                try:
                    contact_type = val['type_contact']
                    value = val['value']
                except KeyError:
                    raise serializers.ValidationError('Incorect dictinary')
                try:
                    contact_type = TypeContact.objects.get(value=contact_type)
                except TypeContact.DoesNotExist:
                    contact_type = TypeContact.objects.create(value=contact_type)
                try:
                    contact_info = ContactInfo.objects.filter(value=value, type_contact=contact_type).first()
                    if contact_info:
                        response.append(contact_info.id)
                    else:
                        contact = ContactInfo.objects.create(value=value, type_contact=contact_type)
                        response.append(contact.id)
                except KeyError:
                    raise serializers.ValidationError('id is requid field')
                except (ValueError, TypeError):
                    raise serializers.ValidationError('id must be a integer field')
            return response


class StatementAgentSerializer(serializers.ModelSerializer):
    contact_info = AgentContactInfoSerializer(queryset=ContactInfo.objects.all(), required=False, allow_null=True,
                                              default=[])
    status_document = StatusDocumentSerializer(queryset=StatusDocument.objects.all(), required=False)
    city = serializers.SlugRelatedField(slug_field='value', queryset=City.objects.all())
    photo = PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    date_create = serializers.ReadOnlyField(source='created_at')
    date_modified = serializers.ReadOnlyField(source='modified_at')

    class Meta:
        model = StatementAgent
        fields = ('id', 'last_name', 'first_name', 'middle_name', 'date_create', 'contact_info', 'date_modified',
                  'photo', 'status_document', 'city', 'group', 'tax_number', 'serial_passport')
        read_only_fields = ('photo',)

    def validate_contact_info(self, data):
        if data:
            email = ContactInfo.objects.filter(id__in=data, type_contact_id=2)
            if email.exists():
                username = email.first().value.split('@')[0]
                users = User.objects.filter(username=username)
                if users.exists():
                    raise ValidationError('email is used')
                statement = StatementAgent.objects.filter(
                    contact_info__overlap=[email.first().id],
                    status_document_id=magic_numbers.status_statement_agent_in_process)
                if statement.exists():
                    raise ValidationError('email is used')
            else:
                return data
        return data

    def update(self, instance, validated_data):
        from agent.tasks import send_agent_email
        from agent.utils import create_user_agent
        old_instance = deepcopy(instance)
        status_document = validated_data.get('status_document')
        group = validated_data.pop('group', None)
        if not group:
            group = AgentGroup.objects.get(id=1)
        user = self.context['request'].user
        user_create = True
        if status_document and status_document.id == magic_numbers.status_statement_agent_valid:
            user_create = create_user_agent(instance, user.id, group)
        if status_document and status_document.id == magic_numbers.status_statement_agent_invalid:
            email = ContactInfo.objects.filter(id__in=instance.contact_info, type_contact_id=2).first()
            send_agent_email.s(email=email.value, approved=False).apply_async()
        if user_create is not True:
            raise ValidationError(user_create)
        contacts = validated_data.pop('contact_info', None)
        if contacts:
            all_contact_ids = instance.contact_info + contacts
            all_contacts = ContactInfo.objects.filter(id__in=all_contact_ids)
            new_contact_type = list(all_contacts.filter(id__in=contacts).values_list('type_contact_id', flat=True))
            old_contact = list(all_contacts.filter(id__in=instance.contact_info, type_contact_id__in=new_contact_type).
                               values_list('id', flat=True))
            new_contact = list(set(instance.contact_info) - set(old_contact)) + contacts
            instance.contact_info = new_contact
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        new_instance = deepcopy(instance)
        user = self.context['request'].user
        save_history.s(user_id=user.id,
                       module='StatementAgent',
                       action_type='edit',
                       content_obj=instance,
                       serializer=StatementAgentSerializer,
                       new_obj=new_instance,
                       old_obj=old_instance,
                       ).apply_async(serializer='pickle')
        return instance

    def to_representation(self, instance):
        response = super(StatementAgentSerializer, self).to_representation(instance)
        response['group'] = AgentGroupsSerializer(instance=instance.group).data
        return response


class StatementAgentSailorSerializer(serializers.ModelSerializer):
    status_document = StatusDocumentSerializer(queryset=StatusDocument.objects.all(), required=False)
    sailor_key = SailorKeySerializer(queryset=SailorKeys.objects.all(), required=False)
    photo = PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    date_modified = serializers.ReadOnlyField(source='modified_at')
    date_create = serializers.ReadOnlyField(source='created_at')

    class Meta:
        model = StatementAgentSailor
        fields = ('id', 'date_create', 'date_modified', 'agent', 'sailor_key', 'status_document', 'photo',
                  'date_end_proxy')
        read_only_fields = ('photo',)

    def update(self, instance: StatementAgentSailor, validated_data: dict):
        if instance.status_document == magic_numbers.status_statement_agent_sailor_invalid:
            raise ValidationError('statement is not active')
        old_instance = deepcopy(instance)
        status_document = validated_data.get('status_document')
        is_agent = validated_data.get('is_agent', False)
        user = self.context['request'].user
        date_end_proxy = validated_data.get('date_end_proxy')
        if instance.date_end_proxy != date_end_proxy:
            instance.date_end_proxy = date_end_proxy
            try:
                agent_sailor = AgentSailor.objects.get(sailor_key=instance.sailor_key,
                                                       agent=user)
                agent_sailor.date_end_proxy = date_end_proxy
                agent_sailor.save(update_fields=['date_end_proxy'])
            except AgentSailor.DoesNotExist:
                pass
        if (not user.is_superuser and
                user.userprofile.type_user != user.userprofile.SECRETARY_SERVICE and
                instance.agent_id != user.id):
            raise ValidationError('statement does not apply to agent')
        if is_agent and status_document and status_document.pk == magic_numbers.STATUS_CREATED_BY_AGENT and \
                not instance.photo:
            raise ValidationError('need to upload a photo of documents')
        if status_document:
            instance.status_document_id = status_document.id
        instance.save()
        save_history.s(user_id=user.id, module='StatementAgentSailor', action_type='edit',
                       content_obj=instance, serializer=StatementAgentSailorSerializer, new_obj=instance,
                       old_obj=old_instance, sailor_key_id=instance.sailor_key).apply_async(serializer='pickle')

        return instance

    def to_representation(self, instance):
        response = super(StatementAgentSailorSerializer, self).to_representation(instance)
        response['agent'] = UserSerializer(instance=instance.agent).data
        return response


class AgentGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentGroup
        fields = ('id', 'name_ukr',)


class StatementAgentSailorPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()
    security_code = serializers.IntegerField(required=False)


class AwaitingCretaeStatementAgentSailorSerializer(serializers.ModelSerializer):
    date_create = serializers.DateTimeField(source='created_at')
    class Meta:
        model = CodeToStatementAgentSailor
        fields = ('phone', 'date_create')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sailor'] = ProfileSailorSerializer(queryset=SailorKeys.objects.all()
                                                     ).to_representation(instance.sailor_key)
        return response
