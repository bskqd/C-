from django.urls import path
from rest_framework import routers

import personal_cabinet.e_sailor.views
import personal_cabinet.views
from . import views

router = routers.SimpleRouter()

router.register('statement_sqc', views.PersonalStatementDKKView, basename='personal-statement-dkk')
router.register(
    'statement_qualification',
    views.ETStatementQualificationView,
    basename='StatementQualification'
)
router.register('statement_service_record', views.ETStatementServiceRecordView, basename='StatementServiceRecord')
router.register('sailor_history', personal_cabinet.e_sailor.views.HistoryUserInPersonalCabinetView)
router.register('statement_sailor_passport', views.ETSStatementSailorPassport,
                basename='pc-statement-sailor-passport')
router.register('education', views.PersonalEducationView, basename='pc-education')
router.register('qual_doc', views.PersonalQualificationDocumentView, basename='pc-qual-doc')
router.register('proof_of_work_diploma', views.PersonalProofOfWorkDiplomaView, basename='pc-proof-of-work-diploma')
router.register('medical', views.PersonalMedicalCertificatesView, basename='pc-medical')
router.register('ntz', views.PersonalNTZCertificatesView, basename='pc-ntz')
router.register('sailor_passport', views.PersonalSailorPassportView, basename='pc-sailor-passport')
router.register('citizen_passport', views.PersonalCitizenPassportView, basename='pc-citizen-passport')
router.register('service_records', views.PersonalServiceRecordsView, basename='pc-service-records')
router.register('line_in_service_record', personal_cabinet.views.LineInServiceRecordsView,
                basename='pc-line-service-record')
router.register('experience_doc', views.PersonalExperienceDocView, basename='pc-experience-certificate')
router.register('protocol_sqc', views.PersonalProtocolDKKView, basename='pc-protocol-sqc')
router.register('students_id', views.ETSStudentIDPerSailor, basename='pc-students-id')

urlpatterns = [
    path('', views.PersonalSailorInfoView.as_view()),
    path('sailor_statement_sqc_per_user/', views.PersonalStatementDKKView.as_view({'get': 'sailor_statements_sqc'}),
         name='personal-statement-dkk-sailor'),
    path('success_statement_sqc_per_sailor/',
         views.PersonalStatementDKKView.as_view({'get': 'success_sailor_statements_sqc'})),
    path('statement_qualification_doc_per_sailor/',
         views.ETStatementQualificationView.as_view({'get': 'sailor_statements_qual_doc'})),
    path(
        'success_statement_qualification_doc_per_sailor/',
        views.ETStatementQualificationView.as_view({'get': 'success_statements_qual_doc'})),
    path('protocol_sqc_for_statement_qual/', views.PersonalProtocolDKKView.as_view({'get': 'for_statement_qual'})),
    path('generate_qr/', personal_cabinet.views.GenerateQr.as_view()),
    path('download_image/<str:name>/', personal_cabinet.views.GenerateMarkedImage.as_view()),
    path('count_docs/', views.ETCountDocsSailorView.as_view()),
    path('check_documents_statement_dkk/', personal_cabinet.views.CheckDocumentsStatementDKKView.as_view()),
    path('no_payed_statement/', personal_cabinet.views.NoPayedStatement.as_view()),
    path('diplomas_for_apply/', views.PersonalQualificationDocumentView.as_view({'get': 'get_diplomas_for_apply'})),
    path('personal_data_processing/', views.PersonalDataProcessingView.as_view({'post': 'create'})),
    # TODO remove when update front
    path('personal_seaman/', views.PersonalAgentView.as_view({'get': 'retrieve',
                                                              'delete': 'delete_agent',
                                                              'post': 'accept_agent'})),
    path('seaman/', views.PersonalAgentView.as_view({'get': 'retrieve',
                                                     'delete': 'delete_agent',
                                                     'post': 'accept_agent'})),
    # TODO remove when update front
    path('personal_seaman/accept/', views.PersonalAgentView.as_view({'post': 'accept_agent'})),
    path('seaman/accept/', views.PersonalAgentView.as_view({'post': 'accept_agent'})),
    path('price_service_record/', personal_cabinet.e_sailor.views.PriceServiceRecord.as_view()),
    path('current_app_version/', personal_cabinet.e_sailor.views.CurrentAppVersionView.as_view()),
    path('change_main_phone/', personal_cabinet.views.ChangeMainPhoneView.as_view()),
    path('power_of_attorney/', personal_cabinet.views.PowerOfAttorney.as_view()),
    path('authorization_html/', views.OldAuthorizationPage.as_view()),
    path('authorization_html_new/', views.AuthorizationPage.as_view()),
]

urlpatterns = urlpatterns + router.urls
