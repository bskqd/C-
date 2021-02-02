from django.urls import path
from . import views
from rest_framework import routers


router = routers.SimpleRouter()
router.register('area', views.AreaView)
router.register('novaposhta_city', views.NovaPoshtaCityView)

urlpatterns = [
    path('novaposhta_warehouse/<int:city>/', views.NovaPoshtaWarehouseView.as_view()),
    path('novaposhta_street/<int:city>/', views.NovaPoshtaStreetView.as_view()),
]
urlpatterns += router.urls
