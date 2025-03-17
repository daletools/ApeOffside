from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from decouple import config
import requests
from django.template.defaulttags import querystring


# Create your views here.

def default(request):
    return HttpResponse("This is the default response to the Core endpoint")

def fetch_nba_statistics(request):
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
    querystring = {"game": "8133"}
    API_KEY = config('API_KEY')
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-nba-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    # Return the data as a JSON response to your front-end
    return JsonResponse(response.json())

def fetch_sports(request):
    url = 'https://api.the-odds-api.com/v4/sports/?apiKey=' + config('API_KEY')
    response = requests.get(url)
    return JsonResponse(response.json(), safe=False)
