import os
import json

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from django.conf import settings
from server.settings import GEMINI_KEY
import re
from decouple import config

from balldontlie import BalldontlieAPI

api = BalldontlieAPI(api_key=config('BALLDONTLIE_API_KEY'))


def fetch_player_season_stats(player_id):
    try:
        # Fetch player information
        player_response = api.nba.players.get(player_id)
        player = player_response.data

        # Fetch player season averages for 2024-2025 season
        season_averages_response = api.nba.season_averages.get(2024, player_id)
        season_stats = season_averages_response.data

        if not player:
            return None

        # Format player information and stats
        player_info = {
            "name": f"{player.first_name} {player.last_name}",
            "position": player.position,
            "team": player.team.full_name if player.team else "N/A",
            "height": player.height,
            "weight": player.weight,
            "jersey_number": player.jersey_number,
        }

        # Add season stats if available
        if season_stats and len(season_stats) > 0:
            stats = season_stats[0]
            player_info["stats"] = {
                "type": "season",
                "season": "2024-2025",
                "games_played": stats.games_played,
                "points": stats.pts,
                "rebounds": stats.reb,
                "assists": stats.ast,
                "steals": stats.stl,
                "blocks": stats.blk,
                "minutes": stats.min,
                "fg_percentage": f"{stats.fg_pct * 100:.1f}%" if stats.fg_pct else "N/A",
                "three_pt_percentage": f"{stats.fg3_pct * 100:.1f}%" if stats.fg3_pct else "N/A",
                "ft_percentage": f"{stats.ft_pct * 100:.1f}%" if stats.ft_pct else "N/A",
            }
        else:
            player_info["stats"] = "No season stats available for 2024-2025"

        return player_info
    except Exception as e:
        print(f"Error fetching player season stats: {str(e)}")
        return None


def fetch_player_game_stats(player_id):
    try:
        # Fetch player information
        player_response = api.nba.players.get(player_id)
        player = player_response.data

        if not player:
            return None

        # Format player information
        player_info = {
            "name": f"{player.first_name} {player.last_name}",
            "position": player.position,
            "team": player.team.full_name if player.team else "N/A",
            "height": player.height,
            "weight": player.weight,
            "jersey_number": player.jersey_number,
        }

        try:
            # Fetch recent games stats (last 5 games)
            # Note: This is a simplified example. In a real implementation, 
            # you would fetch actual game stats from the API
            player_info["stats"] = {
                "type": "game",
                "games": [
                    {
                        "date": "2024-11-01",
                        "opponent": "Team A",
                        "points": 22,
                        "rebounds": 5,
                        "assists": 4,
                        "minutes": "32:15"
                    },
                    {
                        "date": "2024-10-28",
                        "opponent": "Team B",
                        "points": 18,
                        "rebounds": 7,
                        "assists": 6,
                        "minutes": "30:42"
                    },
                    {
                        "date": "2024-10-25",
                        "opponent": "Team C",
                        "points": 25,
                        "rebounds": 4,
                        "assists": 3,
                        "minutes": "35:10"
                    }
                ]
            }
        except Exception as e:
            player_info["stats"] = "No recent game stats available"
            print(f"Error fetching game stats: {str(e)}")

        return player_info
    except Exception as e:
        print(f"Error fetching player game stats: {str(e)}")
        return None


def search_player_by_name(player_name):
    try:
        # Search for players by name
        # The balldontlieAPI likely has a method to search players
        # We'll use a common pattern for REST APIs
        search_response = api.nba.players.all(search=player_name, per_page=5)
        players = search_response.data

        if not players:
            return None

        # Return a list of players with their IDs and names
        player_list = []
        for player in players:
            player_list.append({
                "id": player.id,
                "name": f"{player.first_name} {player.last_name}",
                "team": player.team.full_name if player.team else "N/A",
                "position": player.position
            })

        return player_list
    except Exception as e:
        print(f"Error searching for player: {str(e)}")
        return None


def fetch_player_stats(player_id, stats_type='season'):
    if stats_type == 'game':
        return fetch_player_game_stats(player_id)
    else:
        return fetch_player_season_stats(player_id)


# # Path to context file (adjust as needed)
# CONTEXT_FILE = os.path.join(os.path.dirname(__file__), "context_data", "faq.txt")
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=1)


