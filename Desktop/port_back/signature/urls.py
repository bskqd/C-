from django.urls import path, re_path

import signature.views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('signature', signature.views.SignatureView)
# router.register('io_request_sign', signature.views.IORequestSignView)
router.register('center_certification_key', signature.views.CenterCertificateKeyView)

urlpatterns = [
    path('proxy/', signature.views.ProxyView.as_view()),
    re_path(r'^media_cifra/(?P<path>.*)', signature.views.CifraMediaView.as_view(), name='media-cifra')
]

urlpatterns += router.urls
