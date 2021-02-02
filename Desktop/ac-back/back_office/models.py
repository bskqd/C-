from datetime import date

import workdays
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, F, Max
from django.db.models.functions.comparison import NullIf
from pgcrypto import fields
# Create your models here.
from rest_framework.reverse import reverse

from communication.models import SailorKeys
from directory.models import TypeOfAccrualRules, Course, BranchOffice, TypeDocument, NTZ
from itcs.magic_numbers import AccrualTypes
from sailor.managers import BySailorQuerySet
from sailor.models import Profile
from .managers import TodayFirstFormManager, TodayManager, TodaySecondFormManager, ForDateManager


class ETICoefficient(models.Model):
    date_start = models.DateField()
    date_end = models.DateField(blank=True, null=True)
    packet_coefficient = models.FloatField()
    ntz_coefficient = models.FloatField()
    ntz_non_cash_percent = models.FloatField()
    ntz_cash_percent = models.FloatField()

    def full_clean(self, exclude=None, validate_unique=True):
        if self.ntz_non_cash_percent + self.ntz_cash_percent != 100:
            raise ValidationError('NTZ non cash percent + NTZ cash percent must be 100')
        super(ETICoefficient, self).full_clean(exclude, validate_unique)


class CoursePrice(models.Model):
    TYPE_OF_CURRENCY = (
        ('USD', 'USD'),
        ('UAH', 'UAH')
    )
    FIRST_FORM = 'First'
    SECOND_FORM = 'Second'

    TYPE_OF_FORM_CHOICES = (
        (FIRST_FORM, 'Первая'),
        (SECOND_FORM, 'Вторая')
    )

    objects = models.Manager()
    today = TodayManager()
    today_first_form = TodayFirstFormManager()
    today_second_form = TodaySecondFormManager()
    for_date = ForDateManager()

    date_start = models.DateField()
    date_end = models.DateField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.FloatField()
    currency = models.CharField(max_length=3, default='USD', choices=TYPE_OF_CURRENCY)
    type_of_form = models.CharField(max_length=30, default=SECOND_FORM, choices=TYPE_OF_FORM_CHOICES)


class ETIProfitPart(models.Model):
    objects = models.Manager()
    today = TodayManager()
    today_first_form = TodayFirstFormManager()
    today_second_form = TodaySecondFormManager()
    for_date = ForDateManager()

    percent_of_eti = models.FloatField(verbose_name='Процент НТЗ')
    percent_of_profit = models.FloatField(verbose_name='Процент прибыли')
    date_start = models.DateField()
    date_end = models.DateField(null=True, blank=True)


