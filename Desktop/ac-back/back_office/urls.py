from django.urls import path
from rest_framework.routers import SimpleRouter

from sailor.urls import CustomRouter
from . import views

router = SimpleRouter()

sailor_router = CustomRouter()

router.register('price_for_position', views.PriceForPositionView)
router.register('eti_profit_part', views.ETIProfitView)
router.register('course_price', views.CoursePriceView)
sailor_router.register('packet', views.PacketView)

urlpatterns = [
    path('list/packets/', views.ReportPacketList.as_view()),
    path('<int:sailor_pk>/packet_preview/', views.PacketItemPreview.as_view()),
    path('merge_documents/', views.MergeDocumentView.as_view()),
]

urlpatterns += router.urls
urlpatterns += sailor_router.urls
