import requests
from django.conf import settings

ODDS_BASE_URL = "https://api.the-odds-api.com"

def fetch_player_prop_odds(sport, market_key, limit=5):
    """
    Fetches player prop odds using the per-event Odds API endpoint.

    Args:
        sport (str): e.g., "basketball_nba"
        market_key (str): e.g., "player_points", "player_assists"
        limit (int): Number of games/events to fetch

    Returns:
        list of dicts: Odds data per event
    """
    try:
        # Step 1: Get a list of upcoming games/events
        events_url = f"{ODDS_BASE_URL}/v4/sports/{sport}/events/"
        events_response = requests.get(events_url, params={"apiKey": settings.API_KEY})
        events = events_response.json()[:limit]

        all_odds = []
        for event in events:
            event_id = event["id"]
            odds_url = f"{ODDS_BASE_URL}/v4/sports/{sport}/events/{event_id}/odds/"
            odds_params = {
                "apiKey": settings.API_KEY,
                "markets": market_key,
                "regions": "us",
                "oddsFormat": "decimal"
            }
            event_response = requests.get(odds_url, params=odds_params)
            if event_response.status_code == 200:
                all_odds.append(event_response.json())

        return all_odds

    except Exception as e:
        print("Error fetching player props:", str(e))
        return []
