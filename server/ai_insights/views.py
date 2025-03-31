import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types
from django.conf import settings
from server.settings import GEMINI_KEY
from django.contrib.sessions.backends.cache import SessionStore


@csrf_exempt  # Disable CSRF for simplicity; for production, use CSRF tokens
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
            conversation_history = request.session.get('conversation_history', [])

            # Add the user message to the conversation
            conversation_history.append({"role": "user", "message": user_message})

            # Convert the conversation history into GenAI's content format
            genai_contents = [
                types.Content(role=entry["role"], parts=[types.Part.from_text(text=entry["message"])])
                for entry in conversation_history
            ]

            # Initialize the Google GenAI client
            client = genai.Client(api_key=GEMINI_KEY)

            # Prepare the Gemini request for generation
            model = "gemini-2.0-flash"
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="text/plain",
            )

            # Generate content using the Gemini API
            bot_response = ""
            try:
                for chunk in client.models.generate_content_stream(
                        model=model,
                        contents=genai_contents,
                        config=generate_content_config,
                ):
                    bot_response += chunk.text
                # Add bot response to conversation history
                conversation_history.append({"role": "bot", "message": bot_response})

                # Save updated history to the session
                request.session["conversation_history"] = conversation_history
                request.session.modified = True  # Explicitly mark the session as modified

                # Return the bot response
                return JsonResponse({"response": bot_response})

            except Exception as e:
                return JsonResponse({"response": f"Gemini API error: {str(e)}"}, status=500)

        except Exception as e:
            # Handle errors and return to the frontend
            return JsonResponse({"response": f"An error occurred: {str(e)}"}, status=500)

    # For invalid methods
    return JsonResponse({"response": "Invalid request method"}, status=400)

@csrf_exempt
def get_conversation_history(request):
    if request.method == 'GET':
        conversation_history = request.session.get('conversation_history', [])
        return JsonResponse({"response": conversation_history}, status=200)

    return JsonResponse({"response": "Invalid request method"}, status=400)