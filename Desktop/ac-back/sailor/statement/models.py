from datetime import date

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as postgresfield
from django.core.cache import cache
from django.db import models
from django.db.models import Max
from gm2m import GM2MField
from pgcrypto import fields

from back_office.models import DependencyItem
from communication.models import SailorKeys
from directory.models import Position, ExperinceForDKK
from itcs import magic_numbers
from sailor.document.models import ProtocolSQC
from sailor.managers import BySailorManager, BySailorQuerySet
from sailor.models import AuthorDocumentABC, Profile, SailorPassport, DateTimesABC
from user_profile.mixins import GetAuthorMixin
from user_profile.models import UserProfile


class StatementServiceRecord(AuthorDocumentABC, DateTimesABC):
    """
    Заявка на ПКМ
    """
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    sailor = fields.IntegerPGPSymmetricKeyField()
    status = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True)
    delivery = GenericForeignKey('content_type', 'object_id')
    photo = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)
    is_payed = models.BooleanField(default=False)

    @property
    def profile(self):
        sailor = SailorKeys.objects.get(id=self.sailor)
        profile_id = sailor.profile
        if not profile_id:
            return None
        return Profile.objects.filter(id=profile_id).annotate(
            sailor=models.Value(sailor.id, output_field=models.IntegerField())
        ).first()

    @property
    def get_sailor_ukr(self):
        if self.profile is None:
            return None
        return {'last_name': self.profile.last_name_ukr, 'first_name': self.profile.first_name_ukr,
                'middle_name': self.profile.middle_name_ukr}


class StatementAdvancedTraining(AuthorDocumentABC, DateTimesABC):
    """
    Заявление на свидетельство о повышения квалификации
    """
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    number = models.IntegerField()
    level_qualification = models.ForeignKey('directory.LevelQualification', on_delete=models.PROTECT)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    educational_institution = models.ForeignKey('directory.NZ', on_delete=models.PROTECT)
    is_payed = models.BooleanField(default=False)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, blank=True, null=True)
    date_meeting = models.DateField(null=True)
    date_end_meeting = models.DateField(null=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='adv_training_item')

    class Meta:
        verbose_name = 'Заява на свідоцтво про підвищення кваліфікації'
        ordering = ['-created_at', '-modified_at']
        permissions = (
            ('createAdvancedTraining', 'Создание документа СПК из заявления СПК'),
            ('readReportApplicationATC', 'Просмотр отчета по заявлениям КПК'),
        )

    @classmethod
    def generate_number(cls):
        number = cls.objects.aggregate(number=Max('number'))['number'] or 0
        number += 1
        return number

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.number:
            self.number = self.generate_number()
        super().save(force_insert, force_update, using, update_fields)

    @property
    def get_info_for_statement(self):
        return {'number': self.number, 'name_issued': self.educational_institution.name_ukr,
                'date_start': self.date_meeting,
                'date_end': self.date_end_meeting, 'info': self.level_qualification.name_ukr,
                'type_doc': 'Заява на свідоцтво підвищення кваліфікації', 'is_verification': False,
                'id': self.pk, 'content_type': self._meta.model_name}


class StatementMedicalCertificate(AuthorDocumentABC, DateTimesABC):
    """
    Заявление на мед свидетельство
    """
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    number = models.IntegerField()
    position = models.ForeignKey('directory.PositionForMedical', on_delete=models.PROTECT)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    medical_institution = models.ForeignKey('directory.MedicalInstitution', on_delete=models.PROTECT)
    is_payed = models.BooleanField(default=False)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, blank=True, null=True)
    date_meeting = models.DateField(null=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='statement_medical_cert_item')

    class Meta:
        verbose_name = 'Заява на медичне свідоцтво'
        ordering = ['-created_at', '-modified_at']

    @classmethod
    def generate_number(cls):
        number = cls.objects.aggregate(number=Max('number'))['number'] or 0
        number += 1
        return number

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.number:
            self.number = self.generate_number()
        super(StatementMedicalCertificate, self).save(force_insert=force_insert, force_update=force_update,
                                                      using=using, update_fields=update_fields)

    @property
    def date_end_meeting(self):
        return self.date_meeting

    @property
    def get_info_for_statement(self):
        return {'number': self.number, 'name_issued': self.medical_institution.value,
                'date_start': self.date_meeting,
                'date_end': self.date_end_meeting, 'info': self.position.name_ukr,
                'type_doc': 'Заява на медичне свідоцтво', 'is_verification': False,
                'id': self.pk, 'content_type': self._meta.model_name}

    @property
    def get_number(self):
        return self.number


