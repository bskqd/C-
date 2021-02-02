from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('invite_agent', views.InvitationAgentView)

urlpatterns = [
    path('registration_agent/<str:key>/', views.RegistrationByToken.as_view()),
]

urlpatterns += router.urls
