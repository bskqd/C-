from rest_framework.routers import DefaultRouter
import reports.views
router = DefaultRouter()
router.register('io_requests', reports.views.IORequestView)

urlpatterns = []
urlpatterns += router.urls
