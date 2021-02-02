from django.urls import path
from rest_framework import routers
from rest_framework.routers import Route, DynamicRoute

import sailor.document.views
import sailor.statement.views
from certificates import views as certificates_views
from . import views


class CustomRouter(routers.SimpleRouter):
    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'post': 'create'
            },
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset.
        DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/sailor/{lookup}{trailing_slash}$',
            mapping={
                'get': 'list',
            },
            name='{basename}-sailor-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset.
        DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes. Generated using
        # @action(detail=True) decorator on methods of the viewset.
        DynamicRoute(
            url=r'^{prefix}/{lookup}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
    ]


default_router = routers.SimpleRouter()


urlpatterns = [
    path('search_sailor/', views.SearchSailor.as_view()),
    path('search_sailor/query=<str:query>/is_sorting=<str:is_sorting>/', views.SearchSailor.as_view()),
    path('photo_sailor/', views.SailorPhotoView.as_view()),
    path('create_ntz_sert/', certificates_views.CreateCertificateAPI.as_view()),  # TODO TO DELETE
    path('multiple_create_ntz_cert/', certificates_views.MultipleCreateCertificateAPI.as_view()),  # TO DELETE
    path('count_all_docs/<int:sailor_pk>/', views.CountDocSailor.as_view()),
    path('photo_uploader/', views.PhotoUploader.as_view()),
    path('photo_uploader/<str:pk>/', views.PhotoUploader.as_view()),
    path('available_position/sailor/<int:pk>/', views.AvailablePositionForSailor.as_view({'get': 'retrieve'}),
         name='available-position-sailor'),
    path('history/<int:sailor>/', views.FullUserSailorHistoryView.as_view({'get': 'list'})),
]



