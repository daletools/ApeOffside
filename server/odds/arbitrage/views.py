import json

import requests
from django.conf import settings
from django.http import JsonResponse

from odds.arbitrage.utils import find_arbitrage
from .player_props import player_prop_arbitrage

ODDS_BASE_URL = "https://api.the-odds-api.com"


def player_prop_arbitrage_opportunities(request):
    opportunities, error = player_prop_arbitrage()

    if error:
        return JsonResponse({"error": error}, status=500)

    return JsonResponse(opportunities, safe=False)


# REAL ODDS -> Finds arbitrage opportunities from the Odds API
def arbitrage_opportunities(request):
    sport = "basketball_nba"

    url = f"{ODDS_BASE_URL}/v4/sports/{sport}/odds/"
    params = {
        "apiKey": settings.API_KEY,
        "regions": "us",  # U.S.-based sportsbooks only
        "markets": "h2h",
        "oddsFormat": "decimal",
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return JsonResponse(
                {"error": "Failed to fetch odds.", "details": response.text},
                status=response.status_code,
            )

        games = response.json()

        games = games[:5]  # Limit for performance/testing
        opportunities = find_arbitrage(games)
        opportunities.sort(key=lambda x: x["profit_percent"], reverse=True)
        opportunities = opportunities[:5]

        return JsonResponse(opportunities, safe=False)

    except Exception as e:
        return JsonResponse(
            {"error": "An unexpected error occurred.", "details": str(e)}, status=500
        )


# Calculate stakes and profit based on odds + total stake


def calculate_arbitrage_stakes(request):
    try:
        data = json.loads(request.body)
        odds_team1 = float(data.get("odds_team1"))
        odds_team2 = float(data.get("odds_team2"))
        total_stake = float(data.get("stake"))

        if not (odds_team1 > 1 and odds_team2 > 1 and total_stake > 0):
            return JsonResponse({"error": "Invalid input values."}, status=400)

        # Calculate implied probabilities
        implied_1 = 1 / odds_team1
        implied_2 = 1 / odds_team2
        total_implied = implied_1 + implied_2

        if total_implied >= 1:
            return JsonResponse(
                {"error": "No arbitrage possible with these odds."}, status=400
            )

        # Stake allocation
        stake_team1 = round((implied_2 / total_implied) * total_stake, 2)
        stake_team2 = round((implied_1 / total_implied) * total_stake, 2)

        # Profit from either outcome
        payout = round(stake_team1 * odds_team1, 2)
        profit = round(payout - total_stake, 2)

        return JsonResponse(
            {
                "team1_stake": stake_team1,
                "team2_stake": stake_team2,
                "guaranteed_profit": profit,
            }
        )

    except Exception as e:
        return JsonResponse(
            {"error": "Invalid request format", "details": str(e)}, status=400
        )


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
                                {"name": "Miami Heat", "price": 1.8},
                            ],
                        }
                    ],
                },
                {
                    "title": "FanDuel",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Chicago Bulls", "price": 2.4},
                                {"name": "Miami Heat", "price": 1.7},
                            ],
                        }
                    ],
                },
            ],
        }
    ]

    opportunities = find_arbitrage(fake_games)
    return JsonResponse(opportunities, safe=False)
