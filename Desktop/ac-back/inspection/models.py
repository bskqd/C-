import os

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Create your models here.
from datetime import datetime, date
from django.contrib.postgres import fields as postgresfield
from pgcrypto import fields


def get_upload_path(instance, filename):
    """
    For protocol dkk
    :param instance:
    :param filename:
    :return:
    """
    if not instance.date_meeting:
        instance.date_meeting = date.today()
    if instance.branch_create:
        branch_create = instance.branch_create.code_branch
    else:
        branch_create = '00'
    if instance.statement_dkk:
        direction = instance.statement_dkk.rank.direction.value_abbr
    else:
        direction = ''
    return os.path.join('protocols', f'{instance.number_document}-{instance.date_meeting.year}-{branch_create}-'
                                     f'{direction}', filename)


class InspectionModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'inspection'


class SailorDataModel(models.Model):
    pass

    class Meta:
        abstract = True


class InspTypeRank(InspectionModel):
    """
    Тип звания
    """
    value = models.CharField(max_length=50)

    class Meta(InspectionModel.Meta):
        pass


class InspTypeDocument(InspectionModel):
    """
    Тип документа
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    code = models.IntegerField()
    for_service = models.CharField(max_length=100, null=True, blank=True)
    is_disable = models.BooleanField(default=False)
    summ = models.FloatField(blank=True, null=True)


class InspDirection(InspectionModel):
    """
    Направление при создании звания/квалификации
    Так же направление при создании комиссии
    """
    value_ukr = models.TextField()
    value_eng = models.TextField()
    value_abbr = models.CharField(max_length=10)


class InspRank(InspectionModel):
    """
    Звание/Квалификация
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    type_rank = models.ForeignKey(InspTypeRank, on_delete=models.PROTECT)
    type_document = models.ForeignKey(InspTypeDocument, on_delete=models.PROTECT)
    direction = models.ForeignKey(InspDirection, on_delete=models.PROTECT)
    is_disable = models.BooleanField(default=False)
    summ = models.FloatField(blank=True, null=True)
    is_dkk = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(null=True, default=255)

    @property
    def get_is_dkk(self):
        position_is_dkk = list(self.position_set.filter(is_disable=False).values_list('is_dkk', flat=True))
        return all(position_is_dkk)


class InspLevel(InspectionModel):
    """
    Уровни
    """
    name_ukr = models.CharField(max_length=255)
    name_eng = models.CharField(max_length=255)
    is_disable = models.BooleanField(default=False)


class InspPosition(InspectionModel):
    """
    Посада/Должность
    """
    name_ukr = models.TextField()
    name_eng = models.TextField()
    rank = models.ForeignKey(InspRank, on_delete=models.PROTECT, null=True, blank=True)
    is_dkk = models.BooleanField(default=True)
    team = models.CharField(max_length=200, null=True, blank=True)
    is_disable = models.BooleanField(default=False)
    experience_description = models.TextField(null=True, blank=True)
    standarts_text = models.TextField(null=True, blank=True)
    level = models.ForeignKey(InspLevel, on_delete=models.SET_DEFAULT, default=3)

    @property
    def position_with_rank_ukr(self):
        return '{} ({})'.format(self.name_ukr, self.rank.name_ukr)

    @property
    def position_with_rank_eng(self):
        return '{} ({})'.format(self.name_eng, self.rank.name_eng)


class InspStatusDocument(InspectionModel):
    """
    Статус документов
    """
    name_ukr = models.CharField(max_length=150)
    name_eng = models.CharField(max_length=150)
    for_service = models.CharField(max_length=200)
    is_disable = models.BooleanField(default=False)


class InspBranchOffice(InspectionModel):
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

    def __str__(self):
        return self.name_ukr


