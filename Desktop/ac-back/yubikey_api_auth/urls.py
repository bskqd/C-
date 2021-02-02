from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views
router = routers.SimpleRouter()
router.register('authorization_log', views.AuthorizationLogViewset)
# router.register('register_user', views.CreateUserView, basename='basename')

urlpatterns = [
    path('login_yubi/', views.obtain_auth_token, name='login_password_auth'),
    path('yubikeylogin/', views.u2f_authorization, name='yubikey'),
    path('index/', views.index),
    path('add_key/', views.add_key),
    path('register_user/', views.CreateUserView.as_view()),
    path('check_authozation/', views.CheckAuthorization.as_view()),
    path('login/', views.LoginAuthorization.as_view()),
    path('check_password/', views.CheckPassword.as_view()),
    path('change_password/', views.ChangePassword.as_view()),
]

urlpatterns = urlpatterns + router.urls
