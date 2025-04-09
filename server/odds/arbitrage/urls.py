from django.urls import path
from . import views
from .views import (
    arbitrage_opportunities,
    calculate_arbitrage_stakes,
    test_arbitrage_with_fake_data, # Remove: Later Test Data
)
from .value_detection import value_bet_opportunities
from .player_props import player_prop_arbitrage

app_name = "arbitrage"

urlpatterns = [
    path("find/", arbitrage_opportunities, name="find_arbitrage"),
    path("opportunities/", arbitrage_opportunities, name="arbitrage-opportunities"),
    path("calculate/", calculate_arbitrage_stakes, name="calculate_arbitrage"),
    path("valuebets/", value_bet_opportunities, name="value_bet_opportunities"),
    path("player-props/", player_prop_arbitrage, name="player-prop-arbitrage"),
    path("test/", test_arbitrage_with_fake_data, name="arbitrage-fake"),  # New fake data route
]
