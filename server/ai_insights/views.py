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
                "You are an intelligent assistant specialized in sports betting and arbitrage. "
                "Only answer questions related to this app or those topics. Be brief and direct."
            ]
        }
    ]
)

@csrf_exempt  # Disable CSRF for simplicity; for production, use CSRF tokens
def gemini_view(request):
    if request.method == 'GET':
        try:
            # Retrieve the user message from query parameters
            user_message = request.GET.get("message")

            # Validate if the message is provided
            if not user_message:
                return JsonResponse({"response": "Message parameter is missing."}, status=400)

            # Send message to Gemini chat session
            response = chat_session.send_message(user_message)

            # Return bot reply
            return JsonResponse({"response": response.text})

        except Exception as e:
            return JsonResponse({"response": f"An error occurred: {str(e)}"}, status=500)

    # For invalid methods
    return JsonResponse({"response": "Invalid request method"}, status=400)
