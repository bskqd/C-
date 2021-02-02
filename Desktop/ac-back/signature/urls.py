from django.conf.urls import url
from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
# router.register('commissioner', views.ListCommissionerForProtocolViewset)
# router.register('document_to_sign', views.DocumentToSignForUserViewset)
urlpatterns = [
    path('proxy/', views.Proxy.as_view()),
    # path('upload_signature/', views.UploadSignatureForDKK.as_view()),
]

urlpatterns = urlpatterns + router.urls
