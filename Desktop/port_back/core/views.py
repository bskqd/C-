import os
import urllib

import rest_framework.parsers
import rest_framework.permissions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Value, Q
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseForbidden
from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

import core.filters
import core.permissions
import core.serializers
from authorization.mail.tasks import send_registration_mail
from core.mixins import StandardResultsSetPagination
from core.models import Photo, User
from directory.models import Agency, TowingCompany
from signature.models import Signature


class PhotoUploader(GenericAPIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)
    parser_classes = (rest_framework.parsers.MultiPartParser, rest_framework.parsers.FormParser)
    serializer_class = core.serializers.PhotoUploaderSerializer
    put_serializer_class = core.serializers.PhotoPutSerializer
    delete_serializer_class = core.serializers.PhotoDeleteSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return self.serializer_class
        elif self.request.method == 'PUT':
            return self.put_serializer_class
        elif self.request.method == 'DELETE':
            return self.delete_serializer_class

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=self.request.data)
        ser.is_valid(raise_exception=True)
        photo_file = request.FILES.get('photo')
        data = ser.validated_data
        type_photo = data.get('type_photo')
        try:
            ct = ContentType.objects.get(model=data.get('content_type'))
        except ContentType.DoesNotExist:
            raise NotFound('Content type not found')
        model = ct.model_class()
        try:
            document = model.objects.get(id=data.get('document_id'))
        except ObjectDoesNotExist:
            raise NotFound('Document not found')
        if not hasattr(model, 'photo'):
            raise ValidationError(f'{ct.name} does not have a photo field')
        photo_instance = Photo.objects.create(file=photo_file, type_photo=type_photo)
        document.refresh_from_db()
        while photo_instance.pk not in document.photo:
            old_photos = document.photo
            old_photos.append(photo_instance.pk)
            document.photo = old_photos
            document.save(force_update=True)
            document.refresh_from_db()
        return Response({'status': 'success', 'id': photo_instance.pk,
                         'file': request.build_absolute_uri(photo_instance.file.url),
                         'type_photo': photo_instance.type_photo,
                         'content_type': ct.model})

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('content_type', in_=openapi.IN_QUERY, description='content_type', type=openapi.TYPE_STRING),
        openapi.Parameter('document_id', in_=openapi.IN_QUERY, description='document_id', type=openapi.TYPE_INTEGER),
        openapi.Parameter('photo_id', in_=openapi.IN_QUERY, description='photo_id', type=openapi.TYPE_INTEGER),
    ])
    def delete(self, request):
        data = request.query_params
        content_type = data.get('content_type')
        document_id = int(data.get('document_id'))
        photo_id = int(data.get('photo_id'))
        photo = get_object_or_404(Photo, id=photo_id)
        try:
            ct = ContentType.objects.get(model=content_type)
        except ContentType.DoesNotExist:
            raise NotFound('Content type not found')
        model = ct.model_class()
        try:
            document = model.objects.get(id=document_id)
        except ObjectDoesNotExist:
            raise NotFound('Document not found')
        document_photos = document.photo
        document_photos.remove(photo.pk)
        document.photo = document_photos
        document.save(update_fields=['_photo'])
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        ser = self.get_serializer(data=self.request.data)
        ser.is_valid(raise_exception=True)
        photo_file = request.FILES.get('photo')
        data = ser.validated_data
        photo = data.get('photo_id')
        old_photo_path = photo.file.path
        photo.file = photo_file
        photo.save(update_fields=['file'])
        os.remove(old_photo_path)
        return Response({'status': 'success', 'id': photo.pk,
                         'file': request.build_absolute_uri(photo.file.url),
                         'type_photo': photo.type_photo})


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (rest_framework.permissions.IsAuthenticated, core.permissions.UserPortPermission)
    queryset = User.objects.annotate(
        full_name=Concat('last_name', Value(' '), 'first_name', Value(' '), 'middle_name')
    )
    serializer_class = core.serializers.UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = core.filters.UserFilters
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        user = self.request.user
        if user.type_user in [User.ADMIN_CH, User.MARAD_CH]:
            return self.queryset.all()
        elif user.type_user in [User.HEAD_AGENCY_CH, User.AGENT_CH]:
            return self.queryset.filter(Q(type_user__in=[User.AGENT_CH, User.HEAD_AGENCY_CH]) &
                                        Q(Q(agent__agency=user.get_agency) |
                                          Q(head_agency__agency=user.get_agency)))
        elif user.type_user in [User.HARBOR_MASTER_CH]:
            return self.queryset.filter(type_user__in=[User.HARBOR_WORKER_CH], harbor_worker__port__in=user.get_port)
        return self.queryset.none()

    def get_object(self):
        if self.request.user.pk == int(self.kwargs['pk']):
            return self.request.user
        return super().get_object()

    def create(self, request, *args, **kwargs):
        data = request.data
        if request.data['type_user'] == 'head_agency':
            agency_id = data['head_agency']['agency']
            try:
                return super().create(request, *args, **kwargs)
            except Exception:
                Agency.objects.filter(id=agency_id).delete()
                return Response({'response': 'Email exists'}, status=400)
        elif request.data['type_user'] == 'head_towing':
            towing_company_id = data['head_towing']['towing_company']
            try:
                return super().create(request, *args, **kwargs)
            except Exception:
                TowingCompany.objects.filter(id=towing_company_id).delete()
                return Response({'response': 'Email exists'}, status=400)
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if user.type_user == User.HEAD_AGENCY_CH:
            request.data['head_agency'].pop('agency')
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(rest_framework.permissions.IsAuthenticated,
                                (core.permissions.IsHeadAgency | rest_framework.permissions.IsAdminUser)))
    def agent_admin_permission(self, request, pk):
        author = request.user
        permission = Permission.objects.get(codename='agent_admin_agency')
        user = self.get_object()
        if user.type_user != User.AGENT_CH:
            raise ValidationError('User is not an agent')
        if author.type_user == User.HEAD_AGENCY_CH and user.agent.agency != author.head_agency.agency:
            raise ValidationError('You cannot give permission to this agent')
        if request.method == 'DELETE':
            description = 'deleted'
            user.user_permissions.remove(permission)
        elif request.method == 'POST':
            description = 'added'
            user.user_permissions.add(permission)
        else:
            description = None
        return Response({'status': 'success', 'description': f'Permission {description} to agent'})

    @action(methods=['patch', 'put'], detail=True, serializer_class=core.serializers.ChangePasswordSerializer,
            permission_classes=(rest_framework.permissions.IsAuthenticated,))
    def change_password(self, request, pk):
        author = request.user
        user = self.get_object()
        if author != user:
            raise PermissionDenied
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.data['new_password']
        old_password = serializer.data['old_password']
        if not user.check_password(old_password):
            raise ValidationError('Old password is wrong')
        user.set_password(new_password)
        user.save()
        user.is_changed_password = True
        user.save(update_fields=['is_changed_password'])
        return Response({'status': 'success', 'description': 'Password has been changed'})


