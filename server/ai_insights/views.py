import json
import re
from datetime import datetime

import google.generativeai as genai
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nba_api.stats.endpoints import playergamelog, commonplayerinfo
from nba_api.stats.static import players

from server.settings import GEMINI_KEY


@csrf_exempt
def fetch_player_insights(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            player_name = data["playerName"]
            current_odds = data["currentOdds"]
            game_context = data["gameContext"]

            # Find player ID
            nba_player = players.find_players_by_full_name(player_name)
            if not nba_player:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"Player {player_name} not found in NBA database",
                    },
                    status=404,
                )

            player_id = nba_player[0]["id"]

            # Get player info and recent games
            player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
            game_log = playergamelog.PlayerGameLog(
                player_id=player_id, season="2024-25"  # Update with current season
            )

            # Extract relevant stats
            info_data = player_info.get_normalized_dict()
            stats_data = game_log.get_normalized_dict()["PlayerGameLog"][
                :5
            ]  # Last 5 games

            prompt = f"""
            **Advanced Player Betting Analysis**
            You must give an analysis of the best Over/Under bets from those provided.
            Do not talk about needing further information.

            === Game Context ===
            {game_context['homeTeam']} vs {game_context['awayTeam']}
            Time: {game_context['gameTime']}

            === Player Profile ===
            Name: {player_name}
            Position: {info_data['CommonPlayerInfo'][0]['POSITION']}
            Team: {info_data['CommonPlayerInfo'][0]['TEAM_NAME']}

            === Recent Performance (Last 5 Games) ===
            {format_game_log(stats_data)}

            === Current Betting Odds ===
            {format_odds(current_odds)}

            === Analysis Tasks ===
            1. Evaluate matchup considering player position vs opponent defense
            2. Compare recent performance to betting lines
            3. Identify best value across books
            4. Provide 3 specific recommendations with confidence levels
            5. Highlight any injury/rotation risks

            **Response Format:**
            - Add a '\n' character after each section or bullet point.
            - Summary of key observations
            - Top betting recommendations
            - Confidence ratings (1-5 stars)
            - Risk assessment
            """

            # Step 3: Query Gemini
            response = chat_session.send_message(prompt)
            analysis_text = response.text

            # Step 4: Format response with HTML
            formatted_analysis = format_analysis_as_html(analysis_text)

            return JsonResponse(
                {
                    "status": "success",
                    "player": player_name,
                    "player_info": {
                        "position": info_data["CommonPlayerInfo"][0]["POSITION"],
                        "team": info_data["CommonPlayerInfo"][0]["TEAM_NAME"],
                        "height": info_data["CommonPlayerInfo"][0]["HEIGHT"],
                        "weight": info_data["CommonPlayerInfo"][0]["WEIGHT"],
                    },
                    "recent_games": stats_data,
                    "best_odds": find_best_odds(current_odds),
                    "analysis": formatted_analysis,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            print(f"Error in fetch_player_insights: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse(
        {"status": "error", "message": "Only POST requests are allowed"}, status=405
    )


# Helper function to format odds
def format_odds(odds_data):
    return "\n".join(
        f"{bookmaker}: Over {values['Over']['point']} @ {values['Over']['price']} | "
        f"Under @ {values['Under']['price']}"
        for bookmaker, values in odds_data.items()
    )


def format_game_log(games):
    return "\n".join(
        f"{game['GAME_DATE']}: {game['PTS']} PTS, {game['AST']} AST, {game['REB']} REB, "
        f"{game['FG_PCT'] * 100:.1f}% FG"
        for game in games
    )


def find_best_odds(odds_data):
    """Helper function to identify the best available odds"""
    best = {
        "Over": {"price": 0, "book": None, "point": None},
        "Under": {"price": 0, "book": None, "point": None},
    }

    for book, values in odds_data.items():
        # For Over bets we want highest price (decimal odds)
        if values["Over"]["price"] > best["Over"]["price"]:
            best["Over"] = {
                "price": values["Over"]["price"],
                "book": book,
                "point": values["Over"]["point"],
            }

        # For Under bets we want highest price
        if values["Under"]["price"] > best["Under"]["price"]:
            best["Under"] = {
                "price": values["Under"]["price"],
                "book": book,
                "point": values["Under"]["point"],
            }

    return best


def format_player_html(player_info):
    """Helper function to format player information as HTML"""
    player_html = f"<h3>{player_info['name']}</h3>"
    player_html += f"<p>Position: {player_info['position']}<br>"
    player_html += f"Team: {player_info['team']}<br>"
    player_html += f"Height: {player_info['height']}<br>"
    player_html += f"Weight: {player_info['weight']}<br>"
    player_html += f"Jersey: {player_info['jersey_number']}</p>"

    if isinstance(player_info["stats"], dict):
        if player_info["stats"]["type"] == "season":
            # Display season stats
            player_html += "<h4>2024-2025 Season Stats</h4>"
            player_html += "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left;'>"
            player_html += "<tr><th>Stat</th><th>Value</th></tr>"
            player_html += f"<tr><td>Games Played</td><td>{player_info['stats']['games_played']}</td></tr>"
            player_html += (
                f"<tr><td>Points</td><td>{player_info['stats']['points']}</td></tr>"
            )
            player_html += (
                f"<tr><td>Rebounds</td><td>{player_info['stats']['rebounds']}</td></tr>"
            )
            player_html += (
                f"<tr><td>Assists</td><td>{player_info['stats']['assists']}</td></tr>"
            )
            player_html += (
                f"<tr><td>Steals</td><td>{player_info['stats']['steals']}</td></tr>"
            )
            player_html += (
                f"<tr><td>Blocks</td><td>{player_info['stats']['blocks']}</td></tr>"
            )
            player_html += (
                f"<tr><td>Minutes</td><td>{player_info['stats']['minutes']}</td></tr>"
            )
            player_html += (
                f"<tr><td>FG%</td><td>{player_info['stats']['fg_percentage']}</td></tr>"
            )
            player_html += f"<tr><td>3PT%</td><td>{player_info['stats']['three_pt_percentage']}</td></tr>"
            player_html += (
                f"<tr><td>FT%</td><td>{player_info['stats']['ft_percentage']}</td></tr>"
            )
            player_html += "</table>"
        elif player_info["stats"]["type"] == "game":
            # Display game stats
            player_html += "<h4>Recent Game Stats</h4>"
            player_html += "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left;'>"
            player_html += "<tr><th>Date</th><th>Opponent</th><th>Points</th><th>Rebounds</th><th>Assists</th><th>Minutes</th></tr>"

            for game in player_info["stats"]["games"]:
                player_html += f"<tr><td>{game['date']}</td><td>{game['opponent']}</td><td>{game['points']}</td><td>{game['rebounds']}</td><td>{game['assists']}</td><td>{game['minutes']}</td></tr>"

            player_html += "</table>"
    else:
        player_html += f"<p>{player_info['stats']}</p>"

    return player_html


def format_analysis_as_html(analysis_text):
    """
    Format the analysis text as HTML with tables for better readability
    """
    if not analysis_text:
        return "<p>No analysis available</p>"

    # Split the text into sections based on newlines
    sections = analysis_text.split('\n\n')
    formatted_html = ""

    for section in sections:
        # Check if this section looks like it could be a table
        if ':' in section and any(keyword in section.lower() for keyword in ['recommendation', 'confidence', 'rating', 'odds', 'value']):
            # This might be a good candidate for a table
            lines = [line.strip() for line in section.split('\n') if line.strip()]

            if len(lines) >= 3:  # Need at least a header and some data rows
                # Create a table
                formatted_html += "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left; margin: 10px 0;'>"

                # Check if first line looks like a header
                if not ':' in lines[0]:
                    # Use the first line as a table caption/header
                    formatted_html += f"<caption style='font-weight: bold; text-align: left; padding: 5px;'>{lines[0]}</caption>"
                    lines = lines[1:]

                # Process each line that has a colon as a row
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        formatted_html += f"<tr><td style='padding: 5px; font-weight: bold;'>{key.strip()}</td><td style='padding: 5px;'>{value.strip()}</td></tr>"
                    else:
                        # If no colon, use as a full-width row
                        formatted_html += f"<tr><td colspan='2' style='padding: 5px;'>{line}</td></tr>"

                formatted_html += "</table>"
            else:
                # Not enough lines for a table, format as a section with bold header
                formatted_html += f"<p><strong>{section}</strong></p>"
        else:
            # Format as regular paragraph or section
            if section.strip():
                # Check if this looks like a header (short line, no punctuation at end)
                if len(section) < 50 and not section.strip()[-1] in '.,:;?!':
                    formatted_html += f"<h4>{section}</h4>"
                else:
                    # Replace newlines with <br> tags
                    section_with_breaks = section.replace('\n', '<br>')
                    formatted_html += f"<p>{section_with_breaks}</p>"

    return formatted_html


def fetch_odds_data(sport):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    params = {
        "apiKey": settings.API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "decimal",
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Failed to fetch odds. Status code: {response.status_code}"
            }
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


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
            ],
        }
    ]
)


