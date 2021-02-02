import os

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

urlpatterns = [
    path('', include('itcs.private_urls')),
    url('', include('django_prometheus.urls')),
    path('Go9lYiNcza68F2lzPrXJERcmyR/', admin.site.urls),
    url(r'^admin/clearcache/', include('clearcache.urls')),
    path('api/v1/', include('itcs.public_urls', namespace='v1')),
    path('api/v2/', include('itcs.urls_v2', namespace='v2'))
]

if settings.SWAGGER_URL:
    schema_view_v1 = get_schema_view(
        openapi.Info(
            title="AC ITCS, Personal Cabinet API",
            default_version='v1',
            description="",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="i.golubev@disoft.us"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
        patterns=[
            url(r'^api/v1/', include(('itcs.public_urls', 'api'), namespace='v1')),
        ]
    )
    schema_view_v2 = get_schema_view(
        openapi.Info(
            title="AC ITCS, Personal Cabinet API",
            default_version='v2',
            description="",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="i.golubev@disoft.us"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
        patterns=[
            url(r'^api/v2/', include(('itcs.urls_v2', 'api'), namespace='v2')),
        ]
    )
    urlpatterns += [
        url(r'^api/v1/{}/$'.format(settings.SWAGGER_URL), schema_view_v1.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
        url(r'^api/v2/{}/$'.format(settings.SWAGGER_URL), schema_view_v2.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
        url(r'^api/v1/{}/$'.format(settings.SWAGGER_URL), schema_view_v1.with_ui('redoc', cache_timeout=0),
            name='schema-redoc')
    ]