class StatementSQC(GetAuthorMixin, AuthorDocumentABC, DateTimesABC):
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    number = models.IntegerField()
    is_payed = models.BooleanField(default=False)
    sailor = fields.IntegerPGPSymmetricKeyField()  # так нужно для проверки документов
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    rank = models.ForeignKey('directory.Rank', on_delete=models.PROTECT)
    list_positions = postgresfield.ArrayField(models.IntegerField())
    type_document = models.ForeignKey('directory.TypeDocument', on_delete=models.CASCADE, null=True, blank=True)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    branch_office = models.ForeignKey('directory.BranchOffice', on_delete=models.PROTECT)
    is_continue = models.IntegerField(default=0)
    on_create_rank = models.ManyToManyField('directory.Rank', related_name='on_create_rank')
    related_docs = GM2MField('document.Education', 'document.CertificateETI',
                             'document.QualificationDocument', 'document.ProofOfWorkDiploma',
                             'document.MedicalCertificate',
                             'sailor.DependencyDocuments',
                             related_name='related_state_pr', blank=True)
    userexam_id = models.IntegerField(null=True, blank=True)
    is_cadet = models.BooleanField(default=False)
    date_meeting = models.DateField(null=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='statement_sqc_item')
    is_etransport_pay = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ('writeApplicationSQCStatusRejected', 'Can change status statemnt SQC on "Rejected"'),
        )

    @classmethod
    def generate_number(cls):
        excl = [654369, 654354, 654385, 654374, 654381, 654391, 654390, 654392, 654393, 654397, 654399, 654398, 654394,
                654396, 654395, 654400, 654404, 654406, 654426, 654403, 654407, 654428, 654427, 654434, 654438, 654439,
                654452, 654445, 654446, 654444, 654447, 654448, 654449, 654454, 654453, 654464, 654461, 654465, 654470,
                654489, 654498, 654486, 654496, 654501, 654499, 654502, 654505, 654506, 654504, 654507, 654518, 654520,
                654522, 654521, 654532, 654525, 654530, 654531, 654533, 654534, 654544, 654547, 654548, 654549, 654543,
                654535, 654550, 654536, 654537, 654538, 654539, 654540, 654541, 654542, 654551, 654554, 654555, 654556,
                654557, 654558, 654561, 654559, 654560, 654562, 654563, 654567, 654564, 654565, 654566, 654503, 654376,
                654450, 654455, 654529, 654476, 673592, 673591, 673594, 673593, 673595, 673603]
        number = cls.objects.filter(created_at__year=date.today().year).exclude(
            status_document_id=16).exclude(id__in=excl).aggregate(
            number=Max('number'))['number'] or 0
        number += 1
        return number

    @property
    def date_end_meeting(self):
        return self.date_meeting

    @property
    def get_status_position(self):
        from sailor.misc import CheckSailorForPositionDKK, generate_number_statement_dkk, CheckSailorExperience
        sailor_id = self.sailor
        documents_exists = []
        packet = self.items.first().packet_item \
            if (self.items.exists() and
                self.status_document_id == magic_numbers.STATUS_CREATED_BY_AGENT) \
            else None
        is_packet = True if (packet and not packet.education_with_sqc
                             and packet.agent.userprofile.type_user != UserProfile.MARAD) \
            else False
        checking = CheckSailorForPositionDKK(sailor=sailor_id, is_continue=self.is_continue,
                                             list_position=self.list_positions, packet=is_packet)
        if self.related_docs.exists():
            cache_value = cache.get(f'exists_{sailor_id}_{self.list_positions}_{self.is_continue}_{self.number}')
            if cache_value:
                documents_exists = cache_value
            else:
                for document in self.related_docs.all().exclude(gm2m_ct_id__in=[46, 68, 50]):
                    info_doc = document.get_info_for_statement
                    documents_exists.append(info_doc)
                cache.set(f'exists_{sailor_id}_{self.list_positions}_{self.is_continue}_{self.number}', documents_exists,
                          60 * 15)
            have_all_docs = True
            documents = []
            not_have_educ_doc = False
        else:
            documents_full = checking.get_docs_with_status()
            documents = documents_full['descr']
            have_all_docs = documents_full['have_all_doc']
            documents_exists = documents_full['exists_doc']
            not_have_educ_doc = documents_full['not_have_educ_doc']
            if have_all_docs and hasattr(self, 'protocolsqc'):
                protocol = self.protocolsqc
                all_docs = documents_full.get('all_docs', [])
                self.related_docs = all_docs
                protocol.related_docs = all_docs
        if self.is_continue in [0, 2]:
            checking_exp = CheckSailorExperience(sailor=sailor_id, list_position=self.list_positions)
            experience = checking_exp.check_experience_many_pos()
            if experience:
                have_all_exp = any(exp['value'] for exp in experience)
            else:
                have_all_exp = False
        else:
            from sailor.misc import check_continue_for_experience
            position_qual_doc = self.profile.get_position_from_qual
            if not position_qual_doc:
                ids_positions_in_qual_doc = []
            else:
                ids_positions_in_qual_doc = [doc['id'] for doc in position_qual_doc]
            check_exp = check_continue_for_experience(
                list_positions=self.list_positions, rank_id=self.rank_id,
                ids_positions_in_qual_doc=ids_positions_in_qual_doc)
            if check_exp['is_check_exp']:
                checking_exp = CheckSailorExperience(sailor=sailor_id, list_position=check_exp['list_positions'])
                experience = checking_exp.check_experience_many_pos()
                if experience:
                    have_all_exp = any(exp['value'] for exp in experience)
                else:
                    have_all_exp = False
            else:
                have_all_exp = True
                experience = []
        if (have_all_docs is True and have_all_exp is True and
                self.status_document_id == magic_numbers.status_state_qual_dkk_absense):
            self.status_document_id = magic_numbers.status_state_qual_dkk_in_process
            self.number = generate_number_statement_dkk()
            self.save(update_fields=['status_document', 'number'])
        elif ((have_all_docs is True and have_all_exp is True
               and self.status_document_id == magic_numbers.CREATED_FROM_PERSONAL_CABINET) or
              (not_have_educ_doc and self.is_cadet and self.rank.id in [23, 86, 90]
               and self.status_document_id == magic_numbers.CREATED_FROM_PERSONAL_CABINET)):
            self.status_document_id = magic_numbers.status_state_qual_dkk_in_process
            self.save(update_fields=['status_document'])
        if have_all_docs is True and have_all_exp is True and self.status_document_id == magic_numbers.status_cadets_state_dkk_allowed:
            try:
                self.protocolsqc.is_printeble = True
                self.protocolsqc.save(update_fields=['is_printeble'])
            except ProtocolSQC.DoesNotExist:
                pass
        return {'documents': documents, 'experince': experience, 'have_all_docs': have_all_docs,
                'have_all_exp': have_all_exp, 'exists_docs': documents_exists, 'not_have_educ_doc': not_have_educ_doc}

    @property
    def branch(self):
        return self.branch_office.name_ukr

    @property
    def get_number(self):
        if self.status_document_id == 16:
            return ''
        else:
            return '{}/{}/{}-{}'.format(
                str(self.number).zfill(5),
                self.created_at.year,
                self.branch_office.code_branch,
                self.rank.direction.value_abbr
            )

    @property
    def profile(self):
        if self.sailor:
            profile_id = SailorKeys.objects.filter(id=self.sailor).first().profile
            if not profile_id:
                return None
            return Profile.objects.filter(id=profile_id).first()
        return None

    @property
    def get_position(self):
        if self.list_positions:
            return list(Position.objects.filter(id__in=self.list_positions).values('id', 'name_ukr', 'name_eng'))
        return []

    @property
    def protocol_number(self):
        try:
            if self.protocolsqc:
                return self.protocolsqc.get_number
        except Exception:
            pass
        return None

    @property
    def have_protocol(self):
        return hasattr(self, 'protocolsqc')

    @property
    def is_exp_required(self):
        if self.is_continue == 1:
            return False
        return ExperinceForDKK.objects.filter(position__in=self.list_positions).exists()

    @property
    def is_exp_required_ukr(self):
        if self.is_exp_required:
            return 'Наявні'
        return 'Відсутні'

    @property
    def create_date(self):
        return self.created_at.strftime('%d.%m.%Y')

    @property
    def sailor_full_name(self):
        return self.profile.get_full_name_ukr

    @property
    def sailor_birth_date(self):
        return self.profile.date_birth.strftime('%d.%m.%Y')

    @property
    def positions(self):
        list_positions = self.list_positions
        if list_positions:
            return '; '.join(list(Position.objects.filter(id__in=list_positions).values_list('name_ukr', flat=True)))
        return ''

    @property
    def rank_name(self):
        rank = self.rank
        if rank:
            return rank.name_ukr
        return ''

    @property
    def status_ukr(self):
        return self.status_document.name_ukr

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.number:
            self.number = self.generate_number()
        super().save(force_insert, force_update, using, update_fields)

    @property
    def disabled_dated(self):
        if not self.items.exists():
            return None
        dated = []
        sailor = SailorKeys.objects.get(id=self.sailor)
        dependencies = DependencyItem.objects.filter(
            packet_item_id__in=sailor.packet_item,
            content_type__model__in=['statementeti', 'statementadvancedtraining', 'statementmedicalcertificate',
                                     'statementsailorpassport', 'statementservicerecord',
                                     'statementqualification',
                                     'statementmedicalcertificate', 'statementsqc']). \
            exclude(content_type__model='statementsqc', object_id=self.pk)
        for dependency in dependencies:
            dated.append((dependency.item.date_meeting, dependency.item.date_end_meeting))
        return dated
        # self.items.

    @property
    def get_info_for_statement(self):
        is_verification = False
        info = '{} / {}'.format(self.rank_name, self.positions)
        return {'number': self.get_number, 'name_issued': self.branch_office.name_ukr,
                'date_start': self.date_meeting,
                'date_end': self.date_meeting, 'info': info,
                'type_doc': 'Заява на ДКК', 'is_verification': is_verification,
                'id': self.pk, 'content_type': self._meta.model_name}

    @property
    def verification_info(self):
        return {
            'id': self.pk, 'type_document': 'Заява на ДКК', 'issued': self.branch_office.name_ukr,
            'number': self.get_number, 'sailor': self.sailor, 'content_type': self._meta.model_name,
        }


