from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres import fields as postgresfields
from django.db import models
from django.db.models import Max
from gm2m import GM2MField
from pgcrypto import fields

from communication.models import SailorKeys
from directory.models import ExperinceForDKK, Position
from itcs import magic_numbers
from sailor.managers import BySailorManager, BySailorQuerySet
from sailor.models import AuthorDocumentABC, get_upload_path_protocol, Profile, TYPE_RECORD, DateTimesABC
from user_profile.mixins import GetAuthorMixin

User = get_user_model()


class ServiceRecord(GetAuthorMixin, AuthorDocumentABC, DateTimesABC):
    """
    Послужна книжка

    """
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    number = models.BigIntegerField()  # номер
    issued_by = models.TextField()  # кем выдана
    photo = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)  # фото книжки
    auth_agent_ukr = models.CharField(max_length=200)  # уповноважена особа
    auth_agent_eng = models.CharField(max_length=200)
    branch_office = models.ForeignKey('directory.BranchOffice', on_delete=models.PROTECT)  # филия
    date_issued = models.DateField()  # дата выдачи
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    blank_strict_report = models.BigIntegerField(blank=True, null=True)
    waibill_number = models.CharField(max_length=200, null=True, blank=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='service_record_documents')
    verification_status = GenericRelation('sailor.DocumentInVerification',
                                          related_query_name='service_record_verification')

    class Meta:
        verbose_name = 'Послужна книжка моряка'

    @property
    def get_number(self):
        return self.number

    @property
    def get_name_book(self):
        return '{}/{}/{}'.format(str(self.number).zfill(5), self.date_issued.year, self.branch_office.code_track_record)

    @property
    def verification_info(self):
        sailor = SailorKeys.by_document.id(instance=self)
        if not sailor:
            return None
        return {
            'id': self.pk, 'type_document': self._meta.verbose_name, 'issued': self.branch_office.name_ukr,
            'number': self.get_name_book, 'sailor': sailor.pk, 'content_type': self._meta.model_name
        }

    @classmethod
    def generate_number(cls, branch_office_id):
        today = date.today()
        last_number = cls.objects.filter(
            date_issued__year=today.year,
            branch_office_id=branch_office_id
        ).exclude(status_document_id__in=[34, 74]).aggregate(
            Max('number')
        )['number__max'] or 0
        return last_number + 1

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.number:
            self.number = self.generate_number(self.branch_office_id)
        super().save(force_insert, force_update, using, update_fields)


