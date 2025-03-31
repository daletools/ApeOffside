from django.urls import path
from . import views

urlpatterns = [
    path('<str:sport>/', views.fetch_odds, name='odds'),
    path('event/<str:sport>/<str:event_id>/<str:markets>', views.fetch_event_odds, name='event odds'),
]