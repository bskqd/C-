import itertools
from functools import reduce

from django.db.models import Q, QuerySet
from django.utils import timezone as tz
from django_filters import rest_framework as filters

from cadets.models import StudentID
from communication.models import SailorKeys
from directory.models import (ExperinceForDKK, Position)
from mixins.filter_mixins import SailorFilter
from mixins.page_mixins import PaginationWithCurrent, PaginationWithoutFullUrl
from sailor.document.models import CertificateETI, Education, ProofOfWorkDiploma, ProtocolSQC, QualificationDocument
from sailor.models import SailorPassport
from sailor.statement.models import StatementSQC, StatementServiceRecord


class StandardResultsSetPagination(PaginationWithCurrent):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ShortLinkResultPagination(PaginationWithoutFullUrl):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class DkkFilter(filters.FilterSet, SailorFilter):
    sailor_id = filters.CharFilter(method='sailor_id_filter')
    sailor_name = filters.CharFilter(method='sailor_name_filter')
    sailor_birth = filters.CharFilter(method='sailor_birth_date_filter')
    created = filters.DateFilter(field_name='created_at', lookup_expr='date')

    def sailor_id_filter(self, queryset, name, value):
        prot_ids = self.get_sailor_id(value, self.field_name)
        return queryset.filter(id__in=prot_ids)

    def sailor_name_filter(self, queryset, name, value):
        prot_ids = self.get_sailor_name(value, self.field_name)
        return queryset.filter(id__in=prot_ids)

    def sailor_birth_date_filter(self, queryset, name, value):
        prot_ids = self.get_sailor_birth(value, self.field_name)
        return queryset.filter(id__in=prot_ids)


