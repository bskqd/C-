from django.urls import path, include

app_name = 'v2'
urlpatterns = [
    path('sailor/', include('sailor.urls_v2')),
]