from django.urls import path

from news import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('', views.NewsListViewset, basename='NewsList')

urlpatterns = [
    # path('<str:slug>/', views.NewsListViewset.as_view({'get': 'retrieve'}, name='retrieve_news')),
    path('filter/<str:type>/<str:value>/', views.NewsListViewset.as_view({'get': 'list'}, name='filter_news')),
]

urlpatterns = urlpatterns + router.urls
