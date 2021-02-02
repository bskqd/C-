from copy import deepcopy
from datetime import timedelta, date

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q, When, Case, Value, FloatField, F, Sum, Func
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, generics, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

import back_office.utils
import sailor.misc
import sailor.permissions
from back_office.filters import ETIReportFilter, PacketReportFilter
from back_office.models import (ETICoefficient, PriceForPosition, CoursePrice, ETIProfitPart, PacketItem,
                                DependencyItem)
from back_office.permissions import PacketPermission, PriceForCoursePermission, ETIProfitPartPermission
from back_office.serializers import (PriceForPositionSerializer, CoursePriceSerializer, ETIProfitPartSerializer,
                                     PacketSerializer, PacketReportListSerializer, PacketItemPreviewSerializer)
from back_office.tasks import delete_statement_and_packet
from communication.models import SailorKeys
from itcs.magic_numbers import AccrualTypes
from mixins.core import ObjectFromQuerySetMixin
from reports.filters import StandardResultsSetPagination, ShortLinkResultPagination
from sailor.document.models import CertificateETI, QualificationDocument, ProofOfWorkDiploma, Education
from sailor.tasks import save_history


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s)'


class PriceForPositionView(viewsets.ModelViewSet):
    serializer_class = PriceForPositionSerializer
    queryset = PriceForPosition.objects.filter(is_hidden=False)
    permission_classes = ((IsAdminUser | PriceForCoursePermission),)
    pagination_class = ShortLinkResultPagination

    page_size_param = openapi.Parameter('page_size', openapi.IN_QUERY,
                                        description="Number of results to return per page.", type=openapi.TYPE_INTEGER)
    page_param = openapi.Parameter('page', openapi.IN_QUERY,
                                   description="A page number within the paginated result set.",
                                   type=openapi.TYPE_INTEGER)

    def perform_create(self, serializer):
        date_start = serializer.validated_data['date_start']
        form = serializer.validated_data['type_of_form']
        type_document = serializer.validated_data['type_document']
        form_to_currency = {'Second': 'USD', 'First': 'UAH'}
        if type_document.id == AccrualTypes.AGENT:
            form_to_currency = {'Second': '%', 'First': 'UAH'}
        currency = form_to_currency[form]
        date_end_current_coef = date_start - timedelta(days=1)
        today = date.today()
        try:
            last_coefficient = self.get_queryset().get(date_end__isnull=True, type_of_form=form,
                                                       type_document=type_document)
        except PriceForPosition.DoesNotExist:
            ser = serializer.save(currency=currency)
            save_history.s(user_id=self.request.user.id, module='PriceForPosition',
                           action_type='create', content_obj=ser, serializer=self.serializer_class,
                           new_obj=ser).apply_async(serializer='pickle')
            return None
        if last_coefficient.date_start > today:
            raise ValidationError('New coefficient exists - use update')
        old_last_coefficient = deepcopy(last_coefficient)
        last_coefficient.date_end = date_end_current_coef
        last_coefficient.save(update_fields=['date_end'])
        save_history.s(user_id=self.request.user.id, module='PriceForPosition',
                       action_type='edit', content_obj=last_coefficient, serializer=self.serializer_class,
                       new_obj=last_coefficient, old_obj=old_last_coefficient).apply_async(serializer='pickle')
        ser = serializer.save(currency=currency)
        save_history.s(user_id=self.request.user.id, module='PriceForPosition',
                       action_type='create', content_obj=ser, serializer=self.serializer_class,
                       new_obj=ser).apply_async(serializer='pickle')

    @action(detail=False)
    def actual_values(self, request):
        queryset = PriceForPosition.today.filter(is_hidden=False)
        return Response(self.serializer_class(instance=queryset, many=True).data)

    @swagger_auto_schema(method='get', manual_parameters=[page_param, page_size_param])
    @action(detail=True)
    def future_values(self, request, *args, **kwargs):
        today = date.today()
        obj = self.get_object()
        queryset = PriceForPosition.objects.filter(type_of_form=obj.type_of_form, type_document=obj.type_document,
                                                   is_hidden=False)
        future = queryset.filter(date_start__gt=today)
        page = self.paginate_queryset(future)
        if page is not None:
            data = self.get_response_data(page)
            return self.get_paginated_response(data)
        data = self.get_response_data(future)
        return Response(data)

    @swagger_auto_schema(method='get', manual_parameters=[page_param, page_size_param])
    @action(detail=True)
    def past_values(self, request, *args, **kwargs):
        today = date.today()
        obj = self.get_object()
        queryset = PriceForPosition.objects.filter(type_of_form=obj.type_of_form, type_document=obj.type_document,
                                                   is_hidden=False)
        past_values = queryset.filter(date_start__lt=today, date_end__lt=today)
        page = self.paginate_queryset(past_values)
        if page is not None:
            data = self.get_response_data(page)
            return self.get_paginated_response(data)
        data = self.get_response_data(past_values)
        return Response(data)

    def get_response_data(self, paginated_queryset):
        return self.serializer_class(instance=paginated_queryset, many=True).data

    def perform_destroy(self, instance):
        today = date.today()
        date_end = instance.date_start - timedelta(days=1)
        if date_end < today:
            raise ValidationError('cannot delete record')
        current_coeff = self.queryset.get(date_end=date_end, type_of_form=instance.type_of_form,
                                          type_document=instance.type_document)
        _current_coeff = deepcopy(current_coeff)
        current_coeff.date_end = None
        current_coeff.save(update_fields=['date_end'])
        save_history.s(user_id=self.request.user.id, module='PriceForPosition', action_type='edit',
                       new_obj=current_coeff,
                       content_obj=current_coeff, old_obj=_current_coeff, serializer=self.serializer_class
                       ).apply_async(serializer='pickle')
        _instance = deepcopy(instance)
        instance.delete()
        save_history.s(user_id=self.request.user.id, module='PriceForPosition', action_type='delete',
                       content_obj=_instance, old_obj=_instance, serializer=self.serializer_class
                       ).apply_async(serializer='pickle')


