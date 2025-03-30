from django.urls import path
from . import views
from .views import arbitrage_opportunities

app_name = "arbitrage"

urlpatterns = [
    path("find/", arbitrage_opportunities, name="find_arbitrage"),
    path("opportunities/", arbitrage_opportunities, name="arbitrage-opportunities"),

]
