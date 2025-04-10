from django.http import JsonResponse
from odds.utils.api_helpers import fetch_player_prop_odds
from .utils import find_arbitrage

def player_prop_arbitrage(request):
    sport = request.GET.get("sport", "basketball_nba")
    market = request.GET.get("market", "player_points")

    try:
        all_event_odds = fetch_player_prop_odds(sport, market)
        opportunities, near_arbs = find_arbitrage(all_event_odds, market_key=market)


        response = {
            "arbitrage": opportunities,
            "near_arbitrage": near_arbs,
        }

        return JsonResponse(response, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
