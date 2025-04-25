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
    """
    Fetch and analyze player insights using NBA stats and betting odds data.
    
    Args:
        request: HTTP request containing player name, current odds, and game context
        
    Returns:
        JsonResponse containing player analysis, stats, and best odds recommendations
        
    Raises:
        Exception: If there's an error processing the request or fetching data
    """
    if request.method == "POST":
        try:
            # Parse request data
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
    """Format odds data in a clean, readable format"""
    formatted_odds = []
    for bookmaker, values in odds_data.items():
        over_point = values['Over']['point']
        over_price = values['Over']['price']
        under_price = values['Under']['price']
        formatted_odds.append(
            f"{bookmaker}: Over {over_point} @ {over_price} | Under @ {under_price}"
        )
    return "\n".join(formatted_odds)


def format_game_log(games):
    """Format game log data in a clean, readable format"""
    formatted_games = []
    for game in games:
        game_date = game['GAME_DATE']
        points = game['PTS']
        assists = game['AST']
        rebounds = game['REB']
        fg_pct = game['FG_PCT'] * 100

        formatted_games.append(
            f"{game_date}: {points} PTS, {assists} AST, {rebounds} REB, {fg_pct:.1f}% FG"
        )
    return "\n".join(formatted_games)


def find_best_odds(odds_data):
    """
    Identify the best available odds for Over and Under bets

    Args:
        odds_data (dict): Dictionary containing odds data from different bookmakers

    Returns:
        dict: Dictionary containing the best odds for Over and Under bets
    """
    best = {
        "Over": {"price": 0, "book": None, "point": None},
        "Under": {"price": 0, "book": None, "point": None},
    }

    for book, values in odds_data.items():
        # For Over bets we want highest price (decimal odds)
        over_price = values["Over"]["price"]
        if over_price > best["Over"]["price"]:
            best["Over"] = {
                "price": over_price,
                "book": book,
                "point": values["Over"]["point"],
            }

        # For Under bets we want highest price
        under_price = values["Under"]["price"]
        if under_price > best["Under"]["price"]:
            best["Under"] = {
                "price": under_price,
                "book": book,
                "point": values["Under"]["point"],
            }

    return best


def format_player_html(player_info):
    """
    Format player information as HTML with consistent styling

    Args:
        player_info (dict): Dictionary containing player information and stats

    Returns:
        str: HTML-formatted player information
    """
    # Define consistent styles
    styles = {
        'container': 'font-family: Arial, sans-serif; margin: 0; padding: 0;',
        'heading': 'font-size: 20px; font-weight: bold; margin: 15px 0 10px 0; color: #333;',
        'subheading': 'font-size: 16px; font-weight: bold; margin: 12px 0 8px 0; color: #444;',
        'info': 'margin: 8px 0; line-height: 1.5;',
        'table': 'width: 100%; border-collapse: collapse; margin: 10px 0;',
        'th': 'background-color: #f2f2f2; padding: 8px; text-align: left; border: 1px solid #ddd;',
        'td': 'padding: 8px; border: 1px solid #ddd;',
    }

    # Start building the HTML with a container
    player_html = f"<div style='{styles['container']}'>"

    # Player name and basic info
    player_html += f"<h3 style='{styles['heading']}'>{player_info['name']}</h3>"
    player_html += f"<div style='{styles['info']}'>"
    player_html += f"<p>Position: {player_info['position']}<br>"
    player_html += f"Team: {player_info['team']}<br>"
    player_html += f"Height: {player_info['height']}<br>"
    player_html += f"Weight: {player_info['weight']}<br>"
    player_html += f"Jersey: {player_info['jersey_number']}</p>"
    player_html += "</div>"

    # Player stats
    if isinstance(player_info["stats"], dict):
        if player_info["stats"]["type"] == "season":
            # Season stats table
            player_html += f"<h4 style='{styles['subheading']}'>2024-2025 Season Stats</h4>"
            player_html += f"<table style='{styles['table']}'>"
            player_html += f"<tr><th style='{styles['th']}'>Stat</th><th style='{styles['th']}'>Value</th></tr>"

            # Define stats to display
            season_stats = [
                ("Games Played", "games_played"),
                ("Points", "points"),
                ("Rebounds", "rebounds"),
                ("Assists", "assists"),
                ("Steals", "steals"),
                ("Blocks", "blocks"),
                ("Minutes", "minutes"),
                ("FG%", "fg_percentage"),
                ("3PT%", "three_pt_percentage"),
                ("FT%", "ft_percentage")
            ]

            # Add each stat row
            for label, key in season_stats:
                player_html += f"<tr><td style='{styles['td']}'>{label}</td><td style='{styles['td']}'>{player_info['stats'][key]}</td></tr>"

            player_html += "</table>"

        elif player_info["stats"]["type"] == "game":
            # Game stats table
            player_html += f"<h4 style='{styles['subheading']}'>Recent Game Stats</h4>"
            player_html += f"<table style='{styles['table']}'>"
            player_html += f"<tr>"

            # Table headers
            headers = ["Date", "Opponent", "Points", "Rebounds", "Assists", "Minutes"]
            for header in headers:
                player_html += f"<th style='{styles['th']}'>{header}</th>"
            player_html += "</tr>"

            # Add each game row
            for game in player_info["stats"]["games"]:
                player_html += "<tr>"
                player_html += f"<td style='{styles['td']}'>{game['date']}</td>"
                player_html += f"<td style='{styles['td']}'>{game['opponent']}</td>"
                player_html += f"<td style='{styles['td']}'>{game['points']}</td>"
                player_html += f"<td style='{styles['td']}'>{game['rebounds']}</td>"
                player_html += f"<td style='{styles['td']}'>{game['assists']}</td>"
                player_html += f"<td style='{styles['td']}'>{game['minutes']}</td>"
                player_html += "</tr>"

            player_html += "</table>"
    else:
        # Display text stats if not in dictionary format
        player_html += f"<p style='{styles['info']}'>{player_info['stats']}</p>"

    player_html += "</div>"  # Close container
    return player_html


