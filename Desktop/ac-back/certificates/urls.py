from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register('eti_registry', views.ETIRegistryViewset)
router.register('list_eti', views.ETIMonthRatioViewset)
router.register('institution', views.ETIInstitutionViewset)
router.register('month_ratio', views.MonthRatioByCourse)
router.register('course', views.PublicCourseViewset)
router.register('certificate_api', views.UpdateCertificateAPI)

urlpatterns = [
    path('institute_schedule/<int:course>/', views.ETIScheduleViewset.as_view({'get': 'list'})),
    path('create_eti_certificate/', views.CreateCertificateAPI.as_view()),
    path('create_multiple_eti_certificate/', views.MultipleCreateCertificateAPI.as_view()),
    path('create_certificate_from_statement/', views.CreateCertificateFromStatementAPI.as_view()),
    path('create_certificate_multiple_from_statement/', views.CreateCertificateFromStatemenMultipletAPI.as_view()),
]

urlpatterns += router.urls
