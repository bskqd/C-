from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('price_for_iorequest', views.PriceIORequestViewset)
router.register('price_for_deadweight', views.DeadweightPriceViewset)

urlpatterns = [

]

urlpatterns += router.urls
