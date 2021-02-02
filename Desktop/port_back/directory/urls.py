from django.urls import path
from rest_framework.routers import DefaultRouter

import directory.views

router = DefaultRouter()

router.register('flag', directory.views.FlagView)
router.register('type_vessel', directory.views.TypeVesselView)
router.register('staff_position', directory.views.StaffPositionView)
router.register('status_document', directory.views.StatusDocumentView)
router.register('port', directory.views.PortView)
router.register('type_document', directory.views.TypeDocumentView)
router.register('agency', directory.views.AgencyView)
router.register('country', directory.views.CountryView)
router.register('sex', directory.views.SexView)
router.register('towing_company', directory.views.TowingCompanyView)
router.register('tow', directory.views.TowView)

urlpatterns = [
    path('upload_towing_company_docs', directory.views.TowingCompanyDocsView.as_view()),
    path('upload_tow_docs', directory.views.TowDocsView.as_view())
]

urlpatterns += router.urls
