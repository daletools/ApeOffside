# Repacks JSON data from endpoint as per-player rather than per-bookmaker
def parse_event_odds(full_data):
    parsed_data = {
        "id": full_data["id"],
        "sport_key": full_data["sport_key"],
        "sport_title": full_data["sport_title"],
        "commence_time": full_data["commence_time"],
        "home_team": full_data["home_team"],
        "away_team": full_data["away_team"],
        "market": full_data["bookmakers"][0]["markets"][0]["key"],
        "bookmaker": {},
        "player": {},
    }

    for bookmaker in full_data["bookmakers"]:
        # Bookmakers and their last update time are listed under the 'bookmaker' top level key
        parsed_data["bookmaker"][bookmaker["key"]] = {
            "title": bookmaker["title"],
            "last_update": bookmaker["markets"][0]["last_update"],
        }

        # Each player in 'player' has a list of each bookmaker that carries odds for them
        # Under each bookmaker within the player, the Over/Under price and point values are recorded
        for outcome in bookmaker["markets"][0]["outcomes"]:
            if outcome["description"] not in parsed_data["player"]:
                parsed_data["player"][outcome["description"]] = {}

            if bookmaker["title"] not in parsed_data["player"][outcome["description"]]:
                parsed_data["player"][outcome["description"]][bookmaker["title"]] = {}

            curr = parsed_data["player"][outcome["description"]][bookmaker["title"]]

            curr[outcome["name"]] = {
                "price": outcome["price"],
                "point": outcome["point"],
                "link": outcome["link"],
            }

    return parsed_data


# Example player JSON
# "player": {
#  "Miles Bridges": {
#    "DraftKings": {
#      "Under": {
#        "price": 1.8,
#        "point": 21.5
#      },
#      "Over": {
#        "price": 1.95,
#        "point": 21.5
#      }
#    },
#    "FanDuel": {
#      "Over": {
#        "price": 1.9,
#        "point": 20.5
#      },
#      "Under": {
#        "price": 1.87,
#        "point": 20.5
#      }
#    }
#  }
# }
