from decouple import config
from google import genai
from google.genai import types


def generate():
    # Retrieve API key from the .env file
    api_key = config("GEMINI_API_KEY")  # Automatically retrieves GEMINI_API_KEY from the .env file

    # Validate that the API key exists
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set or invalid in the .env file.")

    # Initialize Google GenAI client
    client = genai.Client(api_key=api_key)

    # Model and input setup
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""What is the home NBA team in Orlando?"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )

    # Generate content stream
    try:
        for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
        ):
            print(chunk.text, end="")
    except Exception as e:
        print(f"An error occurred during content generation: {e}")


# Print output to computer

generate()
