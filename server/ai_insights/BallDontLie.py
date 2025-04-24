import re

from balldontlie import BalldontlieAPI
from django.http import JsonResponse

from ai_insights.views import format_player_html, chat_session

api = BalldontlieAPI(api_key="YOUR_API_KEY")


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
                "fg_percentage": (
                    f"{stats.fg_pct * 100:.1f}%" if stats.fg_pct else "N/A"
                ),
                "three_pt_percentage": (
                    f"{stats.fg3_pct * 100:.1f}%" if stats.fg3_pct else "N/A"
                ),
                "ft_percentage": (
                    f"{stats.ft_pct * 100:.1f}%" if stats.ft_pct else "N/A"
                ),
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
                        "minutes": "32:15",
                    },
                    {
                        "date": "2024-10-28",
                        "opponent": "Team B",
                        "points": 18,
                        "rebounds": 7,
                        "assists": 6,
                        "minutes": "30:42",
                    },
                    {
                        "date": "2024-10-25",
                        "opponent": "Team C",
                        "points": 25,
                        "rebounds": 4,
                        "assists": 3,
                        "minutes": "35:10",
                    },
                ],
            }
        except Exception as e:
            player_info["stats"] = "No recent game stats available"
            print(f"Error fetching game stats: {str(e)}")

        return player_info
    except Exception as e:
        print(f"Error fetching player game stats: {str(e)}")
        return None


def fetch_player_stats(player_id, stats_type="season"):
    if stats_type == "game":
        return fetch_player_game_stats(player_id)
    else:
        return fetch_player_season_stats(player_id)


def search_player_by_name(player_name):
    pass


# This code was excised from the gemini_view when we moved away from the BallDontLie API, keeping here in case we move back.
def gemini_stats_parser(request):
    user_message = request.GET.get("message", "").strip()
    prompt_type = request.GET.get("prompt_type", "").strip()

    # Check if the user is asking about player stats by first and last name
    player_name_match = re.search(
        r"\bplayer\s+([A-Za-z]+)\s+([A-Za-z]+)\b", user_message, re.IGNORECASE
    )

    # Get stats type from session if available
    stats_type = "base"
    if (
        hasattr(request, "session")
        and request.session
        and "stats_type" in request.session
    ):
        stats_type = request.session["stats_type"]

    if player_name_match:
        player_first_name = player_name_match.group(1).strip()
        player_last_name = player_name_match.group(2).strip()
        player_name = f"{player_first_name} {player_last_name}"

        # Search for players by name
        players = search_player_by_name(player_name)
        if players and len(players) > 0:
            if len(players) == 1:
                # If only one player found, show their stats
                player_id = players[0]["id"]

                # Default to season stats if not specified
                if stats_type == "base":
                    stats_type = "season"

                # Fetch player stats
                player_info = fetch_player_stats(player_id, stats_type)

                if player_info:
                    # Format player info as HTML using helper function
                    player_html = format_player_html(player_info)

                    return JsonResponse({"response": player_html})
                else:
                    return JsonResponse(
                        {"response": f"Could not fetch stats for player {player_name}."}
                    )
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
            return JsonResponse(
                {"response": f"Could not find any players matching '{player_name}'."}
            )

    # Check if the user is asking about player stats by ID
    player_id_match = re.search(r"\bplayer\s+(\d+)\b", user_message, re.IGNORECASE)
    if player_id_match:
        player_id = int(player_id_match.group(1))

        # Get stats type from session if available
        stats_type = "season"  # Default to season stats
        if (
            hasattr(request, "session")
            and request.session
            and "stats_type" in request.session
        ):
            stats_type = request.session["stats_type"]

        # Fetch player stats directly by ID
        player_info = fetch_player_stats(player_id, stats_type)

        if player_info:
            # Format player info as HTML using helper function
            player_html = format_player_html(player_info)

            return JsonResponse({"response": player_html})
        else:
            return JsonResponse(
                {"response": f"Could not fetch stats for player ID {player_id}."}
            )

    # Check if the user is asking about a player's stats in natural language
    # Look for patterns like "What are [Player Name] stats" or "[Player Name] stats this year"
    player_stats_match = re.search(
        r"(?:what\s+are\s+|what\'s\s+|show\s+me\s+|get\s+|)([A-Za-z]+(?:\s+[A-Za-z\.]+){1,3})(?:\s+stats|\s+statistics|\s+this\s+year|\s+this\s+season)",
        user_message,
        re.IGNORECASE,
    )

    # If the first pattern doesn't match, try alternative patterns
    if not player_stats_match:
        # Look for patterns like "Tell me about [Player Name]'s stats" or "How is [Player Name] doing this season"
        player_stats_match = re.search(
            r"(?:tell\s+me\s+about|how\s+is|how\'s|info\s+on|information\s+on)\s+([A-Za-z]+(?:\s+[A-Za-z\.]+){1,3})(?:\'s)?(?:\s+stats|\s+statistics|\s+this\s+year|\s+this\s+season|\s+doing|\s+playing)",
            user_message,
            re.IGNORECASE,
        )

    # If still no match, try a more general pattern to catch any mention of a player and stats
    if not player_stats_match:
        # This pattern looks for any mention of "stats" or related terms and tries to find a name-like pattern nearby
        player_stats_match = re.search(
            r"(?:stats|statistics|numbers|performance|record).*?([A-Za-z]+(?:\s+[A-Za-z\.]+){1,3})|([A-Za-z]+(?:\s+[A-Za-z\.]+){1,3}).*?(?:stats|statistics|numbers|performance|record)",
            user_message,
            re.IGNORECASE,
        )

    if player_stats_match:
        # Handle the case where we have multiple capturing groups (from the OR pattern)
        if player_stats_match.group(1):
            potential_player_name = player_stats_match.group(1).strip()
        elif player_stats_match.lastindex > 1 and player_stats_match.group(2):
            potential_player_name = player_stats_match.group(2).strip()
        else:
            potential_player_name = player_stats_match.group(0).strip()

        # Search for players by name
        players = search_player_by_name(potential_player_name)

        if players and len(players) > 0:
            if len(players) == 1:
                # If only one player found, show their stats
                player_id = players[0]["id"]

                # Default to season stats
                stats_type = "season"
                if (
                    hasattr(request, "session")
                    and request.session
                    and "stats_type" in request.session
                ):
                    stats_type = request.session["stats_type"]

                # Fetch player stats
                player_info = fetch_player_stats(player_id, stats_type)

                if player_info:
                    # Format player info as HTML using helper function
                    player_html = format_player_html(player_info)

                    return JsonResponse({"response": player_html})
                else:
                    return JsonResponse(
                        {
                            "response": f"Could not fetch stats for player {potential_player_name}."
                        }
                    )
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
            # If no players found, fall back to Gemini API
            response = chat_session.send_message(user_message)
            return JsonResponse({"response": response.text})
    return