class StatementQualification(GetAuthorMixin, AuthorDocumentABC, DateTimesABC):
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    number = models.IntegerField()
    sailor = fields.IntegerPGPSymmetricKeyField()  # так нужно для проверки стажа
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    rank = models.ForeignKey('directory.Rank', on_delete=models.DO_NOTHING)
    list_positions = postgresfield.ArrayField(models.IntegerField())
    type_document = models.ForeignKey('directory.TypeDocument', on_delete=models.CASCADE, default=49)
    photo = fields.CharPGPSymmetricKeyField(null=True, blank=True, max_length=200)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    protocol_dkk = models.OneToOneField('document.ProtocolSQC', on_delete=models.PROTECT, null=True,
                                        blank=True)  # TODO RESTORE
    is_continue = models.IntegerField(default=0)
    port = models.ForeignKey('directory.Port', on_delete=models.PROTECT)
    is_payed = models.BooleanField(default=False)
    related_docs = GM2MField('document.Education', 'document.CertificateETI',
                             'document.QualificationDocument', 'document.ProofOfWorkDiploma',
                             'document.MedicalCertificate', 'sailor.DependencyDocuments',
                             related_name='related_state_qu', blank=True)
    date_meeting = models.DateField(null=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='statement_qual_doc_item')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.number:
            self.number = self.generate_number()
        super(StatementQualification, self).save(force_insert=force_insert, force_update=force_update,
                                                 using=using, update_fields=update_fields)

    @classmethod
    def generate_number(cls):
        number = cls.objects.filter(created_at__year=date.today().year). \
            exclude(status_document_id__in=[16, 74]).aggregate(number=Max('number'))['number']
        if not number:
            number = 0
        number += 1
        return number

    @property
    def get_status_position(self):
        from sailor.misc import CheckSailorForPositionDKK, CheckSailorExperience
        sailor = self.sailor
        documents_exists = []
        packet = self.items.first().packet_item \
            if (self.items.exists() and
                self.status_document_id == magic_numbers.STATUS_CREATED_BY_AGENT) \
            else None
        is_packet = True if packet and packet.agent.userprofile.type_user != UserProfile.MARAD else False
        checking = CheckSailorForPositionDKK(sailor=sailor, is_continue=self.is_continue,
                                             list_position=self.list_positions, packet=is_packet)
        if self.related_docs.exists():
            for document in self.related_docs.all().exclude(gm2m_ct_id__in=[46, 68, 50]):
                info_doc = document.get_info_for_statement
                info_doc['model_name'] = str(document._meta)
                documents_exists.append(info_doc)
            have_all_docs = True
            documents = []
        else:
            documents_full = checking.get_docs_with_status()
            documents = documents_full['descr']
            have_all_docs = documents_full['have_all_doc']
            documents_exists = documents_full['exists_doc']
            if have_all_docs:
                all_docs = documents_full.get('all_docs', [])
                self.related_docs = all_docs
        if self.is_continue in [0, 2]:
            checking_exp = CheckSailorExperience(sailor=sailor, list_position=self.list_positions)
            experince = checking_exp.check_experience_many_pos()
            if experince:
                have_all_exp = any(exp['value'] for exp in experince)
            else:
                have_all_exp = False
        else:
            experince = []
            have_all_exp = True
        if have_all_docs is True and self.status_document_id == magic_numbers.status_state_qual_dkk_absense:
            self.status_document_id = magic_numbers.status_state_qual_dkk_in_process
            self.save(update_fields=['status_document'])
        return {'documents': documents, 'experince': experince, 'have_all_docs': have_all_docs,
                'have_all_exp': have_all_exp, 'exists_docs': documents_exists}

    @property
    def get_full_response_position(self):
        from sailor.misc import CheckSailorForPositionDKK, CheckSailorExperience
        sailor = self.sailor
        checking = CheckSailorForPositionDKK(list_position=self.list_positions,
                                             sailor=sailor, is_continue=self.is_continue)
        documents = checking.get_docs_with_status()
        if self.is_continue in [0, 2]:
            checking_exp = CheckSailorExperience(sailor=sailor, list_position=self.list_positions)
            experince = checking_exp.check_experience_many_pos()
            if experince:
                have_all_exp = any(exp['value'] for exp in experince)
            else:
                experince = []
                have_all_exp = False
        else:
            have_all_exp = True
            experince = []
        have_all_docs = documents['have_all_doc']
        descr = documents['descr']
        if (have_all_docs is False) and self.status_document_id != 16:  # have_all_exp is False TODO ENABLE CHECK EXP
            self.status_document_id = 16
            self.save(update_fields=['status_document'])
        return {
            'documents': descr,
            'experince': experince,
            'have_all_docs': have_all_docs,
            'have_all_exp': have_all_exp
        }

    def get_full_response_position_docs(self):
        from sailor.misc import CheckSailorForPositionDKK, CheckSailorExperience
        sailor = self.sailor
        checking = CheckSailorForPositionDKK(list_position=self.list_positions,
                                             sailor=sailor, is_continue=self.is_continue)
        documents = checking.get_docs_with_status()
        if self.is_continue in [0, 2]:
            checking_exp = CheckSailorExperience(sailor=sailor, list_position=self.list_positions)
            experince = checking_exp.check_experience_many_pos()
            if experince:
                have_all_exp = any(exp['value'] for exp in experince)
            else:
                experince = []
                have_all_exp = False
        else:
            have_all_exp = True
            experince = []
        have_all_docs = documents['have_all_doc']
        descr = documents['descr']
        if (have_all_docs is False) and self.status_document_id != 16:  # have_all_exp is False TODO ENABLE CHECK EXP
            self.status_document_id = 16
            self.save(update_fields=['status_document'])
        return {
            'documents': descr,
            'experince': experince,
            'have_all_docs': have_all_docs,
            'have_all_exp': have_all_exp,
            'all_docs': documents.get('all_docs')
        }

    @property
    def get_number(self):
        if self.status_document_id != 16:
            return '{}/{}'.format(str(self.number).zfill(5), self.created_at.year)
        else:
            return ''

    @property
    def get_info_for_statement(self):
        return {'number': self.get_number, 'name_issued': self.port.name_ukr,
                'date_start': self.date_meeting,
                'date_end': self.date_meeting, 'info': self.rank.name_ukr,
                'type_doc': 'Заява на ДПВ', 'is_verification': False,
                'id': self.pk, 'content_type': self._meta.model_name}


