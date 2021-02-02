from django.urls import path

import integrations.smallboats.views

urlpatterns = [
    path('create_user/', integrations.smallboats.views.SmallBoatsCreateUser.as_view())
]