class CoursePriceView(viewsets.ModelViewSet):
    queryset = CoursePrice.objects.all()
    serializer_class = CoursePriceSerializer
    permission_classes = ((IsAdminUser | PriceForCoursePermission),)

    @action(detail=False)
    def actual_values(self, request):
        queryset = CoursePrice.today.all()
        return Response(self.serializer_class(instance=queryset, many=True).data)

    def perform_create(self, serializer):
        date_start = serializer.validated_data['date_start']
        form = serializer.validated_data['type_of_form']
        form_to_currency = {'Second': 'USD', 'First': 'UAH'}
        course = serializer.validated_data['course']
        currency = form_to_currency[form]
        date_end_current_coef = date_start - timedelta(days=1)
        today = date.today()
        try:
            last_coefficient = self.get_queryset().get(date_end__isnull=True, type_of_form=form,
                                                       course=course)
        except CoursePrice.DoesNotExist:
            ser = serializer.save(currency=currency)
            save_history.s(user_id=self.request.user.id, module='CoursePrice',
                           action_type='create', content_obj=ser, serializer=self.serializer_class,
                           new_obj=ser).apply_async(serializer='pickle')
            return None
        if last_coefficient.date_start > today:
            raise ValidationError('New coefficient exists - use update')
        old_last_coefficient = deepcopy(last_coefficient)
        last_coefficient.date_end = date_end_current_coef
        last_coefficient.save(update_fields=['date_end'])
        save_history.s(user_id=self.request.user.id, module='CoursePrice',
                       action_type='edit', content_obj=last_coefficient, serializer=self.serializer_class,
                       new_obj=last_coefficient, old_obj=old_last_coefficient).apply_async(serializer='pickle')
        ser = serializer.save(currency=currency)
        save_history.s(user_id=self.request.user.id, module='CoursePrice',
                       action_type='create', content_obj=ser, serializer=self.serializer_class,
                       new_obj=ser).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        today = date.today()
        date_end = instance.date_start - timedelta(days=1)
        if date_end < today:
            raise ValidationError('cannot delete record')
        current_coeff = self.queryset.get(date_end=date_end, type_of_form=instance.type_of_form,
                                          course=instance.course)
        _current_coeff = deepcopy(current_coeff)
        current_coeff.date_end = None
        current_coeff.save(update_fields=['date_end'])
        save_history.s(user_id=self.request.user.id, module='CoursePrice', action_type='edit',
                       new_obj=current_coeff,
                       content_obj=current_coeff, old_obj=_current_coeff, serializer=self.serializer_class
                       ).apply_async(serializer='pickle')
        _instance = deepcopy(instance)
        instance.delete()
        save_history.s(user_id=self.request.user.id, module='CoursePrice', action_type='delete',
                       content_obj=_instance, old_obj=_instance, serializer=self.serializer_class
                       ).apply_async(serializer='pickle')


