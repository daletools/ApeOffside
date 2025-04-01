from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
import requests
import json

from odds.arbitrage.utils import find_arbitrage

ODDS_BASE_URL = "https://api.the-odds-api.com"


# ✅ REAL ODDS -> Finds arbitrage opportunities from the Odds API
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
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return JsonResponse({
                "error": "Failed to fetch odds.",
                "details": response.text
            }, status=response.status_code)

        games = response.json()

        games = games[:5]  # Limit for performance/testing
        opportunities = find_arbitrage(games)
        opportunities.sort(key=lambda x: x['profit_percent'], reverse=True)
        opportunities = opportunities[:5]

        return JsonResponse(opportunities, safe=False)

    except Exception as e:
        return JsonResponse({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }, status=500)


#Calculate stakes and profit based on odds + total stake

def calculate_arbitrage_stakes(request):
    try:
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "Bad JSON"}, status=400)

        o1 = data.get("odds_team1")
        o2 = data.get("odds_team2")
        stake = data.get("stake")

        if o1 is None or o2 is None or stake is None:
            return JsonResponse({"error": "Missing fields"}, status=400)

        try:
            o1 = float(o1)
            o2 = float(o2)
            stake = float(stake)
        except:
            return JsonResponse({"error": "Non-numeric input"}, status=400)

        if o1 <= 1 or o2 <= 1 or stake <= 0:
            return JsonResponse({"error": "Invalid input values."}, status=400)

        imp1 = 1 / o1
        imp2 = 1 / o2
        total_prob = imp1 + imp2

        if total_prob >= 1.0:
            return JsonResponse({"error": "No arbitrage opportunity"}, status=400)

        st1 = round((imp2 / total_prob) * stake, 2)
        st2 = round((imp1 / total_prob) * stake, 2)

        payout1 = round(st1 * o1, 2)
        payout2 = round(st2 * o2, 2)
        profit = round(min(payout1, payout2) - stake, 2)

        return JsonResponse({
            "team1_stake": st1,
            "team2_stake": st2,
            "guaranteed_profit": profit,
            "payout_team1": payout1,
            "payout_team2": payout2,
            "inputs": {
                "odds_team1": o1,
                "odds_team2": o2,
                "stake": stake
            }
        })

    except Exception as e:
        return JsonResponse({"error": "Unexpected error", "details": str(e)}, status=500)


#  FAKE TEST DATA # Remove: Later
def test_arbitrage_with_fake_data(request):
    fake_games = [
        {
            "home_team": "Chicago Bulls",
            "away_team": "Miami Heat",
            "commence_time": "2025-04-01T00:00:00Z",
            "bookmakers": [
                {
                    "title": "DraftKings",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Chicago Bulls", "price": 2.2},
                                {"name": "Miami Heat", "price": 1.8}
                            ]
                        }
                    ]
                },
                {
                    "title": "FanDuel",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Chicago Bulls", "price": 2.4},
                                {"name": "Miami Heat", "price": 1.7}
                            ]
                        }
                    ]
                }
            ]
        }
    ]

    opportunities = find_arbitrage(fake_games)
    return JsonResponse(opportunities, safe=False)