class PriceForPosition(models.Model):
    objects = models.Manager()
    today = TodayManager()
    today_first_form = TodayFirstFormManager()
    today_second_form = TodaySecondFormManager()
    for_date = ForDateManager()

    FIRST_FORM = 'First'
    SECOND_FORM = 'Second'

    TYPE_OF_FORM_CHOICES = (
        (FIRST_FORM, 'Первая'),
        (SECOND_FORM, 'Вторая')
    )
    TYPE_OF_CURRENCY = (
        ('USD', 'USD'),
        ('UAH', 'UAH'),
        ('%', '%')
    )
    type_document = models.ForeignKey(TypeOfAccrualRules, on_delete=models.PROTECT, verbose_name='Тип документа',
                                      related_name='price')
    to_td = models.FloatField(default=0, verbose_name='В Казначейство')
    to_sqc = models.FloatField(default=0, verbose_name='В ДКК')
    to_qd = models.FloatField(default=0, verbose_name='В ДПВ')
    to_sc = models.FloatField(default=0, verbose_name='В сервисный центр')
    to_agent = models.FloatField(default=0, verbose_name='Агенту')
    to_itcs = models.FloatField(default=0, verbose_name='В ИПДМ')
    to_medical = models.FloatField(default=0, verbose_name='В медицинское учереждение')
    to_cec = models.FloatField(default=0, verbose_name='В КПК')
    to_portal = models.FloatField(default=0, verbose_name='В портал')
    to_mrc = models.FloatField(default=0, verbose_name='В морречсервис')
    full_price = models.FloatField(default=0, verbose_name='Полная цена')
    date_start = models.DateField(verbose_name='Дата начала действия')
    date_end = models.DateField(null=True, blank=True, verbose_name='Дата окончания действия')
    type_of_form = models.CharField(choices=TYPE_OF_FORM_CHOICES, default='Second', max_length=30,
                                    verbose_name='Форма')
    currency = models.CharField(choices=TYPE_OF_CURRENCY, default='USD', max_length=30, verbose_name='Валюта')
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.type_document.value} {self.date_end}'

    @property
    def sum_to_distribution(self):
        return (self.to_sqc + self.to_qd + self.to_sc + self.to_agent + self.to_itcs + self.to_medical + self.to_cec +
                + self.to_portal + self.to_td)

    @property
    def profit(self):
        if self.currency == '%':
            return 100 - self.sum_to_distribution
        return self.full_price - self.sum_to_distribution

    @property
    def is_actual_value(self):
        today = date.today()
        # if self.date_end is None and self.date_end
        return (self.date_end is None or self.date_end >= today) and self.date_start <= today

    def get_full_sum_form1(self, rank=None, course=None, is_continue=False):
        if self.type_of_form == self.FIRST_FORM and self.type_document_id in AccrualTypes.LIST_SQC:
            return rank.price
        elif self.type_of_form == self.FIRST_FORM and self.type_document_id in AccrualTypes.LIST_QUALIFICATION:
            amount = rank.type_document.price
            if not is_continue and rank.type_document_id == 49:
                amount = amount + 0.10
            return amount
        elif self.type_of_form == self.FIRST_FORM and self.type_document_id in AccrualTypes.LIST_PROOF:
            amount = TypeDocument.objects.get(id=16).price
            if not is_continue and rank.type_document_id == 49:
                amount = amount + 0.10
            return amount
        elif self.type_of_form == self.FIRST_FORM and self.type_document_id in AccrualTypes.LIST_CERTIFICATE:
            if course._meta.model_name == 'certificateeti':
                return CoursePrice.today_first_form.get(course=course.course_training).price
            elif course._meta.model_name == 'statementeti':
                return CoursePrice.today_first_form.get(course=course.course).price
            elif course._meta.model_name == 'dependencydocuments':
                #   TODO: Not first course, user must choices certificate
                find_course = CoursePrice.today_second_form.filter(course_id__in=course.key_document)
                return find_course.first().price if find_course.exists() else 0
        return self.full_price

    def get_full_sum_form2(self, course=None):
        if course and course._meta.model_name == 'dependencydocuments' and \
                self.type_document_id in AccrualTypes.LIST_CERTIFICATE:
            find_course = CoursePrice.today_second_form.filter(course_id__in=course.key_document)
            return find_course.first().price if find_course.exists() else 0
        elif course and course._meta.model_name == 'statementeti' and \
                self.type_document_id in AccrualTypes.LIST_CERTIFICATE:
            return CoursePrice.today_second_form.get(course_id=course.course).price
        return self.full_price