class LineInServiceRecord(GetAuthorMixin, AuthorDocumentABC, DateTimesABC):
    """
    Запись в послужной книжке
    Имеется связь с directory.models.Function - виконани работы
    если это послужная книжка то имеет поле послужная книжка
    если нет то sailor
    """
    service_record = models.ForeignKey('document.ServiceRecord', on_delete=models.CASCADE, null=True,
                                       blank=True, related_name='lines')  # номер послужной книжки
    name_vessel = models.CharField(max_length=255, null=True, blank=True)  # название судна
    type_vessel = models.ForeignKey('directory.TypeVessel', on_delete=models.PROTECT,
                                    null=True, blank=True)
    mode_of_navigation = models.ForeignKey('directory.ModeOfNavigation', on_delete=models.PROTECT, null=True,
                                           blank=True)  # Режим судноплавства
    type_geu = models.ForeignKey('directory.TypeGeu', on_delete=models.PROTECT, null=True, blank=True)  # тип ГЕУ
    ship_owner = models.CharField(max_length=255, null=True, blank=True)  # судновласник
    number_vessel = models.CharField(max_length=15, null=True, blank=True)  # номер судна
    propulsion_power = models.FloatField(null=True, blank=True)  # потужнисть ГЕУ
    electrical_power = models.FloatField(null=True,
                                         blank=True)  # потужнисть суднового електрообладнення только для
    # електромехаников
    responsibility = postgresfields.ArrayField(models.IntegerField(), null=True, blank=True)  # выконани обовьязки
    refrigerating_power = models.FloatField(null=True, blank=True)  # холодопродуктивнисть только для рефмехаников
    book_registration_practical = models.BooleanField(default=False)  # Книга реєстрації практичної підготовки
    equipment_gmzlb = models.BooleanField(default=False)  # Апаратура ГМЗЛБ
    position = models.ForeignKey('directory.PositionForExperience', on_delete=models.PROTECT, null=True,
                                 blank=True)  # звание на судни
    date_start = models.DateField(null=True, blank=True)  # дата влашитуваня
    place_start = models.CharField(max_length=255, null=True, blank=True)  # места влаштування
    place_end = models.CharField(max_length=255, null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)  # дата звильнення
    trading_area = models.TextField(null=True, blank=True)  # район плавання // TODO переделать потом на массив текстов
    ports_input = models.TextField(null=True, blank=True)  # порты вхождения
    full_name_master = models.CharField(max_length=200, default='', null=True,
                                        blank=True)  # фио и подпис капитана, суднова печатка
    full_name_master_eng = models.CharField(max_length=250, default='', null=True,
                                            blank=True)  # фио капитана на английском
    date_write = models.DateField(null=True, blank=True)  # дата заповнення
    status_line = models.ForeignKey('directory.StatusDocument', on_delete=models.CASCADE)
    gross_capacity = models.FloatField(null=True, blank=True)  # валова місткість
    levelRefrigerPlant = models.FloatField(null=True, blank=True)  # уровни холоднопрудктивной установки
    photo = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)
    number_page_book = models.CharField(max_length=10, null=True, blank=True)
    port_of_registration = models.CharField(max_length=150, null=True, blank=True)
    # тип запису (null для записи в ПКМ)
    record_type = models.CharField(max_length=255, choices=TYPE_RECORD, null=True, blank=True)
    responsibility_work_book = models.ForeignKey('directory.ResponsibilityWorkBook', on_delete=models.PROTECT,
                                                 null=True, blank=True)  # обов`язки для трудовой книжки
    place_work = models.CharField(max_length=255, null=True, blank=True)  # место работы
    days_work = models.IntegerField(null=True, blank=True)  # количество отработанных дней
    is_repaired = models.BooleanField(default=False)  # судно выведено в ремонт
    repair_date_from = models.DateField(null=True, blank=True)  # судно выведено в ремонт с
    repair_date_to = models.DateField(null=True, blank=True)  # судно выведено в ремонт по
    days_repair = models.IntegerField(null=True, blank=True)  # количесто дней судна в ремонте
    verification_status = GenericRelation('sailor.DocumentInVerification',
                                          related_query_name='line_serv_record_verification')

    class Meta:
        verbose_name = 'Запис в ПКМ або довідка про стаж'

    @property
    def get_number(self):
        return self.pk

    @property
    def verification_info(self):
        if self.service_record:
            sailor = SailorKeys.objects.filter(service_records__overlap=[self.service_record_id]).first()
        else:
            sailor = SailorKeys.objects.filter(experience_docs__overlap=[self.pk]).first()
        if not sailor:
            return None
        return {
            'id': self.pk, 'type_document': self._meta.verbose_name, 'issued': self.ship_owner,
            'number': self.get_number, 'sailor': sailor.pk, 'content_type': self._meta.model_name,
            'service_record': self.service_record_id
        }