class ETIProfitView(viewsets.ModelViewSet):
    queryset = ETIProfitPart.objects.all()
    serializer_class = ETIProfitPartSerializer
    permission_classes = ((IsAdminUser | ETIProfitPartPermission),)

    @action(detail=False)
    def actual_values(self, request):
        queryset = ETIProfitPart.today.all()
        return Response(self.serializer_class(instance=queryset, many=True).data)

    def perform_create(self, serializer):
        date_start = serializer.validated_data['date_start']
        date_end_currrent_coef = date_start - timedelta(days=1)
        today = date.today()
        author = self.request.user
        try:
            last_coefficient = self.queryset.get(date_end__isnull=True)
        except ETIProfitPart.DoesNotExist:
            ser = serializer.save()
            save_history.s(user_id=author.id,
                           module='ETIProfitPart',
                           action_type='create',
                           content_obj=ser,
                           serializer=ETIProfitPartSerializer,
                           new_obj=ser,
                           ).apply_async(serializer='pickle')
            return None
        if last_coefficient.date_start > today:
            raise ValidationError('New coefficient exists - use update')
        old_last_coefficient = deepcopy(last_coefficient)
        last_coefficient.date_end = date_end_currrent_coef
        last_coefficient.save(update_fields=['date_end'])
        save_history.s(user_id=author.id,
                       module='ETIProfitPart',
                       action_type='edit',
                       content_obj=last_coefficient,
                       serializer=ETIProfitPartSerializer,
                       new_obj=last_coefficient,
                       old_obj=old_last_coefficient,
                       ).apply_async(serializer='pickle')
        ser = serializer.save()
        save_history.s(user_id=author.id,
                       module='ETIProfitPart',
                       action_type='create',
                       content_obj=ser,
                       serializer=ETIProfitPartSerializer,
                       new_obj=ser,
                       ).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        today = date.today()
        date_end = instance.date_start - timedelta(days=1)
        if date_end < today:
            raise ValidationError('cannot delete record')
        current_coeff = self.queryset.get(date_end=date_end)
        _current_coeff = deepcopy(current_coeff)
        current_coeff.date_end = None
        current_coeff.save(update_fields=['date_end'])
        author = self.request.user
        save_history.s(user_id=author.id,
                       module='ETICoefficient',
                       action_type='edit',
                       new_obj=current_coeff,
                       content_obj=current_coeff,
                       old_obj=_current_coeff,
                       serializer=ETIProfitPartSerializer,
                       ).apply_async(serializer='pickle')
        _instance = deepcopy(instance)
        instance.delete()
        save_history.s(user_id=author.id,
                       module='ETICoefficient',
                       action_type='delete',
                       content_obj=_instance,
                       old_obj=_instance,
                       serializer=ETIProfitPartSerializer,
                       ).apply_async(serializer='pickle')


