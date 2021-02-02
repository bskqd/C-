import json
from datetime import datetime, date, timedelta
from typing import List, Union

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import CharField, Q, F, Value, QuerySet
from django.db.models.functions import Cast, Concat, ExtractYear
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, permissions, mixins, parsers, exceptions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

import notifications.tasks
import port_back.constants
import reports.filters
import ship.filters
import ship.permissions
import ship.serializers
import ship.utils
from back_office.models import DeadweightPricePeriod
from communication.models import ShipKey
from core.mixins import StandardResultsSetPagination
from core.models import User, Photo
from directory.models import Port
from ship.mixins import GetQuerySetMixin
from ship.models import MainInfo, ShipStaff, IORequest, ShipAgentNomination, ShipInPort, DraftDocument, \
    PhotoInDraftDocument
from signature.models import Signature


class MainInfoView(viewsets.ModelViewSet):
    queryset = MainInfo.objects.select_related('author').all()
    serializer_class = ship.serializers.MainInfoSerializer
    permission_classes = (permissions.IsAuthenticated, ship.permissions.MainInfoPermissions)
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ship.filters.ShipFilters

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MainInfo.objects.none()
        user = self.request.user
        if user.type_user in [User.HARBOR_MASTER_CH, User.HARBOR_WORKER_CH]:
            return self.queryset.filter(id__in=self.get_id_main_info_for_port(user.get_port))
        return self.queryset.all()

    def perform_create(self, serializer):
        ser: MainInfo = serializer.save()
        ShipKey.objects.create(imo_number=ser.imo_number, maininfo=ser.pk)

    def get_id_main_info_for_port(self, ports) -> List:
        io_request = list(IORequest.objects.filter(port__in=ports).values_list('id', flat=True))
        id_main_info = list(ShipKey.objects.filter(iorequest__overlap=io_request).values_list('maininfo', flat=True))
        return id_main_info


    @action(methods=['get'], detail=True)
    def last_change(self, request, pk, *args, **kwargs):
        model = MainInfo
        response = ship.utils.last_change_object(request, model, pk)
        return Response(response)


class ShipStaffView(GetQuerySetMixin, viewsets.ModelViewSet):
    queryset = ShipStaff.objects.all()
    serializer_class = ship.serializers.ShipStaffSerializer
    permission_classes = (permissions.IsAuthenticated, ship.permissions.ShipStaffPermission)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ship.filters.ShipStaffFilters

    def perform_create(self, serializer):
        ser: ShipStaff = serializer.save()
        ship_key = ShipKey.objects.get(pk=self.kwargs.get('ship_pk'))
        ship_key.shipstaff.append(ser.pk)
        ship_key.save(update_fields=['shipstaff'])


