from django.urls import path
from rest_framework import routers

import core.views

router = routers.DefaultRouter()
router.register(r'user', core.views.UserViewSet)

urlpatterns = [
    path('get_user_info/', core.views.UserFullInfoView.as_view()),
    path('photo_uploader/', core.views.PhotoUploader.as_view()),
    path('get_user_permissions/', core.views.UserPermissionsView.as_view()),
]

urlpatterns = urlpatterns + router.urls
