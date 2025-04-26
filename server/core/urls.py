from django.urls import path

from . import views

urlpatterns = [
    path("sports/", views.fetch_sports, name="fetch-sports"),
    path(
        "current-games/<str:sport>/",
        views.fetch_current_games,
        name="fetch-current-games",
    ),
]
