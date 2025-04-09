import requests

API_KEY = ""  # 🔁 Replace with your actual Odds API key
SPORT = "basketball_nba"
MARKET = "player_points"
events_url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/events/"
events_params = {"apiKey": API_KEY}
events_response = requests.get(events_url, params=events_params)

if events_response.status_code != 200:
    print("❌ Error fetching events:", events_response.text)
else:
    events = events_response.json()
    print(f"Found {len(events)} events. Checking each for player prop odds...\n")

    for event in events[:10]:  # Check first 10 events
        event_id = event["id"]
        odds_url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/events/{event_id}/odds/"
        odds_params = {
            "apiKey": API_KEY,
            "markets": MARKET,
            "regions": "us",
            "oddsFormat": "decimal"
        }

        odds_response = requests.get(odds_url, params=odds_params)
        if odds_response.status_code == 200:
            data = odds_response.json()
            if data.get("bookmakers"):
                print(f"✅ FOUND for: {event['home_team']} vs {event['away_team']}")
                print(data)
                break  # stop after the first one found
            else:
                print(f"🔍 No player props for {event['home_team']} vs {event['away_team']}")
        else:
            print(f"❌ Failed to fetch odds for {event['id']}: {odds_response.text}")