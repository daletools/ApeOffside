import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types


#@csrf_exempt  # Disable CSRF for simplicity; for production, use CSRF tokens
def chatbot_view(request):
    if request.method == 'GET':
        try:
            # Retrieve the user message from query parameters
            user_message = request.GET.get("message")

            # Validate if the message is provided
            if not user_message:
                return JsonResponse({"response": "Message parameter is missing."}, status=400)

            # Retrieve API key from environment
            api_key = os.environ.get("GEMINI_API_KEY")

            # Validate API key
            if not api_key:
                return JsonResponse({"response": "API key is missing or invalid."}, status=500)

            # Initialize Google GenAI client
            client = genai.Client(api_key=api_key)

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
                return JsonResponse({"response": bot_response})
            except Exception as e:
                return JsonResponse({"response": f"Gemini API error: {str(e)}"}, status=500)

            # Return the chatbot's response

        except Exception as e:
            # Handle errors and return to the frontend
            return JsonResponse({"response": f"An error occurred: {str(e)}"}, status=500)

    # For invalid methods
    return JsonResponse({"response": "Invalid request method"}, status=400)
