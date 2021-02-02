from django.urls import path, include
from rest_framework import routers

import reports.views

router = routers.SimpleRouter()

router.register('list_statement_service_record', reports.views.ListStatementServiceRecordViewset,
                basename='list_statement_service_record')

urlpatterns = [
    path('list/protocol_dkk/', reports.views.ProtocolDkkList.as_view()),
    path('xlsx/protocol_dkk/', reports.views.ProtocolDkkListXlsx.as_view()),
    path('list/statement_dkk/', reports.views.StatementDkkList.as_view()),
    path('xlsx/statement_dkk/', reports.views.StatementDkkListXlsx.as_view()),
    path('list/certificate_ntz/', reports.views.NTZList.as_view()),
    path('xlsx/certificate_ntz/', reports.views.NTZListXlsx.as_view()),
    path('list/qual_doc/', reports.views.QualificationDocumentList.as_view()),
    path('xlsx/qual_doc/', reports.views.QualificationDocumentListXlsx.as_view()),
    path('list/educ_doc/', reports.views.EducationDocumentList.as_view()),
    path('xlsx/educ_doc/', reports.views.EducationDocumentListXlsx.as_view()),
    path('list/student_id/', reports.views.StudentIDReport.as_view()),
    path('report/<str:token>/', reports.views.LoadXlsx.as_view(), name='download-report'),
    path('list_files/', reports.views.ListOfFiles.as_view()),
    path('success_statement_dkk_with_user/', reports.views.AllSuccessStatementDKKViewset.as_view()),
    path('in_process_statement_dkk_with_user/', reports.views.AllInProcessStatementDKK.as_view()),
    path('count_succ_statement_dkk_with_user/', reports.views.CountAllSuccessStatementDKK.as_view()),
    path('count_in_process_statement_dkk_with_user/', reports.views.CountAllInProcessStatementDKK.as_view()),
    path('list_statement_qual_doc_in_packet/', reports.views.ListStatementQualDocInPacket.as_view()),
    path('list/statement_eti/', reports.views.StatementETIList.as_view()),
    path('list/payment/statement_eti/', reports.views.PaymentStatementETIList.as_view()),
    path('list/payment/branch_office/', reports.views.PaymentBranchOfficeList.as_view()),
    path('list/statement_advanced_training/', reports.views.StatementAdvancedTrainingList.as_view()),
    path('list/sailor_passport/', reports.views.SailorPassportList.as_view()),
    path('back_office/', include('reports.back_office_report.urls')),
]

urlpatterns = urlpatterns + router.urls
