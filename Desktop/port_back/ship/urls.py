from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

import ship.views

default_router = DefaultRouter()

router = routers.SimpleRouter()
default_router.register('ship/draft_document', ship.views.DraftDocumentView)

router.register('ship/list_agent_nomination', ship.views.ListAgentNominationView)
router.register('ship/list_ships_in_port', ship.views.ListShipInPortView)
router.register(r'ship', ship.views.MainInfoView)

ship_router = routers.NestedSimpleRouter(router, r'ship', lookup='ship')
ship_router.register('staff', ship.views.ShipStaffView)
ship_router.register('io_request', ship.views.IORequestView)
ship_router.register('agent_nomination', ship.views.ShipAgentNominationView)

urlpatterns = [
    path('ship/io_request/<int:pk>/', ship.views.IORequestView.as_view({'get': 'retrieve'})),
    path('ship/global_search/', ship.views.SearchByShip.as_view()),
    path('ship/iorequest/ship_search/', ship.views.SearchByShipForIORequest.as_view()),
    path('ship/<int:ship_pk>/port_of_departure/', ship.views.PortOfDepartureView.as_view()),
]

urlpatterns += default_router.urls
urlpatterns += router.urls
urlpatterns += ship_router.urls
