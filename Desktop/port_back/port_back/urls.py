"""port_back URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from core.views import MediaAccess


urlpatterns = [
    path('Go9lYiNcza68F2lzPrXJERcmyR/', admin.site.urls),
    path('api/v1/authorization/', include('authorization.urls')),
    path('api/v1/', include('ship.urls')),
    path('api/v1/directory/', include('directory.urls')),
    path('api/v1/core/', include('core.urls')),
    path('api/v1/reports/', include('reports.urls')),
    path('api/v1/signature/', include('signature.urls')),
    path('api/v1/document_generation/', include('document_generation.urls')),
    path('api/v1/back_office/', include('back_office.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/verification/', include('verification.urls')),
    path('', include('django_prometheus.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        url(r'^media/(?P<path>.*)', MediaAccess.as_view(), name='media')
    ]

if settings.SWAGGER_URL:
    schema_view = get_schema_view(
        openapi.Info(
            title="Snippets API",
            default_version='v1',
            description="Test description",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@snippets.local"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    ]
