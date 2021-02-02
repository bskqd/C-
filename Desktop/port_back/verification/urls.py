from django.urls import path

import verification.views

urlpatterns = [
    path('io_request/', verification.views.PublicVerificationView.as_view({'get': 'retrieve'}))
]
