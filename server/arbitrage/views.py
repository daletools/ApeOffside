
from django.http import JsonResponse
from django.conf import settings
import requests

from .utils import find_arbitrage


ODDS_BASE_URL = "https://api.the-odds-api.com"

def arbitrage_opportunities(request):

    sport = "basketball_nba"


    url = f"{ODDS_BASE_URL}/v4/sports/{sport}/odds/"
    params = {
        "apiKey": settings.API_KEY,
        "regions": "us",               # U.S.-based sportsbooks only
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        # Fetch odds from the Odds API
        response = requests.get(url, params=params)

        # Handle any non-200 (error) responses
        if response.status_code != 200:
            return JsonResponse({
                "error": "Failed to fetch odds.",
                "details": response.text
            }, status=response.status_code)

        # Parse the response JSON
        games = response.json()

        #Only process the first 5 games
        games = games[:5]

        # Pass games into our arbitrage finder utility
        opportunities = find_arbitrage(games)

        # Sort arbitrage opportunities by highest profit percent first
        opportunities.sort(key=lambda x: x['profit_percent'], reverse=True)

        # Return only the top 5 most profitable opportunities
        opportunities = opportunities[:5]

        # Respond with the final filtered & sorted list
        return JsonResponse(opportunities, safe=False)

    except Exception as e:
        # Catch unexpected errors
        return JsonResponse({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }, status=500)
