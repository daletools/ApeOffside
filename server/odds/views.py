from django.http import JsonResponse, HttpResponse
from django.conf import settings
import requests

ODDS_BASE_URL = "https://api.the-odds-api.com"
#Fetch Odds Reduced View draftkings ONLY for test purposes
def fetch_odds(request, sport):
    url = f"{ODDS_BASE_URL}/v4/sports/{sport}/odds/"
    params = {
        "apiKey": settings.API_KEY,
        "regions": "us",
        "markets": "h2h",
     #Testing Arbitrage   "bookmakers": "draftkings",  # Limit to one bookmaker
        "oddsFormat": "decimal"
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return JsonResponse(
                {'error': 'Failed to fetch odds', 'details': response.text},
                status=response.status_code
            )

        full_data = response.json()


        trimmed = []
        for game in full_data:
            event = {
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "commence_time": game["commence_time"],
                "bookmaker": None
            }

            for bookmaker in game.get("bookmakers", []):
                if bookmaker["title"].lower() == "draftkings":
                    h2h = next((m for m in bookmaker["markets"] if m["key"] == "h2h"), None)
                    if h2h:
                        event["bookmaker"] = {
                            "title": "DraftKings",
                            "h2h": h2h["outcomes"]
                        }
            trimmed.append(event)

        return JsonResponse(trimmed, safe=False)

    except Exception:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