class UserFullInfoView(generics.RetrieveAPIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)
    serializer_class = core.serializers.FullInfoUserSerializer

    def get_object(self):
        return self.request.user


class UserPermissionsView(APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        all_permissions = self.request.user.get_all_permissions()
        permissions = [perm.split('.')[1] for perm in all_permissions if
                       not perm.startswith(('admin', 'sessions', 'authtoken', 'contenttypes'), )]
        if request.user.type_user in [request.user.AGENT_CH]:
            head_agency = self.request.user.userprofile.agency.agency_user.user
            can_create_request = self.request.user.signatures.filter(is_actual=True, type_signature=Signature.SIGN)\
                                                             .exists() and head_agency.signatures.filter(is_actual=True,
                                                                                type_signature=Signature.STAMP).exists()
        elif request.user.type_user in [request.user.HEAD_AGENCY_CH]:
            head_agency = self.request.user.userprofile.agency.agency_user.user
            can_create_request = head_agency.signatures.filter(is_actual=True).count() == 2
        else:
            can_create_request = None
        return Response({'permissions': permissions, 'can_create_request': can_create_request})


class MediaAccess(APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request, path):
        """
        When trying to access :
        myproject.com/media/uploads/passport.png

        If access is authorized, the request will be redirected to
        myproject.com/protected/media/uploads/passport.png

        This special URL will be handle by nginx we the help of X-Accel
        """
        user = request.user
        if user.is_authenticated:
            response = HttpResponse()
            # Content-type will be detected by nginx
            del response['Content-Type']
            response['X-Accel-Redirect'] = '/protected/' + urllib.parse.quote(path)
            return response
        else:
            return HttpResponseForbidden('Not authorized to access this media.')
