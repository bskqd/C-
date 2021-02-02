import logging
from copy import deepcopy
from datetime import date, datetime
from random import uniform
from time import sleep

from django.db.models import Q
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, exceptions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import certificates.tasks
from back_office.models import ETIMonthRatio
from back_office.tasks import update_ntz_month_amount
from certificates import serializers
from certificates.filters import ETIRegistryFilters, ETIMonthRatioFilter
from certificates.models import ETIRegistry
from certificates.permissions import IntegrationNTZPermission
from communication.models import SailorKeys
from directory.models import NTZ, StatusDocument, Course
from itcs import magic_numbers
from sailor.document.models import CertificateETI
from sailor.document.permissions import CertificatesStatusPermission
from sailor.document.serializers import CertificateNTZSerializer
from sailor.models import Passport, Profile
from sailor.statement.models import StatementETI
from sailor.tasks import save_history

logger = logging.getLogger('ac-back.ntz_cert')

eti_integration_logger = logging.getLogger('eti_integration')


class ETIRegistryViewset(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, (permissions.IsAdminUser | IntegrationNTZPermission),)
    queryset = ETIRegistry.objects.all()
    serializer_class = serializers.ETIRegistrySerializer
    by_institution_serializer_class = serializers.ETIByInstitutionSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ETIRegistryFilters

    @swagger_auto_schema(methods=['get'], responses={200: serializers.ETIByInstitutionSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def by_institution(self, request):
        institution = NTZ.objects.filter(eti_registry__isnull=False).distinct('pk')
        response = self.by_institution_serializer_class(institution, many=True).data
        return Response(response)

    def perform_create(self, serializer):
        ser = serializer.save()
        save_history.s(user_id=self.request.user.id,
                       module='ETIRegistry',
                       action_type='create',
                       content_obj=ser,
                       serializer=serializers.ETIRegistrySerializer,
                       new_obj=ser,
                       ).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        save_history.s(user_id=self.request.user.id,
                       module='ETIRegistry',
                       action_type='delete',
                       content_obj=instance,
                       serializer=serializers.ETIRegistrySerializer,
                       old_obj=instance,
                       ).apply_async(serializer='pickle')
        instance.delete()


class ETIScheduleViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    serializer_class = serializers.ETIRegistrySerializer

    def get_queryset(self):
        course_id = self.kwargs['course']
        today = date.today()
        return ETIRegistry.objects.filter(course_id=course_id, date_end__gt=today)


class ETIMonthRatioViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ETIRegistry.objects.filter(institution__is_red=True)
    serializer_class = serializers.ETIMonthRatioSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ETIMonthRatioFilter
    permission_classes = (IsAuthenticated,)


class CreateCertificateAPI(APIView):
    permission_classes = (IsAuthenticated, CertificatesStatusPermission,)

    def get_param_or_raise(self, data, key):
        value = data.get(key)
        if value is None:
            raise exceptions.NotFound('{} not found. Set {}'.format(key, key))
        return value

    def post(self, request, *args, **kwargs):
        random_sleep = uniform(0.1, 0.5)
        sleep(random_sleep)
        logger.info('POST-request for NTZ certificate creating')
        try:
            type_search = request.data['type_search']
        except KeyError:
            raise ValidationError('Set type_search')
        logger.info('Searching type: {}'.format(type_search))
        if type_search == 'byInn':
            inn = self.get_param_or_raise(data=request.data, key='inn')
            date_birth = self.get_param_or_raise(data=request.data, key='date_birth')
            qs_passport = Passport.objects.filter(inn=inn)
            sailor_key = SailorKeys.objects.filter(citizen_passport__overlap=
                                                   list(qs_passport.values_list('id', flat=True)))
            profile = Profile.objects.filter(id__in=list(sailor_key.values_list('profile', flat=True)),
                                             date_birth=date_birth)
            sailor_key = sailor_key.filter(profile=profile.first().id).first()
            if not sailor_key or profile:
                logger.warning('Sailor not found. Searching type: {}, Parameter: {}'.format(
                    type_search,
                    inn
                ))
                raise exceptions.NotFound('Sailor not found')
        elif type_search == 'byPass':
            date_birth = self.get_param_or_raise(data=request.data, key='date_birth')
            passport_serial = self.get_param_or_raise(data=request.data, key='serial')
            try:
                qs_passport = Passport.objects.filter(serial__iexact=passport_serial)
                sailor_key = SailorKeys.objects.filter(citizen_passport__overlap=
                                                       list(qs_passport.values_list('id', flat=True)))
                profile = Profile.objects.filter(id__in=list(sailor_key.values_list('profile', flat=True)),
                                                 date_birth=date_birth)
                sailor_key = sailor_key.filter(profile=profile.first().id).first()
                if not profile or sailor_key:
                    logger.warning('Sailor not found. Searching type: {}, Parameter: {}'.format(
                        type_search,
                        passport_serial
                    ))
                    raise exceptions.NotFound('Sailor not found')
            except (Profile.DoesNotExist, SailorKeys.DoesNotExist, AttributeError) as e:
                raise exceptions.NotFound('Sailor not found')
        elif type_search == 'byName':
            first_name_ukr = self.get_param_or_raise(data=request.data, key='first_name_ukr')
            last_name_ukr = self.get_param_or_raise(data=request.data, key='last_name_ukr')
            date_birth = self.get_param_or_raise(data=request.data, key='date_birth')
            middle_name_ukr = request.data.get('middle_name_ukr')
            try:
                profile = Profile.objects.filter(last_name_ukr__iexact=last_name_ukr,
                                                 first_name_ukr__iexact=first_name_ukr,
                                                 date_birth=date_birth)
                if middle_name_ukr:
                    profile = profile.filter(middle_name_ukr__iexact=middle_name_ukr)
                profile = profile.first()
                sailor_key = SailorKeys.objects.filter(profile=profile.id).first()
                if not profile or not sailor_key:
                    logger.warning('Sailor not found. Searching type: {}, Parameter: {} {}'.format(
                        type_search,
                        first_name_ukr,
                        last_name_ukr
                    ))
                    raise exceptions.NotFound('Sailor not found')
            except (Profile.DoesNotExist, SailorKeys.DoesNotExist, AttributeError) as e:
                raise exceptions.NotFound('Sailor not found')
        else:
            logger.warning('Incorect type search. Searching type: {}'.format(type_search))
            raise exceptions.NotFound('Incorect type search')
        created_certificate = CertificateETI.objects.create(ntz_number=-1)
        logger.info('Certificate created. NTZ certificate ID: {}'.format(created_certificate.id))
        sailor_key.refresh_from_db()
        while created_certificate.id not in sailor_key.sertificate_ntz:
            sailor_key.sertificate_ntz.append(created_certificate.id)
            sailor_key.save(update_fields=['sertificate_ntz'])
            sailor_key.refresh_from_db()
        save_history.s(user_id=self.request.user.id, module='CertificateNTZ', action_type='create',
                       content_obj=created_certificate,
                       serializer=CertificateNTZSerializer,
                       new_obj=created_certificate,
                       sailor_key_id=sailor_key.id).apply_async(serializer='pickle')
        return Response({'id_sertificate': created_certificate.id, 'number_sert': created_certificate.ntz_number,
                         'rating': profile.get_rating})

    def put(self, request, *args, **kwargs):
        logger.info('PUT-request for NTZ certificate modifying')
        data = request.data
        certificate_id = data['id_sert']
        logger.info('NTZ certificate ID: {}'.format(certificate_id))
        course_training = data['course_traning']
        date_start = data['date_start']
        date_end = data['date_end']
        organisation_id = data.get('organisation_id', 0)
        status_document = data.get('status_document', 19)
        okpo_ntz = data.get('okpo_ntz', None)
        today = date.today()
        number_cert = data.get('number_sert', -1)
        try:
            certificate_instance = CertificateETI.objects.get(id=certificate_id)
            old_ntz = deepcopy(certificate_instance)
            course_instance = Course.objects.get(api_ntz_arr__overlap=[course_training])
            status_document = StatusDocument.objects.get(Q(id=status_document) | Q(name_eng__icontains=status_document)
                                                         | Q(name_ukr__icontains=status_document))
            ntz = NTZ.objects.get(Q(okpo=okpo_ntz) | Q(ntz_integration_id=organisation_id))

        except CertificateETI.DoesNotExist:
            logger.warning('Certificate not found. NTZ certificate ID: {}'.format(certificate_id))
            raise exceptions.NotFound('Sertificate not found')
        except Course.DoesNotExist:
            logger.warning('Course not found. Course ID: {}'.format(course_training))
            raise exceptions.NotFound('Course not found')
        except Course.MultipleObjectsReturned:
            raise exceptions.ParseError('CourseTraining Multiple object returned')
        except StatusDocument.DoesNotExist:
            logger.warning('StatusDocument not found. ID: {}'.format(status_document))
            raise exceptions.NotFound('StatusDocument not found')
        except StatusDocument.MultipleObjectsReturned:
            logger.warning('StatusDocument Multiple object returned. ID: {}'.format(status_document))
            raise exceptions.ParseError('StatusDocument Multiple object returned')
        except NTZ.DoesNotExist:
            logger.warning('NTZ not found. ID: {}'.format(okpo_ntz))
            raise exceptions.NotFound('NTZ not found')
        except NTZ.MultipleObjectsReturned:
            logger.warning('NTZ Multiple object returned. ID: {}'.format(okpo_ntz))
            raise exceptions.ParseError('NTZ Multiple object returned')
        if ETIRegistry.objects.filter(institution=ntz, course=course_instance, date_start__lte=today,
                                      date_end__gte=today).exists() is False:
            raise ValidationError('This institution does not have this course')
        certificate_instance.status_document = status_document
        certificate_instance.course_training = course_instance
        certificate_instance.date_start = date_start
        if date_end == 'None':
            date_end = None
        certificate_instance.date_end = date_end
        certificate_instance.ntz_number = number_cert
        certificate_instance.ntz = ntz
        certificate_instance.is_red = ntz.is_red
        certificate_instance.save()
        new_ntz = deepcopy(certificate_instance)
        save_history.s(user_id=self.request.user.id, module='CertificateNTZ', action_type='edit', old_obj=old_ntz,
                       content_obj=old_ntz, serializer=CertificateNTZSerializer, new_obj=new_ntz,
                       get_sailor=True).apply_async(serializer='pickle')
        logger.info('NTZ certificate updated. ID: {}'.format(certificate_instance.id))
        return Response({'status': 'success'})


class MultipleCreateCertificateAPI(APIView):
    permission_classes = (IsAuthenticated, CertificatesStatusPermission,)

    def get_param_or_raise(self, data, key):
        value = data.get(key)
        if value is None:
            raise exceptions.NotFound('{} not found. Set {}'.format(key, key))
        return value

    def post(self, request, *args, **kwargs):
        logger.info('POST-request for multiple NTZ certificates creating')
        response = list()
        request_data = request.data
        for sailor in request_data:
            first_name = sailor['first_name_ukr']
            last_name = sailor['last_name_ukr']
            date_birth = sailor['date_birth']
            middle_name_ukr = sailor.get('middle_name_ukr')
            profile = Profile.objects.filter(first_name_ukr__iexact=first_name, last_name_ukr__iexact=last_name,
                                             date_birth=date_birth)
            if middle_name_ukr:
                profile = profile.filter(middle_name_ukr__iexact=middle_name_ukr)
            profile = profile.first()
            if not profile:
                response.append({'first_name_ukr': first_name, 'last_name_ukr': last_name, 'date_birth': date_birth,
                                 'id_cert': None, 'rating': None})
                continue
            sailor_key = SailorKeys.objects.filter(profile=profile.id).first()
            if not sailor_key:
                response.append({'first_name_ukr': first_name, 'last_name_ukr': last_name, 'date_birth': date_birth,
                                 'id_cert': None, 'rating': None})
                continue
            certificate_instance = CertificateETI.objects.create(ntz_number=-1)
            logger.info('Certificate ID: {} created. Sailor name: {} {}'.format(
                certificate_instance.id,
                first_name,
                last_name
            ))
            response.append({'first_name_ukr': first_name,
                             'last_name_ukr': last_name,
                             'date_birth': date_birth,
                             'id_cert': certificate_instance.pk,
                             'rating': profile.get_rating,
                             'middle_name_ukr': middle_name_ukr})
            sailor_key.sertificate_ntz.append(certificate_instance.id)
            sailor_key.save(update_fields=['sertificate_ntz'])
        return Response(response)

    def put(self, request):
        logger.info('PUT-request for multiple NTZ certificates modifying')
        data = request.data
        response = list()
        today = date.today()
        for cert in data:
            certificate_id = cert['id_cert']
            logger.info('NTZ certificate ID: {}'.format(certificate_id))
            course_training_id = cert['course_training']
            date_start = cert['date_start']
            date_end = cert.get('date_end')
            if date_end == 'None':
                date_end = None
            status_document = cert['status_document']
            okpo_ntz = cert.get('okpo_ntz', None)
            organisation_id = cert['organisation_id']
            number_cert = cert.get('number_cert', -1)
            try:
                certificate_instance = CertificateETI.objects.get(id=certificate_id)
                old_ntz = deepcopy(certificate_instance)
                course_instance = Course.objects.get(api_ntz_arr__overlap=[course_training_id])
                status_document = StatusDocument.objects.get(
                    Q(id=status_document) | Q(name_eng__icontains=status_document)
                    | Q(name_ukr__icontains=status_document))
                ntz = NTZ.objects.get(Q(okpo=okpo_ntz) | Q(ntz_integration_id=organisation_id))
            except (CertificateETI.DoesNotExist, AttributeError):
                logger.warning('Certificate not found. NTZ certificate ID: {}'.format(certificate_id))
                response.append(
                    {'status': 'error', 'id_cert': certificate_id, 'description': 'Certificate by id not found'})
                continue
            except Course.DoesNotExist:
                logger.warning('Course not found. Course ID: {}'.format(course_training_id))
                response.append(
                    {'status': 'error', 'id_cert': certificate_id, 'description': 'Course training not found'})
                continue
            except Course.MultipleObjectsReturned:
                logger.warning('Course traning Multiple object returned. Course ID: {}'.format(course_training_id))
                response.append(
                    {'status': 'error', 'id_cert': certificate_id, 'description':
                        'Course training Multiple object returned'})
                continue
            except StatusDocument.DoesNotExist:
                logger.warning('StatusDocument not found. ID: {}'.format(status_document))
                response.append(
                    {'status': 'error', 'id_cert': certificate_id, 'description': 'Status document not found'})
                continue
            except StatusDocument.MultipleObjectsReturned:
                logger.warning('StatusDocument Multiple object returned. ID: {}'.format(status_document))
                response.append(
                    {'status': 'error', 'id_cert': certificate_id, 'description':
                        'Status document multiple object returned'})
                continue
            except NTZ.DoesNotExist:
                logger.warning('NTZ not found. ID: {}'.format(okpo_ntz))
                response.append({'status': 'error', 'id_cert': certificate_id, 'description': 'NTZ not found'})
                continue
            except NTZ.MultipleObjectsReturned:
                logger.warning('NTZ Multiple object returned. ID: {}'.format(okpo_ntz))
                response.append(
                    {'status': 'error', 'id_cert': certificate_id, 'description': 'ntz object multiple returned'})
                continue
            if ETIRegistry.objects.filter(course=course_instance, institution=ntz,
                                          date_start__lte=today, date_end__gte=today).exists() is False:
                response.append({'status': 'error', 'id_cert': certificate_id,
                                 'description': 'This institution does not have this course'})
                continue
            certificate_instance.status_document = status_document
            certificate_instance.course_training = course_instance
            certificate_instance.date_start = date_start
            certificate_instance.date_end = date_end
            certificate_instance.ntz_number = number_cert
            certificate_instance.ntz = ntz
            certificate_instance.save()
            response.append({'status': 'success', 'description': None, 'id_cert': certificate_id})
            new_ntz = deepcopy(certificate_instance)
            save_history.s(user_id=self.request.user.id, module='CertificateNTZ', action_type='edit', old_obj=old_ntz,
                           content_obj=old_ntz, serializer=CertificateNTZSerializer, new_obj=new_ntz,
                           get_sailor=True).apply_async(serializer='pickle')
            logger.info('NTZ certificate updated. ID: {}'.format(certificate_instance.id))
        return Response(response)


class CreateCertificateFromStatementAPI(APIView):
    permission_classes = (IsAuthenticated, CertificatesStatusPermission,)

    def post(self, request):
        statement_cert_id = request.data.get('statement_cert_id')
        date_start = request.data.get('date_start')
        date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        number = request.data.get('number')
        date_end = request.data.get('date_end')
        status_document = request.data.get('status_document', 19)
        eti_integration_logger.info('Get request about create statement',
                                    extra={'statement_pk': statement_cert_id,
                                           'request_data': request.data}, )
        # today = date.today()
        statement_certificate = StatementETI.objects.select_related('institution').get(id=statement_cert_id)
        institution = statement_certificate.institution
        # statement_date_end_meeting = statement_certificate.date_end_meeting
        # if statement_date_end_meeting > today:
        #     error_message = 'You can\'t get certificate before date end meeting'
        #     eti_integration_logger.error(error_message,
        #                                  extra={'request_data': request.data})
        #     raise ValidationError(error_message)
        certificate_inst = CertificateETI.objects.create(ntz=institution,
                                                         ntz_number=number,
                                                         course_training_id=statement_certificate.course_id,
                                                         date_start=date_start,
                                                         date_end=date_end,
                                                         status_document_id=status_document,
                                                         is_red=institution.is_red,
                                                         statement_id=statement_cert_id)
        sailor_qs = SailorKeys.objects.filter(statement_eti__overlap=[statement_certificate.pk])
        sailor_instance: SailorKeys = sailor_qs.first()
        if not sailor_instance:
            error_message = 'Sailor does not found'
            eti_integration_logger.error(error_message, extra={'request_data': request.data})
            raise ValidationError(error_message)
        sailor_instance.sertificate_ntz.append(certificate_inst.pk)
        sailor_instance.save(update_fields=['sertificate_ntz'])
        certificates.tasks.add_certificate_to_packet.s(certificate_inst.pk).apply_async()
        statement_certificate.status_document_id = magic_numbers.status_statement_eti_document_created
        statement_certificate.save(update_fields=['status_document_id'])
        eti_integration_logger.info('Success save certificate',
                                    extra={'statement_pk': statement_cert_id,
                                           'certificate_id': certificate_inst.pk,
                                           'request_data': request.data}, )
        certificates.tasks.send_statement_to_eti.s(statement_id=statement_certificate.pk, is_edit=True).apply_async()
        return Response({'status': 'Certificate successfully added', 'certificate_id': certificate_inst.pk}, status=201)


class CreateCertificateFromStatemenMultipletAPI(APIView):
    permission_classes = (IsAuthenticated, CertificatesStatusPermission,)

    def post(self, request):
        data = request.data
        eti_integration_logger.info('Get request about multiple create statement',
                                    extra={'request_data': request.data}, )
        response = []
        for statement in data:
            statement_cert_id = statement.get('statement_cert_id')
            date_start = statement.get('date_start')
            date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
            number = statement.get('number')
            date_end = statement.get('date_end')
            status_document = statement.get('status_document', 19)
            # today = date.today()
            statement_certificate = StatementETI.objects.select_related('institution').get(id=statement_cert_id)
            institution = statement_certificate.institution
            # statement_date_end_meeting = statement_certificate.date_end_meeting
            # if statement_date_end_meeting > today:
            #     error_message = 'You can\'t get certificate before date end meeting'
            #     eti_integration_logger.error(f'MultipleCreate: {error_message}',
            #                                  extra={'request_data': request.data, 'statement_pk': statement_cert_id})
            #     response.append({'status': 'error', 'description': error_message,
            #                      'statement_id': statement_cert_id})
            certificate_inst = CertificateETI.objects.create(ntz=institution,
                                                             ntz_number=number,
                                                             course_training_id=statement_certificate.course_id,
                                                             date_start=date_start,
                                                             date_end=date_end,
                                                             status_document_id=status_document,
                                                             is_red=institution.is_red,
                                                             statement_id=statement_cert_id)
            sailor_qs = SailorKeys.objects.filter(statement_eti__overlap=[statement_certificate.pk])
            sailor_instance: SailorKeys = sailor_qs.first()
            if not sailor_instance:
                error_message = 'Sailor does not found'
                eti_integration_logger.error(f'MultipleCreate: {error_message}',
                                             extra={'request_data': request.data, 'statement_pk': statement_cert_id})
                response.append({'status': 'error', 'description': error_message,
                                 'statement_id': statement_cert_id})
            sailor_instance.sertificate_ntz.append(certificate_inst.pk)
            sailor_instance.save(update_fields=['sertificate_ntz'])
            certificates.tasks.add_certificate_to_packet.s(certificate_inst.pk).apply_async()
            statement_certificate.status_document_id = magic_numbers.status_statement_eti_document_created
            statement_certificate.save(update_fields=['status_document_id'])
            response.append({'status': 'Certificate successfully added', 'certificate_id': certificate_inst.pk,
                             'description': None})
            eti_integration_logger.info('MultipleCreate: Success save certificate',
                                        extra={'statement_pk': statement_cert_id,
                                               'certificate_id': certificate_inst.pk,
                                               'request_data': request.data}, )
            certificates.tasks.send_statement_to_eti.s(statement_id=statement_certificate.pk,
                                                       is_edit=True).apply_async()
        return Response(response, status=201)


class UpdateCertificateAPI(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = CertificateETI.objects.all()
    serializer_class = serializers.PublicUpdateStatusSerializer
    permission_classes = (permissions.IsAuthenticated, IntegrationNTZPermission,)

    def perform_update(self, serializer):
        obj = self.get_object()
        eti_integration_logger.info('Peform update status certificate',
                                    extra={'certificate_id': obj.pk,
                                           'data': self.request.data})
        certificate_inst = serializer.save()
        certificates.tasks.add_certificate_to_packet.s(certificate_inst.pk).apply_async()


class ETIInstitutionViewset(viewsets.ModelViewSet):
    queryset = NTZ.objects.all().order_by('is_disable', '-is_red')
    serializer_class = serializers.InstituteETISerializer
    public_serializer_class = serializers.PublicInstituteETISerializer
    permission_classes = (permissions.IsAuthenticated, (permissions.IsAdminUser | IntegrationNTZPermission),)

    def get_serializer_class(self):
        if self.request.user.pk == 16:
            return self.public_serializer_class
        return self.serializer_class

    def perform_create(self, serializer):
        ser = serializer.save()
        save_history.s(user_id=self.request.user.id,
                       module='ETIInstitution',
                       action_type='create',
                       content_obj=ser,
                       serializer=serializers.InstituteETISerializer,
                       new_obj=ser,
                       ).apply_async(serializer='pickle')

    def perform_destroy(self, instance):
        save_history.s(user_id=self.request.user.id,
                       module='ETIInstitution',
                       action_type='delete',
                       content_obj=instance,
                       serializer=serializers.InstituteETISerializer,
                       old_obj=instance,
                       ).apply_async(serializer='pickle')
        instance.delete()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        if self.request.user.pk == 16:
            filter_kwargs = {'uuid': self.kwargs[lookup_url_kwarg]}
        from rest_framework.generics import get_object_or_404
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class MonthRatioByCourse(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.UpdateModelMixin,
                         mixins.RetrieveModelMixin):
    queryset = Course.objects.filter(is_disable=False).order_by('code_for_parsing')
    serializer_class = serializers.ListMonthRatioByCourse
    update_serializer_class = serializers.UpdateMonthRatioByCourse
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)
    http_method_names = ['get', 'post', 'head', 'options', 'put']

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return self.serializer_class
        if self.action == 'update':
            return self.update_serializer_class
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        course_instance = self.get_object()
        serializer = self.update_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        eti_ratio_to_create = data.get('eti_ratio')
        month_ratio = ETIMonthRatio.objects.filter(course=course_instance)
        del_ratio = serializers.FullInfoETIMonthRatioSerializer(month_ratio, many=True).data
        month_ratio.delete()
        bulk = [ETIMonthRatio(course=course_instance, ntz=ratio['eti_id'],
                              ratio=ratio['eti_ratio'], month_amount=0) for ratio in eti_ratio_to_create]
        ETIMonthRatio.objects.bulk_create(bulk)
        update_ntz_month_amount.delay(course_instance.pk)
        certificates.tasks.history_eti_month_ratio.s(del_ratio, self.request.user.id, course_instance.pk).apply_async()
        return Response(self.serializer_class(course_instance).data)


class PublicCourseViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated, (IntegrationNTZPermission | permissions.IsAdminUser),)
    queryset = Course.objects.all().order_by('name_ukr')
    serializer_class = serializers.PublicCourseSerializer
