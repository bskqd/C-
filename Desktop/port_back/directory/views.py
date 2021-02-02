from django.db.models import Q
from rest_framework import viewsets, permissions, status, views
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

import directory.permissions
import directory.serializers
from directory.serializers import TowingCompanyDocsSerializer, TowDocsSerializer
from core.mixins import StandardResultsSetPagination
from core.models import User
from directory.models import (TypeVessel, Flag, StaffPosition, Port, StatusDocument, TypeDocument, Agency, Country, Sex,
                              TowingCompany, Tow, TowingCompanyDocs, TowDocs)


class TypeVesselView(viewsets.ReadOnlyModelViewSet):
    queryset = TypeVessel.objects.all()
    serializer_class = directory.serializers.TypeVesselSerializer


class FlagView(viewsets.ReadOnlyModelViewSet):
    queryset = Flag.objects.all()
    serializer_class = directory.serializers.FlagSerializer


class StaffPositionView(viewsets.ReadOnlyModelViewSet):
    queryset = StaffPosition.objects.all()
    serializer_class = directory.serializers.PositionSerializer


class PortView(viewsets.ModelViewSet):
    queryset = Port.objects.all()
    serializer_class = directory.serializers.PortSerializer

    def get_queryset(self):
        if self.request.user.type_user in [User.ADMIN_CH]:
            return self.queryset.all()
        return self.queryset.filter(is_disable=False)


class StatusDocumentView(viewsets.ModelViewSet):
    queryset = StatusDocument.objects.all()
    serializer_class = directory.serializers.StatusDocumentSerializer
    permission_classes = (directory.permissions.IsSuperUserOrReadOnly,)


class TypeDocumentView(viewsets.ModelViewSet):
    queryset = TypeDocument.objects.filter(is_disable=False)
    serializer_class = directory.serializers.TypeDocumentSerializer

    def get_queryset(self):
        event = self.request.query_params.get('event')
        filtering = {
            None: [TypeDocument.IN_OUT, TypeDocument.INPUT, TypeDocument.OUTPUT],
            'input': [TypeDocument.IN_OUT, TypeDocument.INPUT],
            'output': [TypeDocument.IN_OUT, TypeDocument.OUTPUT],
        }
        return self.queryset.filter(event__in=filtering[event])


class AgencyView(viewsets.ModelViewSet):
    queryset = Agency.objects.filter(is_disable=False)
    serializer_class = directory.serializers.AgencySerializer
    permission_classes = (permissions.IsAuthenticated, directory.permissions.AgencyPermission)
    pagination_class = StandardResultsSetPagination

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        User.objects.filter(Q(type_user__in=[User.AGENT_CH, User.HEAD_AGENCY_CH]) &
                            (Q(agent__agency=instance) | Q(head_agency__agency=instance))).update(is_active=False)
        instance.is_disable = True
        instance.save(update_fields=['is_disable'])
        return Response({'status': 'success', 'description': 'Agency was deleted'}, status=status.HTTP_200_OK)


class TowingCompanyView(viewsets.ModelViewSet):
    queryset = TowingCompany.objects.filter(is_disable=False)
    serializer_class = directory.serializers.TowingCompanySerializer
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = StandardResultsSetPagination


class TowView(viewsets.ModelViewSet):
    queryset = Tow.objects.filter(is_disable=False)
    serializer_class = directory.serializers.TowSerializer
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = StandardResultsSetPagination


class TowingCompanyDocsView(views.APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):

        file_serializer = TowingCompanyDocsSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TowDocsView(views.APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):

        file_serializer = TowDocsSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CountryView(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = directory.serializers.CountrySerializer
    permission_classes = (permissions.IsAuthenticated,)


class SexView(viewsets.ReadOnlyModelViewSet):
    queryset = Sex.objects.all()
    serializer_class = directory.serializers.SexSerializer
