import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse

# Create your views here.

ODDS_BASE_URL = "https://api.the-odds-api.com"


def default(request):
    return HttpResponse("This is the default response to the Core endpoint")


def fetch_nba_statistics(request):
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
    querystring = {"game": "8133"}
    headers = {
        "x-rapidapi-key": "TODO: get historical stats api key",
        "x-rapidapi-host": "api-nba-v1.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers, params=querystring)
    return JsonResponse(response.json())


def fetch_sports(request):
    url = f"{ODDS_BASE_URL}/v4/sports/?apiKey={settings.API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return JsonResponse(
            {"error": "Failed to fetch sports", "details": response.text},
            status=response.status_code,
        )

    return JsonResponse(response.json(), safe=False)


def fetch_current_games(request, sport):
    url = f"{ODDS_BASE_URL}/v4/sports/{sport}/events?apiKey={settings.API_KEY}"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            return JsonResponse(
                {"error": "Failed to fetch games", "details": response.text},
                status=response.status_code,
            )
        return JsonResponse(response.json(), safe=False)
    except Exception:
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)
