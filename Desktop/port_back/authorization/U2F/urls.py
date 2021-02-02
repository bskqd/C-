from django.urls import path
import authorization.U2F.views

urlpatterns = [
    path('register/', authorization.U2F.views.U2FAddKeys.as_view()),
    path('login/', authorization.U2F.views.U2FAuthorization.as_view())
]