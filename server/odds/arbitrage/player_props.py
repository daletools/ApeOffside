import requests
from django.http import JsonResponse
from django.conf import settings
from odds.utils.api_helpers import fetch_player_prop_odds
from .utils import find_arbitrage  # Placeholder: replace with player-specific logic later

# Endpoint for player prop arbitrage (per-event fetching)
def player_prop_arbitrage(request):
    sport = request.GET.get("sport", "basketball_nba")
    market = request.GET.get("market", "player_points")

    try:
        # Step 1: Use helper to fetch per-event player prop odds
        all_event_odds = fetch_player_prop_odds(sport, market)
        print(f"Fetched {len(all_event_odds)} player prop games.")
        print(all_event_odds)

        # Step 2: Pass those odds to the arbitrage detector
        opportunities = find_arbitrage(all_event_odds, market_key=market)
        opportunities.sort(key=lambda x: x["profit_percent"], reverse=True)

        return JsonResponse(opportunities[:10], safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)