def format_analysis_as_html(analysis_text):
    """
    Format the analysis text as HTML with a clean, consistent structure.
    
    Args:
        analysis_text (str): Raw analysis text from Gemini API
        
    Returns:
        str: HTML-formatted analysis with consistent styling and structure
        
    Note:
        Formats text into sections with headings, tables, lists and paragraphs
        while maintaining consistent styling across all elements.
    """
    if not analysis_text:
        return "<p>No analysis available</p>"

    # Apply consistent styling
    styles = {
        'container': 'margin: 0; padding: 0; font-family: Arial, sans-serif;',
        'section': 'margin-bottom: 15px;',
        'heading': 'font-size: 18px; font-weight: bold; margin: 15px 0 10px 0; color: #333;',
        'subheading': 'font-size: 16px; font-weight: bold; margin: 12px 0 8px 0; color: #444;',
        'paragraph': 'margin: 8px 0; line-height: 1.4;',
        'list': 'margin: 8px 0; padding-left: 20px;',
        'table': 'width: 100%; border-collapse: collapse; margin: 10px 0;',
        'th': 'background-color: #f2f2f2; padding: 8px; text-align: left; border: 1px solid #ddd;',
        'td': 'padding: 8px; border: 1px solid #ddd;',
        'strong': 'font-weight: bold;'
    }

    # Process the text
    # Replace multiple newlines with a single newline to normalize spacing
    normalized_text = re.sub(r'\n{3,}', '\n\n', analysis_text)

    # Split into sections based on double newlines
    sections = normalized_text.split('\n\n')

    # Start building the HTML
    formatted_html = f"<div style='{styles['container']}'>"

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Process the section
        lines = section.split('\n')

        # Check if this section is a heading
        if len(lines) == 1 and len(lines[0]) < 50 and not lines[0][-1] in '.,:;?!':
            formatted_html += f"<h3 style='{styles['heading']}'>{lines[0]}</h3>"
            continue

        # Check if this section contains key-value pairs (contains colons)
        if any(':' in line for line in lines) and len(lines) >= 2:
            # Format as a table
            formatted_html += f"<div style='{styles['section']}'>"
            formatted_html += f"<table style='{styles['table']}'>"

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    formatted_html += f"<tr><td style='{styles['td']} {styles['strong']}'>{key.strip()}</td><td style='{styles['td']}'>{value.strip()}</td></tr>"
                else:
                    # Use as a header row if it's the first line
                    if line == lines[0] and not ':' in line:
                        formatted_html += f"<tr><th style='{styles['th']}' colspan='2'>{line}</th></tr>"
                    else:
                        formatted_html += f"<tr><td style='{styles['td']}' colspan='2'>{line}</td></tr>"

            formatted_html += "</table>"
            formatted_html += "</div>"
        else:
            # Format as a regular paragraph
            # Check for bullet points or numbered lists
            if any(line.strip().startswith(('•', '-', '*', '1.', '2.', '3.')) for line in lines):
                formatted_html += f"<ul style='{styles['list']}'>"
                for line in lines:
                    # Remove bullet point characters
                    clean_line = re.sub(r'^[•\-*]\s*|^\d+\.\s*', '', line.strip())
                    formatted_html += f"<li style='{styles['paragraph']}'>{clean_line}</li>"
                formatted_html += "</ul>"
            else:
                # Regular paragraph
                formatted_html += f"<p style='{styles['paragraph']}'>{section.replace('\n', '<br>')}</p>"

    formatted_html += "</div>"
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
    """
    Handle requests to the Gemini API for odds and statistics.

    Args:
        request: HTTP request containing message and prompt type parameters

    Returns:
        JsonResponse containing:
        - Pre-made prompts if no message/prompt provided
        - Betting advice for betting_advice prompt type
        - Team odds for team_odds prompt type
        - Custom responses for specific text queries
        
    Raises:
        Exception: If there's an error processing the request or API communication
    """
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