from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register('create_protocol', views.CreateProtocolDKK)
router.register('statement_dkk_list', views.StatementDKKList)

urlpatterns = [
    # path('statement_dkk_list/', views.StatementDKKList.as_view())
    path('search_sailor/', views.SearchSailor.as_view()),
    path('start_exam/<int:statement_id>/', views.CreateUserExamOnStatementSQC.as_view()),
]

urlpatterns = urlpatterns + router.urls