class Education(GetAuthorMixin, AuthorDocumentABC, DateTimesABC):
    TYPE_OF_ACCRUAL = 8
    TYPE_OF_ACCRUAL_STUDENT = 8

    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    type_document = models.ForeignKey('directory.TypeDocumentNZ', on_delete=models.PROTECT)
    number_document = models.CharField(max_length=30)
    serial = models.CharField(max_length=50, null=True, blank=True)
    extent = models.ForeignKey('directory.ExtentDiplomaUniversity', on_delete=models.PROTECT, null=True, blank=True)
    name_nz = models.ForeignKey('directory.NZ', on_delete=models.PROTECT)
    qualification = models.ForeignKey('directory.LevelQualification', on_delete=models.PROTECT, null=True, blank=True)
    speciality = models.ForeignKey('directory.Speciality', on_delete=models.PROTECT, null=True,
                                   blank=True)  # специальность
    specialization = models.ForeignKey('directory.Specialization', on_delete=models.PROTECT, null=True, blank=True,
                                       related_name='specialization')  # специализация для ВНЗ
    date_end_educ = models.DateField(null=True, blank=True)
    expired_date = models.DateField(null=True, blank=True)
    date_issue_document = models.DateField(null=True, blank=True)
    special_notes = models.TextField(null=True, blank=True)
    photo = fields.CharPGPSymmetricKeyField(max_length=250, null=True, blank=True)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    registry_number = models.CharField(max_length=50, default='')
    is_duplicate = models.BooleanField(default=False)
    statement_advanced_training = models.OneToOneField('statement.StatementAdvancedTraining', on_delete=models.PROTECT,
                                                       null=True, blank=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='education_documents')
    verification_status = GenericRelation('sailor.DocumentInVerification',
                                          related_query_name='education_verificate')

    class Meta:
        verbose_name = 'Освітні документи'
        ordering = ['-created_at', '-modified_at']
        permissions = (
            ('merge_education_documents', 'Слитие образовательных документов'),
        )

    @property
    def get_info_for_statement(self):
        from ..misc import get_date_or_none
        is_verification = False
        if self.status_document_id in [magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT]:
            is_verification = True
        if self.type_document_id == 1:
            info = '{} / {}'.format(self.extent.name_ukr if self.extent else '',
                                    self.speciality.name_ukr if self.speciality else '')
        else:
            info = self.qualification.name_ukr
        return {'number': self.number_document, 'name_issued': self.name_nz.name_ukr,
                'date_start': get_date_or_none(self.date_issue_document),
                'date_end': get_date_or_none(self.date_end_educ), 'info': info,
                'type_doc': 'Освітній документ', 'is_verification': is_verification,
                'id': self.pk, 'content_type': self._meta.model_name}

    @property
    def profile(self):
        sailor = SailorKeys.objects.filter(education__overlap=[self.id]).first()
        if sailor is None:
            return None
        profile_id = sailor.profile
        if not profile_id:
            return None
        return Profile.objects.filter(id=profile_id).annotate(
            sailor=models.Value(sailor.id, output_field=models.IntegerField())
        ).first()

    @property
    def sailor_full_name(self):
        if self.profile is None:
            return None
        return self.profile.get_full_name_ukr

    @property
    def sailor_birth_date(self):
        if self.profile is None:
            return None
        return self.profile.date_birth.strftime('%d.%m.%Y')

    @property
    def sailor_id(self):
        if self.profile is None:
            return None
        return self.profile.sailor

    @property
    def name_nz_ukr(self):
        return self.name_nz.name_ukr

    @property
    def serial_document(self):
        return self.serial

    @property
    def registry_number_document(self):
        return self.registry_number

    @property
    def get_number(self):
        return self.number_document

    @property
    def extent_ukr(self):
        if self.extent is None:
            return None
        return self.extent.name_ukr

    @property
    def qualification_ukr(self):
        if self.qualification is None:
            return None
        return self.qualification.name_ukr

    @property
    def speciality_ukr(self):
        if self.speciality is None:
            return None
        return self.speciality.name_ukr

    @property
    def specialization_ukr(self):
        if self.specialization is None:
            return None
        return self.specialization.name_ukr

    @property
    def date_start_document(self):
        if self.date_issue_document is None:
            return None
        return self.date_issue_document.strftime('%d.%m.%Y')

    @property
    def date_end_document(self):
        if self.expired_date is None:
            return None
        return self.expired_date.strftime('%d.%m.%Y')

    @property
    def status_ukr(self):
        return self.status_document.name_ukr

    @property
    def get_type_document(self):
        type_document = self.type_document
        if type_document:
            return {'id': type_document.id, 'name_ukr': type_document.name_ukr, 'name_eng': type_document.name_eng}
        else:
            return {}

    @property
    def type_document_ukr(self):
        if self.get_type_document:
            return self.get_type_document['name_ukr']
        return None

    @property
    def verification_info(self):
        sailor = SailorKeys.by_document.id(instance=self)
        if not sailor:
            return None
        return {
            'id': self.pk, 'type_document': self._meta.verbose_name, 'issued': self.name_nz_ukr,
            'number': self.get_number, 'sailor': sailor.pk, 'content_type': self._meta.model_name
        }


