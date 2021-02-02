import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as postgresfields
from django.db import models


# Create your models here.


class Country(models.Model):
    """
    Страны
    Так же используется для громадянств
    """
    value = models.CharField(max_length=100)
    value_eng = models.CharField(max_length=100)
    value_abbr = models.CharField(max_length=10)


class Region(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    value = models.CharField(max_length=150)
    value_eng = models.CharField(max_length=200)


class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    value = models.CharField(max_length=150)
    value_eng = models.CharField(max_length=255, default='')
    city_type = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.value


class NTZ(models.Model):
    """
    Учебные тренажерные заведения
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    name_abbr = models.CharField(max_length=20, blank=True, default='')
    contract_number = models.CharField(max_length=150, blank=True, default='')
    contract_number_date = models.DateField(null=True)
    address = models.CharField(max_length=255, blank=True, default='')
    requisites = models.CharField(max_length=100, blank=True, default='')
    director_name = models.CharField(max_length=255, blank=True, default='')
    director_position = models.CharField(max_length=200, default='', blank=True)
    accountant_full_name = models.CharField(max_length=255, default='', blank=True)
    bank_name = models.CharField(max_length=255, default='', blank=True)
    check_number = models.CharField(max_length=60, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    phone2 = models.CharField(max_length=15, blank=True, default='')
    email = models.EmailField(max_length=100, blank=True, default='')
    okpo = models.CharField(max_length=10, default='')
    mfo = models.CharField(max_length=15, default='')
    inn = models.CharField(max_length=15, default='')
    nds_number = models.CharField(max_length=50, default='')
    is_red = models.BooleanField(default=False)
    is_disable = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True)
    date_start = models.DateField(null=True)
    date_end = models.DateField(null=True)
    ntz_integration_id = models.SmallIntegerField(null=True, blank=True)
    can_pay_platon = models.BooleanField(default=False)


class TypeRank(models.Model):
    """
    Тип звания
    """
    value = models.CharField(max_length=50)


class TypeDocument(models.Model):
    """
    Тип документа
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    code = models.IntegerField()
    for_service = models.CharField(max_length=100, null=True, blank=True)
    is_disable = models.BooleanField(default=False)
    price = models.FloatField(blank=True, null=True)


class Direction(models.Model):
    """
    Направление при создании звания/квалификации
    Так же направление при создании комиссии
    """
    value_ukr = models.TextField()
    value_eng = models.TextField()
    value_abbr = models.CharField(max_length=10)


class Rank(models.Model):
    """
    Звание/Квалификация
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    type_rank = models.ForeignKey(TypeRank, on_delete=models.PROTECT)
    type_document = models.ForeignKey(TypeDocument, on_delete=models.PROTECT)
    direction = models.ForeignKey(Direction, on_delete=models.PROTECT)
    is_disable = models.BooleanField(default=False)
    price = models.FloatField(blank=True, null=True)
    is_dkk = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(null=True, default=255)
    allowed_to_get = models.ManyToManyField('self', related_name='allowed_from', symmetrical=False)

    @property
    def get_is_dkk(self):
        position_is_dkk = list(self.position_set.filter(is_disable=False).values_list('is_dkk', flat=True))
        return all(position_is_dkk)


class Limitations(models.Model):
    """
    Ограничения
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    is_disable = models.BooleanField(default=False)


class Course(models.Model):
    """
    Курсы
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    code = models.IntegerField(null=True, blank=True)
    is_disable = models.BooleanField(default=False)
    api_ntz_id = models.PositiveIntegerField()
    api_ntz_arr = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
    code_for_parsing = models.FloatField(default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True)
    is_continue = models.BooleanField(default=False)
    continue_merge = models.IntegerField(null=True)


class Responsibility(models.Model):
    """
    Функции
    Обовьязки
    Используется для значения в послужной книжке
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    is_disable = models.BooleanField(default=False)


class Rule(models.Model):
    """
    Правила
    """
    value = models.CharField(max_length=20)
    is_disable = models.BooleanField(default=False)


class TypeNZ(models.Model):
    """
    Тип учебного заведения
    """
    value = models.CharField(max_length=150)
    is_disable = models.BooleanField(default=False)

    def __str__(self):
        return self.value


class NZ(models.Model):
    """
    Учебные заведения
    postal_address - почтовый адрес(физический адресс)
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    type_nz = models.ForeignKey(TypeNZ, on_delete=models.PROTECT)
    name_abbr = models.CharField(max_length=100)
    postal_address = models.TextField(null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    web_site = models.URLField(null=True, blank=True)
    phone_fax = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    email2 = models.EmailField(null=True, blank=True)
    is_disable = models.BooleanField(default=True)
    note = models.TextField(null=True, blank=True)
    is_red = models.BooleanField(default=False)


class Level(models.Model):
    """
    Уровни
    """
    name_ukr = models.CharField(max_length=255)
    name_eng = models.CharField(max_length=255)
    is_disable = models.BooleanField(default=False)


class Position(models.Model):
    """
    Посада/Должность
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    rank = models.ForeignKey(Rank, on_delete=models.PROTECT, null=True, blank=True)
    is_dkk = models.BooleanField(default=True)
    team = models.CharField(max_length=200, null=True, blank=True)
    is_disable = models.BooleanField(default=False)
    experience_description = models.TextField(null=True, blank=True)
    standarts_text = models.TextField(null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.SET_DEFAULT, default=3)
    allowed_to_get = models.ManyToManyField('self', related_name='allowed_from', symmetrical=False)

    @property
    def position_with_rank_ukr(self):
        return '{} ({})'.format(self.name_ukr, self.rank.name_ukr)

    @property
    def position_with_rank_eng(self):
        return '{} ({})'.format(self.name_eng, self.rank.name_eng)


class RulesForPosition(models.Model):
    """
    Правила для должностей/посад
    """
    rule = models.ForeignKey(Rule, on_delete=models.PROTECT)
    rank = models.ForeignKey(Rank, on_delete=models.PROTECT, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.PROTECT)
    is_disable = models.BooleanField(default=False)


class FunctionForPosition(models.Model):
    """
    Функции которые используются при генерации документов
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    is_disable = models.BooleanField(default=False)


class FunctionAndLevelForPosition(models.Model):
    """
    Функции и уровни для должностей/посад
    """
    function = models.ForeignKey(FunctionForPosition, on_delete=models.PROTECT)
    num_function = models.IntegerField()
    rank = models.ForeignKey(Rank, on_delete=models.PROTECT, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.PROTECT)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    is_disable = models.BooleanField(default=False)


class LimitationForFunction(models.Model):
    """
    Ограничения для функций
    """
    function = models.ForeignKey(FunctionForPosition, on_delete=models.PROTECT)
    limitation = models.ForeignKey(Limitations, on_delete=models.PROTECT)
    is_disable = models.BooleanField(default=False)


class StatusDocument(models.Model):
    """
    Статус документов
    """
    name_ukr = models.CharField(max_length=150)
    name_eng = models.CharField(max_length=150)
    for_service = models.CharField(max_length=200)
    is_disable = models.BooleanField(default=False)


class LevelQualification(models.Model):
    """
    Уровень квалификации
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    type_NZ = models.ForeignKey(TypeNZ, on_delete=models.PROTECT, null=True, blank=True)
    course_time_hours = models.FloatField(default=0)
    is_disable = models.BooleanField(default=False)


class TypeDocumentNZ(models.Model):
    name_ukr = models.CharField(max_length=200)
    name_eng = models.CharField(max_length=200)

    def __str__(self):
        return self.name_ukr


class Speciality(models.Model):
    """
    Специальности
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    is_disable = models.BooleanField(default=False)
    type_document_nz = models.ForeignKey(TypeDocumentNZ, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name_ukr


class Specialization(models.Model):
    """
    Специализация к специальности
    """
    speciality = models.ForeignKey(Speciality,
                                   on_delete=models.CASCADE)  # СПОРНО TODO Подумать что можно сделать со специализацией
    name_ukr = models.TextField()
    name_eng = models.TextField()
    is_disable = models.BooleanField(default=False)

    def __str__(self):
        return self.name_ukr


# ОРГАНИЗАЦИИ
# КОНТРАГЕНТЫ ПРОПУСТИЛ ПОКА ТК ТАБЛИЦА ПУСТАЯ МБ НЕ НУЖНА
# ИНОЗЕМНЫЕ АДМИНИСТРАЦИИ ТАК ЖЕ
# ОРГАНИЗАЦИИ СПРАШИВАТЕЛИ КОТОРЫМ РАЗРЕШЕНО РАБОТАТЬ В СИСТЕМЕ ТАК ЖЕ


class Port(models.Model):
    """
    Порты
    """
    code_port = models.CharField(max_length=7)
    name_ukr = models.TextField()
    name_eng = models.TextField()
    position_capitan_ukr = models.TextField()
    position_capitan_eng = models.TextField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_disable = models.BooleanField(default=False)


class FIOCapitanOfPort(models.Model):
    """
    Фио капитанов порта
    """
    name_ukr = models.CharField(max_length=200)
    name_eng = models.CharField(max_length=200)
    port = models.ForeignKey(Port, on_delete=models.SET_NULL, null=True, blank=True)


class BranchOffice(models.Model):
    """
    Филиал/Філії
    """
    code_branch = models.CharField(max_length=7)
    code_track_record = models.CharField(max_length=7, null=True, blank=True)
    name_ukr = models.CharField(max_length=150)
    name_eng = models.CharField(max_length=150)
    address = models.CharField(max_length=255, null=True, blank=True)
    house_num = models.CharField(max_length=15)
    index = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    FIO_director = models.CharField(max_length=150, null=True, blank=True)
    is_disable = models.BooleanField(default=False)
    requisites = models.TextField(default='')
    okpo = models.CharField(default='', max_length=15, blank=True)

    def __str__(self):
        return self.name_ukr


class Commisioner(models.Model):
    """

    Член комиссии. Используется при создании комиссии
    """
    name = models.CharField(max_length=250)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, unique=True)
    is_disable = models.BooleanField(default=False)


class Crew(models.Model):
    """
    Крюїнг
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    name_abbr = models.CharField(max_length=20, null=True, blank=True)
    contract_number = models.CharField(max_length=150, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    house_num = models.CharField(max_length=10, null=True, blank=True)
    index = models.CharField(max_length=10, null=True, blank=True)
    bank_details = models.CharField(max_length=200, null=True, blank=True)
    director_name = models.CharField(max_length=200, null=True, blank=True)
    director_name_rodovoy = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    fax = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    email2 = models.EmailField(null=True, blank=True)
    is_disabled = models.BooleanField(default=False)


class AuthorizatedUsers(models.Model):
    FIO_ukr = models.CharField(max_length=255)
    FIO_eng = models.CharField(max_length=255)
    for_documents_ukr = models.CharField(max_length=255)
    for_documents_eng = models.CharField(max_length=255)
    city = models.ForeignKey(BranchOffice, on_delete=models.PROTECT)


class BlankStrictReport(models.Model):
    number = models.BigIntegerField()


class CourseTraining(models.Model):
    value = models.TextField()


class MedicalInstitution(models.Model):
    value = models.TextField()
    address = models.TextField()
    phone = postgresfields.ArrayField(models.CharField(max_length=15), null=True, blank=True)
    email = postgresfields.ArrayField(models.EmailField(), null=True, blank=True)
    leader = models.CharField(max_length=255, null=True, blank=True)


class DoctrorInMedicalInstitution(models.Model):
    FIO = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    medical_institution = models.ForeignKey(MedicalInstitution, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.FIO}'


class PositionForMedical(models.Model):
    name_ukr = models.CharField(max_length=255)
    name_eng = models.CharField(max_length=255)
    is_disabled = models.BooleanField(default=False)


class ExtentDiplomaUniversity(models.Model):
    """
    степень образования
    """
    name_ukr = models.CharField(max_length=200)
    name_eng = models.CharField(max_length=200)
    priority = models.SmallIntegerField()


class PositionForExperience(models.Model):
    """
    Посада на судні для довидок про стаж или записей в послужной книжке
    """
    name_ukr = models.CharField(max_length=255)
    name_eng = models.CharField(max_length=255)
    is_disable = models.BooleanField(default=False)


class DocsForPosition(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    file = models.FileField()
    is_continue = models.BooleanField(default=False)
    with_position = models.BooleanField(default=False)
    for_service = models.CharField(max_length=100)


class LimitationForMedical(models.Model):
    name_ukr = models.TextField()
    name_eng = models.TextField()
    is_disable = models.BooleanField(default=False)


class RegulatoryGround(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    text_regulatory = models.TextField()
    limitation = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)
    rule = models.ForeignKey(Rule, on_delete=models.SET_NULL, null=True, blank=True)


class Decision(models.Model):
    name_ukr = models.CharField(max_length=200)
    name_eng = models.CharField(max_length=200)


class Faculty(models.Model):
    """Факультеты в ВУЗах"""
    name_ukr = models.CharField(max_length=500)
    name_eng = models.CharField(max_length=500)
    is_disable = models.BooleanField(default=False)


class EducationForm(models.Model):
    """Форма обучения в ВУЗах"""
    name_ukr = models.CharField(max_length=50)
    name_eng = models.CharField(max_length=50)
    is_disable = models.BooleanField(default=False)


class ResponsibilityWorkBook(models.Model):
    """Обязанности для Довідки про стаж типа Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо"""
    name_ukr = models.CharField(max_length=200)
    name_eng = models.CharField(max_length=200)
    is_disable = models.BooleanField(default=False)
    is_not_conventional = models.BooleanField(default=False)


class TypeOfAccrualRules(models.Model):
    class TypeSailor(models.IntegerChoices):
        DEFAULT = (0, 'Default')
        CADET = (1, 'Cadet')

    value = models.CharField(max_length=255)
    document_type = postgresfields.ArrayField(models.TextField(), null=True, blank=True)
    type_sailor = models.IntegerField(choices=TypeSailor.choices, default=TypeSailor.DEFAULT)

    def __str__(self):
        return self.value


class TypeContact(models.Model):
    value = models.CharField(max_length=100)


class Sex(models.Model):
    value_ukr = models.CharField(max_length=20)
    value_eng = models.CharField(max_length=20)


class TypeVessel(models.Model):
    """
    Тип судна
    """
    name_ukr = models.CharField(max_length=100)
    name_eng = models.CharField(max_length=100)


class ModeOfNavigation(models.Model):
    """
    Режим судноплавства
    """
    name_ukr = models.CharField(max_length=100)
    name_eng = models.CharField(max_length=100)


class TypeGeu(models.Model):
    name_ukr = models.CharField(max_length=10)
    name_eng = models.CharField(max_length=10)


class ExperinceForDKK(models.Model):
    """
    Стаж для ДКК
    """
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    experince_value = models.JSONField()
    experince_descr = models.TextField(blank=True, null=True)
    standarts_text = models.TextField(blank=True, null=True)
    month_required = models.PositiveSmallIntegerField(default='6', null=False)


class VerificationStage(models.Model):
    """
    Statuses for documents undergoing verification
    """
    name_ukr = models.CharField(max_length=150)
    name_eng = models.CharField(max_length=150)
    for_service = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True)
    is_disable = models.BooleanField(default=False)
    order_number = models.IntegerField()

    class Meta:
        unique_together = (('order_number', 'for_service'),)
