from django.urls import path
from . import views

urlpatterns = [
    path('<str:sport>/', views.fetch_odds, name='odds'),
]