class ProtocolSQC(GetAuthorMixin, AuthorDocumentABC, DateTimesABC):
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    statement_dkk = models.OneToOneField('statement.StatementSQC', on_delete=models.PROTECT, null=True,
                                         blank=True)
    number_document = models.IntegerField()
    date_meeting = models.DateField(null=True, blank=True)
    branch_create = models.ForeignKey('directory.BranchOffice', on_delete=models.SET_NULL, null=True, blank=True)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    decision = models.ForeignKey('directory.Decision', on_delete=models.PROTECT, default=2, null=True)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, default=magic_numbers.CLEAR_USER)
    related_docs = GM2MField('document.Education', 'document.CertificateETI', 'document.QualificationDocument',
                             'document.ProofOfWorkDiploma', 'document.MedicalCertificate', 'sailor.DependencyDocuments',
                             related_name='related_protocol', blank=True)
    function_limitation = models.JSONField(null=True, blank=True)  # первое - функция и уровни с таблицы

    # FunctionAndLevelForPosition,  2- ограничение. [{"id_func": 166, "id_limit": [153]}]
    _sailor = fields.IntegerPGPSymmetricKeyField(null=True, default=None)
    date_end = models.DateField(null=True, blank=True)
    is_printeble = models.BooleanField(default=True)
    document_file_docx = models.FileField(upload_to=get_upload_path_protocol, null=True, blank=True)
    document_file_pdf = models.FileField(upload_to=get_upload_path_protocol, null=True, blank=True)
    vchasno_id = models.CharField(max_length=200, null=True, blank=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='protocol_documents')

    @property
    def get_is_cadet(self):
        return self.statement_dkk.is_cadet

    @property
    def get_committe_head_full_name(self):
        if self.commissioner_sign.filter(commissioner_type='HD').exists():
            committe_head = self.commissioner_sign.filter(commissioner_type='HD').first().signer.name
        else:
            committe_head = ''
        return committe_head

    @property
    def get_commissioners_full_name(self):
        commissioners_name = list(self.commissioner_sign.filter(commissioner_type='CH').
                                  values_list('signer__name', flat=True))
        all_commissioners = ', '.join(filter(None, commissioners_name))
        return all_commissioners

    @property
    def downloadable_with_sign(self):
        from signature.models import CommissionerSignProtocol
        if self.vchasno_id and CommissionerSignProtocol.objects.filter(protocol_dkk_id=self.pk,
                                                                       is_signatured=True).exists() is True:
            return True
        return False

    @property
    def sailor(self):
        if not self._sailor:
            return self.statement_dkk.sailor
        return self._sailor

    @property
    def create_date(self):
        return self.created_at.strftime('%d.%m.%Y')

    @property
    def statement_number(self):
        return self.statement_dkk.get_number

    @property
    def branch(self):
        return self.branch_create.name_ukr

    @property
    def sailor_full_name(self):
        return self.profile.get_full_name_ukr

    @property
    def sailor_birth_date(self):
        return self.profile.date_birth.strftime('%d.%m.%Y')

    @property
    def protocol_decision(self):
        return self.decision.name_ukr

    @property
    def positions(self):
        statement_dkk = self.statement_dkk
        if statement_dkk:
            position = statement_dkk.list_positions
            return '; '.join(list(Position.objects.filter(id__in=position).values_list('name_ukr', flat=True)))
        return ''

    @property
    def rank_name(self):
        statement_dkk = self.statement_dkk
        if statement_dkk:
            rank = statement_dkk.rank.name_ukr
            return rank
        return ''

    @property
    def get_number(self):
        direction_abbr = self.statement_dkk.rank.direction.value_abbr
        code_branch = self.branch_create.code_branch
        return '{}/{}/{}-{}'.format(self.number_document, self.date_meeting.year, code_branch, direction_abbr)

    @property
    def get_position(self):
        statement_dkk = self.statement_dkk
        if statement_dkk:
            position = statement_dkk.list_positions
            return list(Position.objects.filter(id__in=position).values('id', 'name_ukr', 'name_eng'))
        else:
            return {}

    @property
    def get_rank(self):
        statement_dkk = self.statement_dkk
        if statement_dkk:
            rank = statement_dkk.rank
            return {'id': rank.id, 'name_ukr': rank.name_ukr, 'name_eng': rank.name_eng}
        else:
            return {}

    @property
    def profile(self):
        if self.sailor:
            profile_id = SailorKeys.objects.filter(id=self.sailor).first().profile
            if not profile_id:
                return None
            return Profile.objects.filter(id=profile_id).first()
        elif self.statement_dkk:
            return self.statement_dkk.profile
        return None

    @property
    def is_exp_required(self):
        if self.statement_dkk.is_continue == 1:
            return False
        return ExperinceForDKK.objects.filter(position__in=self.statement_dkk.list_positions).exists()

    @property
    def is_exp_required_ukr(self):
        if self.is_exp_required:
            return 'Наявні'
        return 'Відсутні'

    @property
    def get_full_number_statement(self):
        return self.statement_dkk.get_number

    @property
    def _is_continue(self):
        if self.statement_dkk.rank.type_rank_id == 3:
            return True
        return self.statement_dkk.is_continue

    @property
    def _document_property(self):
        assign = (not (bool(self.statement_dkk.is_continue) and self.statement_dkk.rank.type_rank_id == 21)
                  and self.decision_id == 1)
        not_tankers = self.statement_dkk.rank.direction_id != 7
        not_assign = (not (bool(self.statement_dkk.is_continue) and self.statement_dkk.rank.type_rank_id == 21)
                      and self.decision_id == 2)
        confirm = ((bool(self.statement_dkk.is_continue) or self.statement_dkk.rank.type_rank_id == 3) and
                   self.decision_id == 1)
        not_confirm = ((bool(self.statement_dkk.is_continue) or self.statement_dkk.rank.type_rank_id == 3) and
                       self.decision_id == 2)
        give = (self.statement_dkk.rank.direction_id == 7 and self.decision_id == 1)
        not_give = (self.statement_dkk.rank.direction_id == 7 and self.decision_id == 2)
        if assign and not_tankers:
            return 'assign'
        elif not_assign and not_tankers:
            return 'not_assign'
        elif confirm and not_tankers:
            return 'confirm'
        elif not_confirm and not_tankers:
            return 'not_confirm'
        elif give and not not_tankers:
            return 'give'
        elif not_give and not not_tankers:
            return 'not_give'

    @property
    def _document_property_name(self):
        converter_to_human = {'assign': 'Присвоїти',
                              'not_assign': 'Не присвоїти',
                              'confirm': 'Підтвердити',
                              'not_confirm': 'Не підтвердити',
                              'give': 'Видати',
                              'not_give': 'Не видати'}
        return converter_to_human[self._document_property]

    @property
    def get_info_for_statement(self):
        return {'number': self.get_number, 'name_issued': self.branch,
                'date_start': self.date_meeting, 'date_end': self.date_end,
                'info': '{} {}'.format(self.rank_name, self.positions),
                'type_doc': 'Протокол ДКК', 'is_verification': False,
                'id': self.pk, 'content_type': self._meta.model_name}