class ProtocolDkkFilter(DkkFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'protocol_dkk'

    from_date = filters.DateFilter(field_name='date_meeting', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='date_meeting', lookup_expr='lte')
    protocol_number = filters.NumberFilter(field_name='number_document')
    protocol_year = filters.NumberFilter(field_name='date_meeting__year')
    branch = filters.CharFilter(method='branch_list_filter')
    direction_abbr = filters.CharFilter(method='direction_abbr_filter')
    statement_number = filters.NumberFilter(field_name='statement_dkk__number')
    statement_year = filters.NumberFilter(field_name='statement__created_at__year')
    statement_branch = filters.CharFilter(method='statement_branch_list_filter')
    valid_till = filters.DateFilter(field_name='date_meeting', method='valid_till_filter')
    decision = filters.CharFilter(method='decision_list_filter')
    rank = filters.CharFilter(method='rank_list_filter')
    position = filters.CharFilter(method='positions_list_filter')
    experience_required = filters.BooleanFilter(method='exp_required_filter')
    is_continue = filters.BooleanFilter(method='is_continue_filter')
    document_property = filters.CharFilter(method='document_property_filter')
    is_cadet = filters.BooleanFilter(field_name='statement_dkk__is_cadet')
    committe_head = filters.CharFilter(method='committee_head_filter')
    commissioner = filters.CharFilter(method='commissioner_filter')
    with_agent = filters.BooleanFilter(method='with_agent_filter')

    ordering = filters.OrderingFilter(
        fields=(
            ('number_document', 'numberProtocol'),
            ('branch_create__name_ukr', 'affiliate'),
            ('decision_id', 'solution'),
            ('statement_dkk__rank__name_ukr', 'rank'),
            ('statement_dkk__rank__priority', 'rank_priority'),
            ('date_meeting', 'dateCreated'),
            ('statement_dkk__is_continue', 'is_continue'),
            # ('experience_required', 'experience_required')
        )
    )

    def with_agent_filter(self, queryset, name, value):
        value = not value
        return queryset.filter(items__isnull=value)

    def valid_till_filter(self, queryset, name, value):
        valid_date = value - tz.timedelta(days=365)
        return queryset.filter(date_meeting__range=(valid_date, value))

    def positions_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(statement_dkk__list_positions__overlap=positions_list)

    def rank_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(statement_dkk__rank_id__in=positions_list)

    def decision_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(decision_id__in=positions_list)

    def branch_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(branch_create_id__in=positions_list)

    def direction_abbr_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(statement_dkk__rank__direction__value_abbr__in=positions_list)

    def statement_branch_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(statement_dkk__branch_office_id__in=positions_list)

    def exp_required_filter(self, queryset, name, value):
        exps = list(ExperinceForDKK.objects.all().distinct('position_id').values_list('position_id', flat=True))
        if value:
            return queryset.filter(statement_dkk__list_positions__overlap=exps, statement_dkk__is_continue__in=[0, 2])
        else:
            return queryset.exclude(statement_dkk__list_positions__overlap=exps, statement_dkk__is_continue__in=[0, 2])

    def is_continue_filter(self, queryset, name, value):
        if value:
            return queryset.filter(Q(statement_dkk__is_continue__in=[1, 2]) | Q(statement_dkk__rank__type_rank_id=3))
        else:
            return queryset.filter(statement_dkk__is_continue=0).exclude(statement_dkk__rank__type_rank_id=3)

    def document_property_filter(self, queryset, name, value):
        values = value.split(',')
        assign = Q(statement_dkk__is_continue=0) & Q(statement_dkk__rank__type_rank_id=21) & Q(decision_id=1)
        exclude_tankers = Q(statement_dkk__rank__direction_id=7)
        not_assign = Q(Q(statement_dkk__is_continue=0) & Q(statement_dkk__rank__type_rank_id=21) & Q(decision_id=2))
        confirm = Q((Q(statement_dkk__is_continue__in=[1, 2]) | Q(statement_dkk__rank__type_rank_id=3)) & Q(
            decision_id=1))
        not_confirm = Q((Q(statement_dkk__is_continue__in=[1, 2]) | Q(statement_dkk__rank__type_rank_id=3)) &
                        Q(decision_id=2))
        give = Q(Q(statement_dkk__rank__direction_id=7) & Q(decision_id=1))
        not_give = Q(Q(statement_dkk__rank__direction_id=7) & Q(decision_id=2))
        filtering = Q()
        d = {'assign': assign, 'not_assign': not_assign, 'confirm': confirm, 'not_confirm': not_confirm, 'give': give,
             'not_give': not_give}
        for filter in values:
            filtering |= d[filter]
        exclude = Q()
        if 'not_give' not in values and 'give' not in values:
            exclude = exclude_tankers
        return queryset.filter(filtering).exclude(exclude)

    def committee_head_filter(self, queryset, name, value):
        print(value)
        return queryset.filter(commissioner_sign__signer__name=value, commissioner_sign__commissioner_type='HD')

    def commissioner_filter(self, queryset, name, value):
        commissioner_split = value.split(',')
        return queryset.filter(commissioner_sign__signer__name__in=commissioner_split,
                               commissioner_sign__commissioner_type='CH')

    class Meta:
        model = ProtocolSQC
        fields = ['from_date', 'to_date', 'sailor_id', 'sailor_name', 'sailor_birth', 'branch', 'protocol_number',
                  'valid_till', 'decision', 'rank', 'position', 'statement_year', 'statement_branch',
                  'protocol_year', 'direction_abbr', 'statement_number', 'is_cadet', 'committe_head']


class StatementDkkFilter(DkkFilter):
    """Фильтр заявок ДКК"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'statement_dkk'

    from_date = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    to_date = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    from_date_meeting = filters.DateFilter(field_name='date_meeting', lookup_expr='gte')
    to_date_meeting = filters.DateFilter(field_name='date_meeting', lookup_expr='lte')
    with_agent = filters.BooleanFilter(method='with_agent_filter')
    number = filters.NumberFilter(field_name='number')
    statement_year = filters.NumberFilter(field_name='created_at__year')
    protocol_year = filters.NumberFilter(field_name='protocolsqc__date_meeting__year')
    branch = filters.CharFilter(method='branch_list_filter')
    protocol_number = filters.NumberFilter(field_name='protocolsqc__number_document')
    rank = filters.CharFilter(method='rank_list_filter')
    position = filters.CharFilter(method='positions_list_filter')
    status_document = filters.CharFilter(method='status_document_filter')
    experience_required = filters.BooleanFilter(method='exp_required_filter')
    have_protocol = filters.BooleanFilter(method='have_protocol_filter')
    direction_abbr = filters.CharFilter(method='direction_abbr_filter')
    is_cadet = filters.BooleanFilter(field_name='is_cadet')

    ordering = filters.OrderingFilter(
        fields=(
            ('branch_office__name_ukr', 'branch'),
            ('rank__name_ukr', 'rank'),
            ('created_at', 'dateCreated'),
            # ('experience_required', 'experience_required'),
        )
    )

    def with_agent_filter(self, queryset, name, value):
        value = not value
        return queryset.filter(Q(items__isnull=value) | Q(protocolsqc__items__isnull=value))

    def have_protocol_filter(self, queryset, name, value):
        value = not value
        return queryset.filter(protocolsqc__isnull=value)

    def positions_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(list_positions__overlap=positions_list)

    def branch_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(branch_office_id__in=positions_list)

    def rank_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(rank_id__in=positions_list)

    def exp_required_filter(self, queryset, name, value):
        if value:
            exps = list(ExperinceForDKK.objects.all().distinct('position_id').values_list('position_id', flat=True))
            return queryset.filter(list_positions__overlap=exps, is_continue__in=[0, 2])
        else:
            exps = list(Position.objects.filter(experincefordkk__isnull=True).values_list('id', flat=True))
            return queryset.exclude(list_positions__overlap=exps, is_continue__in=[0,2])

    def direction_abbr_filter(self, queryset, name, value):
        return queryset.filter(rank__direction__value_abbr=value)

    def status_document_filter(self, queryset, name, value):
        status_id = value.split(',')
        return queryset.filter(status_document_id__in=status_id)

    class Meta:
        model = StatementSQC
        fields = ['from_date', 'to_date', 'created', 'sailor_id', 'sailor_name', 'sailor_birth', 'number', 'branch',
                  'rank', 'protocol_number', 'position', 'status_document', 'created_at', 'experience_required',
                  'direction_abbr', 'is_cadet']


class NTZFilter(DkkFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'sertificate_ntz'

    from_date = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    nz_id = filters.CharFilter(method='nz_list_filter')
    number = filters.NumberFilter(field_name='ntz_number')
    course_traning = filters.CharFilter(method='course_training_filter')
    date_start = filters.DateFilter(field_name='date_start')
    date_end = filters.DateFilter(field_name='date_end')

    o = filters.OrderingFilter(
        fields=(
            ('ntz_id', 'nz_id'),
            ('course_traning__name_ukr', 'course_training'),
        )
    )

    def nz_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(ntz_id__in=positions_list)

    def course_training_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(course_training_id__in=positions_list)

    class Meta:
        model = CertificateETI
        fields = ['from_date', 'to_date', 'sailor_id', 'sailor_name', 'sailor_birth', 'nz_id', 'number',
                  'course_traning', 'date_start', 'date_end']


class QualificationFilter(filters.FilterSet, SailorFilter):
    """Базовый фильтр квалификационных документов"""
    from_date = filters.DateFilter(field_name='date_start', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='date_start', lookup_expr='lte')
    sailor_id = filters.CharFilter(method='sailor_id_filter')
    sailor_name = filters.CharFilter(method='sailor_name_filter')
    sailor_birth = filters.CharFilter(method='sailor_birth_date_filter')
    document_year = filters.NumberFilter(field_name='date_start__year')

    def sailor_id_filter(self, queryset, name, value):
        qual_doc_ids = self.get_sailor_id(value, self.field_name)
        return queryset.filter(id__in=qual_doc_ids)

    def sailor_name_filter(self, queryset, name, value):
        qual_doc_ids = self.get_sailor_name(value, self.field_name)
        return queryset.filter(id__in=qual_doc_ids)

    def sailor_birth_date_filter(self, queryset, name, value):
        qual_doc_ids = self.get_sailor_birth(value, self.field_name)
        return queryset.filter(id__in=qual_doc_ids)


class QualificationDocumentFilter(QualificationFilter):
    """Фильтр квалификационных документов"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'qualification_documents'

    date_end = filters.DateFilter(field_name='date_end')
    date_start = filters.DateFilter(field_name='date_start')
    number_document = filters.NumberFilter(field_name='number_document')
    port = filters.CharFilter(method='port_filter')
    other_port = filters.CharFilter(method='other_port_filter')
    status_document = filters.CharFilter(method='status_document_filter')

    o = filters.OrderingFilter(
        fields=(
            ('port__name_ukr', 'port'),
            ('other_port', 'other_port'),
            ('rank__name_ukr', 'rank'),
            ('status_document__name_ukr', 'status_document'),
        )
    )

    def port_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(port_id__in=positions_list)

    def other_port_filter(self, queryset, name, value):
        positions_list = value.split(',')
        _filters = map(lambda port: Q(other_port__iexact=port), positions_list)
        _filters = reduce(lambda a, b: a | b, _filters)
        return queryset.filter(_filters)

    def status_document_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(status_document_id__in=positions_list)


class QualificationDocumentAllFilter(QualificationDocumentFilter):
    """Фильтр квалификационных документов (диплом, свидетельство фахивця, квалификационный документ)"""

    rank = filters.CharFilter(method='rank_list_filter')
    position = filters.CharFilter(method='positions_list_filter')
    type_document = filters.NumberFilter(field_name='type_document_id')
    country = filters.CharFilter(method='country_filter')
    other_number = filters.CharFilter(field_name='other_number')

    def country_filter(self, queryset, name, value):
        country = value.split(',')
        return queryset.filter(country_id__in=country)

    def rank_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(rank_id__in=positions_list)

    def positions_list_filter(self, queryset, name, value):
        positions_list = value.split(',')[:4]
        return queryset.filter(list_positions__overlap=positions_list)

    class Meta:
        models = QualificationDocument
        fields = ['from_date', 'to_date', 'sailor_id', 'sailor_name', 'sailor_birth', 'date_start', 'date_end',
                  'number_document', 'rank', 'port', 'position', 'status_document', 'other_port', 'country',
                  'other_number']


class ProofOfWorkDiplomaFilter(QualificationDocumentFilter):
    """Фильтр квалификационных документов (подтверждения дипломов)"""

    rank = filters.CharFilter(method='rank_list_filter')
    position = filters.CharFilter(method='positions_list_filter')
    sailor_id = filters.CharFilter(method='sailor_id_filter_proof_diploma')
    sailor_name = filters.CharFilter(method='sailor_name_filter_proof_diploma')
    sailor_birth = filters.CharFilter(method='sailor_birth_date_filter_proof_diploma')

    def sailor_id_filter_proof_diploma(self, queryset, name, value):
        qual_doc = super().sailor_id_filter(QualificationDocument.objects.all(), name, value)
        return queryset.filter(diploma_id__in=qual_doc)

    def sailor_name_filter_proof_diploma(self, queryset, name, value):
        qual_doc = super().sailor_name_filter(QualificationDocument.objects.all(), name, value)
        return queryset.filter(diploma_id__in=qual_doc)

    def sailor_birth_date_filter_proof_diploma(self, queryset, name, value):
        qual_doc = super().sailor_birth_date_filter(QualificationDocument.objects.all(), name, value)
        return queryset.filter(diploma_id__in=qual_doc)

    def rank_list_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(diploma__rank_id__in=positions_list)

    def positions_list_filter(self, queryset, name, value):
        positions_list = value.split(',')[:4]
        return queryset.filter(diploma__list_positions__overlap=positions_list)

    o = filters.OrderingFilter(
        fields=(
            ('port__name_ukr', 'port'),
            ('other_port', 'other_port'),
            ('diploma__rank__name_ukr', 'rank'),
            ('status_document__name_ukr', 'status_document'),
        )
    )

    class Meta:
        models = ProofOfWorkDiploma
        fields = ['from_date', 'to_date', 'sailor_id', 'sailor_name', 'sailor_birth', 'date_start', 'date_end',
                  'number_document', 'rank', 'port', 'position', 'status_document', 'other_port']


class QualificationDocumentCertificatesFilter(QualificationDocumentFilter):
    """Фильтр квалификационных документов (свидетельства танкеристов и офицер охраны судна)"""

    certificate_name = filters.CharFilter(method='certificate_name_filter')
    type_document = filters.NumberFilter(field_name='type_document_id')

    def certificate_name_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(rank_id__in=positions_list)

    class Meta:
        models = QualificationDocument
        fields = ['from_date', 'to_date', 'sailor_id', 'sailor_name', 'sailor_birth', 'date_start', 'date_end',
                  'number_document', 'port', 'certificate_name', 'status_document', 'other_port']


class EducationDocumentFilter(DkkFilter):
    """Фильтр образовательных документов"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'education'

    from_date = filters.DateFilter(field_name='date_issue_document', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='date_issue_document', lookup_expr='lte')
    registry_number = filters.CharFilter(field_name='registry_number')
    serial = filters.CharFilter(field_name='serial')
    number_document = filters.CharFilter(field_name='number_document')
    type_document = filters.NumberFilter(field_name='type_document_id')
    id_nz = filters.CharFilter(method='name_nz_filter')
    qualification = filters.CharFilter(method='qualification_filter')
    experied_date = filters.DateFilter(field_name='expired_date')
    status_document = filters.CharFilter(method='status_document_filter')
    extent = filters.CharFilter(method='extent_filter')
    speciality = filters.CharFilter(method='speciality_filter')
    specialization = filters.CharFilter(field_name='specialization_id')

    def name_nz_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(name_nz_id__in=positions_list)

    def qualification_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(qualification_id__in=positions_list)

    def status_document_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(status_document_id__in=positions_list)

    def extent_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(extent_id__in=positions_list)

    def speciality_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(speciality_id__in=positions_list)

    def specialization_filter(self, queryset, name, value):
        positions_list = value.split(',')
        return queryset.filter(specialization_id__in=positions_list)

    class Meta:
        model = Education
        fields = ['from_date', 'to_date', 'sailor_id', 'sailor_name', 'sailor_birth', 'registry_number', 'serial',
                  'number_document', 'type_document', 'name_nz', 'qualification', 'date_issue_document',
                  'experied_date', 'status_document', 'extent', 'speciality', 'specialization']

    o = filters.OrderingFilter(
        fields=(
            ('name_nz__name_ukr', 'name_nz'),
            ('extent__name_ukr', 'extent'),
            ('qualification__name_ukr', 'qualification'),
            ('speciality__name_ukr', 'speciality'),
            ('specialization__name_ukr', 'specialization'),
            ('status_document__name_ukr', 'status_document'),
        )
    )


class StudentIDFilter(filters.FilterSet, SailorFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'students_id'

    have_statement = filters.BooleanFilter(method='have_statement_filter')
    have_protocol = filters.BooleanFilter(method='have_protocol_filter')
    educ_with_dkk = filters.BooleanFilter()
    passed_educ_exam = filters.BooleanFilter()
    id_nz = filters.CharFilter(method='id_nz_filter')
    sailor_id = filters.CharFilter(method='sailor_id_filter')
    sailor_name = filters.CharFilter(method='sailor_name_filter')
    sailor_birth = filters.CharFilter(method='sailor_birth_date_filter')
    faculty = filters.CharFilter(method='faculty_filter')

    def id_nz_filter(self, queryset, name, value):
        nz_id = value.split(',')
        return queryset.filter(name_nz_id__in=nz_id)

    def faculty_filter(self, queryset, name, value):
        faculty_ids = value.split(',')
        return queryset.filter(faculty__id__in=faculty_ids)

    def sailor_id_filter(self, queryset, name, value):
        prot_ids = self.get_sailor_id(value, self.field_name)
        return queryset.filter(id__in=prot_ids)

    def sailor_name_filter(self, queryset, name, value):
        prot_ids = self.get_sailor_name(value, self.field_name)
        return queryset.filter(id__in=prot_ids)

    def sailor_birth_date_filter(self, queryset, name, value):
        prot_ids = self.get_sailor_birth(value, self.field_name)
        return queryset.filter(id__in=prot_ids)

    def have_statement_filter(self, queryset, name, value):
        sailors = SailorKeys.objects.filter(students_id__overlap=list(queryset.values_list('pk', flat=True)))
        statements_id = list(sailors.values_list('statement_dkk', flat=True))
        statements_id_merged = list(itertools.chain.from_iterable(statements_id))
        self.statement_is_cadet = statements = StatementSQC.objects.filter(id__in=statements_id_merged,
                                                                           is_cadet=value).values_list('pk',
                                                                                                       flat=True)
        self.sailor_with_statement = sailors_with_statement = sailors.filter(statement_dkk__overlap=list(statements))
        students_id = sailors_with_statement.values_list('students_id', flat=True)
        students_id_merged = list(itertools.chain.from_iterable(students_id))
        return queryset.filter(id__in=list(students_id_merged))

    def have_protocol_filter(self, queryset, name, value):
        if not hasattr(self, 'sailor_with_statement') or not hasattr(self, 'statement_is_cadet'):
            self.have_statement_filter(queryset, name, value)
        protocols = ProtocolSQC.objects.filter(statement_dkk__in=self.statement_is_cadet)
        sailor_with_protocol = self.sailor_with_statement.filter(
            protocol_dkk__overlap=list(protocols.values_list('pk', flat=True)))
        sailor_without_protocol = self.sailor_with_statement.exclude(
            protocol_dkk__overlap=list(protocols.values_list('pk', flat=True)))
        if value is True:
            students_id = sailor_with_protocol.values_list('students_id', flat=True)
            students_id_merged = list(itertools.chain.from_iterable(students_id))
            return queryset.filter(id__in=students_id_merged)
        else:
            students_id = sailor_without_protocol.values_list('students_id', flat=True)
            students_id_merged = list(itertools.chain.from_iterable(students_id))
            return queryset.filter(id__in=students_id_merged)

    class Meta:
        model = StudentID
        fields = ['have_statement', 'sailor_id', 'sailor_name', 'sailor_birth', 'id_nz', 'passed_educ_exam',
                  'educ_with_dkk', 'have_protocol']


class StatementServiceRecordFilter(filters.FilterSet, SailorFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'statement_service_records'

    from_date = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    to_date = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    created = filters.DateFilter(field_name='created_at', lookup_expr='date')
    is_payed = filters.BooleanFilter(field_name='is_payed')
    status_document = filters.CharFilter(method='status_id_filter')
    status_exclude = filters.CharFilter(method='status_id_exclude')
    sailor_id = filters.CharFilter(method='sailor_id_filter')
    sailor_name = filters.CharFilter(method='sailor_name_filter')

    def status_id_filter(self, queryset, name, value):
        status_ids = value.split(',')
        return queryset.filter(status_id__in=status_ids)

    def status_id_exclude(self, queryset, name, value):
        status_ids = value.split(',')
        return queryset.exclude(status_id__in=status_ids)

    def sailor_id_filter(self, queryset, name, value):
        statement_ids = self.get_sailor_id(value, self.field_name)
        return queryset.filter(id__in=statement_ids)

    def sailor_name_filter(self, queryset, name, value):
        statement_ids = self.get_sailor_name(value, self.field_name)
        return queryset.filter(id__in=statement_ids)

    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'createdDate'),
            ('status__name_ukr', 'statusDocument'),
        )
    )

    class Meta:
        model = StatementServiceRecord
        fields = ['from_date', 'to_date', 'created', 'sailor_id', 'sailor_name', 'status', 'is_payed']


class StatementETIFilter(filters.FilterSet, SailorFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'statement_eti'

    from_date = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    to_date = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    created = filters.DateFilter(field_name='created_at', lookup_expr='date')
    from_date_meeting = filters.DateFilter(field_name='date_meeting', lookup_expr='gte')
    to_date_meeting = filters.DateFilter(field_name='date_meeting', lookup_expr='lte')
    date_meeting = filters.DateFilter(field_name='date_meeting')
    from_date_end_meeting = filters.DateFilter(field_name='date_end_meeting', lookup_expr='gte')
    to_date_end_meeting = filters.DateFilter(field_name='date_end_meeting', lookup_expr='lte')
    date_end_meeting = filters.DateFilter(field_name='date_end_meeting')
    sailor_id = filters.CharFilter(method='sailor_id_filter')
    sailor_name = filters.CharFilter(method='sailor_name_filter')
    status_document = filters.CharFilter(method='status_document_filter')
    institution = filters.CharFilter(method='institution_filter')
    course = filters.CharFilter(method='course_filter')
    is_payed = filters.BooleanFilter()

    def status_document_filter(self, queryset, name, value):
        status_ids = value.split(',')
        return queryset.filter(status_document_id__in=status_ids)

    def sailor_id_filter(self, queryset, name, value):
        statement_ids = self.get_sailor_id(value, self.field_name)
        return queryset.filter(id__in=statement_ids)

    def sailor_name_filter(self, queryset, name, value):
        statement_ids = self.get_sailor_name(value, self.field_name)
        return queryset.filter(id__in=statement_ids)

    def institution_filter(self, queryset, name, value):
        institution_ids = value.split(',')
        return queryset.filter(institution__in=institution_ids)

    def course_filter(self, queryset, name, value):
        course_ids = value.split(',')
        return queryset.filter(course__in=course_ids)

    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'date_create'),
            ('date_meeting', 'date_meeting'),
            ('date_end_meeting', 'date_end_meeting'),
            ('status_document__name_ukr', 'status_document'),
            ('course__name_ukr', 'course'),
            ('institution__name_ukr', 'institution'),
            ('is_payed', 'is_payed'),
        )
    )


class PaymentStatementETIFilter(filters.FilterSet, SailorFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'statement_eti'

    from_pay_date = filters.DateFilter(field_name='pay_time', lookup_expr='date__gte')
    to_pay_date = filters.DateFilter(field_name='pay_time', lookup_expr='date__lte')
    course = filters.CharFilter(method='course_filter')
    institution = filters.CharFilter(method='institution_filter')
    sailor_id = filters.CharFilter(method='sailor_id_filter')
    sailor_name = filters.CharFilter(method='sailor_name_filter')

    def course_filter(self, queryset, name, value):
        course_ids = value.split(',')
        return queryset.filter(statement_eti_payments__course_id__in=course_ids)

    def institution_filter(self, queryset, name, value):
        institution_ids = value.split(',')
        return queryset.filter(statement_eti_payments__institution_id__in=institution_ids)

    def sailor_id_filter(self, queryset, name, value):
        statement_ids = self.get_sailor_id(value, self.field_name)
        return queryset.filter(statement_eti_payments__id__in=statement_ids)

    def sailor_name_filter(self, queryset, name, value):
        statement_ids = self.get_sailor_name(value, self.field_name)
        return queryset.filter(statement_eti_payments__id__in=statement_ids)

    ordering = filters.OrderingFilter(
        fields=(
            ('pay_time', 'pay_date'),
            ('statement_eti_payments__course__name_ukr', 'course'),
            ('statement_eti_payments__institution__name_ukr', 'institution'),
        )
    )


class PaymentBranchOfficeFilter(filters.FilterSet, SailorFilter):
    field_name = 'packet_item'

    from_pay_date = filters.DateFilter(field_name='pay_time', lookup_expr='date__gte')
    to_pay_date = filters.DateFilter(field_name='pay_time', lookup_expr='date__lte')
    branch_office = filters.CharFilter(method='branch_office_filter')
    sailor_id = filters.CharFilter(method='sailor_id_filter')
    sailor_name = filters.CharFilter(method='sailor_name_filter')

    def branch_office_filter(self, queryset, name, value):
        branch_office_ids = value.split(',')
        return queryset.filter(dependecy_payments__object_id__in=branch_office_ids)

    def sailor_id_filter(self, queryset, name, value):
        packet_item_ids = self.get_sailor_id(value, self.field_name)
        return queryset.filter(dependecy_payments__packet_item_id__in=packet_item_ids)

    def sailor_name_filter(self, queryset, name, value):
        packet_item_ids = self.get_sailor_name(value, self.field_name)
        return queryset.filter(dependecy_payments__packet_item_id__in=packet_item_ids)

    ordering = filters.OrderingFilter(
        fields=(
            ('pay_time', 'pay_date'),
        )
    )


class StatementAdvancedTrainingFilter(filters.FilterSet, SailorFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'statement_advanced_training'

    from_date = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    to_date = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    created = filters.DateFilter(field_name='created_at', lookup_expr='date')
    from_date_meeting = filters.DateFilter(field_name='date_meeting', lookup_expr='gte')
    to_date_meeting = filters.DateFilter(field_name='date_meeting', lookup_expr='lte')
    date_meeting = filters.DateFilter(field_name='date_meeting')
    from_date_end_meeting = filters.DateFilter(field_name='date_end_meeting', lookup_expr='gte')
    to_date_end_meeting = filters.DateFilter(field_name='date_end_meeting', lookup_expr='lte')
    date_end_meeting = filters.DateFilter(field_name='date_end_meeting')
    sailor_id = filters.CharFilter(method='sailor_id_filter')
    sailor_name = filters.CharFilter(method='sailor_name_filter')
    status_document = filters.CharFilter(method='status_document_filter')
    education_institution = filters.CharFilter(method='education_institution_filter')
    level_qualification = filters.CharFilter(method='level_qualification_filter')
    is_payed = filters.BooleanFilter()

    def status_document_filter(self, queryset, name, value):
        status_ids = value.split(',')
        return queryset.filter(status_document_id__in=status_ids)

    def sailor_id_filter(self, queryset, name, value):
        statement_ids = self.get_sailor_id(value, self.field_name)
        return queryset.filter(id__in=statement_ids)

    def sailor_name_filter(self, queryset, name, value):
        statement_ids = self.get_sailor_name(value, self.field_name)
        return queryset.filter(id__in=statement_ids)

    def education_institution_filter(self, queryset, name, value):
        institution_ids = value.split(',')
        return queryset.filter(educational_institution__in=institution_ids)

    def level_qualification_filter(self, queryset, name, value):
        level_qualification_ids = value.split(',')
        return queryset.filter(level_qualification__in=level_qualification_ids)

    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'date_create'),
            ('date_meeting', 'date_meeting'),
            ('date_end_meeting', 'date_end_meeting'),
            ('status_document__name_ukr', 'status_document'),
            ('level_qualification__name_ukr', 'level_qualification'),
            ('educational_institution__name_ukr', 'education_institution'),
            ('is_payed', 'is_payed'),
        )
    )


class SailorPassportFilter(filters.FilterSet, SailorFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = 'sailor_passport'

    from_date = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    to_date = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    from_date_start = filters.DateFilter(field_name='date_start', lookup_expr='date__gte')
    to_date_start = filters.DateFilter(field_name='date_start', lookup_expr='date__lte')
    from_date_end = filters.DateFilter(field_name='date_end', lookup_expr='date__gte')
    to_date_end = filters.DateFilter(field_name='date_end', lookup_expr='date__lte')
    sailor_id = filters.CharFilter(method='sailor_id_filter')
    sailor_name = filters.CharFilter(method='sailor_name_filter')
    is_continue = filters.BooleanFilter(method='is_continue_filter')
    status_document = filters.CharFilter(method='status_document_filter')
    port = filters.CharFilter(method='port_filter')
    with_agent = filters.BooleanFilter(method='with_agent_filter')
    is_new_document = filters.BooleanFilter()
    other_port = filters.CharFilter(method='other_port_filter')
    country = filters.CharFilter(method='country_filter')

    def is_continue_filter(self, queryset: QuerySet[SailorPassport], name, value):
        if value:
            return queryset.filter(items__isnull=False, statements__is_continue=True).distinct('id')
        return queryset.filter(items__isnull=False, statements__is_continue=False).distinct('id')

    def status_document_filter(self, queryset: QuerySet[SailorPassport], name, value):
        status_ids = value.split(',')
        return queryset.filter(status_document_id__in=status_ids)

    def port_filter(self, queryset: QuerySet[SailorPassport], name, value):
        port_ids = value.split(',')
        return queryset.filter(port_id__in=port_ids)

    def with_agent_filter(self, queryset: QuerySet[SailorPassport], name, value):
        if value:
            return queryset.filter(items__isnull=False).distinct('id')
        return queryset.filter(items__isnull=True)

    def sailor_id_filter(self, queryset: QuerySet[SailorPassport], name, value):
        passport_ids = self.get_sailor_id(value, self.field_name)
        return queryset.filter(id__in=passport_ids)

    def sailor_name_filter(self, queryset: QuerySet[SailorPassport], name, value):
        passport_ids = self.get_sailor_name(value, self.field_name)
        return queryset.filter(id__in=passport_ids)

    def other_port_filter(self, queryset: QuerySet[SailorPassport], name, value):
        port_list = value.split(',')
        _filters = map(lambda port: Q(other_port__iexact=port), port_list)
        _filters = reduce(lambda a, b: a | b, _filters)
        return queryset.filter(_filters)

    def country_filter(self, queryset: QuerySet[SailorPassport], name, value):
        country_ids = value.split(',')
        return queryset.filter(country_id__in=country_ids)

    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'date_create'),
            ('date_start', 'date_start'),
            ('date_end', 'date_end'),
            ('status_document__name_ukr', 'status_document'),
            ('port__name_ukr', 'port'),
            ('country__value', 'counrty'),
        )
    )
