from django.contrib import admin
from django.urls import path, include
from . import views
app_name = 'docs'

urlpatterns = [
    path('auth_service_record/', views.AuthServiceRecordBook.as_view(), name='auth_service_record_book'),
    path('generate_service_record/<str:token>/', views.GenerateServiceRecordBook.as_view(),
         name='generate_service_record'),
    path('auth_statement_for_record_book/',
         views.AuthStatementForServiceRecord.as_view(), name='auth_zayavu_for_service_record'),
    path('generate_statemenet_for_record_book/<str:token>/', views.GenerateStatementForServiceRecord.as_view(),
         name='generate_statement_for_service_record'),

    path('generate_statement_for_dkk/<str:token>/', views.GenerateDocForStatementDKK.as_view(),
         name='generate_statement_for_dkk'),
    path('auth_statement_for_dkk/', views.AuthDocForStatementDKK.as_view(), name='auth_statement_for_dkk'),
    path('auth_protocol_dkk/', views.AuthDocForProtocolDKK.as_view(), name='auth_protocol_dkk'),
    path('generate_protocol_ast/<int:protocol_id>/', views.GenerateProtocolForAST.as_view()),
    path('auth_statement_for_qualification/',
         views.AuthStatementQualification.as_view(), name='auth_statement_for_qualification'),
    path('generate_statement_for_qualification/<str:token>',
         views.GenerateDocForStatementQualification.as_view(), name='generate_statement_for_qualification'),
    path('auth_qualification_diplima/', views.AuthDiplomaDocuments.as_view(),
         name='auth_qualification_specialist_certificate'),
    path('generate_qualification_diplima/<str:token>/', views.GenerateDiplomaDocuments.as_view(),
         name='generate_qualification_specialist_certificate'),
    path('auth_qualification_proof_of_diplima/', views.AuthProofOfDiplomaDocuments.as_view(),
         name='auth_qualification_proof_of_diplima'),
    path('generate_qualification_proof_of_diplima/<str:token>/', views.GenerateProofOfDiplomaDocuments.as_view(),
         name='generate_qualification_proof_of_diplima'),
    path('auth_qualification_specialist_certificate/', views.AuthCertificateSpecialist.as_view(),
         name='auth_qualification_specialist_certificate'),
    path('generate_qualification_specialist_certificate/<str:token>/', views.GenerateCertificateSpecialist.as_view(),
         name='generate_qualification_specialist_certificate'),
    path('generate_protocol_with_conclusion/<str:token>/', views.GenerateProtocolWithConcusionDKK.as_view(),
         name='generate_protocol_dkk'),
    path('download_signed_protocol/<str:token>/', views.SignedProtocolDKK.as_view())

]
