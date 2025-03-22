from django.http import JsonResponse, HttpResponse
from django.conf import settings
import requests

# Create your views here.

def default(request):
    return HttpResponse("This is the default response to the Core endpoint")

def fetch_nba_statistics(request):
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
    querystring = {"game": "8133"}
    headers = {
        "x-rapidapi-key": "TODO: get historical stats api key",
        "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    return JsonResponse(response.json())

def fetch_sports(request):
    url = f"{settings.ODDS_URL}/v4/sports/?apiKey={settings.API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return JsonResponse(
            {'error': 'Failed to fetch sports', 'details': response.text},
            status=response.status_code
        )

    return JsonResponse(response.json(), safe=False)

def fetch_current_games(request, sport):
    url = f"{settings.ODDS_URL}/v4/sports/{sport}/events?apiKey={settings.API_KEY}"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            return JsonResponse(
                {'error': 'Failed to fetch games', 'details': response.text},
                status=response.status_code
            )
        return JsonResponse(response.json(), safe=False)
    except Exception:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    #Fetch Odds Reduced View draftkings ONLY for test purposes
def fetch_odds(request, sport):
    url = f"{settings.ODDS_URL}/v4/sports/{sport}/odds/"
    params = {
        "apiKey": settings.API_KEY,
        "regions": "us",
        "markets": "h2h",
        "bookmakers": "draftkings",  # Limit to one bookmaker
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
