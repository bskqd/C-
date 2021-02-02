from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
router = routers.SimpleRouter()
router.register('list_verification', views.StatementSailorVerificationView, basename='list_verification')


urlpatterns = [
    path('login/', views.SMSLoginView.as_view()),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verification/', views.UserStatementVerificationView.as_view()),
    path('check_authorization/', views.CheckAuthorization.as_view()),
    path('registration/', views.UserRegistrationView.as_view()),
    # path('verification/<int:pk>', views.UserStatementVerificationView.as_view()),
]
urlpatterns = urlpatterns + router.urls

