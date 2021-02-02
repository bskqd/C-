from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register('medical', views.MRSPersonalMedicalCertificatesView, basename='mrs-medical')
router.register('education', views.MRSPersonalEducationView, basename='mrs-education')
router.register('eti', views.MRSPersonalETICertificatesView, basename='mrs-eti')
router.register('sailor_passport', views.MRSPersonalSailorPassportView, basename='mrs-sailor-passport')
router.register('citizen_passport', views.MRSPersonalCitizenPassportView, basename='mrs-citizen-passport')
router.register('qual_doc', views.MRSPersonalQualificationDocumentView, basename='mrs-qual-doc')
router.register('proof_of_work_diploma', views.MRSPersonalProofOfWorkDiplomaView, basename='mrs-proof-of-work-diploma')
router.register('service_records', views.MRSPersonalServiceRecordsView, basename='mrs-service-records')
router.register('protocol_sqc', views.MRSPersonalProtocolDKKView, basename='mrs-protocol-sqc')
router.register('experience_doc', views.MRSPersonalExperienceDocView, basename='mrs-experience-certificate')
router.register('statement_sqc', views.MRSPersonalStatementDKKView, basename='mrs-personal-statement-dkk')
router.register('statement_service_record', views.MRSStatementServiceRecordView, basename='MRSStatementServiceRecord')
router.register(
    'statement_qualification', views.MRSStatementQualificationView)
router.register('statement_sailor_passport', views.MRSStatementSailorPassport,
                basename='mrs-statement-sailor-passport')

urlpatterns = [
    path('main_info/', views.MRSPersonalSailorInfoView.as_view()),
    path('protocol_sqc_for_statement_qual/', views.MRSPersonalProtocolDKKView.as_view({'get': 'for_statement_qual'})),
    path('personal_data_processing/', views.MRSPersonalDataProcessingView.as_view({'post': 'create'})),
    path('sailor_statement_sqc_per_user/', views.MRSPersonalStatementDKKView.as_view({'get': 'sailor_statements_sqc'}),
         name='personal-statement-dkk-sailor'),
    path('success_statement_sqc_per_sailor/',
         views.MRSPersonalStatementDKKView.as_view({'get': 'success_sailor_statements_sqc'})),
    path('count_docs/', views.MRSCountDocsSailorView.as_view()),

]

urlpatterns += router.urls
