BOOKMAKER_URLS = {
    "FanDuel": "https://sportsbook.fanduel.com",
    "DraftKings": "https://sportsbook.draftkings.com",
    "BetMGM": "https://sports.betmgm.com",
    "Caesars": "https://www.caesars.com/sportsbook",
    "BetRivers": "https://www.betrivers.com",
    "Bovada": "https://www.bovada.lv",
    "BetOnline.ag": "https://www.betonline.ag",
    "BetUS": "https://www.betus.com.pa",
    "MyBookie": "https://mybookie.ag",
    "Fanatics": "https://www.fanatics.com",
    "ESPN BET": "https://www.espnbet.com",
    "Hard Rock": "https://www.hardrock.bet",
    "BetAnySports": "https://www.betanysports.eu",
    "Bally Bet": "https://www.ballybet.com",
    "Fliff": "https://www.fliff.com",
    "Wind Creek": "https://www.windcreek.com",
}


def calculate_arbitrage(odds_team1, odds_team2):
    """
    Given decimal odds for two outcomes, calculates if arbitrage exists.
    Returns:
        (is_arbitrage: bool, profit_percent: float)
    """
    try:
        # Convert odds to implied probabilities
        implied_1 = 1 / odds_team1
        implied_2 = 1 / odds_team2
        total = implied_1 + implied_2

        # Arbitrage exists if total implied probability < 1
        is_arbitrage = total < 1
        profit_percent = round((1 - total) * 100, 2) if is_arbitrage else 0
        return is_arbitrage, profit_percent

    except ZeroDivisionError:
        # Fail if odds are invalid
        return False, 0


def find_arbitrage(games, market_key="player_points", include_same_book=False):
    opportunities = []
    near_arbs = []

    for game in games:
        event = f"{game['home_team']} vs {game['away_team']}"
        commence_time = game["commence_time"]
        player_markets = {}

        for bookmaker in game.get("bookmakers", []):
            title = bookmaker["title"]
            for market in bookmaker.get("markets", []):
                if market["key"] != market_key:
                    continue

                for outcome in market.get("outcomes", []):
                    name = outcome.get("name")
                    player = outcome.get("description")
                    price = outcome.get("price")
                    point = outcome.get("point")

                    if not all([name, player, price, point]):
                        continue

                    key = (player, point)
                    player_markets.setdefault(key, {"Over": [], "Under": []})
                    player_markets[key][name].append(
                        {
                            "bookmaker": title,
                            "price": price,
                        }
                    )

        for (player, point), sides in player_markets.items():
            #  print(f"\n[CHECK] Player: {player} | Line: {point}")
            # print(f"  Over: {[o['bookmaker'] + '@' + str(o['price']) for o in sides['Over']]}")
            # print(f"  Under: {[u['bookmaker'] + '@' + str(u['price']) for u in sides['Under']]}")

            for over in sides["Over"]:
                for under in sides["Under"]:
                    if over["bookmaker"] == under["bookmaker"]:
                        continue

                    implied_1 = 1 / over["price"]
                    implied_2 = 1 / under["price"]
                    total = implied_1 + implied_2
                    profit = round((1 - total) * 100, 2)

                    entry = {
                        "type": market_key,
                        "event": event,
                        "commence_time": commence_time,
                        "player": player,
                        "line": point,
                        "side_1": {
                            **over,
                            "name": "Over",
                            "site": BOOKMAKER_URLS.get(over["bookmaker"]),
                        },
                        "side_2": {
                            **under,
                            "name": "Under",
                            "site": BOOKMAKER_URLS.get(under["bookmaker"]),
                        },
                    }

                    if total < 1:
                        entry["profit_percent"] = profit
                        opportunities.append(entry)

                        import json

                        print("[DEBUG] Arbitrage Entry:", json.dumps(entry, indent=2))

                    else:
                        entry["implied_total"] = round(total, 3)
                        near_arbs.append(entry)

                opportunities = sorted(
                    opportunities, key=lambda x: x["profit_percent"], reverse=True
                )[:3]
                near_arbs = sorted(near_arbs, key=lambda x: x["implied_total"])[:3]

    # print(f"[DEBUG] Found {len(opportunities)} arbitrage opportunities.")
    return opportunities, near_arbs


# VALUE BET DETECTOR
# Detects value bets based on deviation from consensus odds.
# We'll return opportunities with EV% over a given threshold.
def detect_value_bets(games, threshold=5.0):
    value_bets = []

    for game in games:
        market_odds = {}  # Dictionary to collect odds for each team

        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":
                    for outcome in market.get("outcomes", []):
                        team = outcome["name"]
                        odds = outcome["price"]

                        # Group odds by team
                        market_odds.setdefault(team, []).append(
                            {"bookmaker": bookmaker["title"], "odds": odds}
                        )
        # Iterate over teams and evaluate value
        for team, entries in market_odds.items():
            if len(entries) < 2:
                continue  # Not enough data to compare

            # Calculate consensus implied probability
            implied_probs = [1 / e["odds"] for e in entries]
            consensus_prob = sum(implied_probs) / len(implied_probs)
            consensus_odds = 1 / consensus_prob

            for entry in entries:
                bookmaker_odds = entry["odds"]
                # Calculate value percentage (potential misprice)
                value_percentage = (
                    (bookmaker_odds - consensus_odds) / consensus_odds
                ) * 100

                # Only include bets above the value threshold
                if value_percentage >= threshold:
                    value_bets.append(
                        {
                            "team": team,
                            "bookmaker": entry["bookmaker"],
                            "odds": bookmaker_odds,
                            "consensus_odds": round(consensus_odds, 2),
                            "value_percentage": round(value_percentage, 2),
                            "game": {
                                "home_team": game["home_team"],
                                "away_team": game["away_team"],
                                "commence_time": game["commence_time"],
                            },
                        }
                    )

    return value_bets
