import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types
from django.conf import settings
from server.settings import GEMINI_KEY
from django.contrib.sessions.backends.cache import SessionStore


# @csrf_exempt  # Disable CSRF for simplicity; for production, use CSRF tokens
def gemini_view(request):
    if request.method == 'GET':
        try:
            print('Trying to retrieve user message.')

            # Retrieve the user message from query parameters
            user_message = request.GET.get("message")

            print('user_message', user_message)

            # Validate if the message is provided
            if not user_message:
                return JsonResponse({"response": "Message parameter is missing."}, status=400)

            # Validate API key
            if not GEMINI_KEY:
                return JsonResponse({"response": "API key is missing or invalid."}, status=500)

            # Initialize conversation history
            x = request.session.get('conversation_history', [])

            x.append({"role": "user", "message": user_message})

            # Prepare the conversation history for the API
            y = [
                types.Content(role=entry["role"], parts=[types.Part.from_text(text=entry["message"])])
                for entry in x
            ]

            # Initialize Google GenAI client
            client = genai.Client(api_key=GEMINI_KEY)

            # Prepare the request for the Gemini model
            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_message)],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="text/plain",
            )

            # Generate content from the Gemini API
            try:
                bot_response = ""
                for chunk in client.models.generate_content_stream(
                        model=model,
                        contents=contents,
                        config=generate_content_config,
                ):
                    bot_response += chunk.text

                    # Add chatbot response to conversation history
                    x.append({
                        "role": "bot", "message": bot_response})

                    # Save updated history in the session
                    request.session["x"] = x

                return JsonResponse({"response": bot_response})
            except Exception as e:
                return JsonResponse({"response": f"Gemini API error: {str(e)}"}, status=500)

            # Return the chatbot's response

        except Exception as e:
            # Handle errors and return to the frontend
            return JsonResponse({"response": f"An error occurred: {str(e)}"}, status=500)

    # For invalid methods
    return JsonResponse({"response": "Invalid request method"}, status=400)