class PacketItem(models.Model):
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    @staticmethod
    def tomorrow():
        today = date.today()
        return workdays.workday(today, 1)

    TYPE_OF_POSITION = (
        (-1, 'Отримання документів'),
        (0, 'Присвоєння'),
        (1, 'Подовження'),
        (2, 'Подовження з новою должностю')
    )
    INCLUDE_SAILOR_PASSPORT_CHOICES = (
        (0, 'Не потрібна'),
        (1, 'Потрібна, за 20 днів'),
        (2, 'Потрібна за 7 днів'),
        (3, 'Подовження за 20 днів'),
        (4, 'Подовження за 7 днів'),
    )

    number = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sailor_id = fields.IntegerPGPSymmetricKeyField()
    is_payed = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True)
    position = models.ManyToManyField('directory.Position')
    position_type = models.IntegerField(choices=TYPE_OF_POSITION, default=0)
    full_price_form1 = models.FloatField(null=True)
    full_price_form2 = models.FloatField(null=True)
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    service_center = models.ForeignKey(BranchOffice, on_delete=models.CASCADE, null=True)
    include_sailor_passport = models.IntegerField(choices=INCLUDE_SAILOR_PASSPORT_CHOICES, default=0)
    date_start_meeting = models.DateField(null=True)
    date_end_meeting = models.DateField(null=True)
    is_rated = models.BooleanField(default=False)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, blank=True, null=True)
    education_with_sqc = models.BooleanField(default=False)

    @property
    def full_number(self):
        try:
            coefficient = self.current_form2_price / self.current_form1_price
        except ZeroDivisionError:
            return 0
        coefficient_round = round(coefficient, 6)
        coefficient_round_str = f'{coefficient_round:.6f}'
        resp = f'{coefficient_round_str[2:-3]}/{coefficient_round_str[-3:]}'
        if coefficient_round > 1:
            resp = str(int(coefficient_round)) + resp
        return f'{self.number}/{resp}'

    @property
    def current_form1_price(self):
        if not self.is_payed:
            return round(sum((dep.get_price_form1 for dep in self.dependencies.filter(
                item_status__in=[DependencyItem.TO_BUY, DependencyItem.WAS_BOUGHT]))), 2)
        else:
            return self.full_price_form1

    @property
    def current_form2_price(self):
        if not self.is_payed:
            return round(
                sum(
                    (dep.get_price_form2 for dep in self.dependencies.filter(
                        item_status__in=[DependencyItem.TO_BUY, DependencyItem.WAS_BOUGHT])
                     )
                ), 2)
        else:
            return self.full_price_form2

    @property
    def rank(self):
        position = self.position.first()
        if position:
            rank_obj = position.rank
            return {'id': rank_obj.pk, 'name_ukr': rank_obj.name_ukr, 'name_eng': rank_obj.name_eng}
        return None

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.number:
            today = date.today()
            max_number = PacketItem.objects.filter(
                created_at__year=today.year
            ).aggregate(max_number=Max('number'))['max_number'] or 0
            self.number = max_number + 1
        return super(PacketItem, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                            update_fields=update_fields)

    @property
    def sailor_full_name(self):
        try:
            sailor = SailorKeys.objects.get(id=self.sailor_id)
            profile = Profile.objects.filter(id=sailor.profile).first()
        except (SailorKeys.DoesNotExist, Profile.DoesNotExist):
            return ''
        return profile.get_full_name_ukr

    @property
    def get_agent_full_name(self):
        if hasattr(self.agent, 'userprofile'):
            return f'{self.agent.last_name} {self.agent.first_name} {self.agent.userprofile.middle_name}'
        return f'{self.agent.last_name} {self.agent.first_name}'