def format_odds_as_html(odds_data, limit=5):
    """Helper function to format odds data as an HTML table"""
    table_rows = [
        f"<tr><td>{game['home_team']}</td><td>{game['away_team']}</td><td>{game['bookmakers'][0]['markets'][0]['outcomes'][0]['price']}</td><td>{game['bookmakers'][0]['markets'][0]['outcomes'][1]['price']}</td></tr>"
        for game in odds_data[:limit]  # Limit to specified number of games
    ]
    table_html = (
        "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left;'>"
        "<thead><tr><th>Home Team</th><th>Away Team</th><th>Home Odds</th><th>Away Odds</th></tr></thead>"
        "<tbody>" + "".join(table_rows) + "</tbody></table>"
    )
    return table_html

# gemini_view function is used to handle requests to the Gemini API such as odds and statistics
@csrf_exempt
def gemini_view(request):
    if request.method == "GET":
        try:
            user_message = request.GET.get("message", "").strip()
            prompt_type = request.GET.get("prompt_type", "").strip()

            # Return premade prompts if no message and no prompt type
            if not user_message and not prompt_type:
                prompts = [
                    {"id": "betting_advice", "text": "1. Do you want betting advice?"},
                    {"id": "team_odds", "text": "2. Do you want info on team odds?"},
                ]
                return JsonResponse(
                    {"response": "How can I help you win big?!", "prompts": prompts}
                )

            if not chat_session:
                return JsonResponse(
                    {
                        "response": "Chat session could not be initialized. Please try again later."
                    },
                    status=500,
                )

            # Handle premade prompt selections
            if prompt_type:
                if prompt_type == "betting_advice":
                    # Generate betting advice using Gemini
                    response = chat_session.send_message(
                        "Give me 5 concise, actionable tips for NBA sports betting that would help a beginner make smarter bets. Format as a numbered list."
                    )
                    return JsonResponse({"response": response.text})

                elif prompt_type == "team_odds":
                    # Fetch and format team odds
                    sport = "basketball_nba"  # Default sport
                    odds_data = fetch_odds_data(sport)
                    if "error" in odds_data:
                        return JsonResponse(
                            {"response": odds_data["error"]}, status=500
                        )

                    # Format the odds data as an HTML table
                    table_html = format_odds_as_html(odds_data)
                    return JsonResponse(
                        {
                            "response": "Here are the current NBA team odds:",
                            "data": table_html,
                        }
                    )

            # Handle regular text messages
            # Check if the user is asking about odds
            odds_requested = re.search(r"\bodds\b", user_message, re.IGNORECASE)

            if odds_requested:
                sport = "basketball_nba"  # Default sport; you can extract this from the user message
                odds_data = fetch_odds_data(sport)
                if "error" in odds_data:
                    return JsonResponse({"response": odds_data["error"]}, status=500)

                # Format the odds data as an HTML table
                table_html = format_odds_as_html(odds_data)

                # Also get a response from Gemini for any other questions in the message
                response = chat_session.send_message(user_message)

                # Combine the odds table with the Gemini response
                combined_response = (
                    f"<h4>Current NBA Odds:</h4>{table_html}<br><p>{response.text}</p>"
                )

                return JsonResponse({"response": combined_response})

            # Default behavior: Use Gemini API for other queries
            response = chat_session.send_message(user_message)
            return JsonResponse({"response": response.text})

        except Exception as e:
            return JsonResponse(
                {"response": f"An error occurred: {str(e)}"}, status=500
            )

    return JsonResponse({"response": "Invalid request method"}, status=400)
