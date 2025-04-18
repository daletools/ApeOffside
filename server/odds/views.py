from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.cache import cache
import requests
from datetime import datetime
from odds.utils.view_helpers import parse_event_odds

ODDS_BASE_URL = "https://api.the-odds-api.com"


# Fetch Odds Reduced View draftkings ONLY for test purposes
def fetch_odds(request, sport):
    url = f"{ODDS_BASE_URL}/v4/sports/{sport}/odds/"
    params = {
        "apiKey": settings.API_KEY,
        "regions": "us",
        "bookmakers": "draftkings",
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


# GET /v4/sports/{sport}/events/{eventId}/odds?apiKey={apiKey}&regions={regions}&markets={markets}&dateFormat={dateFormat}&oddsFormat={oddsFormat}
def fetch_event_odds(request, sport, event_id, markets):
    cache_key = f"event_odds_{sport}_{event_id}_{markets}"
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        response_data = {
            'data': cached_data,
            'metadata': {
                'cached': True,
                'timestamp': datetime.now().isoformat(),
                'message': 'Served from cache (60 second TTL)'
            }
        }
        return JsonResponse(response_data, safe=False)

    url = (f"{ODDS_BASE_URL}"
           f"/v4/sports/{sport}"
           f"/events/{event_id}"
           f"/odds?apiKey={settings.API_KEY}"
           f"&regions=us&markets={markets}"
           f"&includeLinks=true")

    try:
        response = requests.get(url)
        if response.status_code != 200:
            return JsonResponse(
                {'error': 'Failed to fetch odds', 'details': response.text},
                status=response.status_code
            )

        print(response.json())

        full_data = response.json()
        parsed_data = parse_event_odds(full_data)

        cache.set(cache_key, parsed_data, 60)
        response_data = {
            'data': parsed_data,
            'metadata': {
                'cached': False,
                'timestamp': datetime.now().isoformat(),
                'message': 'Freshly fetched data'
            }
        }

        return JsonResponse(response_data, safe=False)

    except Exception as e:
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=500)


def fetch_historical_odds(request, sport, date):
    url = f"{ODDS_BASE_URL}/v4/sports/{sport}/events/"
    params = {
        "apiKey": settings.API_KEY,
        "regions": "us",
        "oddsFormat": "decimal",
        "date": date  # Add date parameter to the request for historical odds
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            return JsonResponse({
                'error': 'Failed to fetch historical odds',
                'details': response.text
            }, status=response.status_code)

        data = response.json()
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    # Fetch historical stats for a specific player


def fetch_historical_player_data(request, player_name, date):
    url = f"{ODDS_BASE_URL}/v4/player/{player_name}/events/"
    params = {
        "player": player_name,
        "date": date,  # If date filtering is supported
    }

    headers = {
        "x-rapidapi-key": settings.API_KEY,  # Make sure this API Key is set in your Django settings
        "x-rapidapi-host": "api.the-odds-api.com"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return JsonResponse({
                "error": "Failed to fetch historical player data",
                "details": response.text
            }, status=response.status_code)

        raw_data = response.json()
        formatted_data = []

        # Process the data to make it user-friendly
        for stat in raw_data["response"]:  # Modify according to the API's response structure
            formatted_data.append({
                "date": stat.get("game", {}).get("date", "N/A"),
                "points": stat.get("points", "N/A"),
                "rebounds": stat.get("totReb", "N/A"),
                "assists": stat.get("assists", "N/A"),
                "steals": stat.get("steals", "N/A"),
                "blocks": stat.get("blocks", "N/A")
            })

        return JsonResponse(formatted_data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
