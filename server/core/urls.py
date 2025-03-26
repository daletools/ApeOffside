from django.urls import path
from django.urls.conf import include

from . import views
from .views import fetch_sports


urlpatterns = [
    path('', views.default, name='default'),
    path('nba-statistics/', views.fetch_nba_statistics, name='nba-statistics'),
    path('sports/', views.fetch_sports, name='fetch-sports'),
    path('current-games/<str:sport>/', views.fetch_current_games, name='fetch-current-games'),
]

