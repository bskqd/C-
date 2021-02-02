from django.urls import path
from rest_framework_nested import routers

import sailor.document.views
import sailor.statement.views
from . import views

router = routers.SimpleRouter()
router.register(r'', views.SailorMainInfoView, basename='profile')

sailor_router = routers.NestedSimpleRouter(router, r'', lookup='sailor')
sailor_router.register('certificate', sailor.document.views.CertificateETIView, basename='certificate')
sailor_router.register('statement/certificate', sailor.statement.views.StatementETIView)
sailor_router.register('service_record', sailor.document.views.ServiceRecordSailorView, basename='service-record')
sailor_router.register('statement/service_record', sailor.statement.views.StatementServiceRecordSailorView,
                       basename='statement-service-record')
sailor_router.register('education', sailor.document.views.EducationView, basename='education')
sailor_router.register('qualification', sailor.document.views.QualificationDocumentView, basename='qualification')
sailor_router.register('statement/qualification', sailor.statement.views.StatementQualificationView)
sailor_router.register('medical', sailor.document.views.MedicalCertificateView, basename='medical')
sailor_router.register('sailor_passport', views.SailorPassportView, basename='sailor-passport')
sailor_router.register('statement/sailor_passport', sailor.statement.views.StatementSailorPassportView,
                       basename='statement-sailor-passport')
sailor_router.register('protocol_sqc', sailor.document.views.ProtocolSQCView, basename='protocol-sqc')
sailor_router.register('statement/protocol_sqc', sailor.statement.views.StatementSQCView, basename='statement-sqc')
sailor_router.register('demand', views.DemandPositionDKKView, basename='demand')
sailor_router.register('citizen_passport', views.CitizenPassportView, basename='citizen-passport')
sailor_router.register('proof_diploma', sailor.document.views.ProofOfWorkDiplomaView)
sailor_router.register('history', views.FullUserSailorHistoryView)
sailor_router.register('old_name', views.OldNameView)
sailor_router.register('experience_certificate', sailor.document.views.ExperienceDocumentView)
sailor_router.register('statement/medical_certificate', sailor.statement.views.StatementMedicalCertificateView,
                       basename='statement-medical-certificate')
sailor_router.register('statement/advanced_training', sailor.statement.views.StatementAdvancedTrainingView,
                       basename='statement-advanced-training')
sailor_router.register('comment_for_verification', sailor.views.CommentForVerificationDocViewset,
                       basename='comment-for-verification')

service_record_router = routers.NestedSimpleRouter(sailor_router, r'service_record', lookup='service_record')
service_record_router.register('line', sailor.document.views.LineInServiceRecordView)

urlpatterns = [
    path('search/', views.SearchSailor.as_view()),
    path('<int:sailor_pk>/count_docs/', views.CountDocSailor.as_view()),
    path('<int:sailor_pk>/available_position/', views.AvailablePositionForSailor.as_view({'get': 'retrieve'}),
         name='available-position-detail'),
    # path('<int:sailor_pk>/add_agent/', views.SailorAgentView.as_view()),
    path('<int:sailor_pk>/seaman/', views.SailorAgentView.as_view()),
    # path('<int:sailor_pk>/agent_info/', views.AgentInfoView.as_view()),
    path('<int:sailor_pk>/seaman_info/', views.AgentInfoView.as_view()),
    path('<int:sailor_pk>/rating/', views.RatingView.as_view({'get': 'retrieve', 'post': 'create'})),
    path('<int:sailor_pk>/check_is_continue/', views.CheckContinueView.as_view()),
    path('<int:sailor_pk>/merge_sailor/', views.MergeSailorView.as_view()),
]
urlpatterns += router.urls
urlpatterns += sailor_router.urls
urlpatterns += service_record_router.urls
