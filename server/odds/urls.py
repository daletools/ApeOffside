from django.urls import path

from . import views

urlpatterns = [
    path(
        "event/<str:sport>/<str:event_id>/<str:markets>",
        views.fetch_event_odds,
        name="event odds",
    ),
]