class PacketView(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin, mixins.ListModelMixin, ObjectFromQuerySetMixin):
    queryset = PacketItem.objects.all().order_by('created_at')
    serializer_class = PacketSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        PacketPermission,
        sailor.permissions.CheckHeadAgentGroup,
        sailor.permissions.CheckAgentPermission,
    )

    def perform_create(self, serializer):
        from .tasks import create_notification_about_new_packet
        ser = serializer.save()
        save_history.s(user_id=self.request.user.id, module=PacketItem._meta.object_name, action_type='create',
                       content_obj=ser, serializer=PacketSerializer, new_obj=ser,
                       sailor_key_id=ser.sailor_id).apply_async(serializer='pickle')
        create_notification_about_new_packet.s(packet_id=ser.pk).apply_async()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return PacketItem.objects.none()
        sailor_id = self.kwargs['pk']
        try:
            keys = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise ValidationError('Sailor does not exists')
        return PacketItem.objects.filter(id__in=keys.packet_item).order_by('-id')

    def perform_destroy(self, instance):
        delete_statement_and_packet(instance.id, only_statement=True)
        _instance = deepcopy(instance)
        sailor_key = SailorKeys.by_document.id(instance=instance)
        instance.delete()
        save_history.s(user_id=self.request.user.id, sailor_key_id=sailor_key.pk,
                       module=instance._meta.object_name, action_type='delete',
                       content_obj=_instance, serializer=self.serializer_class,
                       old_obj=_instance).apply_async(serializer='pickle')
        if sailor_key:
            sailor_key.packet_item.remove(_instance.pk)
            sailor_key.save(update_fields=['packet_item'])

    @action(detail=True, methods=['post'])
    def create_diploma_for_proof(self, request, pk):
        packet: PacketItem = self.get_object()
        sailor_instance = SailorKeys.objects.filter(packet_item__overlap=[packet.pk]).first()
        checking_for_create_proof = packet.dependencies.filter(
            Q(type_document_id=AccrualTypes.PROOF_OF_DIPLOMA, content_type__model='statementqualification',
              item_status=DependencyItem.TO_BUY) &
            ~Q(type_document_id=AccrualTypes.QUALIFICATION,
               item_status__in=[DependencyItem.TO_BUY, DependencyItem.WAS_BOUGHT])
        )
        if packet.position_type != 1 or not checking_for_create_proof.exists():
            raise ValidationError('You can\'t create proof for this packet')
        with transaction.atomic():
            instance = PacketItem.objects.create(
                sailor_id=sailor_instance.pk,
                position_type=1,
                agent=packet.agent,
                service_center=packet.service_center
            )
            instance.position.set(packet.position.all())
            sailor_instance.packet_item.append(instance.pk)
            sailor_instance.save(update_fields=['packet_item'])
            dependency: DependencyItem = checking_for_create_proof.first()
            DependencyItem.objects.create(
                packet_item=instance, item=dependency.item,
                item_status=DependencyItem.TO_BUY,
                type_document_id=AccrualTypes.QUALIFICATION
            )
        return Response(self.serializer_class(instance=instance).data)


class ReportPacketList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated, PacketPermission,)
    queryset = DependencyItem.objects.filter(item_status=DependencyItem.WAS_BOUGHT)
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = PacketReportFilter
    pagination_class = ShortLinkResultPagination
    serializer_class = PacketReportListSerializer

    def list(self, request, *args, **kwargs):
        save_history.s(user_id=self.request.user.pk, module='Report PacketList', action_type='generate',
                       new_obj={'url': self.request.build_absolute_uri(), 'params': dict(request.GET)}).apply_async()
        return super(ReportPacketList, self).list(request, *args, **kwargs)


