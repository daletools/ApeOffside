
def calculate_arbitrage(odds_team1, odds_team2):
    """
    Given decimal odds for two outcomes, calculates if arbitrage exists.
    Returns a tuple:
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


def find_arbitrage(games, market_key="h2h"):
    """
    Dynamically detects arbitrage opportunities.
    Works for both team-level and player prop markets.
    """
    opportunities = []

    for game in games:
        event = f"{game['home_team']} vs {game['away_team']}"
        commence_time = game["commence_time"]

        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market["key"] != market_key:
                    continue

                outcomes = market.get("outcomes", [])
                if len(outcomes) < 2:
                    continue

                # Detect over/under arbitrage (e.g., Player Props)
                for i in range(len(outcomes)):
                    for j in range(i + 1, len(outcomes)):
                        side1 = outcomes[i]
                        side2 = outcomes[j]

                        # Must be opposing sides of the same prop
                        if side1.get("description") != side2.get("description"):
                            continue

                        odds1 = side1.get("price")
                        odds2 = side2.get("price")
                        if not odds1 or not odds2:
                            continue

                        is_arb, profit = calculate_arbitrage(odds1, odds2)
                        if is_arb:
                            opportunities.append({
                                "type": market_key,
                                "event": event,
                                "commence_time": commence_time,
                                "player": side1.get("description", "Unknown"),
                                "line": side1.get("point"),
                                "side_1": {
                                    "name": side1["name"],
                                    "bookmaker": bookmaker["title"],
                                    "price": odds1
                                },
                                "side_2": {
                                    "name": side2["name"],
                                    "bookmaker": bookmaker["title"],
                                    "price": odds2
                                },
                                "profit_percent": profit
                            })

    return opportunities

#VALUE BET DETECTOR
# Detects value bets based on deviation from consensus odds.
#We'll return opportunities with EV% over a given threshold.
def detect_value_bets(games, threshold=5.0):
    value_bets = []

    for game in games:
        market_odds = {} # Dictionary to collect odds for each team

        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":
                    for outcome in market.get("outcomes", []):
                        team = outcome["name"]
                        odds = outcome["price"]

                        # Group odds by team
                        market_odds.setdefault(team, []).append({
                            "bookmaker": bookmaker["title"],
                            "odds": odds
                        })
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
                value_percentage = ((bookmaker_odds - consensus_odds) / consensus_odds) * 100

                # Only include bets above the value threshold
                if value_percentage >= threshold:
                    value_bets.append({
                        "team": team,
                        "bookmaker": entry["bookmaker"],
                        "odds": bookmaker_odds,
                        "consensus_odds": round(consensus_odds, 2),
                        "value_percentage": round(value_percentage, 2),
                        "game": {
                            "home_team": game["home_team"],
                            "away_team": game["away_team"],
                            "commence_time": game["commence_time"]
                        }
                    })

    return value_bets
