from django.urls import path, include

app_name = 'v1'

urlpatterns = [
    path('docs/', include('docs.urls')),
    path('auth/', include('user_profile.urls')),
    path('directory/', include('directory.urls')),
    path('sailor/', include('sailor.urls')),
    path('verification/', include('verification.urls')),
    path('personal_cabinet/', include('personal_cabinet.e_transport.urls')),
    path('sms_auth/', include('sms_auth.urls')),
    path('news/', include('news.urls')),
    path('reports/', include('reports.urls')),
    path('auth_govua/', include('idgovua_auth.urls')),
    path('delivery/', include('delivery.urls')),
    path('public_api/', include('public_api.urls')),
    path('training/', include('training.urls')),
    path('cadets/', include('cadets.urls')),
    path('signature/', include('signature.urls')),
    path('back_off/', include('back_office.urls')),
    path('back_off/certificates/', include('certificates.urls')),
    path('seaman/', include('agent.urls')),
    path('notifications/', include('notifications.urls')),
    path('personal_cabinet/morrichservice/', include('personal_cabinet.morrichservice.urls')),
    path('integrations/', include('integrations.urls')),
]
