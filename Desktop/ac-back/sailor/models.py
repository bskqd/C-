import os
from datetime import date
from itertools import chain

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as postgresfield
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from gm2m import GM2MField
from pgcrypto import fields

from communication.models import SailorKeys
from directory.models import (Position, VerificationStage)
from itcs import magic_numbers
from itcs.middleware import get_current_authenticated_user
from user_profile.mixins import GetAuthorMixin
from user_profile.models import UserProfile
from .managers import BySailorManager, BySailorQuerySet
User = get_user_model()

TYPE_RECORD = [('Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо',
                'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'),
               ('Довідка про стаж плавання', 'Довідка про стаж плавання')]


class AuthorDocumentABC(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, default=get_current_authenticated_user)

    class Meta:
        abstract = True


class DateTimesABC(models.Model):
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-created_at', '-modified_at']


def get_upload_path_protocol(instance, filename):
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


def get_upload_photo_path(instance, filename):
    today = date.today()
    return f'{today.year}/{today.month}/{today.day}/{filename}'


class ContactInfo(models.Model):
    type_contact = models.ForeignKey('directory.TypeContact', on_delete=models.PROTECT)
    value = models.CharField(max_length=200)
    is_actual = models.BooleanField(default=False)


class Passport(models.Model, GetAuthorMixin):
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    serial = models.CharField(max_length=30, default='')
    date = models.DateField(null=True, blank=True)
    issued_by = models.CharField(max_length=200, null=True, blank=True)
    photo = fields.TextPGPSymmetricKeyField(null=True, blank=True)
    country = models.ForeignKey('directory.Country', on_delete=models.PROTECT, default=2)
    city_registration = fields.IntegerPGPSymmetricKeyField(null=True, blank=True)  # прописка
    resident = fields.IntegerPGPSymmetricKeyField(null=True, blank=True)  # проживания
    inn = models.CharField(max_length=20, null=True, blank=True)
    city_birth = models.ForeignKey('directory.City', on_delete=models.SET_NULL, default=None, null=True,
                                   blank=True)  # мисце народження
    country_birth = models.ForeignKey('directory.Country', on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='country_birth')

    class Meta:
        unique_together = [['serial', 'inn', 'country']]


