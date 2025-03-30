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
        "markets": "player_points",
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

#GET /v4/sports/{sport}/events/{eventId}/odds?apiKey={apiKey}&regions={regions}&markets={markets}&dateFormat={dateFormat}&oddsFormat={oddsFormat}
def fetch_event_odds(request, sport, event_id, markets):
    url=url = f"{ODDS_BASE_URL}/v4/sports/{sport}/events/{event_id}/odds?apiKey={settings.API_KEY}&regions=us&markets={markets}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return JsonResponse(
                {'error': 'Failed to fetch odds', 'details': response.text},
                status=response.status_code
            )

        full_data = response.json()

        parsed_data = {
            'id': full_data['id'],
            'sport_key': full_data['sport_key'],
            'sport_title': full_data['sport_title'],
            'commence_time': full_data['commence_time'],
            'home_team': full_data['home_team'],
            'away_team': full_data['away_team'],
            'market': full_data['bookmakers'][0]['markets'][0]['key'],
            'bookmaker': {},
            'player': {}
        }
        for bookmaker in full_data['bookmakers']:
            parsed_data['bookmaker'][bookmaker['key']] = {
                'title': bookmaker['title'],
                'last_update': bookmaker['markets'][0]['last_update'],
            }
            for outcome in bookmaker['markets'][0]['outcomes']:
                if outcome['description'] not in parsed_data['player']:
                    print('Adding player {}'.format(outcome['description']))
                    parsed_data['player'][outcome['description']] = {}
                if bookmaker['title'] not in parsed_data['player'][outcome['description']]:
                    parsed_data['player'][outcome['description']][bookmaker['title']] = {}
                curr = parsed_data['player'][outcome['description']][bookmaker['title']]
                curr[outcome['name']] = {
                    'price': outcome['price'],
                    'point': outcome['point'],
                }
        return JsonResponse(parsed_data, safe=False)

    except Exception:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)