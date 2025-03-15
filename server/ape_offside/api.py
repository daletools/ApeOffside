from django.http import JsonResponse
import requests


def fetch_nba_statistics(request):
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
    querystring = {"game": "8133"}
    headers = {
        "x-rapidapi-key": "YOUR_RAPIDAPI_KEY",
        "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    # Return the data as a JSON response to your front-end
    return JsonResponse(response.json())
