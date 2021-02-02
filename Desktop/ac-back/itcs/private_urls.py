from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path, include

from itcs import settings
from sms_auth.views import MediaAccess

urlpatterns = [
    path('payments/', include('payments.urls')),
    path('accounts/', include('yubikey_api_auth.urls')),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        url(r'^media/(?P<path>.*)', MediaAccess.as_view(), name='media')
    ]
