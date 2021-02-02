from django.urls import path

from . import views

urlpatterns = [
    path('num_of_docs/', views.NumOfVerifyDocuments.as_view()),
    path('verification_for_personal_cabinet/', views.UserVerifyForPersonalCabinetView.as_view()),
    path('post_verification_list/', views.PostVerifyDocsList.as_view()),
    # path('agent_document/', views.AgentVerificationView.as_view({'get': 'list'})),
    path('seaman_document/', views.AgentVerificationView.as_view({'get': 'list'})),
]