class CertificateETI(GetAuthorMixin, DateTimesABC):
    TYPE_OF_ACCRUAL = 12
    TYPE_OF_STUDENT = 12

    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    ntz = models.ForeignKey('directory.NTZ', on_delete=models.PROTECT, null=True, blank=True)
    ntz_number = models.BigIntegerField()
    course_training = models.ForeignKey('directory.Course', on_delete=models.PROTECT, null=True,
                                        blank=True)  # напрям подготовки
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT, null=True, blank=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='cert_item')
    is_red = models.BooleanField(default=False)
    statement = models.OneToOneField('statement.StatementETI', on_delete=models.SET_NULL, null=True)
    photo = fields.CharPGPSymmetricKeyField(max_length=250, null=True, blank=True)
    is_only_dpd = models.BooleanField(default=False)

    @property
    def get_info_for_statement(self):
        is_verification = False
        if self.status_document_id in [magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT]:
            is_verification = True
        from sailor.misc import get_date_or_none
        return {'number': self.ntz_number, 'name_issued': self.ntz.name_ukr,
                'date_start': get_date_or_none(self.date_start),
                'date_end': get_date_or_none(self.date_end),
                'info': self.course_training.name_ukr, 'type_doc': 'НТЗ', 'is_verification': is_verification,
                'id': self.pk, 'content_type': self._meta.model_name}

    @property
    def institution_name_ukr(self):
        return self.ntz.name_ukr

    @property
    def course_name_ukr(self):
        return self.course_training.name_ukr

    @property
    def status(self):
        return self.status_document.name_ukr

    @property
    def start_date(self):
        try:
            return self.date_start.strftime('%d.%m.%Y')
        except AttributeError:
            return ''

    @property
    def end_date(self):
        try:
            return self.date_end.strftime('%d.%m.%Y')
        except AttributeError:
            return ''

    @property
    def profile(self):
        try:
            sailor = SailorKeys.objects.filter(sertificate_ntz__overlap=[self.id]).first()
            profile_id = sailor.profile
        except AttributeError:
            return None
        if not profile_id:
            return None
        return Profile.objects.filter(id=profile_id).annotate(
            sailor=models.Value(sailor.id, output_field=models.IntegerField())
        ).first()

    @property
    def sailor_full_name(self):
        return self.profile.get_full_name_ukr

    @property
    def sailor_birth_date(self):
        return self.profile.date_birth.strftime('%d.%m.%Y')

    @property
    def sailor_id(self):
        return self.profile.sailor

    @property
    def number(self):
        return self.ntz_number

    @property
    def date_for_report(self):
        return self.date_start.strftime('%d-%m-%Y')


