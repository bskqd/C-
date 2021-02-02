from django.urls import path

from . import views

urlpatterns = [
    path('registration/', views.IDGovUARegistration.as_view()),
    path('e-sailor-auth/', views.ESailorIDGovUaRegistration.as_view()),
    path('mrs-auth/', views.ESailorIDGovUaRegistration.as_view()),
    path('mdu-auth/', views.MDUIDGovUaRegistration.as_view()),
]