class IORequestView(GetQuerySetMixin, viewsets.ModelViewSet):
    queryset = IORequest.objects.all()
    serializer_class = ship.serializers.IORequestSerializer
    permission_classes = (permissions.IsAuthenticated, ship.permissions.IORequestPermissions)
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = reports.filters.IORequestFilters

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return IORequest.objects.none()
        queryset = super().get_queryset()
        user = self.request.user
        if user.type_user in [User.HARBOR_MASTER_CH, User.HARBOR_WORKER_CH]:
            return queryset.filter(port__in=user.get_port)
        elif user.type_user in [User.BORDER_GUARD_CH, User.PORT_MANAGER_CH]:
            return queryset.filter(port__in=user.get_port,
                                   datetime_issued__gte=datetime.now() - timedelta(days=2))
        return queryset

    def check_exists_signs(self):
        head_agency = self.request.user.userprofile.agency.agency_user.user

        return self.request.user.signatures.filter(is_actual=True).exists() and head_agency.signatures.filter(
            is_actual=True, type_signature='stamp').exists()

    def perform_create(self, serializer):
        data = serializer.validated_data
        draft = data.pop('draft', None)
        deadweight = data.get('deadweight', 0)
        ship_key = ShipKey.objects.get(pk=self.kwargs.get('ship_pk'))
        main_info_obj = MainInfo.objects.get(id=ship_key.maininfo)
        if main_info_obj.is_ban:
            raise ValidationError('Ship is banned')
        if self.request.user.type_user in [self.request.user.AGENT_CH, self.request.user.HEAD_AGENCY_CH]:
            self.check_exists_signs()
        ship_staff = data.get('ship_staff', [])
        request_info = self.get_json_info_for_iorequest(ship_staff, main_info_obj)
        price_form1 = self.get_price_for_iorequest(deadweight)
        with transaction.atomic():
            ser: IORequest = serializer.save(status_document_id=port_back.constants.PROCESSED,
                                             ship_name=main_info_obj.name,
                                             request_info=request_info,
                                             price_form1=price_form1)
            ship_key.iorequest.append(ser.pk)
            ship_key.save(update_fields=['iorequest'])
            signature_password = serializer.validated_data.pop('signature_password')
            if draft:
                json_document = draft.document_json
                photos = json_document.get('photo_tmp')
                request_photo = ser.photo
                bulk_update = []
                for type_doc in photos:
                    array_photos = photos[type_doc]
                    for photo in array_photos:
                        name = photo['name']
                        photo_draft = draft.photos.get(photo__endswith=name)
                        photo, _ = Photo.objects.get_or_create(type_photo=type_doc, file=photo_draft.photo.name)
                        request_photo.append(photo.pk)
                        if self.request.user.type_user in [self.request.user.AGENT_CH,
                                                           self.request.user.HEAD_AGENCY_CH]:
                            cifra_uuid = self.send_file_to_cifra(photo)
                            photo.cifra_uuid = cifra_uuid
                            self.signing_file_in_cifra(photo, signature_password)
                            photo.is_signed = True
                            bulk_update.append(photo)
                Photo.objects.bulk_update(bulk_update, ['is_signed', 'cifra_uuid'])
                ser.photo = request_photo
                ser.save()
                draft.delete()
        notifications.tasks.create_notification_about_new_iorequest.s(ser.pk, ship_key.pk).apply_async()

    def send_file_to_cifra(self, photo_instance: Photo):
        date_create_document = date.today()
        number_document = photo_instance.type_photo
        files_to_send = {'document_original': open(photo_instance.file.path, 'rb')}
        data_to_send = {'date_create_document': date_create_document, 'type_document': 'Input/Output File',
                        'number': number_document}
        headers_to_send = {'Authorization': f'Bearer {self.request.user.userprofile.cifra_key}'}
        url = f'{settings.CIFRA_URL}api/v1/documents/'
        response_cifra = requests.post(url=url, data=data_to_send, files=files_to_send, headers=headers_to_send)
        response_cifra_json = response_cifra.json()
        if response_cifra.status_code not in [requests.status_codes.codes.ok, requests.status_codes.codes.created]:
            raise exceptions.ValidationError(response_cifra.json(), code=response_cifra.status_code)
        return response_cifra_json.get('uuid')

    def signing_file_in_cifra(self, document: Photo, password):
        signatures = self.request.user.signatures.filter(is_actual=True)
        signatures = signatures | self.request.user.userprofile.agency.agency_user.user.signatures.filter(
            is_actual=True, type_signature=Signature.STAMP
        )
        for signature in signatures:
            file_to_send = {'signature': open(signature.file_signature.path, 'rb')}
            headers = {'Authorization': f'Bearer {self.request.user.userprofile.cifra_key}'}
            url = f'{settings.CIFRA_URL}api/v1/signature/{document.cifra_uuid}/signature/'
            password_to_send = password if signature.type_signature == Signature.SIGN else signature.password
            data_to_send = {'password': password_to_send}
            response = requests.post(url=url, data=data_to_send, files=file_to_send, headers=headers)
            if response.status_code in [requests.status_codes.codes.ok, requests.status_codes.codes.created]:
                response_json = response.json()
                document.is_signed = True
        return document

    def get_json_info_for_iorequest(self, ship_staff, main_info_obj):
        staff = [ship.utils.custom_model_to_dict(staff) for staff in ship_staff]
        main_info = ship.utils.custom_model_to_dict(main_info_obj)
        response = {'staff': staff, 'main_info': main_info}
        return json.loads(json.dumps(response, cls=DjangoJSONEncoder))

    def get_price_for_iorequest(self, deadweight=0):
        """
        Returns the price for IORequest based on the deadweight of the vessel and the current price for today
        """
        today = date.today()
        current_period = DeadweightPricePeriod.objects.filter((Q(date_end__gte=today) | Q(date_end__isnull=True)) &
                                                              Q(date_start__lte=today)).first()
        deadweight_prices = current_period.prices.filter(
            (Q(from_deadweight__lte=deadweight) & Q(to_deadweight__gte=deadweight)) |
            (Q(from_deadweight__lte=deadweight) & Q(to_deadweight__isnull=True))
        )
        return deadweight_prices.first().price

    @action(methods=['get'], detail=False)
    def port(self, request, *args, **kwargs):
        user = request.user
        if user.type_user not in [User.AGENT_CH, User.HEAD_AGENCY_CH]:
            ports = list(Port.objects.filter(is_disable=False).values_list('id', flat=True))
        else:
            min_date_nomination = datetime.now() - relativedelta(months=port_back.constants.VALID_NOMINATION_MONTHS)
            ports = ShipAgentNomination.objects.filter(
                Q(ship_key=self.kwargs.get('ship_pk')) &
                Q(status_document_id=port_back.constants.ISSUED) &
                Q(date_verification__gte=min_date_nomination) &
                (Q(agent__agent__agency=user.get_agency) | Q(agent__head_agency__agency=user.get_agency))
            ).order_by('port_id').distinct('port_id').values_list('port_id', flat=True)
        return Response(ports)

    @swagger_auto_schema(request_body=no_body,
                         manual_parameters=[openapi.Parameter(name='inspection_act',
                                                              type=openapi.TYPE_FILE,
                                                              in_=openapi.IN_FORM,
                                                              description='Ship\'s inspection act')])
    @action(methods=['post'], detail=True, parser_classes=(MultiPartParser,))
    def inspection_act(self, request, *args, **kwargs):
        """
        Loads the ship's inspection act to IO Request
        """
        inspection_act = request.FILES.get('inspection_act')
        io_request = self.get_object()
        io_request.inspection_act = inspection_act
        io_request.save(update_fields=['inspection_act'])
        return Response({'status': 'success'})


