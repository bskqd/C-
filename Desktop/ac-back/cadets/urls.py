from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register('student_id', views.StudentIDViewset, basename='studentid')

urlpatterns = [
    path('students_id_per_sailor/<int:sailor>/', views.SailorStudentIDViewset.as_view()),
]

urlpatterns = urlpatterns + router.urls
