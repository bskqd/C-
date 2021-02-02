from django.urls import path

from . import views

urlpatterns = [
    path('check_qr/<str:payload>/', views.CheckQr.as_view()),
    path('check_qual_document/', views.DocumentWihUser.as_view()),
]
