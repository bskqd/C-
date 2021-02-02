from django.urls import path
import reports.back_office_report.views

urlpatterns = [
    path('main_report/group/', reports.back_office_report.views.GlobalPacketByGroupReportView.as_view()),
    # path('main_report/agent/', reports.back_office_report.views.GlobalPacketByAgentReportView.as_view()),
    # TODO TO delete
    path('main_report/seaman/', reports.back_office_report.views.GlobalPacketByAgentReportView.as_view()),
    path('main_report/sailor/', reports.back_office_report.views.GlobalPacketBySailorReportView.as_view()),
    path('main_report/packet/', reports.back_office_report.views.GlobalPacketByPacketReportView.as_view()),
    path('main_report/document/', reports.back_office_report.views.GlobalPacketByDocumentReportView.as_view())
]

distribution_reports = [
    path('distribution/dpd/',
         reports.back_office_report.views.DistributionDPDReportView.as_view()),
    path('distribution/dpd/document/',
         reports.back_office_report.views.DistributionDPDDocumentReportView.as_view()),
    path('distribution/dpd/sailor_passport/',
         reports.back_office_report.views.DistributionDPDSailorPassportReportView.as_view()),
    path('distribution/dpd/sailor_passport/xlsx/',
         reports.back_office_report.views.DPDSailorPassportXlsxReportView.as_view()),
    path('distribution/dpd/qual_doc/',
         reports.back_office_report.views.DistributionDPDQualDocReportView.as_view()),
    path('distribution/dpd/qual_doc/xlsx/',
         reports.back_office_report.views.DPDQualDocXlsxReportView.as_view()),
    path('distribution/adv_training/',
         reports.back_office_report.views.DistributionAdvTrainingReportView.as_view()),
    path('distribution/adv_training/sailor/',
         reports.back_office_report.views.DistributionAdvTrainingSailorReportView.as_view()),
    path('distribution/adv_training/sailor/xlsx/',
         reports.back_office_report.views.AdvTrainingXlsxReportView.as_view()),
    path('distribution/medical/',
         reports.back_office_report.views.DistributionMedicalInstitutionReportView.as_view()),
    path('distribution/medical/doctor/',
         reports.back_office_report.views.DistributionDoctorReportView.as_view()),
    path('distribution/medical/sailor/',
         reports.back_office_report.views.DistributionMedicalSailorReportView.as_view()),
    path('distribution/medical/sailor/xlsx/', reports.back_office_report.views.MedicalXlsxReportView.as_view()),
    path('distribution/sqc/', reports.back_office_report.views.DistributionSQCReportView.as_view()),
    # path('distribution/sqc/agent/', reports.back_office_report.views.DistributionSQCAgentReportView.as_view()),
    # TODO TO delete
    path('distribution/sqc/seaman/', reports.back_office_report.views.DistributionSQCAgentReportView.as_view()),
    path('distribution/sqc/sailor/', reports.back_office_report.views.DistributionSQCSailorReportView.as_view()),
    path('distribution/sqc/sailor/xlsx/', reports.back_office_report.views.SQCXlsxReportView.as_view()),
    path('distribution/sc/', reports.back_office_report.views.DistributionServiceCenterReportView.as_view()),
    # path('distribution/sc/agent/', reports.back_office_report.views.DistributionServiceCenterAgentReportView.as_view()),
    # TODO TO delete
    path('distribution/sc/seaman/',
         reports.back_office_report.views.DistributionServiceCenterAgentReportView.as_view()),
    path('distribution/sc/sailor/',
         reports.back_office_report.views.DistributionServiceCenterSailorReportView.as_view()),
    path('distribution/sc/sailor/xlsx/', reports.back_office_report.views.ServiceCenterXlsxReportView.as_view()),
    path('distribution/portal/', reports.back_office_report.views.DistributionPortalReportView.as_view()),
    # path('distribution/portal/agent/', reports.back_office_report.views.DistributionPortalAgentReportView.as_view()),
    # TODO TO delete
    path('distribution/portal/seaman/', reports.back_office_report.views.DistributionPortalAgentReportView.as_view()),
    path('distribution/portal/sailor/', reports.back_office_report.views.DistributionPortalSailorReportView.as_view()),
    path('distribution/portal/sailor/xlsx/', reports.back_office_report.views.PortalXlsxReportView.as_view()),
    # path('distribution/agent/', reports.back_office_report.views.DistributionAgentGroupReportView.as_view()),
    # TODO TO delete
    path('distribution/seaman/', reports.back_office_report.views.DistributionAgentGroupReportView.as_view()),
    # path('distribution/agent/agent/', reports.back_office_report.views.DistributionAgentsReportView.as_view()),
    # TODO TO delete
    path('distribution/seaman/seaman/', reports.back_office_report.views.DistributionAgentsReportView.as_view()),
    # path('distribution/agent/sailor/', reports.back_office_report.views.DistributionAgentSailorReportView.as_view()),
    # TODO TO delete
    path('distribution/seaman/sailor/', reports.back_office_report.views.DistributionAgentSailorReportView.as_view()),
    # path('distribution/agent/sailor/xlsx/', reports.back_office_report.views.AgentXlsxReportView.as_view()),
    # TODO TO delete
    path('distribution/seaman/sailor/xlsx/', reports.back_office_report.views.AgentXlsxReportView.as_view()),
    path('distribution/eti/', reports.back_office_report.views.DistributionETIReportView.as_view()),
    path('distribution/eti/courses/', reports.back_office_report.views.DistributionETICoursesReportView.as_view()),
    path('distribution/eti/sailor/', reports.back_office_report.views.DistributionETISailorReportView.as_view()),
    path('distribution/eti/sailor/xlsx/', reports.back_office_report.views.ETIXlsxReportView.as_view()),
]

urlpatterns += distribution_reports