class Profile(DateTimesABC, AuthorDocumentABC, GetAuthorMixin):
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    first_name_ukr = models.CharField(max_length=200)
    first_name_eng = models.CharField(max_length=200)
    last_name_ukr = models.CharField(max_length=200)
    last_name_eng = models.CharField(max_length=200)
    middle_name_eng = models.CharField(max_length=200, null=True, blank=True)
    middle_name_ukr = models.CharField(max_length=200)
    date_birth = fields.DatePGPSymmetricKeyField()
    sex = models.ForeignKey('directory.Sex', on_delete=models.PROTECT)
    contact_info = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, blank=True, null=True)

    @property
    def get_full_name_ukr(self):
        return '{} {} {}'.format(self.last_name_ukr, self.first_name_ukr, self.middle_name_ukr)

    @property
    def get_full_name_eng(self):
        return '{} {}'.format(self.first_name_eng, self.last_name_eng)

    @property
    def get_position_from_qual(self):
        from .document.models import QualificationDocument
        self._sailor = keys = SailorKeys.objects.get(profile=self.id)
        if keys.qualification_documents:
            positions = list(QualificationDocument.objects.filter(
                id__in=keys.qualification_documents, status_document_id=19).values_list('list_positions', flat=True))
            if positions:
                positions = list(chain.from_iterable(positions))
                exclude_ids = [98, 99, 145, 141, 142, 143, 144, 127]
                return list(
                    Position.objects.filter(id__in=positions).exclude(rank_id__in=exclude_ids).
                        values('id', 'name_ukr', 'name_eng', 'rank'))
            else:
                return []
        else:
            return []

    @property
    def get_rank_from_qual(self):
        from cadets.models import StudentID
        exclude_ids = [98, 99, 145, 141, 142, 143, 144, 127]
        self._sailor = keys = SailorKeys.objects.get(profile=self.id)

        if keys.qualification_documents:
            from .document.models import QualificationDocument
            ranks = list(QualificationDocument.objects.filter(id__in=keys.qualification_documents,
                                                              status_document_id=19).exclude(
                rank_id__in=exclude_ids).order_by(
                '-date_start').distinct('rank', 'date_start').values('rank__id', 'rank__name_ukr', 'rank__name_eng'))
            if ranks:
                students_exists = False
                if keys.students_id:
                    students_exists = StudentID.objects.filter(id__in=keys.students_id,
                                                               status_document_id=magic_numbers.status_student_id_valid).exists()
                for r in ranks:
                    r['id'] = r.pop('rank__id')
                    r['name_ukr'] = r.pop('rank__name_ukr')
                    r['name_eng'] = r.pop('rank__name_eng')
                if students_exists is True:
                    ranks.insert(0, {'id': 0, 'name_ukr': 'Курсант', 'name_eng': 'Cadet'})
                return ranks

            return []
        else:
            return []

    @property
    def get_passport(self):
        from sailor.serializers import CitizenPassportSerializer
        self._sailor = keys = SailorKeys.objects.get(profile=self.id)
        if keys.citizen_passport:
            qs = Passport.objects.filter(id__in=keys.citizen_passport).first()
            return CitizenPassportSerializer(qs).data
        else:
            return {'serial': '', 'date': '', 'issued_by': '', 'photo': '',
                    'country': {'id': '', 'value': '',
                                'value_eng': '',
                                'value_abbr': ''}}

    @property
    def sailor_is_dkk(self):
        from .document.models import ProtocolSQC
        self._sailor = keys = SailorKeys.objects.get(profile=self.id)
        if keys.protocol_dkk:
            return ProtocolSQC.objects.filter(id__in=keys.protocol_dkk).exists()
        else:
            return False

    @property
    def exists_account_personal_cabinet(self):
        self._sailor = keys = SailorKeys.objects.get(profile=self.id)
        if keys.user_id:
            return True
        else:
            return False

    @property
    def get_financial_phone(self):
        keys = self._sailor if getattr(self, '_sailor', None) else SailorKeys.objects.get(profile=self.id)
        if keys.user_id:
            return User.objects.get(id=keys.user_id).username
        return None

    def get_full_name_to_date(self, date=None):
        if date is None or not self.old_name.exists():
            return {'ukr': self.get_full_name_ukr, 'eng': self.get_full_name_eng}
        old_names = self.old_name.filter(profile_id=self.id, change_date__gte=date).order_by('change_date')
        if old_names.exists():
            old_name = old_names.first()
            full_name_ukr = f'{old_name.old_last_name_ukr} {old_name.old_first_name_ukr} {old_name.old_middle_name_ukr}'
            full_name_eng = f'{old_name.old_last_name_eng} {old_name.old_first_name_eng} {old_name.old_middle_name_eng}'
            return {'ukr': full_name_ukr, 'eng': full_name_eng}
        return {'ukr': self.get_full_name_ukr, 'eng': self.get_full_name_eng}

    def get_old_full_name(self):
        old_name = self.old_name.filter(profile_id=self.id).order_by('-change_date').first()
        if old_name:
            return f'{old_name.old_last_name_ukr} {old_name.old_first_name_ukr} {old_name.old_middle_name_ukr}'
        return ''

    @property
    def get_rating(self):
        if hasattr(self, '_sailor') and self._sailor:
            sailor = self._sailor
        else:
            sailor = SailorKeys.objects.get(profile=self.pk)
        rating = Rating.objects.filter(sailor_key=sailor.pk)
        if rating.filter(rating=4).exists():
            return 4
        if rating.exists():
            return rating.last().rating
        return 0

    def can_verify(self, user_id):
        from agent.models import AgentSailor
        if hasattr(self, '_sailor') and self._sailor:
            sailor = self._sailor
        else:
            sailor = SailorKeys.objects.get(profile=self.pk)
        if User.objects.get(id=user_id).is_superuser:
            return True
        agent = AgentSailor.objects.filter(sailor_key=sailor.pk, is_disable=False).first()
        try:
            if agent:
                user_agent: User = agent.agent
                agent_group = user_agent.userprofile.agent_group.first()
                return agent_group.userprofile_set.filter(
                    type_user=UserProfile.SECRETARY_SERVICE, user_id=user_id,
                ).exists()
            else:
                return False
        except ObjectDoesNotExist:
            return False

    @property
    def has_agent(self):
        from agent.models import AgentSailor
        sailor = getattr(self, '_sailor', None)
        if not sailor:
            sailor = SailorKeys.objects.get(profile=self.pk)
        return AgentSailor.objects.filter(sailor_key=sailor.pk).exists()

    @property
    def is_cadet(self):
        from cadets.models import StudentID
        sailor = getattr(self, '_sailor', None)
        if not sailor:
            sailor = SailorKeys.objects.get(profile=self.pk)
        return StudentID.objects.filter(
            id__in=sailor.students_id,
            status_document=magic_numbers.status_student_id_valid
        ).exists()


