from copy import deepcopy

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from communication.models import SailorKeys
from directory.models import StatusDocument
from sailor import forModelSerializer as custom_serializer
from sailor.tasks import save_history
from sms_auth import forModelSerializer
from .misc import create_user_for_personal_cabinet
from .models import UserStatementVerification, PhotoDocumentForVerification


class UserStatementVerificationSerializer(serializers.ModelSerializer):
    """Заявка на верификацию пользователя для регистрации в ЛК"""

    photo = forModelSerializer.PhotoSerializer(queryset=PhotoDocumentForVerification.objects.all())
    status_document = custom_serializer.StatusDocumentSerializer(queryset=StatusDocument.objects.all(),
                                                                 allow_null=True, required=False)
    sailor_id = serializers.IntegerField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S', required=False, read_only=True)
    service = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='e-sailor')

    class Meta:
        model = UserStatementVerification
        fields = ('id', 'sailor_id', 'phone', 'created_at', 'inn', 'passport', 'status_document', 'photo', 'email',
                  'last_name', 'first_name', 'middle_name', 'birthday', 'service')
        read_only_fields = ('created_at',)

    def update(self, instance, validated_data):
        old_instance = deepcopy(instance)
        status_statement = validated_data.get('status_document')
        if status_statement and status_statement.pk == 36:
            instance.status_document = status_statement
            instance.save()
            return instance
        sailor_id = validated_data.get('sailor_id')
        try:
            SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        if sailor_id and not instance.sailor_id:
            instance.sailor_id = sailor_id
        user = self.context['request'].user
        if status_statement:
            if status_statement.id == 41 and instance.sailor_id is None and sailor_id is None:
                raise ValidationError({'error': 'Сannot change status sailor_id not defined'})
            instance.status_document = status_statement
        instance.save()
        if (instance.status_document.id == 41) and instance.sailor_id:  # Схвалено
            create_user_for_personal_cabinet(statement=instance, user_ver=user.pk)

        save_history.s(user_id=user.id,
                       module='UserStatementVerification',
                       action_type='edit',
                       content_obj=instance,
                       old_obj=old_instance,
                       serializer=UserStatementVerificationSerializer,
                       new_obj=instance,
                       ).apply_async(serializer='pickle')
        return instance


class UserRegistrationSerializer(serializers.Serializer):
    """Регистрация моряка непосредственно из сервиса"""

    phone = serializers.CharField(max_length=30)
    security_code = serializers.IntegerField(required=False, allow_null=True)
    sailor_id = serializers.IntegerField()


class SMSLoginSerializer(serializers.Serializer):
    """Аутентификация пользователя"""

    phone = serializers.CharField(max_length=30)
    security_code = serializers.IntegerField(required=False, allow_null=True)
    is_morrichservice = serializers.BooleanField(default=False)
