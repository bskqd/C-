from django.urls import path
from rest_framework.routers import SimpleRouter

from agent import views

router = SimpleRouter()

router.register('sailors', views.ListOfMySailorViewset)
router.register('list_of_seaman', views.ListOfAgent)
router.register('statement_seaman', views.StatementAgentView)
router.register('statement_seaman_sailor', views.StatementAgentSailorViewset, basename='StatementSeamanSailor')
router.register('seaman_groups', views.AgentGroupsViewset)
router.register('seaman_by_group', views.AgentsByGroupViewset)

urlpatterns = [
    path('search_sailor/query=<str:query>/', views.SearchSailorByAgent.as_view({'get': 'list'})),
    path('qr_code/generate/', views.GetAgentQRCode.as_view()),
    path('qr_code/<str:payload>/info/', views.GetInfoAgentByQR.as_view()),
    path('qr_code/<str:payload>/statement/', views.StatementSailorToAgentView.as_view()),
    path('<int:sailor_id>/check_statement_seaman/', views.CheckAgentStatementView.as_view({'get': 'get'})),
    path('phone/statement_seaman_sailor/', views.PhoneCodeToStatementAgentSailor.as_view({'get': 'list',
                                                                                         'post': 'post'}))
]

urlpatterns += router.urls
