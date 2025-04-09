import os
import json

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from django.conf import settings
from server.settings import GEMINI_KEY
import re
from bs4 import BeautifulSoup
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Path to context file (adjust as needed)
CONTEXT_FILE = os.path.join(os.path.dirname(__file__), "context_data", "faq.txt")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=1)


def calculate_relevance(query, content):
    vectorizer = TfidfVectorizer().fit_transform([query, content])
    vectors = vectorizer.toarray()
    return cosine_similarity([vectors[0]], [vectors[1]])[0][0]


def perform_search_and_extract(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": settings.SEARCH_API_KEY,
        "cx": settings.SEARCH_ENGINE_ID,
        "q": query,
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return [
                {"title": "Error", "content": f"Failed to fetch search results. Status code: {response.status_code}"}]

        search_results = response.json().get("items", [])
        if not search_results:
            return [{"title": "No Results", "content": "No relevant results found for your query."}]

        extracted_content = []
        for result in search_results[:3]:  # Limit to top 3 results
            try:
                page_response = requests.get(result["link"], timeout=5)
                soup = BeautifulSoup(page_response.content, "html.parser")
                paragraphs = soup.find_all("p")
                text = " ".join([p.get_text() for p in paragraphs[:5]])  # Limit to first 5 paragraphs

                relevance = calculate_relevance(query, text)
                if relevance > 0.2:  # Adjust threshold as needed
                    extracted_content.append({"title": result["title"], "content": text, "relevance": relevance})
            except Exception as e:
                extracted_content.append({"title": result["title"], "content": f"Error extracting content: {str(e)}"})

        if not extracted_content:
            return [{"title": "No Relevant Content", "content": "No relevant content could be extracted."}]

        extracted_content.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        return extracted_content

    except Exception as e:
        return [{"title": "Error", "content": f"An error occurred: {str(e)}"}]


# Step 3: Summarize the extracted content
def summarize_content(content):
    try:
        summaries = []
        for item in content:
            input_length = len(item["content"].split())
            max_length = max(5, min(50, input_length // 2))
            min_length = max(3, min(max_length - 1, input_length // 4))

            summary = summarizer(item["content"], max_length=max_length, min_length=min_length, do_sample=False)
            summaries.append({"title": item["title"], "summary": summary[0]["summary_text"]})

        return summaries
    except Exception as e:
        return [{"title": "Error", "summary": f"Error summarizing content: {str(e)}"}]


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


def perform_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": settings.SEARCH_API_KEY,
        "cx": settings.SEARCH_ENGINE_ID,
        "q": query,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        try:
            return response.json().get("items", [])[:5]  # Limit to top 5 results
        except ValueError:
            return []
    return [{"title": "Error", "link": "Failed to fetch search results."}]


@csrf_exempt
def gemini_view(request):
    if request.method == 'GET':
        try:
            user_message = request.GET.get("message", "").strip()

            if not user_message:
                return JsonResponse({"response": "How can I help you win big?!"})

            if not chat_session:
                return JsonResponse({"response": "Chat session could not be initialized. Please try again later."}, status=500)

            if re.search(r"\bsearch\b", user_message, re.IGNORECASE):
                search_query = user_message.replace("search", "").strip()
                extracted_content = perform_search_and_extract(search_query)
                summarized_results = summarize_content(extracted_content)
                formatted_results = [
                    f"{item['title']}:\n{item['summary']}" for item in summarized_results
                ]
                return JsonResponse({"response": "\n\n".join(formatted_results)})

            response = chat_session.send_message(user_message)
            return JsonResponse({"response": response.text})

        except Exception as e:
            return JsonResponse({"response": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"response": "Invalid request method"}, status=400)