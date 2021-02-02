from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from user_profile import views
from user_profile.views import UserViewSet, GroupViewSet, SomeDataAPI, MainGroupViewSet, VersionViewset, \
    BranchOfficeRestriction

router = routers.SimpleRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'subgroups', GroupViewSet)
router.register(r'groups', MainGroupViewSet)
router.register('version', VersionViewset)
router.register('branch_office_restr', BranchOfficeRestriction, basename='branch_office_restr')
router.register('history', views.HistoryByUser)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^get_data', SomeDataAPI.as_view()),
    path('get_user_info/', views.GetInfoByMyUser.as_view()),
    path('get_user_language/', views.GetLanguageUser.as_view()),
    path('get_user_permissions/', views.GetUserPermissions.as_view()),
    path('get_user_history/', views.HistorySailorByUser.as_view()),
    path('user_notification/', views.UserNotificationCounter.as_view()),
    path('user_is_trained/', views.UserIsTrainedView.as_view()),
]