class MedicalCertificate(GetAuthorMixin, AuthorDocumentABC, DateTimesABC):
    TYPE_OF_ACCRUAL = 7
    TYPE_OF_STUDENT = 7

    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    number = models.IntegerField()
    position = models.ForeignKey('directory.PositionForMedical', on_delete=models.PROTECT)
    limitation = models.ForeignKey('directory.LimitationForMedical', on_delete=models.PROTECT, null=True, blank=True)
    date_end = models.DateField()
    date_start = models.DateField()
    photo = fields.CharPGPSymmetricKeyField(max_length=200, blank=True, null=True)
    doctor = models.ForeignKey('directory.DoctrorInMedicalInstitution', on_delete=models.PROTECT)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    medical_statement = models.OneToOneField('statement.StatementMedicalCertificate', on_delete=models.PROTECT,
                                             null=True, blank=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='medical_cert_item')
    verification_status = GenericRelation('sailor.DocumentInVerification',
                                          related_query_name='medical_cert_verification')

    class Meta:
        verbose_name = 'Медична справка'

    @property
    def get_info_for_statement(self):
        from sailor.misc import get_date_or_none
        is_verification = False
        if self.status_document_id in [magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT]:
            is_verification = True
        return {'number': self.number, 'name_issued': self.doctor.FIO,
                'date_start': get_date_or_none(self.date_start), 'date_end': get_date_or_none(self.date_end),
                'info': self.position.name_ukr, 'type_doc': 'Медичне свідоцтво', 'is_verification': is_verification,
                'id': self.pk, 'content_type': self._meta.model_name}

    @property
    def get_number(self):
        return self.number

    @property
    def verification_info(self):
        sailor = SailorKeys.by_document.id(instance=self)
        if not sailor:
            return None
        return {
            'id': self.pk, 'type_document': self._meta.verbose_name, 'issued': self.doctor.FIO,
            'number': self.get_number, 'sailor': sailor.pk, 'content_type': self._meta.model_name
        }

    @property
    def profile(self):
        sailor = SailorKeys.objects.filter(medical_sertificate__overlap=[self.id]).first()
        profile_id = sailor.profile
        if not profile_id:
            return None
        return Profile.objects.filter(id=profile_id).annotate(
            sailor=models.Value(sailor.id, output_field=models.IntegerField())
        ).first()

    @property
    def sailor_full_name(self):
        return self.profile.get_full_name_ukr

    @property
    def sailor_id(self):
        return self.profile.sailor


