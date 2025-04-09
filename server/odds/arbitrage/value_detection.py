import requests
from django.http import JsonResponse
from django.conf import settings

from .utils import detect_value_bets

#VALUE BETS FOR NBA
def value_bet_opportunities(request):
    sport = "basketball_nba" #change when ready to expand on sports
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    params = {
        "apiKey": settings.API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        # Request odds from the Odds API
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return JsonResponse({"error": "Failed to fetch odds."}, status=response.status_code)

        # Parse and process the data
        games = response.json()
        value_bets = detect_value_bets(games) # Call utility to detect value bets

        return JsonResponse(value_bets, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)