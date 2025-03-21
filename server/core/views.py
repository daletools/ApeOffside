from http.client import responses

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import requests
from django.template.defaulttags import querystring


# Create your views here.

def default(request):
    return HttpResponse("This is the default response to the Core endpoint")

def fetch_nba_statistics(request):
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
    querystring = {"game": "8133"}
    headers = {
        "x-rapidapi-key": "TODO: get historical stats api key",
        "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    # Return the data as a JSON response to your front-end
    return JsonResponse(response.json())

def fetch_sports(request):
    url = f'{settings.ODDS_URL}/v4/sports/?apiKey={settings.API_KEY}'
    response = requests.get(url)
    return JsonResponse(response.json(), safe=False)

def fetch_current_games(request, sport):
    url = f'{settings.ODDS_URL}/v4/sports/{sport}/events?apiKey={settings.API_KEY}'
    response = requests.get(url)
    return JsonResponse(response.json(), safe=False)

