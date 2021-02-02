from django.urls import path, include

import authorization.TOTP.views
import authorization.views

urlpatterns = [
    path('login/', authorization.views.EmailAuthView.as_view()),
    path('totp/', include('authorization.TOTP.urls')),
    path('u2f/', include('authorization.U2F.urls')),
    path('login/totp/', authorization.TOTP.views.TOTPAuthView.as_view()),
    path('mail/', include('authorization.mail.urls')),
]
