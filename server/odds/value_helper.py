from .utils.view_helpers import fetch_odds_data
from .arbitrage.value_detection import find_value_bets  # Or wherever you defined it

def get_live_value_bets():
    try:
        games = fetch_odds_data(sport="basketball_nba")  # Change if we need sports to be swappable
        value_bets = find_value_bets(games)
        return value_bets
    except Exception as e:
        return []
