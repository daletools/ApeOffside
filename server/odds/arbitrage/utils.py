
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


def find_arbitrage(games):
    """
    Parses raw game odds data (from OddsAPI) and finds arbitrage opportunities.

    Args:
        games (list): List of games from the Odds API response.

    Returns:
        List of dicts describing profitable arbitrage matchups.
    """
    opportunities = []

    for game in games:
        bookmakers = game.get("bookmakers", [])

        # Skip games with fewer than two bookmakers
        if len(bookmakers) < 2:
            continue

        # Dictionary to collect all prices for each team
        h2h_odds = {}

        for bookmaker in bookmakers:
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":  # Only care about moneyline (h2h) markets
                    for outcome in market.get("outcomes", []):
                        team = outcome.get("name")
                        price = outcome.get("price")
                        if team and price:
                            h2h_odds.setdefault(team, []).append({
                                "bookmaker": bookmaker["title"],
                                "price": price
                            })
        if len(h2h_odds) != 2:
            continue

        team1, team2 = list(h2h_odds.keys())

        # Compare all bookmaker combinations for both teams
        for t1_odds in h2h_odds[team1]:
            for t2_odds in h2h_odds[team2]:
                is_arb, profit = calculate_arbitrage(t1_odds["price"], t2_odds["price"])
                if is_arb:
                    # Store the profitable arbitrage opportunity
                    opportunities.append({
                        "home_team": game.get("home_team"),
                        "away_team": game.get("away_team"),
                        "commence_time": game.get("commence_time"),
                        "team_1": {
                            "name": team1,
                            "bookmaker": t1_odds["bookmaker"],
                            "price": t1_odds["price"]
                        },
                        "team_2": {
                            "name": team2,
                            "bookmaker": t2_odds["bookmaker"],
                            "price": t2_odds["price"]
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