class StatementETI(AuthorDocumentABC, DateTimesABC):
    """
    Заявления на прохождение курса в НТЗ
    """

    class StatusDocument:
        IN_PROCESS = 63
        REJECTED = 62
        APPROVED = 61
        CERTIFICATE_CREATED = 85
        COURSE_ASSIGNED = 90

    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    number = models.IntegerField()
    date_meeting = models.DateField(null=True, blank=True)
    course = models.ForeignKey('directory.Course', on_delete=models.PROTECT)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    institution = models.ForeignKey('directory.NTZ', on_delete=models.PROTECT)
    is_payed = models.BooleanField(default=False)
    date_end_meeting = models.DateField(null=True)
    is_continue = models.BooleanField(default=False)
    items = GenericRelation('back_office.DependencyItem', related_query_name='statement_eti_item')
    payments = GenericRelation('platon.PlatonPayments', related_query_name='statement_eti_payments')

    class Meta:
        ordering = ['-created_at', '-modified_at']
        verbose_name = 'Заява на НТЗ'
        permissions = (
            ('readReportApplicationETI', 'Просмотр отчета по заявлениям НТЗ'),
            ('readPaymentsETI', 'Просмотр информации по оплате заявлениий НТЗ'),
        )

    @classmethod
    def generate_number(cls):
        number = StatementETI.objects.aggregate(number=Max('number'))['number'] or 0
        number += 1
        return number

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.number:
            self.number = self.generate_number()
        super(StatementETI, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                       update_fields=update_fields)

    @property
    def get_info_for_statement(self):
        return {'number': self.number, 'name_issued': self.institution.name_ukr,
                'date_start': self.date_meeting,
                'date_end': self.date_end_meeting, 'info': self.course.name_ukr,
                'type_doc': 'Заява на НТЗ', 'is_verification': False,
                'id': self.pk, 'content_type': self._meta.model_name}

    @property
    def requisites(self):
        payment_due = self.course.name_ukr
        requisites = self.institution.requisites
        amount = 0
        dependency_item = self.items.first()
        if dependency_item:
            amount = dependency_item.get_price_form1
        return {'bank': requisites, 'payment_due': payment_due, 'amount': amount}

    @property
    def institution_name_ukr(self):
        return self.institution.name_ukr

    @property
    def course_name_ukr(self):
        return self.course.name_ukr

    @property
    def date_for_report(self):
        return self.date_meeting.strftime('%d-%m-%Y')


