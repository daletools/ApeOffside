
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


def find_arbitrage(games, market_key="player_points"):
    opportunities = []

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
                    player_markets[key][name].append({
                        "bookmaker": title,
                        "price": price
                    })

        for (player, point), sides in player_markets.items():
            #print(f"\n[CHECK] Player: {player} | Line: {point}")
            #print(f"  Over: {[o['bookmaker'] + '@' + str(o['price']) for o in sides['Over']]}")
            #print(f"  Under: {[u['bookmaker'] + '@' + str(u['price']) for u in sides['Under']]}")

            for over in sides["Over"]:
                for under in sides["Under"]:
                    if over["bookmaker"] == under["bookmaker"]:
                        continue

                    is_arb, profit = calculate_arbitrage(over["price"], under["price"])
                    if is_arb:
                       # print(f"✅ ARB FOUND: {player} - {over['price']} vs {under['price']} ({profit}%)")
                        opportunities.append({
                            "type": market_key,
                            "event": event,
                            "commence_time": commence_time,
                            "player": player,
                            "line": point,
                            "side_1": {
                                "name": "Over",
                                "bookmaker": over["bookmaker"],
                                "price": over["price"]
                            },
                            "side_2": {
                                "name": "Under",
                                "bookmaker": under["bookmaker"],
                                "price": under["price"]
                            },
                            "profit_percent": profit
                        })

  #  print(f"[DEBUG] Found {len(opportunities)} arbitrage opportunities.")
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