class InspCommitte(InspectionModel):
    """
    Комиссии. Используются при создании филлиала
    """
    branch_office = models.ForeignKey(InspBranchOffice, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    direction = models.ForeignKey(InspDirection, on_delete=models.PROTECT)
    FIO_main = models.CharField(max_length=150)
    FIO_secretary = models.CharField(max_length=150, null=True, blank=True)
    is_disable = models.BooleanField(default=False)


class InspPort(InspectionModel):
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


class InspCommisioner(InspectionModel):
    """
    Член комиссии. Используется при создании комиссии
    """
    committe = models.ForeignKey(InspCommitte, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150)


class InspDecision(InspectionModel):
    name_ukr = models.CharField(max_length=200)
    name_eng = models.CharField(max_length=200)


class InspSailorStatementDKK(InspectionModel, SailorDataModel):
    number = models.IntegerField()
    created_at = models.DateTimeField(default=datetime.now)
    is_payed = models.BooleanField(default=False)
    rank = models.ForeignKey(InspRank, on_delete=models.PROTECT)
    list_positions = postgresfield.ArrayField(models.IntegerField())
    status_document = models.ForeignKey(InspStatusDocument, on_delete=models.PROTECT)
    branch_office = models.ForeignKey(InspBranchOffice, on_delete=models.PROTECT)
    author = models.CharField(max_length=250, null=True, blank=True)
    is_continue = models.IntegerField(default=0)
    on_create_rank = models.ManyToManyField(InspRank, related_name='on_create_rank')


class InspProtocolDKK(InspectionModel, SailorDataModel):
    statement_dkk = models.ForeignKey(InspSailorStatementDKK, null=True, on_delete=models.CASCADE)
    number_document = models.IntegerField()
    date_meeting = models.DateField(null=True, blank=True)
    committe = models.ForeignKey(InspCommitte, on_delete=models.SET_NULL, null=True, blank=True)
    commisioners = postgresfield.ArrayField(models.IntegerField(), null=True, blank=True)
    branch_create = models.ForeignKey(InspBranchOffice, on_delete=models.SET_NULL, null=True, blank=True)
    status_document = models.ForeignKey(InspStatusDocument, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=datetime.now)
    decision = models.ForeignKey(InspDecision, on_delete=models.PROTECT, default=2)
    author = models.CharField(max_length=250, null=True, blank=True)
    function_limitation = models.JSONField(null=True, blank=True)  # первое - функция и уровни с таблицы
    date_end = models.DateField(null=True, blank=True)


class InspStatementQualificationDocument(InspectionModel, SailorDataModel):
    number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    rank = models.ForeignKey(InspRank, on_delete=models.DO_NOTHING)
    list_positions = postgresfield.ArrayField(models.IntegerField())
    type_document = models.ForeignKey(InspTypeDocument, on_delete=models.CASCADE, default=49)
    status_document = models.ForeignKey(InspStatusDocument, on_delete=models.PROTECT)
    protocol_dkk = models.OneToOneField(InspProtocolDKK, on_delete=models.PROTECT, null=True, blank=True)
    is_continue = models.BooleanField(default=False)
    port = models.ForeignKey(InspPort, on_delete=models.PROTECT)
    is_payed = models.BooleanField(default=False)
    author = models.CharField(max_length=250, null=True, blank=True)


class InspQualificationDocument(InspectionModel, SailorDataModel):
    country = models.CharField(max_length=255)
    number_document = models.BigIntegerField(null=True, blank=True)
    other_number = models.CharField(max_length=50, null=True, blank=True)
    list_positions = postgresfield.ArrayField(models.IntegerField(), default=list)
    rank = models.ForeignKey(InspRank, on_delete=models.DO_NOTHING)
    date_start = models.DateField()
    date_end = models.DateField(null=True, blank=True)
    type_document = models.ForeignKey(InspTypeDocument, on_delete=models.PROTECT)
    status_document = models.ForeignKey(InspStatusDocument, on_delete=models.PROTECT)
    statement = models.ForeignKey(InspStatementQualificationDocument, on_delete=models.PROTECT, null=True, blank=True)
    port = models.ForeignKey(InspPort, on_delete=models.PROTECT, null=True, blank=True)
    other_port = models.CharField(max_length=250, null=True, blank=True)
    fio_captain_ukr = models.CharField(max_length=200, null=True, blank=True)
    fio_captain_eng = models.CharField(max_length=200, null=True, blank=True)
    new_document = models.BooleanField(default=True)
    function_limitation = models.JSONField(null=True, blank=True)  # первое - функция и уровни с таблицы
    # FunctionAndLevelForPosition,  2- ограничение. [{"id_func": 166, "id_limit": [153]}]
    strict_blank = models.CharField(max_length=30, null=True, blank=True)

    class Meta(InspectionModel.Meta):
        verbose_name = 'Кваліфікаційний документ'


class InspServiceRecordSailor(InspectionModel, SailorDataModel):
    """
    Послужна книжка

    """
    number = models.BigIntegerField()  # номер
    issued_by = models.TextField()  # кем выдана
    auth_agent_ukr = models.CharField(max_length=200)  # уповноважена особа
    auth_agent_eng = models.CharField(max_length=200)
    branch_office = models.ForeignKey(InspBranchOffice, on_delete=models.PROTECT)  # филия
    date_issued = models.DateField()  # дата выдачи
    status_document = models.ForeignKey(InspStatusDocument, on_delete=models.PROTECT)
    blank_strict_report = models.BigIntegerField(blank=True, null=True)

    class Meta(InspectionModel.Meta):
        verbose_name = 'Послужна книжка моряка'


class InspSailorPassport(InspectionModel, SailorDataModel):
    country = models.CharField(max_length=255)
    number_document = models.CharField(max_length=20)
    date_start = models.DateField()
    date_end = models.DateField()
    port = models.ForeignKey(InspPort, on_delete=models.PROTECT, null=True, blank=True)
    other_port = models.CharField(null=True, blank=True, max_length=250)
    captain = models.CharField(max_length=255)  # оставить текстом, должна быть статическая инфа
    status_document = models.ForeignKey(InspStatusDocument, on_delete=models.PROTECT)
    date_renewal = models.DateField(null=True, blank=True)

    class Meta(InspectionModel.Meta):
        verbose_name = 'Посвідчення особи моряка'


class InspProfile(InspectionModel):

    first_name_ukr = models.CharField(max_length=200)
    first_name_eng = models.CharField(max_length=200)
    last_name_ukr = models.CharField(max_length=200)
    last_name_eng = models.CharField(max_length=200)
    middle_name_eng = models.CharField(max_length=200, null=True, blank=True)
    middle_name_ukr = models.CharField(max_length=200)
    date_birth = fields.DatePGPSymmetricKeyField(null=True)
    sex = models.IntegerField(default=0)
    contact_info = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)
    user_id = models.IntegerField(blank=True, null=True)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, blank=True, null=True)