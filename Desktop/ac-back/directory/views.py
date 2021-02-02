import django_filters.rest_framework
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

import directory.permissions
from mixins.core import DeprecatedApi
from directory import serializers
from .filters import CityFilter
from .models import (AuthorizatedUsers, BranchOffice, City, Commisioner, Country, Course, Decision,
                     Direction, DoctrorInMedicalInstitution, EducationForm, ExtentDiplomaUniversity, Faculty,
                     FunctionAndLevelForPosition, LevelQualification, Limitations, MedicalInstitution, ModeOfNavigation,
                     NTZ, NZ, Port, Position, PositionForExperience, PositionForMedical, Rank, Region, Responsibility,
                     ResponsibilityWorkBook, Sex, Speciality, Specialization, StatusDocument, TypeContact, TypeDocument,
                     TypeDocumentNZ, TypeGeu, TypeOfAccrualRules, TypeRank, TypeVessel, VerificationStage)
from .serializers import TypeOfAccrualRulesSerializer


class NTZViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = NTZ.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.NTZSerializer

    @method_decorator(cache_page(60 * 60 * 4, key_prefix='eti_viewset'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def clear_cache():
        keys = cache.keys('*eti_viewset*')
        cache.delete_many(keys)

    def perform_create(self, serializer):
        self.clear_cache()
        return super(NTZViewset, self).perform_create(serializer)

    def perform_destroy(self, instance):
        self.clear_cache()
        return super(NTZViewset, self).perform_destroy(instance)

    def perform_update(self, serializer):
        self.clear_cache()
        return super(NTZViewset, self).perform_update(serializer)


class CountryViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Country.objects.all().order_by('value')
    serializer_class = serializers.CountrySerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['id', 'value', 'value_eng']

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class RegionViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Region.objects.all().order_by('value')
    serializer_class = serializers.RegionSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['country', 'value', 'value_eng']

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CityViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = City.objects.all().order_by('city_type')
    serializer_class = serializers.CitySerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = CityFilter

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class RankViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Rank.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.RankSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, request, *args, **kwargs):
        return super(RankViewset, self).dispatch(request, *args, **kwargs)


class ResponsibilityViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Responsibility.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.FunctionSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PositionViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Position.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.PositionSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class StatusDocumentViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = StatusDocument.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.StatusDocumentSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PortVieset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Port.objects.all().order_by('name_ukr')
    serializer_class = serializers.PortSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class BranchOfficeViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = BranchOffice.objects.all().order_by('name_ukr')
    serializer_class = serializers.BranchOfficeSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class MedicalInstitutionViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = MedicalInstitution.objects.all().order_by('value')
    serializer_class = serializers.MedicalInstitutionSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DoctorInMedicalViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = DoctrorInMedicalInstitution.objects.all()
    serializer_class = serializers.DoctrorInMedicalInstitutionSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PositionForMedicalViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = PositionForMedical.objects.all().order_by('name_ukr')
    serializer_class = serializers.PositionForMedicalSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PositionForExperienceViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = PositionForExperience.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.PositionForExperienceSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TypeDocumentNZViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = TypeDocumentNZ.objects.all().order_by('name_ukr')
    serializer_class = serializers.TypeDocumentNZSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ExtentViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = ExtentDiplomaUniversity.objects.all()
    serializer_class = serializers.ExtentSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SpecialityViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Speciality.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.SpecialitySerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SpecializationViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Specialization.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.SpecializationSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class LevelQualitifcationViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = LevelQualification.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.LevelQualitifcationSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class NameNZViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = NZ.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.NZSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class LimitationsViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Limitations.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.LimitationsSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AuthorizatedUsersViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = AuthorizatedUsers.objects.all()
    serializer_class = serializers.AuthUsersSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        queryset = self.queryset.all()
        query_set = queryset.filter(city_id=self.request.user.userprofile.branch_office_id).order_by('FIO_ukr')
        return query_set

    @method_decorator(cache_page(60 * 60 * 4))
    @method_decorator(vary_on_headers('Authorization'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TypeDocumentViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = TypeDocument.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.TypeDocumentQualSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CommisionerForCommitteViewset(DeprecatedApi, viewsets.ModelViewSet):  # outdated
    """
     retrieve:
       Получить из справочника данные записи о метрике по *uuid*
    Outdated
    """
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Commisioner.objects.filter(is_disable=False).order_by('name')
    serializer_class = serializers.CommisionerForCommitteSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CourseForNTZViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Course.objects.all().order_by('name_ukr')
    serializer_class = serializers.CourseForNTZSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DecisionViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Decision.objects.all().order_by('name_ukr')
    serializer_class = serializers.DecisionSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class FunctionAndLevelForPositionViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = FunctionAndLevelForPosition.objects.all()
    serializer_class = serializers.FunctionAndLevelForPositionSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TypeRankViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = TypeRank.objects.all()
    serializer_class = serializers.TypeRankSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DirectionViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Direction.objects.all()
    serializer_class = serializers.DirectionSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class EducationFormViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = EducationForm.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.EducationFormSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class FacultyViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Faculty.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.FacultySerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class SexViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = Sex.objects.all()
    serializer_class = serializers.SexSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TypeContactViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = TypeContact.objects.all()
    serializer_class = serializers.TypeContactSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TypeVesselViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = TypeVessel.objects.all()
    serializer_class = serializers.TypeVesselSailorSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ModeOfNavigationViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = ModeOfNavigation.objects.all()
    serializer_class = serializers.ModeOfNavigationSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class TypeGeuViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = TypeGeu.objects.all()
    serializer_class = serializers.TypeGeuSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ResponsibilityWorkBookViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    serializer_class = serializers.ResponsibilityWorkBookSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ResponsibilityWorkBook.objects.none()
        if hasattr(self.request.user, 'userprofile') and \
                self.request.user.userprofile.main_group.filter(id=37).exists():
            return ResponsibilityWorkBook.objects.filter(is_disable=False).filter(is_not_conventional=True)
        return ResponsibilityWorkBook.objects.filter(is_disable=False)


class AllCommissionersViews(APIView):
    """
    retrieve:
        For statement DKK report filtration
    Все члены коммиссий ДКК
    """
    permission_classes = (directory.permissions.IsSuperUserEdit,)

    @swagger_auto_schema(operation_summary='For statement DKK report filtration')
    def get(self, request, *args, **kwargs):
        """
        For statement DKK report filtration
        """
        new_commissioners = Commisioner.objects.all().values_list('name', flat=True)
        return Response({'commissioners': new_commissioners})


class TypeOfAccrualRulesView(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    serializer_class = TypeOfAccrualRulesSerializer
    queryset = TypeOfAccrualRules.objects.all()


class VerificationStageViewset(viewsets.ModelViewSet):
    permission_classes = (directory.permissions.IsSuperUserEdit,)
    queryset = VerificationStage.objects.filter(is_disable=False).order_by('name_ukr')
    serializer_class = serializers.VerificationStageSerializer

    @method_decorator(cache_page(60 * 60 * 4))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
