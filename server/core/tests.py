import json

from django.test import TestCase

# Create your tests here.
from django.test import TestCase, RequestFactory
from django.conf import settings
from core.views import *
import requests
import requests_mock

class FetchSportsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_server_responding(self):
        request = self.factory.get('/fetch-sports/')
        response = fetch_sports(request)
        self.assertEqual(response.status_code, 200)

class FetchCurrentGamesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.sport = "basketball_nba"  # Valid sport key

    def test_fetch_current_games_valid_sport(self):
        request = self.factory.get(f'/fetch-current-games/{self.sport}/')
        response = fetch_current_games(request, sport=self.sport)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIsInstance(response_data, list)

        if response_data:  #TODO: add logic to catch failures when nba not in season
            first_event = response_data[0]
            self.assertIn("id", first_event)
            self.assertIn("sport_key", first_event)
            self.assertIn("sport_title", first_event)
            self.assertIn("commence_time", first_event)
            self.assertIn("home_team", first_event)
            self.assertIn("away_team", first_event)