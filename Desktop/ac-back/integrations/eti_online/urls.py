from django.urls import path
from rest_framework import routers

from integrations.eti_online import views

router = routers.SimpleRouter()
router.register('certificate_eti', views.CertificateETIView)

urlpatterns = [
    path('statement_eti/<int:institution_id>/', views.StatementETIView.as_view({'get': 'list'})),
    path('statement_eti/<int:institution_id>/<int:pk>/', views.StatementETIView.as_view(
        {'patch': 'partial_update',
         'get': 'retrieve'}))
]
urlpatterns += router.urls
