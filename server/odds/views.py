import json
from datetime import datetime
from django.test import TestCase, RequestFactory
from unittest.mock import MagicMock, patch

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from odds.utils.view_helpers import parse_event_odds

ODDS_BASE_URL = "https://api.the-odds-api.com"


# GET /v4/sports/{sport}/events/{eventId}/odds?apiKey={apiKey}&regions={regions}&markets={markets}&dateFormat={dateFormat}&oddsFormat={oddsFormat}
def fetch_event_odds(request, sport, event_id, markets):
    cache_key = f"event_odds_{sport}_{event_id}_{markets}"
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        response_data = {
            "data": cached_data,
            "metadata": {
                "cached": True,
                "timestamp": datetime.now().isoformat(),
                "message": "Served from cache (60 second TTL)",
            },
        }
        return JsonResponse(response_data, safe=False)

    url = (
        f"{ODDS_BASE_URL}"
        f"/v4/sports/{sport}"
        f"/events/{event_id}"
        f"/odds?apiKey={settings.API_KEY}"
        f"&regions=us&markets={markets}"
        f"&includeLinks=true"
    )

    try:
        response = requests.get(url)
        if response.status_code != 200:
            return JsonResponse(
                {"error": "Failed to fetch odds", "details": response.text},
                status=response.status_code,
            )

        full_data = response.json()
        parsed_data = parse_event_odds(full_data)

        cache.set(cache_key, parsed_data, 60)
        response_data = {
            "data": parsed_data,
            "metadata": {
                "cached": False,
                "timestamp": datetime.now().isoformat(),
                "message": "Freshly fetched data",
            },
        }

        return JsonResponse(response_data, safe=False)

    except Exception as e:
        return JsonResponse(
            {"error": "An unexpected error occurred", "details": str(e)}, status=500
        )
