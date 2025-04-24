from .arbitrage.value_detection import value_bet_opportunities
from .utils.view_helpers import parse_event_odds


def get_live_value_bets():
    try:
        games = parse_event_odds(
            sport="basketball_nba"
        )  # Change if we need sports to be swappable
        value_bets = value_bet_opportunities(games)
        return value_bets
    except Exception as e:
        return []