class FullAddress(models.Model):
    city = models.ForeignKey('directory.City', on_delete=models.SET_NULL, null=True, blank=True)
    index = models.CharField(max_length=8, null=True, blank=True)
    street = models.CharField(max_length=250, null=True, blank=True)
    house = models.CharField(max_length=250, null=True, blank=True)
    flat = models.CharField(max_length=250, null=True, blank=True)


class PhotoProfile(models.Model):
    photo = models.ImageField(max_length=500, upload_to=get_upload_photo_path)
    is_delete = models.BooleanField(default=False)


class SailorPassport(DateTimesABC, AuthorDocumentABC, GetAuthorMixin):
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    class StatusDocument:
        IN_PROCESS = 21
        INVALID = 20
        VALID = 19
        LOST = 18
        DESTROYED = 17
        EXPIRED = 7
        CANCELED = 33

    country = models.ForeignKey('directory.Country', on_delete=models.PROTECT)
    number_document = models.CharField(max_length=20)
    date_start = models.DateField()
    date_end = models.DateField()
    port = models.ForeignKey('directory.Port', on_delete=models.PROTECT, null=True, blank=True)
    other_port = models.CharField(null=True, blank=True, max_length=250)
    captain = models.CharField(max_length=255)  # оставить текстом, должна быть статическая инфа
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, blank=True, null=True)
    date_renewal = models.DateField(null=True, blank=True)
    items = GenericRelation('back_office.DependencyItem', related_query_name='sailor_passport_document')
    verification_status = GenericRelation('sailor.DocumentInVerification',
                                          related_query_name='sailor_passport_verification')
    is_new_document = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Посвідчення особи моряка'
        permissions = (
            ('readReportSailorPassport', 'Просмотр отчета по ПОМ'),
            ('createNewSailorPassport', 'Создание нового паспорта моряка')
        )

    @property
    def get_number(self):
        return self.number_document

    @property
    def get_info_for_statement(self):
        is_verification = False
        port = self.port.name_ukr if self.port else self.other_port
        date_end = self.date_renewal if self.date_renewal else self.date_end
        return {'number': self.get_number, 'name_issued': port,
                'date_start': self.date_start,
                'date_end': date_end,
                'info': self.captain, 'type_doc': 'Посвідчення особи моряка', 'is_verification': is_verification,
                'id': self.pk, 'content_type': self._meta.model_name}


class DependencyDocuments(models.Model):
    for_what_choices = [
        ('both', 'both'),
        ('continue', 'continue'),
        ('start', 'start')
    ]
    type_document = models.TextField()
    key_document = models.JSONField()
    document_description = models.TextField()
    standarts_text = models.TextField()
    position = models.ForeignKey('directory.Position', on_delete=models.CASCADE)
    limitation_id = models.ForeignKey('directory.Limitations', on_delete=models.SET_NULL, null=True, blank=True)
    for_what = models.CharField(max_length=10, default='both', choices=for_what_choices)

    @property
    def get_name_type_document(self):
        name_type_document = {
            'Диплом': 'Кваліфікаційний документ моряка',
            'Танкерист': 'Кваліфікаційний документ моряка',
            'Танкерист хотелка': 'Кваліфікаційний документ моряка',
            'Свідоцтво фахівця': 'Кваліфікаційний документ моряка',
            'Підтвердження робочого диплому': 'Кваліфікаційний документ моряка',
            'Образование': 'Документ про освіту',
            'Диплом про вищу освіту': 'Документ про освіту',
            'Свідоцтво про підвищення кваліфікації': 'Документ про освіту',
            'NTZ': 'Свідоцтво НТЗ',
            'Medical': 'Медичне свідоцтво'
        }
        return name_type_document[self.type_document]

    @property
    def get_info_for_statement(self):
        return {'document_description': self.document_description, 'standarts_text': self.standarts_text}


