from django.urls import path
from . import views

urlpatterns = [
    path('', views.default, name='default'),
    path('nba-statistics/', views.fetch_nba_statistics, name='nba-statistics'),
    path('sports/', views.fetch_sports, name='fetch-sports'),
]