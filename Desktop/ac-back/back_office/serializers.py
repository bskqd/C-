from copy import deepcopy
from datetime import date, timedelta, datetime

import workdays
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

import back_office.utils
from agent.models import AgentGroup
from back_office.tasks import create_statements
from certificates.models import TimeForCourse
from communication.models import SailorKeys
from directory.models import BranchOffice, TypeOfAccrualRules, LevelQualification, Position
from directory.serializers import BranchOfficeSerializer, CourseForNTZSerializer, PositionSerializer, \
    TypeOfAccrualRulesSerializer
from itcs import magic_numbers
from itcs.magic_numbers import AccrualTypes
from sailor import forModelSerializer as customSerializers
from sailor.document.models import CertificateETI
from sailor.misc import check_is_continue, CheckSailorForPositionDKK as CSP
from sailor.models import PhotoProfile, DependencyDocuments
from sailor.statement.models import (StatementETI, StatementSailorPassport, StatementMedicalCertificate,
                                     StatementAdvancedTraining)
from sailor.tasks import save_history
from user_profile.models import UserProfile
from .models import (CoursePrice, DependencyItem, ETICoefficient, ETIProfitPart, PacketItem,
                     PriceForPosition, ETIMonthRatio)

User = get_user_model()


class ETICoefficientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETICoefficient
        fields = '__all__'

    def validate(self, data):
        today = date.today()
        date_start = data['date_start']
        if date_start <= today:
            raise serializers.ValidationError('Date start is early')
        return data

    def update(self, instance, validated_data):
        if instance.date_end:
            raise ValidationError({'error': 'cannot update record'})
        today = date.today()
        if instance.date_start <= today:
            raise ValidationError({'error': 'Coefficient used - use creat'})
        date_end = instance.date_start - timedelta(days=1)
        new_date_end = validated_data['date_start'] - timedelta(days=1)
        user = self.context['request'].user
        try:
            current_coeff = ETICoefficient.objects.get(date_end=date_end)
            old_current_coeff = deepcopy(current_coeff)
            current_coeff.date_end = new_date_end
            current_coeff.save(update_fields=['date_end'])
            save_history.s(user_id=user.id, module='ETICoefficient', action_type='edit',
                           content_obj=current_coeff, old_obj=old_current_coeff,
                           serializer=ETICoefficientSerializer, new_obj=current_coeff).apply_async(serializer='pickle')
        except ETICoefficient.DoesNotExist:
            pass
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        save_history.s(user_id=user.id, module='ETICoefficient', action_type='edit',
                       content_obj=instance, old_obj=old_instance,
                       serializer=ETICoefficientSerializer, new_obj=instance).apply_async(serializer='pickle')
        return instance


class PriceForPositionSerializer(serializers.ModelSerializer):
    sum_to_distribution = serializers.ReadOnlyField()
    profit = serializers.ReadOnlyField()
    is_actual_value = serializers.ReadOnlyField()

    class Meta:
        model = PriceForPosition
        fields = '__all__'
        read_only_fields = ('currency', 'date_end')

    def to_representation(self, instance):
        response = super(PriceForPositionSerializer, self).to_representation(instance)
        response['type_document'] = TypeOfAccrualRulesSerializer(instance.type_document).data
        return response

    def validate(self, attrs):
        today = date.today()
        if attrs['date_start'] <= today:
            raise ValidationError('Minimum date can be tomorrow')
        return super(PriceForPositionSerializer, self).validate(attrs)

    def update(self, instance, validated_data):
        if instance.date_end:
            raise ValidationError({'error': 'cannot update record'})
        today = date.today()
        if instance.date_start <= today:
            raise ValidationError({'error': 'Price used - use creat'})
        date_end = instance.date_start - timedelta(days=1)
        new_date_end = validated_data['date_start'] - timedelta(days=1)
        user = self.context['request'].user
        try:
            current_price = PriceForPosition.objects.get(date_end=date_end, type_of_form=instance.type_of_form,
                                                         type_document=instance.type_document)
            old_current_price = deepcopy(current_price)
            current_price.date_end = new_date_end
            current_price.save(update_fields=['date_end'])
            save_history.s(user_id=user.id, module='PriceForPosition', action_type='edit',
                           content_obj=current_price, old_obj=old_current_price,
                           serializer=PriceForPositionSerializer,
                           new_obj=current_price).apply_async(serializer='pickle')
        except PriceForPosition.DoesNotExist:
            pass
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        save_history.s(user_id=user.id, module='PriceForPosition', action_type='edit',
                       content_obj=instance, old_obj=old_instance,
                       serializer=PriceForPositionSerializer,
                       new_obj=instance).apply_async(serializer='pickle')
        return instance


class CoursePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePrice
        fields = '__all__'
        read_only_fields = ('currency',)

    def to_representation(self, instance):
        response = super(CoursePriceSerializer, self).to_representation(instance)
        response['course'] = CourseForNTZSerializer(instance=instance.course).data
        return response

    def validate(self, attrs):
        today = date.today()
        if attrs['date_start'] <= today:
            raise ValidationError('Minimum date can be tomorrow')
        return super(CoursePriceSerializer, self).validate(attrs)

    def update(self, instance, validated_data):
        if instance.date_end:
            raise ValidationError({'error': 'cannot update record'})
        today = date.today()
        if instance.date_start <= today:
            raise ValidationError({'error': 'Price used - use create'})
        date_end = instance.date_start - timedelta(days=1)
        new_date_end = validated_data['date_start'] - timedelta(days=1)
        user = self.context['request'].user
        try:
            current_price = CoursePrice.objects.get(date_end=date_end, type_of_form=instance.type_of_form,
                                                    course=instance.course)
            old_current_price = deepcopy(current_price)
            current_price.date_end = new_date_end
            current_price.save(update_fields=['date_end'])
            save_history.s(user_id=user.id, module='CoursePrice', action_type='edit',
                           content_obj=current_price, old_obj=old_current_price,
                           serializer=CoursePriceSerializer,
                           new_obj=current_price).apply_async(serializer='pickle')
        except CoursePrice.DoesNotExist:
            pass
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        save_history.s(user_id=user.id, module='PriceForPosition', action_type='edit',
                       content_obj=instance, old_obj=old_instance,
                       serializer=CoursePriceSerializer,
                       new_obj=instance).apply_async(serializer='pickle')
        return instance


class ETIProfitPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETIProfitPart
        fields = '__all__'
        read_only_fields = ('date_end',)

    def update(self, instance, validated_data):
        if instance.date_end:
            raise ValidationError({'error': 'cannot update record'})
        today = date.today()
        if instance.date_start <= today:
            raise ValidationError({'error': 'Coefficient used - use creat'})
        date_end = instance.date_start - timedelta(days=1)
        new_date_end = validated_data['date_start'] - timedelta(days=1)
        user = self.context['request'].user
        try:
            current_coeff = ETIProfitPart.objects.get(date_end=date_end)
            old_current_coeff = deepcopy(current_coeff)
            current_coeff.date_end = new_date_end
            current_coeff.save(update_fields=['date_end'])
            save_history.s(user_id=user.id,
                           module='ETIProfitPart',
                           action_type='edit',
                           content_obj=current_coeff,
                           old_obj=old_current_coeff,
                           serializer=ETIProfitPartSerializer,
                           new_obj=current_coeff,
                           ).apply_async(serializer='pickle')
        except ETIProfitPart.DoesNotExist:
            pass
        old_instance = deepcopy(instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        save_history.s(user_id=user.id,
                       module='ETIProfitPart',
                       action_type='edit',
                       content_obj=instance,
                       old_obj=old_instance,
                       serializer=ETIProfitPartSerializer,
                       new_obj=instance,
                       ).apply_async(serializer='pickle')
        return instance


class DependencyItemSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()  # form 1
    status = serializers.ReadOnlyField()
    date_meeting = serializers.SerializerMethodField()
    payment_info = serializers.ReadOnlyField(source='information_for_payment')
    document_object = serializers.DictField(write_only=True)
    payment_url = serializers.ReadOnlyField()

    class Meta:
        model = DependencyItem
        fields = ('id', 'type_document_name', 'get_info_for_statement', 'price',
                  'status', 'date_meeting', 'payment_info', 'content_type', 'document_object', 'payment_url')
        read_only_fields = ('id', 'type_document_name', 'get_info_for_statement', 'price', 'status', 'date_meeting',
                            'payment_info')

    def get_price(self, instance):
        """
        Get price Form 1
        :param instance:
        :return:
        """
        if not hasattr(self.root.instance, '_full_price_form1'):
            self.root.instance._full_price_form1 = 0
        price_form_1 = instance.get_price_form1
        self.root.instance._full_price_form1 += price_form_1
        return price_form_1

    def get_date_meeting(self, instance):
        instance: DependencyItem
        if instance.content_type_id != 76 and instance.content_type_id is not None:
            return None
        sailor_id = instance.packet_item.sailor_id
        if not hasattr(self, 'sailor_key'):
            self.sailor_key = SailorKeys.objects.get(id=sailor_id)
        if not hasattr(self, 'last_date'):
            today = date.today()
            packet_after_today = PacketItem.by_sailor.filter_by_sailor(
                sailor_key=sailor_id, date_end_meeting__gt=today
            ).exclude(id=instance.packet_item_id)
            if packet_after_today.exists() and not instance.packet_item.date_end_meeting:
                date_start = packet_after_today.order_by('date_end_meeting').last().date_end_meeting
            elif instance.packet_item.date_end_meeting and instance.packet_item.date_start_meeting:
                date_start = instance.packet_item.date_start_meeting
            else:
                date_start = today
            tomorrow = date_start + timedelta(days=1)
            self.last_date = tomorrow
            if self.last_date.isoweekday() in [6, 7]:
                self.last_date += timedelta(days=8 - self.last_date.isoweekday())
            instance.packet_item.date_start_meeting = self.last_date - timedelta(days=1)
            instance.packet_item.save(update_fields=['date_start_meeting'])
        date_end_meeting = self.last_date
        if instance.type_document_id in AccrualTypes.LIST_CERTIFICATE:
            course_id = instance.item.key_document[0]
            if hasattr(self, 'certificates') is False:
                self.certificates = CertificateETI.objects.filter(
                    id__in=self.sailor_key.sertificate_ntz)
            is_continue = self.certificates.filter(
                course_training_id=course_id,
                status_document_id__in=[2, 19, 7]).exists()
            default_time = 8 * 10
            try:
                time = TimeForCourse.objects.get(is_continue=is_continue, course_id=course_id).full_time
            except TimeForCourse.DoesNotExist:
                try:
                    time = TimeForCourse.objects.get(is_continue=False, course_id=course_id).full_time
                except TimeForCourse.DoesNotExist:
                    time = default_time
            days = back_office.utils.hours_to_date(time, working_day=12)
            date_end_meeting = workdays.workday(self.last_date, days)
            # date_end_meeting = workdays.workday(self.last_date, days + 1)
        elif instance.type_document_id in (AccrualTypes.LIST_SAILOR_PASSPORT +
                                           AccrualTypes.LIST_MEDICAL +
                                           AccrualTypes.LIST_SQC +
                                           AccrualTypes.LIST_QUALIFICATION):
            pass
            # days = hours_to_date(8)
            # date_end_meeting = workdays.workday(self.last_date, days)
            # date_end_meeting = workdays.workday(self.last_date, days + 1)
        elif instance.type_document_id in AccrualTypes.LIST_ADVANCED_TRAINING:
            qualification = LevelQualification.objects.get(
                id=instance.item.key_document[0].get('qualitification')
            )
            date_end_meeting = workdays.workday(self.last_date, qualification.course_time_hours)
            # date_end_meeting = workdays.workday(self.last_date, qualification.course_time_hours)
        response = {'date_start_meeting': self.last_date.strftime('%d.%m.%Y'),
                    'date_end_meeting': date_end_meeting.strftime('%d.%m.%Y')}
        self.last_date = date_end_meeting + timedelta(days=1)
        if not instance.packet_item.date_end_meeting or instance.packet_item.date_end_meeting < self.last_date:
            instance.packet_item.date_end_meeting = self.last_date + timedelta(days=1)
            instance.packet_item.save(update_fields=['date_end_meeting'])
        return response


class PacketSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField(source='current_form1_price')
    agent = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(), read_only=True)
    dependencies = serializers.ListField(required=False, allow_null=True, allow_empty=True,
                                         child=serializers.DictField(), write_only=True)
    include_sailor_passport = serializers.ChoiceField(choices=(
        (0, 'Не потрібна'),
        (1, 'Потрібна, за 20 днів'),
        (2, 'Потрібна за 7 днів'),
        (3, 'Подовження за 20 днів'),
        (4, 'Подовження за 7 днів'),
    ), required=False)
    full_price = serializers.SerializerMethodField()  # form 1
    position_type = serializers.SerializerMethodField()
    rank = serializers.ReadOnlyField()
    full_number = serializers.SerializerMethodField()
    photo = customSerializers.PhotoSerializer(queryset=PhotoProfile.objects.all(), required=False, allow_null=True)
    is_only_proof = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = PacketItem
        exclude = ('full_price_form1', 'full_price_form2', 'number')
        read_only_fields = ('payment_date', 'position_type', 'price',
                            'rank')
        extra_kwargs = {'position': {'required': False}}

    def get_full_number(self, instance):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and hasattr(user, 'userprofile') and user.userprofile.type_user == user.userprofile.MARAD:
            return instance.number
        return instance.full_number

    def to_representation(self, instance):
        response = super(PacketSerializer, self).to_representation(instance)
        dependencies = {
            'documents_and_statement':
                DependencyItemSerializer(instance.dependencies.all().exclude(
                    Q(type_document_id__in=(AccrualTypes.LIST_AGENT +
                                            AccrualTypes.LIST_SERVICE_CENTER +
                                            AccrualTypes.LIST_MORRICHSERVICE)) |
                    Q(content_type_id=76) |
                    Q(content_type=None)
                ), many=True).data,
            'missing': DependencyItemSerializer(
                instance.dependencies.exclude(
                    type_document_id=AccrualTypes.MORRICHSERVICE
                ).filter(
                    Q(content_type_id__in=[76]) | Q(content_type=None)
                ), many=True).data,
            'agent_and_service': DependencyItemSerializer(
                instance.dependencies.filter(
                    type_document_id__in=(AccrualTypes.LIST_AGENT +
                                          AccrualTypes.LIST_SERVICE_CENTER +
                                          AccrualTypes.LIST_AGENT)
                ), many=True).data

        }
        response['dependencies'] = dependencies
        response['position'] = PositionSerializer(instance.position.all(), many=True).data
        response['service_center'] = BranchOfficeSerializer(instance.service_center).data
        return response

    def get_full_price(self, instance):
        if hasattr(self.instance, '_full_price_form1'):
            return self.instance._full_price_form1
        else:
            return instance.current_form1_price

    def get_position_type(self, instance):
        return instance.get_position_type_display()

    @staticmethod
    def has_dependency_in_another_document(dependency: DependencyDocuments, actual_dependency_item):
        if dependency.type_document == 'NTZ':
            course_list = dependency.key_document
            checking = actual_dependency_item.filter(
                Q(statement_eti_item__course__in=course_list) |
                Q(cert_item__course_training__in=course_list)
            ).exists()
        elif dependency.type_document == 'Medical':
            positions_list = [dp.get('position') for dp in dependency.key_document]
            checking = actual_dependency_item.filter(
                Q(medical_cert_item__position__in=positions_list) |
                Q(statement_medical_cert_item__position__in=positions_list)
            )
        elif dependency.type_document == 'Свідоцтво про підвищення кваліфікації':
            qualification_list = [dp.get('qualitification') for dp in dependency.key_document]
            checking = actual_dependency_item.filter(
                Q(education_documents__qualification__in=qualification_list) |
                Q(adv_training_item__level_qualification__in=qualification_list)
            )
        else:
            checking = False
        return checking

    @staticmethod
    def check_document_in_another_packet(instance, dependencies):
        if isinstance(instance, StatementETI):
            document = dependencies.filter(
                Q(statement_eti_item__course=instance.course_id) |
                Q(cert_item__course_training=instance.course_id,
                  cert_item__status_document_id=19)
            )
        elif isinstance(instance, StatementMedicalCertificate):
            document = dependencies.filter(
                Q(statement_medical_cert_item__position=instance.position_id) |
                Q(medical_cert_item__position=instance.position_id,
                  medical_cert_item__status_document_id=19)
            )
        elif isinstance(instance, StatementAdvancedTraining):
            document = dependencies.filter(
                Q(adv_training_item__level_qualification=instance.level_qualification_id) |
                Q(education_documents__qualification=instance.level_qualification_id,
                  education_documents__status_document_id=2)
            )
        else:
            return
        if document.exists():
            raise ValidationError({'error': 'You have some document in another statement',
                                   'number': document.first().packet_item.number,
                                   'document_name': document.first().item._meta.verbose_name})

    def create_dependencies_from_position(self, validated_data, sailor, positions, agent, branch_office):
        list_position = [pos.pk for pos in positions]
        rank = positions[0].rank
        is_continue = check_is_continue(sailor, rank.pk, list_position)
        user: User = self.context['request'].user
        up = user.userprofile
        education_with_sqc = validated_data.get('education_with_sqc')
        packet = False if up.type_user == up.MARAD or education_with_sqc else True
        docs = CSP(
            sailor=validated_data.get('sailor_id'),
            list_position=list_position,
            demand_position=True,
            is_continue=is_continue,
            packet=packet
        ).get_docs_with_status()
        if not education_with_sqc:
            back_office.utils.check_diploma_of_higher_education(docs)
        item = PacketItem.objects.create(
            sailor_id=validated_data.get('sailor_id'),
            position_type=is_continue,
            agent=agent,
            service_center=branch_office,
            include_sailor_passport=validated_data.get('include_sailor_passport', 0),
            education_with_sqc=education_with_sqc
        )
        sailor.packet_item.append(item.pk)
        sailor.save(update_fields=['packet_item'])
        item.position.set(positions)
        # Adds dependencies on required and non existing documents/certificates
        dependency_actual = DependencyItem.objects.filter(
            packet_item__in=sailor.packet_item,
            item_status__in=[DependencyItem.TO_BUY, DependencyItem.WAS_BOUGHT],
            packet_item__is_payed=True
        )
        ordering = '-type_sailor' if education_with_sqc else 'type_sailor'
        bulk_dependency = [
            DependencyItem(
                packet_item=item,
                item=ne_doc,
                type_document=TypeOfAccrualRules.objects.filter(
                    document_type__overlap=[ne_doc.type_document]
                ).order_by(ordering).first(),
                item_status=DependencyItem.TO_BUY
            )
            for ne_doc in docs['not_exists_docs']
            if (ne_doc.type_document not in [
                'Диплом про вищу освіту', 'Образование', 'Диплом', 'Підтвердження робочого диплому',
                'Свідоцтво фахівця', 'Танкерист хотелка', 'Танкерист'
            ]) and not self.has_dependency_in_another_document(ne_doc, dependency_actual)
        ]

        # Adds existing and check-passed documents/certificates
        bulk_dependency += [
            DependencyItem(
                packet_item=item,
                item=ex_doc,
                item_status=DependencyItem.WAS_BE,
                type_document_id=ex_doc._meta.model.TYPE_OF_ACCRUAL
            )
            for ex_doc in docs['all_docs']
        ]

        include_sailor_passport = validated_data.get('include_sailor_passport')
        # Adds and checks a SailorPassport (ПОМ)
        if include_sailor_passport in [1, 2, 3, 4]:
            bulk_dependency += back_office.utils.add_sailor_passport_to_packet(sailor, item, include_sailor_passport)
        # add agent
        type_document_agent = AccrualTypes.CADET_AGENT if education_with_sqc else AccrualTypes.AGENT
        bulk_dependency.append(
            DependencyItem(packet_item=item, item=agent,
                           type_document_id=type_document_agent, item_status=DependencyItem.TO_BUY)
        )
        if not education_with_sqc:
            bulk_dependency.append(
                DependencyItem(packet_item=item,
                               type_document_id=AccrualTypes.MORRICHSERVICE, item_status=DependencyItem.TO_BUY)
            )

        # Adds service center
        if not education_with_sqc:
            group: AgentGroup = agent.userprofile.agent_group.first()
            try:
                secretary: UserProfile = group.userprofile_set.filter(type_user=UserProfile.SECRETARY_SERVICE).first()
                pay_branch_office = secretary.branch_office
            except AttributeError:
                pay_branch_office = branch_office
            bulk_dependency.append(
                DependencyItem(packet_item=item, item=pay_branch_office,
                               type_document_id=AccrualTypes.SERVICE_CENTER, item_status=DependencyItem.TO_BUY)
            )

        # Checks DKK statement
        if rank.is_dkk:
            bulk_dependency.append(
                back_office.utils.add_statement_sqc_to_packet(
                    sailor_key=sailor,
                    packet_item=item,
                    is_continue=is_continue,
                    education_with_sqc=education_with_sqc)
            )

        # Add qualification document to packet
        type_document_qualification = AccrualTypes.QUALIFICATION if not education_with_sqc \
            else AccrualTypes.CADET_QUALIFICATION
        type_document_proof = AccrualTypes.PROOF_OF_DIPLOMA if not education_with_sqc \
            else AccrualTypes.CADET_PROOF_OF_DIPLOMA
        if rank.type_document_id in [57, 85, 86, 87, 88, 89, 21]:
            bulk_dependency.append(
                DependencyItem(
                    packet_item=item,
                    type_document_id=type_document_qualification,
                    item_status=DependencyItem.TO_BUY)
            )
        elif is_continue == 1:
            if not validated_data.get('is_only_proof', True):
                bulk_dependency.append(
                    DependencyItem(packet_item=item, type_document_id=type_document_qualification,
                                   item_status=DependencyItem.TO_BUY)
                )
            bulk_dependency.append(
                DependencyItem(
                    packet_item=item,
                    type_document_id=type_document_proof,
                    item_status=DependencyItem.TO_BUY
                )
            )
        elif is_continue in [0, 2]:
            bulk_dependency.append(
                DependencyItem(
                    packet_item=item,
                    type_document_id=type_document_qualification,
                    item_status=DependencyItem.TO_BUY)
            )
            bulk_dependency.append(
                DependencyItem(
                    packet_item=item,
                    type_document_id=type_document_proof,
                    item_status=DependencyItem.TO_BUY)
            )
        DependencyItem.objects.bulk_create(bulk_dependency)
        request = self.context.get('request')
        user = request.user.id if request else None
        if validated_data.get('is_payed') is True:
            edit_packet_data = back_office.utils.on_pay_packet_item(item.pk, user)
            for attr, value in edit_packet_data.items():
                setattr(item, attr, value)
            item.save(force_update=True)
        create_statements.delay(item.pk, user)
        return item

    def create_per_item_dependencies(self, validated_data, sailor: SailorKeys, agent, branch_office):
        """
               Create dependencies per document,  without rank/position
               For create StatementETI receive object:
                {
                "content_type": "statementeti",
                "document_object": {
                    "course_id": 104,
                    "institution_id": 460,
                    "date_meeting": "2020-09-01"(not required)
                    }
                }
                For create StatementSailorPassport receive object:
                {
                "content_type": "statementsailorpassport",
                "document_object": {
                    "port_id": 70,(not required, can get by branch office)
                    "date_meeting": "2020-05-07",(not required)
                    "is_continue": false,(default false, not required, can only 1 times to be continued)
                    "fast_obtaining": true(default true, not required)
                    }
                }
                For create StatementMedicalCertificate receive object:
                {
                "content_type": "statementmedicalcertificate",
                "document_object" : {
                    "position_id": 1,(limitation position)
                    "medical_institution_id": 3,
                    "date_meeting": "2020-01-01",(not required)
                    }
                }
                For create StatementAdvancedTraining receive object:
                {
                "content_type": "statementadvancedtraining",
                "document_object":{
                    "level_qualification_id": 3,
                    "educational_institution_id": 74,
                    "date_meeting": "2020-01-01"(not required)
                    }
                }
                Else skip
       """
        port_converter = {41: 70, 3: 69, 47: 21, 2: 0, 22: 67, 48: 38, 1: 0, 4: 66, 5: 64, 21: 1}
        dependencies = validated_data.get('dependencies')
        with transaction.atomic():
            packet = PacketItem.objects.create(
                sailor_id=validated_data.get('sailor_id'),
                position_type=-1,
                agent=agent,
                service_center=branch_office,
                include_sailor_passport=validated_data.get('include_sailor_passport', 0)
            )
            sailor.packet_item.append(packet.pk)
            dependency_bulk = []
            old_dependency = DependencyItem.objects.filter(
                packet_item__in=sailor.packet_item,
                packet_item__is_payed=True,
                item_status__in=[DependencyItem.WAS_BOUGHT, DependencyItem.TO_BUY])
            last_date_meeting = back_office.utils.get_available_day_for_start_packet(sailor.pk, packet.pk,
                                                                                     add_one_day=False)
            packet.date_start_meeting = last_date_meeting
            for dependency in dependencies:
                if StatementETI._meta.model_name == dependency.get('content_type'):
                    document_object = dependency.get('document_object')
                    course_id = document_object.get('course_id')
                    is_continue = CertificateETI.by_sailor.filter_by_sailor(
                        sailor_key=sailor, course_training_id=course_id).exists()
                    month_ratio = ETIMonthRatio.objects.filter(course_id=course_id).order_by('order')
                    last_date_meeting = workdays.workday(last_date_meeting, 1)
                    date_end_meeting = back_office.utils.get_date_end_meeting_for_certificate_eti(
                        document_object.get('date_meeting', last_date_meeting), course_id, is_continue
                    )
                    obj = StatementETI.objects.create(
                        **document_object,
                        status_document_id=magic_numbers.status_statement_eti_in_process,
                        is_payed=False,
                        is_continue=is_continue,
                        institution_id=document_object.pop('institution_id', month_ratio.first().pk),
                        date_meeting=document_object.pop('date_meeting', last_date_meeting),
                        date_end_meeting=date_end_meeting
                    )
                    self.check_document_in_another_packet(obj, old_dependency)
                    type_document = AccrualTypes.CERTIFICATE
                    sailor.statement_eti.append(obj.pk)
                    last_date_meeting = date_end_meeting
                elif StatementSailorPassport._meta.model_name == dependency.get('content_type'):
                    document_object = dependency.get('document_object')
                    last_date_meeting = workdays.workday(last_date_meeting, 1)
                    obj_date_meeting = document_object.pop('date_meeting', last_date_meeting)
                    type_receipt = document_object['type_receipt']
                    fast_obtaining = True if type_receipt in [2, 4] else False
                    obj = StatementSailorPassport.objects.create(
                        status_document_id=magic_numbers.status_statement_sailor_passport_in_process,
                        port_id=document_object.pop('port_id', port_converter[branch_office.pk]),
                        is_payed=False,
                        is_payed_blank=False,
                        date_meeting=obj_date_meeting,
                        type_receipt=document_object['type_receipt'],
                        fast_obtaining=fast_obtaining,
                    )
                    self.check_document_in_another_packet(obj, old_dependency)
                    packet.include_sailor_passport = document_object['type_receipt']
                    type_document = obj.type_of_accrual_rules_id
                    if type_document in [AccrualTypes.SAILOR_PASSPORT_GETTING_7,
                                         AccrualTypes.SAILOR_PASSPORT_GETTING_20]:
                        dependency_bulk.append(DependencyItem(
                            packet_item=packet,
                            item_status=DependencyItem.TO_BUY,
                            type_document_id=15))
                    sailor.statement_sailor_passport.append(obj.pk)
                    last_date_meeting = obj_date_meeting
                elif StatementMedicalCertificate._meta.model_name == dependency.get('content_type'):
                    document_object = dependency.get('document_object')
                    last_date_meeting = workdays.workday(last_date_meeting, 1)
                    obj_date_meeting = document_object.pop('date_meeting', last_date_meeting)
                    obj = StatementMedicalCertificate.objects.create(
                        status_document_id=magic_numbers.status_statement_medical_cert_in_process,
                        is_payed=False,
                        date_meeting=obj_date_meeting,
                        **document_object
                    )
                    self.check_document_in_another_packet(obj, old_dependency)
                    type_document = AccrualTypes.MEDICAL
                    sailor.statement_medical_certificate.append(obj.pk)
                    last_date_meeting = obj_date_meeting
                elif StatementAdvancedTraining._meta.model_name == dependency.get('content_type'):
                    document_object = dependency.get('document_object')
                    qualification = LevelQualification.objects.get(id=document_object.get('level_qualification_id'))
                    last_date_meeting = workdays.workday(last_date_meeting, 1)
                    date_end_meeting = workdays.workday(document_object.get('date_meeting', last_date_meeting),
                                                        back_office.utils.hours_to_date(
                                                            qualification.course_time_hours))
                    obj = StatementAdvancedTraining.objects.create(
                        status_document_id=magic_numbers.status_statement_adv_training_in_process,
                        is_payed=False,
                        date_meeting=document_object.pop('date_meeting', last_date_meeting),
                        date_end_meeting=date_end_meeting,
                        **document_object
                    )
                    self.check_document_in_another_packet(obj, old_dependency)
                    type_document = AccrualTypes.ADVANCED_TRAINING
                    sailor.statement_advanced_training.append(obj.pk)
                    last_date_meeting = date_end_meeting
                else:
                    continue
                dependency_bulk.append(DependencyItem(
                    packet_item=packet,
                    item_status=DependencyItem.TO_BUY,
                    type_document_id=type_document,
                    item=obj
                ))
            DependencyItem.objects.bulk_create(dependency_bulk)
            packet.date_end_meeting = last_date_meeting
            sailor.save(force_update=True)
            if validated_data.get('is_payed') is True:
                edit_packet_data = back_office.utils.on_pay_packet_item(packet.pk, agent)
                for attr, value in edit_packet_data.items():
                    setattr(packet, attr, value)
            packet.save(force_update=True)
            return packet

    def create(self, validated_data):
        agent: User = self.context['request'].user
        now = datetime.now()
        month_next_day = (now + timedelta(days=1)).month
        if month_next_day != now.month and now.hour >= 15:
            raise ValidationError('Package creation is closed this month')

        if agent.userprofile.type_user not in (agent.userprofile.AGENT,
                                               agent.userprofile.BACK_OFFICE,
                                               agent.userprofile.MARAD):
            raise ValidationError('Only seamans permitted')
        branch_office = validated_data.get('service_center')
        if branch_office.is_disable:
            raise ValidationError('Service centre is disabled')
        positions = validated_data.get('position')
        sailor = SailorKeys.objects.get(id=validated_data.get('sailor_id'))
        if positions:
            item = self.create_dependencies_from_position(validated_data=validated_data,
                                                          sailor=sailor,
                                                          positions=positions,
                                                          agent=agent,
                                                          branch_office=branch_office)
        else:
            item = self.create_per_item_dependencies(validated_data=validated_data,
                                                     sailor=sailor,
                                                     agent=agent,
                                                     branch_office=branch_office)

        return item

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        old_instance = deepcopy(instance)

        sailor = instance.sailor_id
        sailor_obj = SailorKeys.objects.get(id=sailor)

        request = self.context.get('request')
        user = request.user.id if request else None

        new_is_payed = validated_data.get('is_payed')
        if validated_data.get('service_center') and validated_data.get('service_center') != instance.service_center:
            instance.dependencies.filter(
                type_document_id__in=AccrualTypes.LIST_SERVICE_CENTER
            ).update(item=validated_data.get('service_center'))

        if (validated_data.get('include_sailor_passport') in [1, 2, 3, 4] and
                not instance.dependencies.filter(type_document_id__in=AccrualTypes.LIST_SAILOR_PASSPORT).exists()):
            bulk_sailor_passport = back_office.utils.add_sailor_passport_to_packet(
                sailor_obj,
                instance,
                validated_data.get('include_sailor_passport')
            )
            DependencyItem.objects.bulk_create(bulk_sailor_passport)

        if new_is_payed and not instance.is_payed:
            data_to_update = back_office.utils.on_pay_packet_item(instance.pk, user)
            validated_data.update(data_to_update)
            back_office.tasks.check_for_adding_diploma_to_proof.s(instance.pk).apply_async()

        if new_is_payed is not None and not new_is_payed and instance.is_payed is True:
            instance.dependencies.update(payment_form1=0, payment_form2=0)

        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
        instance.save()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        save_history.s(user_id=user, module=PacketItem._meta.object_name, action_type='edit',
                       content_obj=instance, serializer=PacketSerializer, new_obj=instance,
                       old_obj=old_instance, sailor_key_id=sailor).apply_async(serializer='pickle')
        return instance