class DemandPositionDKK(AuthorDocumentABC, DateTimesABC):
    objects = models.Manager()
    by_sailor = BySailorQuerySet.as_manager()

    list_positions = postgresfield.ArrayField(models.IntegerField())
    rank = models.ForeignKey('directory.Rank', on_delete=models.PROTECT)
    status_document = models.ForeignKey('directory.StatusDocument', on_delete=models.PROTECT)
    is_continue = models.IntegerField(default=0)
    is_experience = models.BooleanField(default=False)
    dependency_docs = models.ManyToManyField(DependencyDocuments, related_name='dependency_docs')

    related_docs = GM2MField('document.Education', 'document.CertificateETI', 'document.QualificationDocument',
                             'document.ProofOfWorkDiploma', 'document.MedicalCertificate', 'sailor.DependencyDocuments',
                             related_name='related_demand', blank=True)

    @property
    def get_demand_position(self):
        have_all_exp = self.is_experience
        have_all_docs = False
        documents = []
        documents_exists = []
        documents_not_exists = self.dependency_docs.all()
        if documents_not_exists.exists():
            documents = [{'document_descr': doc.document_description, 'standarts_text': doc.standarts_text,
                          'type_document': doc.get_name_type_document} for doc in documents_not_exists]
        else:
            have_all_docs = True
        if self.related_docs.exists():
            for document in self.related_docs.all().exclude(gm2m_ct_id__in=[46, 68, 50]):
                info_doc = document.get_info_for_statement
                documents_exists.append(info_doc)
        return {'documents': documents, 'have_all_docs': have_all_docs,
                'have_all_exp': have_all_exp, 'exists_docs': documents_exists}


class OldName(DateTimesABC, AuthorDocumentABC):
    """
    Смена фамилии/имени/отчества у моряка
    """
    old_last_name_ukr = models.CharField(max_length=200)
    old_last_name_eng = models.CharField(max_length=200)
    old_first_name_ukr = models.CharField(max_length=200)
    old_first_name_eng = models.CharField(max_length=200)
    old_middle_name_ukr = models.CharField(max_length=200)
    old_middle_name_eng = models.CharField(max_length=200, null=True, blank=True)
    new_last_name_ukr = models.CharField(max_length=200)
    new_last_name_eng = models.CharField(max_length=200)
    new_first_name_ukr = models.CharField(max_length=200)
    new_first_name_eng = models.CharField(max_length=200)
    new_middle_name_ukr = models.CharField(max_length=200)
    new_middle_name_eng = models.CharField(max_length=200, null=True, blank=True)
    photo = fields.CharPGPSymmetricKeyField(max_length=200, null=True, blank=True)
    change_date = models.DateField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='old_name')


class Rating(DateTimesABC, AuthorDocumentABC):
    rating = models.FloatField()
    sailor_key = models.IntegerField()


class DocumentInVerification(DateTimesABC):
    item = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True)
    object_id = models.PositiveIntegerField(null=True)

    verification_status = models.ForeignKey(VerificationStage, on_delete=models.PROTECT,
                                            null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['verification_status__order_number']


class CommentForVerificationDocument(DateTimesABC, AuthorDocumentABC, GetAuthorMixin):
    """
    Сomment on a document in the verification status
    """
    comment = models.TextField(default='')
    document = models.ForeignKey(DocumentInVerification, on_delete=models.PROTECT, related_name='comments')
