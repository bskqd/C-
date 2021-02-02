from django.urls import path
from rest_framework.routers import SimpleRouter

from notifications import views

router = SimpleRouter()

router.register('history', views.HistoryPushDataView)
router.register('user_notification', views.NotificationByUser)


urlpatterns = [
    path('device/', views.UserDeviceInfo.as_view()),

]

urlpatterns += router.urls
