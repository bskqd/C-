from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

import personal_cabinet.serializers
import sailor.serializers
from communication.models import SailorKeys
from itcs import magic_numbers
from sailor.models import (PhotoProfile, Profile)
from sailor.statement.models import StatementSQC, StatementServiceRecord, StatementQualification
from sailor.statement.serializers import StatementDKKSerializer
from training.models import AvailableExamsToday

User = get_user_model()


class MRSPersonalProfileMainInfoSerializer(sailor.serializers.ProfileMainInfoSerializer):
    sailor_key = serializers.SerializerMethodField()
    photo = personal_cabinet.serializers.PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(),
                                                                 allow_null=True, required=False)
    is_main_phone = serializers.SerializerMethodField()

    def get_sailor_key(self, *args, **kwargs):
        return self.sailor_key_val

    def get_is_main_phone(self, *args, **kwargs):
        sailor = SailorKeys.objects.get(id=self.sailor_key_val)
        user = User.objects.get(id=sailor.user_id)
        return user.username.startswith('+')

    class Meta:
        fields = ('first_name_ukr', 'first_name_eng', 'last_name_ukr', 'last_name_eng', 'middle_name_ukr',
                  'middle_name_eng', 'sex', 'contact_info', 'position', 'rank', 'date_birth', 'photo', 'passport',
                  'created_by', 'is_dkk', 'sailor_key', 'is_main_phone')
        model = Profile


class MRSPersonalServiceRecordSailorSerializer(personal_cabinet.serializers.BasePersonalServiceRecordSailorSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        lines = instance.lines.exclude(status_line_id__in=(magic_numbers.STATUS_REMOVED_DOCUMENT,
                                                           magic_numbers.STATUS_CREATED_BY_AGENT,
                                                           magic_numbers.CREATED_FROM_PERSONAL_CABINET))
        response['lines'] = personal_cabinet.serializers.PersonalLineInServiceRecordSerializer(lines, many=True).data
        return response


class MRSPersonalSailorStatementDKKSerialize(personal_cabinet.serializers.PersonalSailorStatementDKKSerialize):
    photo = personal_cabinet.serializers.PersonalPhotoSerializer(queryset=PhotoProfile.objects.all(),
                                                                 allow_null=True, required=False)
    status_sqc = serializers.ReadOnlyField(source='get_status_position', read_only=True)
    date_create = serializers.DateTimeField(format='%m-%d-%Y', read_only=True, source='created_at')
    payment_info = serializers.SerializerMethodField()
    payment_price = serializers.SerializerMethodField()
    can_create_exam = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StatementSQC
        fields = ('id', 'sailor', 'is_payed', 'status_sqc',
                  'number', 'status_document', 'rank', 'list_positions', 'rank', 'date_create', 'photo',
                  'payment_info', 'payment_price', 'can_create_exam')

    def get_payment_info(self, instance):
        return '''Отримувач: Державне підприємство "Моррічсервіс" у
м. Києві, пр. Правди, 35, 04108;
Код ЄДРПОУ 42615235;
IBAN: UA473204780000026008924857203;
Сума до сплати: 270,00 грн.
Призначення платежу: за організаційно-технічні послуги з ПДВ.'''

    def get_payment_price(self, instance):
        return 270.0


class MRSStatementServiceRecord(sailor.statement.serializers.StatementServiceRecordSerializer):
    payment_info = serializers.SerializerMethodField()
    payment_price = serializers.SerializerMethodField()
    recipient = serializers.ReadOnlyField(source='get_sailor_ukr')

    class Meta:
        model = StatementServiceRecord
        fields = ('id', 'status', 'sailor', 'is_payed', 'date_created',
                  'date_modified', 'delivery', 'recipient', 'photo',
                  'payment_info', 'payment_price')

    def get_payment_info(self, instance):
        return '''Отримувач: Державне підприємство "Моррічсервіс" у
м. Києві, пр. Правди, 35, 04108;
Код ЄДРПОУ 42615235;
IBAN: UA473204780000026008924857203;
Призначення платежу: за організаційно-технічні послуги з ПДВ.'''

    def get_payment_price(self, instance):
        return 270.0


class MRSStatementQualificationDocumentSerializer(
    personal_cabinet.serializers.PersonalStatementQualificationDocumentSerializer):
    payment_info = serializers.SerializerMethodField()
    payment_price = serializers.SerializerMethodField()

    class Meta:
        model = StatementQualification
        fields = ('id', 'status_dkk', 'number', 'status_document', 'protocol_dkk',
                  'port', 'type_document', 'rank', 'list_positions', 'is_payed', 'date_create', 'photo',
                  'payment_info', 'payment_price')
        read_only = ('photo',)

    def get_payment_info(self, instance):
        statement: StatementQualification = instance
        if not statement.is_continue and statement.rank.type_document_id == 49:
            return '''Отримувач: Державне підприємство "Моррічсервіс" у м. Києві, пр. Правди, 35, 04108;
    Код ЄДРПОУ 42615235;
    IBAN: UA473204780000026008924857203;
    Сума до сплати: 540,00 грн.
    Призначення платежу: за організаційно-технічні послуги з ПДВ;
    оформлення дипломів та підтверджень особам командного
    складу морських суден
    '''
        elif statement.is_continue and statement.rank.type_document_id == 49:
            return '''Отримувач: Державне підприємство "Моррічсервіс" у
    м. Києві, пр. Правди, 35, 04108;
    Код ЄДРПОУ 42615235;
    IBAN: UA473204780000026008924857203;
    Призначення платежу: за організаційно-технічні послуги з ПДВ;
    підтвердження до дипломів особам командного складу морських
    суден'''
        elif not statement.is_continue and statement.rank.direction_id == 4:
            return '''Отримувач: Державне підприємство "Моррічсервіс" у
    м. Києві, пр. Правди, 35, 04108;
    Код ЄДРПОУ 42615235;
    IBAN: UA473204780000026008924857203;
    Призначення платежу: за організаційно-технічні послуги з ПДВ;
    отримання дипломів та підтверджень Радіоспеціалістів'''
        elif statement.is_continue and statement.rank.direction_id == 4:
            return '''Отримувач: Державне підприємство "Моррічсервіс" у
    м. Києві, пр. Правди, 35, 04108;
    Код ЄДРПОУ 42615235;
    IBAN: UA473204780000026008924857203;
    Сума до сплати: 540,00 грн.
    Призначення платежу: організаційно-технічні послуги з ПДВ;
    Підтвердження дипломів Радіоспеціалістів'''
        elif statement.type_document_id == 87:
            return '''Отримувач: Державне підприємство "Моррічсервіс" у
            м. Києві, пр. Правди, 35, 04108;
            Код ЄДРПОУ 42615235;
            IBAN: UA473204780000026008924857203;
            Сума до сплати:540,00грн.
            Призначення платежу: за організаційно-технічні послуги з ПДВ; 
            Отримання Свідоцтва фахівця'''
        return ''

    def get_payment_price(self, instance):
        return 540.0
