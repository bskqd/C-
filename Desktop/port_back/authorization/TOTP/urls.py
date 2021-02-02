from django.urls import path

import authorization.TOTP.views

urlpatterns = [
    path('create/', authorization.TOTP.views.TOTPCreateView.as_view()),
    path('verify/', authorization.TOTP.views.TOTPVerifyView.as_view()),
]