def fetch_odds_data(sport):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    params = {
        "apiKey": settings.API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch odds. Status code: {response.status_code}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


# system_context = load_context()

# Configure the GenAI API key
genai.configure(api_key=GEMINI_KEY)

# Create global chat session object
chat_session = genai.GenerativeModel("gemini-1.5-flash").start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                """Your primary role is to provide accurate, concise, and actionable advice regarding this app's features, tools, 
                and topics, such as finding value in betting odds, minimizing risks, and tracking results effectively. 
                Assume the user is talking about NBA first. When asked about a specific player, provide their stats and 
                odds for the whole current season by default. 
                If the user asks about a specific game, provide the odds and stats for that game. If the user asks about a 
                specific betting strategy, provide a brief overview. 
                Assume the user is talking about the most current game first.
                Assume you are always being asked about the 2024-2025 season.
                Always keep responses brief, to the point, and aligned with the needs of the user interacting with this app. 
                If you are unsure about a query or it falls outside this domain, politely suggest the user narrow down their 
                question to sports betting or this app's features.
                Keep the first response short and general to encourage further questions."""
            ]
        }
    ]
)


# gemini_view function is used to handle requests to the Gemini API such as odds and statistics
@csrf_exempt
def gemini_view(request, players=None, player_name=None):
    if request.method == 'GET':
        try:
            user_message = request.GET.get("message", "").strip()
            prompt_type = request.GET.get("prompt_type", "").strip()

            # Return premade prompts if no message and no prompt type
            if not user_message and not prompt_type:
                prompts = [
                    {"id": "betting_advice", "text": "1. Do you want betting advice?"},
                    {"id": "team_odds", "text": "2. Do you want info on team odds?"},
                    {"id": "player_stats", "text": "3. Do you want player stats?"}
                ]
                return JsonResponse({"response": "How can I help you win big?!", "prompts": prompts})

            if not chat_session:
                return JsonResponse({"response": "Chat session could not be initialized. Please try again later."},
                                    status=500)

            # Handle premade prompt selections
            if prompt_type:
                if prompt_type == "betting_advice":
                    # Generate betting advice using Gemini
                    response = chat_session.send_message(
                        "Give me 5 concise, actionable tips for NBA sports betting that would help a beginner make smarter bets. Format as a numbered list.")
                    return JsonResponse({"response": response.text})

                elif prompt_type == "team_odds":
                    # Fetch and format team odds
                    sport = "basketball_nba"  # Default sport
                    odds_data = fetch_odds_data(sport)
                    if "error" in odds_data:
                        return JsonResponse({"response": odds_data["error"]}, status=500)

                    # Format the odds data as an HTML table
                    table_rows = [
                        f"<tr><td>{game['home_team']}</td><td>{game['away_team']}</td><td>{game['bookmakers'][0]['markets'][0]['outcomes'][0]['price']}</td><td>{game['bookmakers'][0]['markets'][0]['outcomes'][1]['price']}</td></tr>"
                        for game in odds_data[:5]  # Limit to top 5 games
                    ]
                    table_html = (
                            "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left;'>"
                            "<thead><tr><th>Home Team</th><th>Away Team</th><th>Home Odds</th><th>Away Odds</th></tr></thead>"
                            "<tbody>" + "".join(table_rows) + "</tbody></table>"
                    )
                    return JsonResponse({"response": "Here are the current NBA team odds:", "data": table_html})

                elif prompt_type == "player_stats":
                    # Return sub-prompts for player stats
                    prompts = [
                        {"id": "season_stats", "text": "a) Season stats"},
                        {"id": "game_stats", "text": "b) Game stats"}
                    ]
                    return JsonResponse({
                        "response": "What type of player stats would you like to see?",
                        "prompts": prompts
                    })

                elif prompt_type == "season_stats":
                    # Ask user to specify a player for season stats
                    # Store the stat type in the session
                    request.session = request.session or {}
                    request.session['stats_type'] = 'season'
                    return JsonResponse({
                        "response": "Please enter a player's name by typing 'player' followed by their first and last name. For example: 'player LeBron James'",
                    })

                elif prompt_type == "game_stats":
                    # Ask user to specify a player for game stats
                    # Store the stat type in the session
                    request.session = request.session or {}
                    request.session['stats_type'] = 'game'
                    return JsonResponse({
                        "response": "Please enter a player's name by typing 'player' followed by their first and last name. For example: 'player Stephen Curry'",
                        "info": "Game stats will show the player's performance in recent games."
                    })

            # Handle regular text messages
            # Check if the user is asking about odds
            if re.search(r"\bodds\b", user_message, re.IGNORECASE):
                sport = "basketball_nba"  # Default sport; you can extract this from the user message
                odds_data = fetch_odds_data(sport)
                if "error" in odds_data:
                    return JsonResponse({"response": odds_data["error"]}, status=500)

                # Format the odds data as an HTML table
                table_rows = [
                    f"<tr><td>{game['home_team']}</td><td>{game['away_team']}</td><td>{game['bookmakers'][0]['markets'][0]['outcomes'][0]['price']}</td><td>{game['bookmakers'][0]['markets'][0]['outcomes'][1]['price']}</td></tr>"
                    for game in odds_data[:5]  # Limit to top 5 games
                ]
                table_html = (
                        "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left;'>"
                        "<thead><tr><th>Home Team</th><th>Away Team</th><th>Home Odds</th><th>Away Odds</th></tr></thead>"
                        "<tbody>" + "".join(table_rows) + "</tbody></table>"
                )
                return JsonResponse({"response": table_html})

            # Check if the user is asking about player stats by first and last name
            player_name_match = re.search(r"\bplayer\s+([A-Za-z]+)\s+([A-Za-z]+)\b", user_message, re.IGNORECASE)

            # Get stats type from session if available
            stats_type = 'base'
            if hasattr(request, 'session') and request.session and 'stats_type' in request.session:
                stats_type = request.session['stats_type']

            if player_name_match:
                player_first_name = player_name_match.group(1).strip()
                player_last_name = player_name_match.group(2).strip()
                player_name = f"{player_first_name} {player_last_name}"

                # Search for players by name
                players = search_player_by_name(player_name)
                if players and len(players) > 0:
                    if len(players) == 1:
                        # If only one player found, show their stats
                        player_id = players[0]['id']

                        # Default to season stats if not specified
                        if stats_type == 'base':
                            stats_type = 'season'

                        # Fetch player stats
                        player_info = fetch_player_stats(player_id, stats_type)

                        if player_info:
                            # Initialize HTML output
                            player_html = f"<h3>{player_info['name']}</h3>"
                            player_html += f"<p>Position: {player_info['position']}<br>"
                            player_html += f"Team: {player_info['team']}<br>"
                            player_html += f"Height: {player_info['height']}<br>"
                            player_html += f"Weight: {player_info['weight']}<br>"
                            player_html += f"Jersey: {player_info['jersey_number']}</p>"

                            if isinstance(player_info['stats'], dict):
                                if player_info['stats']['type'] == 'season':
                                    # Display season stats
                                    player_html += "<h4>2024-2025 Season Stats</h4>"
                                    player_html += "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left;'>"
                                    player_html += "<tr><th>Stat</th><th>Value</th></tr>"
                                    player_html += f"<tr><td>Games Played</td><td>{player_info['stats']['games_played']}</td></tr>"
                                    player_html += f"<tr><td>Points</td><td>{player_info['stats']['points']}</td></tr>"
                                    player_html += f"<tr><td>Rebounds</td><td>{player_info['stats']['rebounds']}</td></tr>"
                                    player_html += f"<tr><td>Assists</td><td>{player_info['stats']['assists']}</td></tr>"
                                    player_html += f"<tr><td>Steals</td><td>{player_info['stats']['steals']}</td></tr>"
                                    player_html += f"<tr><td>Blocks</td><td>{player_info['stats']['blocks']}</td></tr>"
                                    player_html += f"<tr><td>Minutes</td><td>{player_info['stats']['minutes']}</td></tr>"
                                    player_html += f"<tr><td>FG%</td><td>{player_info['stats']['fg_percentage']}</td></tr>"
                                    player_html += f"<tr><td>3PT%</td><td>{player_info['stats']['three_pt_percentage']}</td></tr>"
                                    player_html += f"<tr><td>FT%</td><td>{player_info['stats']['ft_percentage']}</td></tr>"
                                    player_html += "</table>"
                                elif player_info['stats']['type'] == 'game':
                                    # Display game stats
                                    player_html += "<h4>Recent Game Stats</h4>"
                                    player_html += "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left;'>"
                                    player_html += "<tr><th>Date</th><th>Opponent</th><th>Points</th><th>Rebounds</th><th>Assists</th><th>Minutes</th></tr>"

                                    for game in player_info['stats']['games']:
                                        player_html += f"<tr><td>{game['date']}</td><td>{game['opponent']}</td><td>{game['points']}</td><td>{game['rebounds']}</td><td>{game['assists']}</td><td>{game['minutes']}</td></tr>"

                                    player_html += "</table>"
                            else:
                                player_html += f"<p>{player_info['stats']}</p>"

                            return JsonResponse({"response": player_html})
                        else:
                            return JsonResponse({"response": f"Could not fetch stats for player {player_name}."})
                    else:
                        # If multiple players found, show a list to choose from
                        player_html = "<h3>Multiple players found. Please select one:</h3>"
                        player_html += "<ul>"
                        for player in players:
                            player_html += f"<li><a href='#' onclick='selectPlayer({player['id']})' style='color: blue; text-decoration: underline; cursor: pointer;'>{player['name']} ({player['team']}, {player['position']})</a></li>"
                        player_html += "</ul>"
                        player_html += "<script>function selectPlayer(id) { document.getElementById('chat-input').value = 'player ' + id; document.getElementById('send-button').click(); }</script>"

                        return JsonResponse({"response": player_html})
                else:
                    return JsonResponse({"response": f"Could not find any players matching '{player_name}'."})

            # Check if the user is asking about player stats by ID
            player_id_match = re.search(r"\bplayer\s+(\d+)\b", user_message, re.IGNORECASE)
            if player_id_match:
                player_id = int(player_id_match.group(1))

                # Get stats type from session if available
                stats_type = 'season'  # Default to season stats
                if hasattr(request, 'session') and request.session and 'stats_type' in request.session:
                    stats_type = request.session['stats_type']

                if players and len(players) > 0:
                    if len(players) == 1:
                        # If only one player found, show their stats
                        player_id = players[0]['id']

                        # Get stats type from session if available
                        stats_type = 'season'  # Default to season stats
                        if hasattr(request, 'session') and request.session and 'stats_type' in request.session:
                            stats_type = request.session['stats_type']

                        player_info = fetch_player_stats(player_id, stats_type)

                        if player_info:
                            # Format player info as HTML (same as above)
                            player_html = f"<h3>{player_info['name']}</h3>"
                            player_html += f"<p>Position: {player_info['position']}<br>"
                            player_html += f"Team: {player_info['team']}<br>"
                            player_html += f"Height: {player_info['height']}<br>"
                            player_html += f"Weight: {player_info['weight']}<br>"
                            player_html += f"Jersey: {player_info['jersey_number']}</p>"

                            if isinstance(player_info['stats'], dict):
                                if player_info['stats']['type'] == 'season':
                                    # Display season stats
                                    player_html += "<h4>2024-2025 Season Stats</h4>"
                                    player_html += "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left;'>"
                                    player_html += "<tr><th>Stat</th><th>Value</th></tr>"
                                    player_html += f"<tr><td>Games Played</td><td>{player_info['stats']['games_played']}</td></tr>"
                                    player_html += f"<tr><td>Points</td><td>{player_info['stats']['points']}</td></tr>"
                                    player_html += f"<tr><td>Rebounds</td><td>{player_info['stats']['rebounds']}</td></tr>"
                                    player_html += f"<tr><td>Assists</td><td>{player_info['stats']['assists']}</td></tr>"
                                    player_html += f"<tr><td>Steals</td><td>{player_info['stats']['steals']}</td></tr>"
                                    player_html += f"<tr><td>Blocks</td><td>{player_info['stats']['blocks']}</td></tr>"
                                    player_html += f"<tr><td>Minutes</td><td>{player_info['stats']['minutes']}</td></tr>"
                                    player_html += f"<tr><td>FG%</td><td>{player_info['stats']['fg_percentage']}</td></tr>"
                                    player_html += f"<tr><td>3PT%</td><td>{player_info['stats']['three_pt_percentage']}</td></tr>"
                                    player_html += f"<tr><td>FT%</td><td>{player_info['stats']['ft_percentage']}</td></tr>"
                                    player_html += "</table>"
                                elif player_info['stats']['type'] == 'game':
                                    # Display game stats
                                    player_html += "<h4>Recent Game Stats</h4>"
                                    player_html += "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left;'>"
                                    player_html += "<tr><th>Date</th><th>Opponent</th><th>Points</th><th>Rebounds</th><th>Assists</th><th>Minutes</th></tr>"

                                    for game in player_info['stats']['games']:
                                        player_html += f"<tr><td>{game['date']}</td><td>{game['opponent']}</td><td>{game['points']}</td><td>{game['rebounds']}</td><td>{game['assists']}</td><td>{game['minutes']}</td></tr>"

                                    player_html += "</table>"
                            else:
                                player_html += f"<p>{player_info['stats']}</p>"

                            return JsonResponse({"response": player_html})
                    else:
                        # If multiple players found, show a list to choose from
                        player_html = "<h3>Multiple players found. Please select one:</h3>"
                        player_html += "<ul>"
                        for player in players:
                            player_html += f"<li><a href='#' onclick='selectPlayer({player['id']})' style='color: blue; text-decoration: underline; cursor: pointer;'>{player['name']} ({player['team']}, {player['position']})</a></li>"
                        player_html += "</ul>"
                        player_html += "<script>function selectPlayer(id) { document.getElementById('chat-input').value = 'player ' + id; document.getElementById('send-button').click(); }</script>"

                        return JsonResponse({"response": player_html})
                else:
                    return JsonResponse({"response": f"Could not find any players matching '{player_name}'."})

            # Default behavior: Use Gemini API for other queries
            response = chat_session.send_message(user_message)
            return JsonResponse({"response": response.text})

        except Exception as e:
            return JsonResponse({"response": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"response": "Invalid request method"}, status=400)
