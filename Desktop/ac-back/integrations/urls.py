from django.urls import path, include

from integrations import views

urlpatterns = [
    path('smallboats/', include('integrations.smallboats.urls')),
    path('eti_online/', include('integrations.eti_online.urls')),
    path('search_sailor/<int:sailor_id>/', views.SearchSailorView.as_view())
]