class PacketReportListSerializer(serializers.ModelSerializer):
    number = serializers.SerializerMethodField()
    sailor_id = serializers.SerializerMethodField()
    price_form1 = serializers.ReadOnlyField(source='get_price_form1')
    price_form2 = serializers.ReadOnlyField(source='get_price_form2')
    document_info = serializers.SerializerMethodField()
    sum_to_distribution_f1 = serializers.SerializerMethodField()
    sum_to_distribution_f2 = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    payment_date = serializers.SerializerMethodField()

    def get_number(self, instance):
        return instance.packet_item.number

    def get_sailor_id(self, instance):
        return instance.packet_item.sailor_id

    def get_payment_date(self, instance):
        payment_date = instance.packet_item.payment_date
        return payment_date.strftime('%d.%m.%Y')

    def get_document_info(self, instance):
        if isinstance(instance.item, BranchOffice):
            return f'{instance.item.name_ukr} {instance.type_document.value}'
        if isinstance(instance.item, User):
            return f'{instance.item.userprofile.full_name_ukr} {instance.type_document.value}'
        if hasattr(instance.item, 'get_info_for_statement'):
            number = instance.item.get_info_for_statement.get('number', '')
            return f'{number} {instance.type_document.value}'
        return instance.type_document.value

    def get_sum_to_distribution(self, instance, form):
        instance: DependencyItem
        payment_date = instance.packet_item.payment_date
        if instance.content_type and instance.content_type.model == 'certificateeti':
            course = instance.item.course_training
            price_cource = CoursePrice.for_date.date(date=payment_date, course=course,
                                                     type_of_form=form).first().price
            eti_percent = ETIProfitPart.for_date.date(date=payment_date).first().percent_of_eti
            self.distribution = round(price_cource * (eti_percent / 100), 2)
            response = {
                'amount': self.distribution,
                'to_eti': self.distribution,
                'to_td': 0,
                'to_sqc': 0,
                'to_qd': 0,
                'to_sc': 0,
                'to_agent': 0,
                'to_itcs': 0,
                'to_medical': 0,
                'to_cec': 0,
                'to_portal': 0,
            }
        else:
            price_for_position = PriceForPosition.for_date.date(date=payment_date, type_of_form=form,
                                                                type_document=instance.type_document)
            price_position_inst = price_for_position.first()
            response = model_to_dict(price_position_inst, exclude=['id', 'date_start', 'date_end', 'type_document',
                                                                   'type_of_form', 'currency', 'is_hidden',
                                                                   'full_price'])
            response.update({'to_eti': 0, 'amount': sum(response.values())})
            self.distribution = price_position_inst.sum_to_distribution
        return response

    def get_sum_to_distribution_f1(self, instance):
        return self.get_sum_to_distribution(instance, CoursePrice.FIRST_FORM)

    def get_sum_to_distribution_f2(self, instance):
        return self.get_sum_to_distribution(instance, CoursePrice.SECOND_FORM)

    def get_profit(self, instance):
        if not hasattr(self, 'price'):
            self.get_sum_to_distribution_f2(instance)
        return instance.get_price_form2 - self.distribution

    class Meta:
        model = DependencyItem
        fields = ('number', 'sailor_id', 'price_form1', 'price_form2', 'document_info', 'sum_to_distribution_f1',
                  'sum_to_distribution_f2', 'profit', 'payment_date')


class PacketItemPreviewSerializer(serializers.Serializer):
    position = serializers.PrimaryKeyRelatedField(queryset=Position.objects.all(), many=True)
    education_with_sqc = serializers.BooleanField(write_only=True)


class MergeDocumentSerializer(serializers.Serializer):
    sailor_key = serializers.PrimaryKeyRelatedField(queryset=SailorKeys.objects.all())
    content_type = serializers.SlugRelatedField(queryset=ContentType.objects.all(), slug_field='model')
    old_document = serializers.IntegerField()
    new_document = serializers.IntegerField()
