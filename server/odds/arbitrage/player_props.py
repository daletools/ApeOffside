import requests
from django.http import JsonResponse
from django.conf import settings
from odds.utils.api_helpers import fetch_player_prop_odds
from .utils import find_arbitrage  # Placeholder: replace with player-specific logic later

# Base URL for the Odds API
ODDS_BASE_URL = "https://api.the-odds-api.com"

# Endpoint: Handles requests for player prop arbitrage opportunities
def player_prop_arbitrage(request):
    sport = request.GET.get("sport", "basketball_nba")
    market_key = request.GET.get("market", "player_points")

    try:
        # Use the helper to get per-event odds
        game_odds = fetch_player_prop_odds(sport, market_key)

        # Flatten into a single list if needed
        combined = []
        for event in game_odds:
            if "bookmakers" in event:
                combined.append(event)

        opportunities = find_arbitrage(combined, market_key=market_key)
        opportunities.sort(key=lambda x: x['profit_percent'], reverse=True)
        return JsonResponse(opportunities[:5], safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