class DependencyItem(models.Model):
    WAS_BE = 'Was be'
    TO_BUY = 'To buy'
    WAS_BOUGHT = 'Was bought'

    ITEM_STATUS_CHOICES = (
        (WAS_BE, 'Sailor have a item before'),
        (TO_BUY, 'Sailor must a buy item'),
        (WAS_BOUGHT, 'Sailor was bought item')
    )

    packet_item = models.ForeignKey(PacketItem, on_delete=models.CASCADE, related_name='dependencies')
    payment_form1 = models.FloatField(default=0.0)
    payment_form2 = models.FloatField(default=0.0)
    item = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True)
    object_id = models.PositiveIntegerField(null=True)
    item_status = models.CharField(max_length=10, default=WAS_BE, choices=ITEM_STATUS_CHOICES)  # Bcs we must know
    # item was bought or sailor was have its before Packet
    type_document = models.ForeignKey(
        TypeOfAccrualRules, on_delete=models.PROTECT, related_name='dependency', null=True
    )
    updated_at = models.DateField(auto_now=True)
    is_etransport_pay = models.BooleanField(default=False)
    payments = GenericRelation('platon.PlatonPayments', related_query_name='dependecy_payments')

    class Meta:
        permissions = (
            ('readPaymentsSC', 'Просмотр информации по оплате сервисным центрам'),
        )

    @property
    def status(self):
        converter = {self.WAS_BE: 0, self.TO_BUY: 1,
                     self.WAS_BOUGHT: 2}
        return converter[self.item_status]

    @property
    def get_price_form1(self):
        if not self.payment_form1 and self.item_status != self.WAS_BE:
            try:
                position = self.packet_item.position.first()
                rank = position.rank if position else None
                return PriceForPosition.today_first_form.get(type_document=self.type_document).get_full_sum_form1(
                    rank=rank, course=self.item, is_continue=bool(self.packet_item.position_type)
                )
            except PriceForPosition.DoesNotExist:
                return 0
        return self.payment_form1

    @property
    def get_price_form2(self):
        if not self.payment_form2 and self.item_status != self.WAS_BE:
            if not self.item_status == self.WAS_BE:
                return PriceForPosition.today_second_form.get(type_document=self.type_document).get_full_sum_form2(
                    self.item
                )
        else:
            return self.payment_form2
        return 0

    @property
    def get_info_for_statement(self):
        if self.content_type and self.content_type.model in (
                'servicerecord', 'education', 'certificateeti', 'qualificationdocument',
                'medicalcertificate',
                'sailorpassport', 'statementsqc', 'dependencydocuments', 'protocolsqc', 'proofofworkdiploma',
                'statementeti', 'statementsailorpassport', 'statementmedicalcertificate', 'statementadvancedtraining',
                'statementqualification'
        ):
            return self.item.get_info_for_statement
        # elif self.content_type_id in [76]:
        #     return {'main': self.item.document_description, 'additional': self.item.standarts_text}
        elif self.content_type and self.content_type.model in ['user']:
            return {'name': self.item.get_full_name(), 'additional': ''}
        elif self.content_type and self.content_type.model in ['branchoffice']:
            return {'name': self.item.name_ukr, 'additional': self.item.name_eng}
        elif self.type_document_id in AccrualTypes.LIST_MORRICHSERVICE:
            return {'name': '', 'additional': ''}
        elif self.type_document_id in AccrualTypes.LIST_SAILOR_PASSPORT:
            return {'document_description': 'Посвідчення особи моряка',
                    'standarts_text': 'Наказ МІУ № 811 від 18.10.2013'}
        elif self.type_document_id in AccrualTypes.LIST_SQC:
            return {'document_description': 'Чинний протокол ДКК', 'standarts_text': 'Нормативка такая то'}
        elif self.type_document_id in AccrualTypes.LIST_QUALIFICATION:
            return {'document_description': 'Кваліфікаційний документ',
                    'standarts_text': 'Наказ МІУ № 812 від 18.10.2013'}
        elif self.type_document_id in AccrualTypes.LIST_PROOF:
            return {'document_description': 'Підтверждення (Endorsement)',
                    'standarts_text': 'Наказ МІУ № 812 від 18.10.2013'}
        elif self.type_document_id == AccrualTypes.BLANK_SERVICE_RECORD:
            return {'document_description': 'Бланк посвідчення особи моряка',
                    'standarts_text': 'Постанова КМУ № 441 від 26.06.2015 (зі змінами)'}

    @property
    def type_document_name(self):
        return self.type_document.value

    @property
    def information_for_payment(self):
        if self.type_document_id in AccrualTypes.LIST_SQC:
            payment_due = 'Послуги з підтвердження кваліфікації моряків з ПДВ.'
            requisites = '''Отримувач: Інспекція з питань підготовки та дипломування
моряків у м. Києві, вул. Оленівська 25, 04080
Код ЄДРПОУ 25958804;
IBAN: UA863204780000026007924867108;'''

        elif self.type_document_id in (AccrualTypes.LIST_SAILOR_PASSPORT + AccrualTypes.LIST_BLANK_SAILOR_PASSPORT):
            payment_due = 'за адміністративні послуги'
            requisites = '''Отримувач: ГУК у м. Києві/м. Київ/25010100;
Код ЄДРПОУ 37993783;
Банк отримувача: Казначейство України (ЕАП);
IBAN: UA028201720313241001201053925;'''

        elif self.type_document_id in (
                AccrualTypes.LIST_QUALIFICATION +
                AccrualTypes.LIST_PROOF):
            payment_due = 'сплата за адміністративні послуги'
            requisites = '''Отримувач: ГУК у м. Києві/м. Київ/22012500;
Код ЄДРПОУ 37993783;
Банк отримувача: Казначейство України (ЕАП);
Номер рахунку (IBAN) UA128999980334129879047026001;'''
        elif self.type_document_id in AccrualTypes.LIST_CERTIFICATE \
                and self.content_type and self.content_type.model == 'statementeti':
            statement = self.item
            payment_due = statement.course.name_ukr
            requisites = statement.institution.requisites
        elif self.type_document_id in AccrualTypes.LIST_SERVICE_CENTER:
            return self.item.requisites
        elif self.type_document_id in AccrualTypes.LIST_MORRICHSERVICE:
            payment_due = 'за організаційно-технічні послуги з ПДВ; '
            requisites = '''Отримувач: Державне підприємство "Моррічсервіс" у 
            м. Києві, пр. Правди, 35, 04108;
            Код ЄДРПОУ 42615235;
            IBAN: UA473204780000026008924857203;
            Призначення платежу: за організаційно-технічні послуги з ПДВ'''
        else:
            return None
        amount = self.get_price_form1
        return {'payment_due': payment_due, 'requisites': requisites, 'amount': amount}

    @property
    def payment_url(self):
        item = self.item
        if self.type_document_id == AccrualTypes.SERVICE_CENTER:
            pay_url = reverse('packet-branch-office-pay', args=[self.pk]) \
                if self.item_status == DependencyItem.TO_BUY else None
        elif self.type_document_id in AccrualTypes.LIST_SQC:
            pay_url = reverse('statement-sqc-pay', args=[self.object_id]) if not item.is_payed else None
        elif self.type_document_id in AccrualTypes.LIST_CERTIFICATE:
            pay_url = reverse('pay_for_certificate', args=[self.object_id]) \
                if not item.is_payed and item.institution.can_pay_platon \
                else None
        else:
            pay_url = None
        if pay_url:
            pay_url = pay_url[1:]
        return pay_url


