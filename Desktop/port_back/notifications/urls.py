from rest_framework import routers

import notifications.views

router = routers.DefaultRouter()
router.register(r'user_notifications', notifications.views.NotificationByUser)

urlpatterns = [

]

urlpatterns = urlpatterns + router.urls