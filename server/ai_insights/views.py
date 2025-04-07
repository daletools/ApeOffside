import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from django.conf import settings
from server.settings import GEMINI_KEY

# Path to context file (adjust as needed)
CONTEXT_FILE = os.path.join(os.path.dirname(__file__), "context_data", "faq.txt")


def load_context():
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as file:
            return file.read()
    except Exception:
        return ""


system_context = load_context()

# Configure the GenAI API key
genai.configure(api_key=GEMINI_KEY)

# Create global chat session object
chat_session = genai.GenerativeModel("gemini-1.5-flash").start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                "Your primary role is to provide accurate, concise, and actionable advice regarding this app's features, tools, and topics, such as finding value in betting odds, minimizing risks, and tracking results effectively. "
                "Do not engage in unrelated topics or provide information outside the scope of sports betting and arbitrage. "
                "Always keep responses brief, to the point, and aligned with the needs of the user interacting with this app. "
                "If you are unsure about a query or it falls outside this domain, politely suggest the user narrow down their question to sports betting or this app’s features."

            ]
        }
    ]
)

@csrf_exempt
def gemini_view(request):
    if request.method == 'GET':
        try:
            # Retrieve user message from query parameters
            user_message = request.GET.get("message", "").strip()

            # Validate input and provide the default prompt
            if not user_message:
                return JsonResponse({"response": "How can I help you win big?!"})

            # Forward the user's message to the chatbot
            response = chat_session.send_message(user_message)

            # Return bot reply
            return JsonResponse({"response": response.text})

        except Exception as e:
            return JsonResponse({"response": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"response": "Invalid request method"}, status=400)