class NtzManager(models.Manager):
    def find_active_ntz(self):
        ids = self.get_queryset().filter(order__isnull=False).order_by('order').values_list('ntz_id', flat=True)
        return NTZ.objects.filter(id__in=ids)


class ETIMonthRatio(models.Model):
    objects = NtzManager()

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ntz_ratio')
    ntz = models.ForeignKey(NTZ, on_delete=models.CASCADE, related_name='ntz_ratio')
    month_amount = models.FloatField()
    ratio = models.FloatField(null=True)
    order = models.PositiveSmallIntegerField(null=True)

    @classmethod
    def reorder(cls, course=None):
        def reorder_course(_course):
            price = cls.objects.filter(course=_course).aggregate(Sum('month_amount'))
            ordered_ntz = cls.objects.filter(course=_course). \
                annotate(r=F('ratio') - F('month_amount') / NullIf(price['month_amount__sum'], 0)).order_by('-r')
            for ind, ntz in enumerate(ordered_ntz):
                if not ntz.r:
                    ntz.order = 1
                elif ntz.r > 0:
                    ntz.order = ind
                elif ntz.r < 0:
                    ntz.order = None
                # ntz.order = ind if ntz.r and ntz.r > 0 else None
            cls.objects.bulk_update(ordered_ntz, ['order'])

        if course:
            reorder_course(course)
        else:
            for ratio in cls.objects.distinct('course'):
                reorder_course(ratio.course)
