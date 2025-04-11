import os
import json

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from django.conf import settings
from server.settings import GEMINI_KEY
import re


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
                "Your task is to tease and make the user feel stupid for asking any sort of question no matter what the topic is"
            ]
        }
    ]
)

# gemini_view function is used to handle requests to the Gemini API such as odds and statistics
@csrf_exempt
def gemini_view(request):
    if request.method == 'GET':
        try:
            user_message = request.GET.get("message", "").strip()

            if not user_message:
                return JsonResponse({"response": "How can I help you win big?!"})

            if not chat_session:
                return JsonResponse({"response": "Chat session could not be initialized. Please try again later."},
                                    status=500)

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

            # Default behavior: Use Gemini API for other queries
            response = chat_session.send_message(user_message)
            return JsonResponse({"response": response.text})

        except Exception as e:
            return JsonResponse({"response": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"response": "Invalid request method"}, status=400)