class PacketItemPreview(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, PacketPermission,)
    serializer_class = PacketItemPreviewSerializer

    def post(self, request, *args, **kwargs):
        can_create_packet = True
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sailor_id = kwargs.get('sailor_pk')
        try:
            sailor_instance = SailorKeys.objects.get(id=sailor_id)
        except SailorKeys.DoesNotExist:
            raise NotFound('Sailor does not found')
        positions = data.get('position')
        rank_id = positions[0].rank.pk
        list_positions = [position.pk for position in positions]
        is_continue = sailor.misc.check_is_continue(sailor_instance, rank_id, list_positions)
        experience = {'used_verification': False, 'experience_info': []}
        if is_continue in [0, 2]:
            experience = self.check_experience(sailor_instance.pk, list_positions)
            can_create_packet = experience['have_all_exp']
        user = self.request.user
        up = user.userprofile
        packet = False if up.type_user == up.MARAD else True
        docs = sailor.misc.CheckSailorForPositionDKK(
            sailor=sailor_instance.pk,
            list_position=list_positions,
            demand_position=True,
            is_continue=is_continue,
            packet=packet
        ).get_docs_with_status()
        education_with_sqc = data.get('education_with_sqc', False)
        if not education_with_sqc:
            try:
                back_office.utils.check_diploma_of_higher_education(docs)
            except ValidationError:
                can_create_packet = False
            if any([document['is_verification'] for document in docs['exists_doc']]):
                can_create_packet = False
        else:
            can_create_packet = True
        return Response({'can_create_packet': can_create_packet,
                         'used_verification_exp': experience['used_verification'],
                         'experience': experience['experience_info'],
                         'documents_not_exists': docs['descr'],
                         'documents_exists': docs['exists_doc']})

    def check_experience(self, sailor_id, list_positions):
        """
        Checking the sailor's experience for creating a packet
        """
        used_verification = False
        checking_exp = sailor.misc.CheckSailorExperience(sailor=sailor_id, list_position=list_positions)
        experience = checking_exp.check_experience_many_pos()
        have_all_exp = False
        if experience:
            have_all_exp = any(exp['value'] for exp in experience)
        if not have_all_exp:
            experience_with_verification = checking_exp.check_experience_many_pos(is_verification=True)
            if not experience_with_verification == experience:
                used_verification = True
                experience = experience_with_verification
        return {'used_verification': used_verification, 'experience_info': experience, 'have_all_exp': have_all_exp}


class MergeDocumentView(GenericAPIView):
    serializer_class = back_office.serializers.MergeDocumentSerializer
    permission_classes = (permissions.IsAuthenticated, back_office.permissions.MergeDocumentPermission)

    def update_field(self, new_instance, old_instance, exclude_fields):
        for field in new_instance._meta.fields:
            field_name = field.name
            if field_name in exclude_fields:
                continue
            setattr(old_instance, field_name, getattr(new_instance, field_name))

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        ct: ContentType = validated_data.get('content_type')
        model = ct.model_class()
        old_instance = model.objects.get(id=validated_data.get('old_document'))
        new_instance = model.objects.get(id=validated_data.get('new_document'))
        if new_instance.pk < old_instance.pk:
            new_instance, old_instance = old_instance, new_instance
        if old_instance.get_number != new_instance.get_number:
            raise ValidationError('Number new document not equals old document')
        if model is QualificationDocument or model is ProofOfWorkDiploma:
            self.update_field(new_instance, old_instance, ['id', 'pk', 'author', 'created_at', 'modified_at'])
            if hasattr(old_instance, 'related_docs'):
                old_instance.related_docs.set(new_instance.related_docs.all())
            old_instance.verification_status.set(new_instance.verification_status.all())
            old_instance.save(force_update=True)
            if hasattr(new_instance, 'proofofworkdiploma_set') and new_instance.proofofworkdiploma_set.exists():
                proofs = new_instance.proofofworkdiploma_set.all()
                proofs.update(diploma=old_instance)
            new_instance.delete()
        elif model is Education:
            self.update_field(new_instance, old_instance, ['id', 'pk', 'author', 'created_at', 'modified_at'])
            old_instance.verification_status.set(new_instance.verification_status.all())
            old_instance.save(force_update=True)
            new_instance.delete()
        else:
            raise ValidationError('You cant merge this documents')
        return Response({'status': 'success'})
