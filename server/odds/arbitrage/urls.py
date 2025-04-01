from django.urls import path
from . import views
from .views import (
    arbitrage_opportunities,
    calculate_arbitrage_stakes,
    test_arbitrage_with_fake_data, # Remove: Later Test Data
)

app_name = "arbitrage"

urlpatterns = [
    path("find/", arbitrage_opportunities, name="find_arbitrage"),
    path("opportunities/", arbitrage_opportunities, name="arbitrage-opportunities"),
    path("calculate/", calculate_arbitrage_stakes, name="calculate_arbitrage"),
    path("test/", test_arbitrage_with_fake_data, name="arbitrage-fake"),  # New fake data route
]