class StatementSailorPassport(GetAuthorMixin, AuthorDocumentABC, DateTimesABC):
    """
    Заявление на ПОМ
    """
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    class StatusDocument:
        APPROVED = 70
        REJECTED = 71
        IN_PROCESS = 72

    SAILOR_PASSPORT_CHOICES = (
        (1, 'Потрібна за 20 днів'),
        (2, 'Потрібна за 7 днів'),
        (3, 'Подовження за 20 днів'),
        (4, 'Подовження за 7 днів'),
    )

    number = models.IntegerField()
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    port = models.ForeignKey('directory.Port', on_delete=models.PROTECT)
    sailor_passport = models.ForeignKey(SailorPassport, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='statements')
    is_payed = models.BooleanField(default=False)
    is_continue = models.BooleanField(default=False)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, blank=True, null=True)
    date_meeting = models.DateField(null=True)
    is_payed_blank = models.BooleanField(default=False)
    fast_obtaining = models.BooleanField(default=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='sailor_passport_item')
    type_receipt = models.IntegerField(choices=SAILOR_PASSPORT_CHOICES, null=True)

    class Meta:
        verbose_name = 'Заява на посвідчення особи моряка'

    @classmethod
    def generate_number(cls):
        number = cls.objects.aggregate(number=Max('number'))['number'] or 0
        number += 1
        return number

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.number:
            self.number = self.generate_number()
        super(StatementSailorPassport, self).save(force_insert=force_insert, force_update=force_update,
                                                  using=using, update_fields=update_fields)

    @property
    def date_end_meeting(self):
        return self.date_meeting

    @property
    def get_info_for_statement(self):
        return {'number': self.number, 'name_issued': self.port.name_ukr,
                'date_start': self.date_meeting,
                'date_end': self.date_end_meeting, 'info': 'Заява на отримання посвідчення особи моряка',
                'type_doc': 'Заява на ПОМ', 'is_verification': False,
                'id': self.pk, 'content_type': self._meta.model_name}

    @property
    def type_of_accrual_rules_id(self):
        """
        Getter: first param in key is fast_obtaining, second in key is_continue
        """
        getter_type_of_accrual_rules = {(True, True): 13, (True, False): 14,
                                        (False, True): 6, (False, False): 5}
        return getter_type_of_accrual_rules[(self.fast_obtaining, self.is_continue)]