class SearchByShip(APIView):

    @swagger_auto_schema(request_body=ship.serializers.SearchSerializer)
    def post(self, request, *args, **kwargs):
        query = request.data.get('query')
        main_info = MainInfo.objects.annotate(
            imo_number_char=Cast('imo_number', CharField())
        ).filter(Q(imo_number_char__contains=query) | Q(name__icontains=query))[:20]
        io_requests = IORequest.objects.annotate(
            search_number=Concat(
                F('number'), Value('/'), ExtractYear(F('created_at')),
                output_field=CharField())
        ).filter(search_number__icontains=query).order_by('pk')[:20]
        io_requests_response = []
        for io_req in io_requests:
            ship_key = ShipKey.objects.filter(iorequest__overlap=[io_req.pk])
            if not ship_key.exists():
                continue
            io_requests_response.append({'id': io_req.pk,
                                         'search_number': io_req.full_number,
                                         'port__name': io_req.port.name,
                                         'ship_pk': ship_key.first().pk,
                                         })
        response = {'vessels': main_info.values('id', 'imo_number', 'name', 'is_ban'),
                    'IO_requests': io_requests_response}
        return Response(response)


class SearchByShipForIORequest(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(request_body=ship.serializers.SearchSerializer)
    def post(self, request, *args, **kwargs):
        query = request.data.get('query')
        if not query:
            return Response([])
        user = request.user
        main_info = MainInfo.objects.annotate(
            imo_number_char=Cast('imo_number', CharField())
        ).filter(Q(imo_number_char__contains=query) | Q(name__icontains=query))
        if user.type_user in [User.AGENT_CH, User.HEAD_AGENCY_CH]:
            min_date_nomination = datetime.now() - relativedelta(months=port_back.constants.VALID_NOMINATION_MONTHS)
            valid_ships = set(ShipAgentNomination.objects.filter(
                Q(date_verification__gte=min_date_nomination) &
                Q(status_document_id=port_back.constants.ISSUED) &
                (Q(agent__agent__agency=user.get_agency) | Q(agent__head_agency__agency=user.get_agency))
            ).values_list('ship_key', flat=True))
            main_info = main_info.filter(id__in=valid_ships)
        response = {'vessels': main_info[:20].values('id', 'imo_number', 'name', 'is_ban')}
        return Response(response)


class PortOfDepartureView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        ship_key = ShipKey.objects.get(pk=self.kwargs.get('ship_pk'))
        response = None
        if not ship_key.iorequest:
            response = None
        else:
            last_iorequest = IORequest.objects.filter(id__in=ship_key.iorequest).order_by('datetime_issued').last()
            if last_iorequest.type == IORequest.INPUT:
                response = {'port': last_iorequest.port.id}
        return Response(response)


class ShipAgentNominationView(viewsets.ModelViewSet):
    queryset = ShipAgentNomination.objects.all()
    permission_classes = (permissions.IsAuthenticated, ship.permissions.AgentNominationPermissions)
    serializer_class = ship.serializers.ShipAgentNominationSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ShipAgentNomination.objects.none()
        user = self.request.user
        if user.type_user in [User.HARBOR_MASTER_CH, User.HARBOR_WORKER_CH]:
            return self.queryset.filter(port__in=user.get_port)
        elif user.type_user in [User.HEAD_AGENCY_CH, User.AGENT_CH]:
            return self.queryset.filter(
                Q(agent__agent__agency=user.get_agency) | Q(agent__head_agency__agency=user.get_agency))
        return self.queryset.all()

    def perform_create(self, serializer):
        try:
            ship_key = ShipKey.objects.get(pk=self.kwargs.get('ship_pk'))
        except ShipKey.DoesNotExist:
            raise ValidationError('Ship does not exists')
        data = serializer.validated_data
        port = data.get('port')
        if ShipAgentNomination.objects.filter(
                ship_key=ship_key.maininfo, port=port, status_document_id=port_back.constants.PROCESSED
        ).exists():
            raise ValidationError('Statement exists')
        status_document = port_back.constants.ISSUED
        date_verification = datetime.today()
        verifier = self.request.user
        serializer.save(status_document_id=status_document,
                        ship_key=ship_key.maininfo,
                        date_verification=date_verification,
                        verifier=verifier)


class ListAgentNominationView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ShipAgentNomination.objects.all()
    permission_classes = (permissions.IsAuthenticated, ship.permissions.AgentNominationPermissions)
    serializer_class = ship.serializers.ShipAgentNominationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ship.filters.AgentNominationFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ShipAgentNomination.objects.none()
        user = self.request.user
        if user.type_user in [User.HARBOR_MASTER_CH, User.HARBOR_WORKER_CH]:
            return self.queryset.filter(port__in=user.get_port)
        elif user.type_user in [User.HEAD_AGENCY_CH, User.AGENT_CH]:
            return self.queryset.filter(
                Q(agent__agent__agency=user.get_agency) | Q(agent__head_agency__agency=user.get_agency))
        return self.queryset.all()


class ListShipInPortView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ShipInPort.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ship.serializers.ShipInPortSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ship.filters.ShipInPortFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ShipInPort.objects.none()
        user = self.request.user
        if user.type_user in [User.HARBOR_MASTER_CH, User.HARBOR_WORKER_CH]:
            return self.queryset.filter(port__in=user.get_port)
        elif user.type_user in [User.HEAD_AGENCY_CH, User.AGENT_CH]:
            return self.queryset.filter(agency=user.get_agency)
        return self.queryset.all()


class DraftDocumentView(viewsets.ModelViewSet):
    queryset = DraftDocument.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ship.serializers.DraftDocumentSerializer

    def get_parsers(self):
        if self.get_view_name() == 'Upload':
            self.parser_classes = (parsers.MultiPartParser, parsers.FormParser)
        return super().get_parsers()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        user = self.request.user
        if user.type_user == user.HARBOR_WORKER_CH:
            queryset = self.queryset.filter(author__harbor_worker__port__in=user.get_port)
        elif user.type_user == user.HARBOR_MASTER_CH:
            queryset = self.queryset.filter(author__harbor_master__port__in=user.get_port)
        elif user.type_user == user.AGENT_CH:
            queryset = self.queryset.filter(author__agent__agency=user.get_agency)
        elif user.type_user == user.HEAD_AGENCY_CH:
            queryset = self.queryset.filter(author__head_agency__agency=user.get_agency)
        else:
            queryset = self.queryset.filter(author=self.request.user)
        return queryset

    @action(methods=['post'], detail=True)
    def upload(self, request, *args, **kwargs):
        obj = self.get_object()
        files = request.FILES.getlist('photo')
        _ = [PhotoInDraftDocument.objects.create(photo=file, draft=obj).pk for file in files]
        return Response({'status': 'success'})