class QualificationDocument(GetAuthorMixin, AuthorDocumentABC, DateTimesABC):
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    TYPE_OF_ACCRUAL = 3
    TYPE_OF_ACCRUAL_STUDENT = 21

    country = models.ForeignKey('directory.Country', on_delete=models.PROTECT, default=2)
    number_document = models.BigIntegerField(null=True, blank=True)
    other_number = models.CharField(max_length=50, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    list_positions = postgresfields.ArrayField(models.IntegerField(), default=list)
    rank = models.ForeignKey('directory.Rank', on_delete=models.DO_NOTHING)
    date_start = models.DateField()
    date_end = models.DateField(null=True, blank=True)
    type_document = models.ForeignKey('directory.TypeDocument', on_delete=models.PROTECT)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    statement = models.ForeignKey('statement.StatementQualification',
                                  on_delete=models.PROTECT, null=True, blank=True)
    port = models.ForeignKey('directory.Port', on_delete=models.PROTECT, null=True, blank=True)
    other_port = models.CharField(max_length=250, null=True, blank=True)
    fio_captain_ukr = models.CharField(max_length=200, null=True, blank=True)
    fio_captain_eng = models.CharField(max_length=200, null=True, blank=True)
    new_document = models.BooleanField(default=True)
    function_limitation = models.JSONField(null=True, blank=True)  # первое - функция и уровни с таблицы
    # FunctionAndLevelForPosition,  2- ограничение. [{"id_func": 166, "id_limit": [153]}]
    strict_blank = models.CharField(max_length=30, null=True, blank=True)

    related_docs = GM2MField('document.Education', 'document.CertificateETI', 'document.QualificationDocument',
                             'document.ProofOfWorkDiploma', 'document.MedicalCertificate', 'sailor.DependencyDocuments',
                             related_name='related_qualification',
                             blank=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='qualification_documents')
    verification_status = GenericRelation('sailor.DocumentInVerification',
                                          related_query_name='qual_doc_verification')

    class Meta:
        verbose_name = 'Кваліфікаційний документ'
        permissions = (
            ('merge_qualification_documents', 'Слитие квалификационных документов'),
        )
        ordering = ['-created_at', '-modified_at']

    @property
    def sailor_id(self):
        sailor = SailorKeys.objects.filter(qualification_documents__overlap=[self.id]).first()
        if not sailor:
            return None
        return sailor.id

    @property
    def profile(self):
        sailor = SailorKeys.objects.filter(qualification_documents__overlap=[self.id]).first()
        profile_id = sailor.profile
        if not profile_id:
            return None
        return Profile.objects.filter(id=profile_id).annotate(
            sailor=models.Value(sailor.id, output_field=models.IntegerField())
        ).first()

    @property
    def get_number(self):
        if not self.number_document:
            return self.other_number
        if not self.port and self.number_document:
            return str(self.number_document).zfill(5)
        return f'{str(self.number_document).zfill(5)}/{self.date_start.year}/{self.port.code_port}'

    @property
    def get_info_for_statement(self):
        if self.port:
            port_name_ukr = self.port.name_ukr
        else:
            port_name_ukr = self.other_port
        is_verification = False
        if self.status_document_id in [magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT]:
            is_verification = True
        from sailor.misc import get_date_or_none
        return {'number': self.get_number, 'name_issued': port_name_ukr,
                'date_start': get_date_or_none(self.date_start), 'date_end': get_date_or_none(self.date_end),
                'info': f'{self.type_document.name_ukr} {self.rank.name_ukr}',
                'type_doc': 'Кваліфікаційний документ', 'is_verification': is_verification,
                'id': self.pk, 'content_type': self._meta.model_name}

    @property
    def get_position(self):
        position = self.list_positions
        if position:
            return list(Position.objects.filter(id__in=position).values('id', 'name_ukr', 'name_eng'))
        return {}

    @property
    def get_rank(self):
        rank = self.rank
        if rank:
            return {'id': rank.id, 'name_ukr': rank.name_ukr, 'name_eng': rank.name_eng}
        else:
            return {}

    @property
    def get_type_document(self):
        type_document = self.type_document
        if type_document:
            return {'id': type_document.id, 'name_ukr': type_document.name_ukr, 'name_eng': type_document.name_eng}
        else:
            return {}

    @property
    def sailor_full_name(self):
        return self.profile.get_full_name_ukr

    @property
    def sailor_birth_date(self):
        return self.profile.date_birth.strftime('%d.%m.%Y')

    @property
    def port_ukr(self):
        if not self.port:
            return None
        return self.port.name_ukr

    @property
    def other_port_name(self):
        return self.other_port

    @property
    def rank_name(self):
        return self.rank.name_ukr

    @property
    def positions(self):
        return '; '.join(list(Position.objects.filter(id__in=self.list_positions).values_list('name_ukr', flat=True)))

    @property
    def start_date(self):
        return self.date_start.strftime('%d.%m.%Y')

    @property
    def end_date(self):
        if not self.date_end:
            return None
        return self.date_end.strftime('%d.%m.%Y')

    @property
    def status_ukr(self):
        return self.status_document.name_ukr

    @property
    def type_document_name(self):
        if self.get_type_document:
            return self.get_type_document['name_ukr']
        return None

    @property
    def verification_info(self):
        sailor = SailorKeys.by_document.id(instance=self)
        if not sailor:
            return None
        return {
            'id': self.pk, 'type_document': self._meta.verbose_name, 'issued': self.port_ukr,
            'number': self.get_number, 'sailor': sailor.pk, 'content_type': self._meta.model_name
        }

    @classmethod
    def generate_number(cls, year_of_issue, port_id, type_document_id):
        filtering_type_doc = [49, 1] if type_document_id in [49, 1] else [87, 89, 88, 88, 57, 86, 85, 21]
        last_number = cls.objects.filter(
            date_start__year=int(year_of_issue),
            port_id=port_id,
            type_document_id__in=filtering_type_doc,
            status_document_id__in=[19, 21, 18, 7]
        ).aggregate(number_doc=Max('number_document'))['number_doc'] or 0
        return last_number + 1


class ProofOfWorkDiploma(GetAuthorMixin, AuthorDocumentABC, DateTimesABC):
    TYPE_OF_ACCRUAL = 4
    TYPE_OF_ACCRUAL_STUDENT = 22

    diploma = models.ForeignKey('document.QualificationDocument', on_delete=models.CASCADE)
    number_document = models.BigIntegerField(null=True, blank=True)
    other_number = models.CharField(max_length=50, null=True, blank=True)
    date_start = models.DateField()
    date_end = models.DateField()
    photo = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    is_continue = models.IntegerField(default=0)
    port = models.ForeignKey('directory.Port', on_delete=models.PROTECT, null=True, blank=True)
    other_port = models.CharField(max_length=250, null=True, blank=True)
    fio_captain_ukr = models.CharField(max_length=200, null=True, blank=True)
    fio_captain_eng = models.CharField(max_length=200, null=True, blank=True)
    statement = models.ForeignKey('statement.StatementQualification', on_delete=models.SET_NULL, null=True,
                                  blank=True)
    strict_blank = models.CharField(max_length=30, null=True, blank=True)
    function_limitation = models.JSONField(null=True, blank=True)
    diploma_year = models.DateField(default=date.today)
    items = GenericRelation('back_office.DependencyItem', related_query_name='proof_documents')
    verification_status = GenericRelation('sailor.DocumentInVerification',
                                          related_query_name='proof_diploma_verification')

    class Meta:
        verbose_name = 'Підтвердження к диплому'

    @property
    def get_city(self):
        country = {'id': self.diploma.country.id, 'name': self.diploma.country.value,
                   'name_eng': self.diploma.country.value_eng,
                   'value_abbr': self.diploma.country.value_abbr}
        return country

    @property
    def get_list_positions(self):
        if getattr(self, 'statement') and getattr(self.statement, 'protocol_dkk'):
            positions = self.statement.protocol_dkk.statement_dkk.list_positions
        else:
            positions = self.diploma.list_positions
        return positions

    @property
    def get_position(self):
        positions = self.get_list_positions
        if positions:
            positions = Position.objects.filter(id__in=positions)
            return list(positions.values('id', 'name_ukr', 'name_eng'))
        else:
            return {}

    @property
    def get_rank(self):
        rank = self.diploma.rank
        return {'id': rank.id, 'name_ukr': rank.name_ukr, 'name_eng': rank.name_eng}

    @property
    def get_type_document(self):
        type_doc = {'id': 16, 'name_ukr': 'Підтвердження робочого диплому',
                    'name_eng': 'Підтвердження робочого диплому'}
        return type_doc

    @property
    def get_number(self):
        if self.diploma.country_id != 2:
            return self.number_document or self.other_number
        if self.number_document:
            if not self.diploma.port_id:
                return '{}/{}'.format(str(self.number_document).zfill(5), self.diploma.date_start.year)
            return '{}/{}/{}'.format(str(self.number_document).zfill(5), self.diploma.date_start.year,
                                     self.diploma.port.code_port)
        else:
            return self.other_number

    @property
    def get_info_for_statement(self):
        is_verification = False
        if self.status_document_id in [magic_numbers.VERIFICATION_STATUS, magic_numbers.STATUS_CREATED_BY_AGENT]:
            is_verification = True
        from ..misc import get_date_or_none
        return {'number': self.get_number, 'name_issued': self.port.name_ukr if self.port else self.other_port,
                'date_start': get_date_or_none(self.date_start), 'date_end': get_date_or_none(self.date_end),
                'info': '{}'.format(self.diploma.rank.name_ukr), 'type_doc': 'Підтвердження к диплому',
                'is_verification': is_verification, 'id': self.pk, 'content_type': self._meta.model_name}

    @property
    def sailor_id(self):
        sailor = SailorKeys.objects.filter(qualification_documents__overlap=[self.diploma_id]).first()
        if not sailor:
            return None
        return sailor.id

    @property
    def profile(self):
        sailor = SailorKeys.objects.filter(qualification_documents__overlap=[self.diploma_id]).first()
        profile_id = sailor.profile
        if not profile_id:
            return None
        return Profile.objects.filter(id=profile_id).annotate(
            sailor=models.Value(sailor.id, output_field=models.IntegerField())
        ).first()

    @property
    def sailor_full_name(self):
        return self.profile.get_full_name_ukr

    @property
    def sailor_birth_date(self):
        return self.profile.date_birth.strftime('%d.%m.%Y')

    @property
    def port_ukr(self):
        if not self.port:
            return None
        return self.port.name_ukr

    @property
    def other_port_name(self):
        return self.other_port

    @property
    def rank_name(self):
        return self.diploma.rank.name_ukr

    @property
    def positions(self):
        return '; '.join(list(Position.objects.filter(id__in=self.get_list_positions
                                                      ).values_list('name_ukr', flat=True)))

    @property
    def start_date(self):
        return self.date_start.strftime('%d.%m.%Y')

    @property
    def end_date(self):
        if not self.date_end:
            return None
        return self.date_end.strftime('%d.%m.%Y')

    @property
    def status_ukr(self):
        return self.status_document.name_ukr

    @property
    def type_document_name(self):
        return self.get_type_document['name_ukr']

    def save(self, *args, **kwargs):
        self.number_document = self.diploma.number_document
        self.other_number = self.diploma.other_number
        super(ProofOfWorkDiploma, self).save(*args, **kwargs)

    @property
    def verification_info(self):
        sailor = SailorKeys.by_document.id(instance=self)
        if not sailor:
            return None
        return {
            'id': self.pk, 'type_document': self._meta.verbose_name, 'issued': self.port_ukr,
            'number': self.get_number, 'sailor': sailor.pk, 'content_type': self._meta.model_name
        }


class ResponsibilityServiceRecord(DateTimesABC):
    """
    Внесенные в ПКМ интеравалы времени или дни отработанные моряком в рейсе на разных обязанностях
    """
    service_record_line = models.ForeignKey('document.LineInServiceRecord', on_delete=models.PROTECT,
                                            related_name='service_record_line')
    responsibility = models.ForeignKey('directory.Responsibility', on_delete=models.PROTECT, null=True, blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    days_work = models.IntegerField(null=True, blank=True)
    is_repaired = models.BooleanField(default=False)  # судно выведено в ремонт

    class Meta:
        ordering = ['date_from']
