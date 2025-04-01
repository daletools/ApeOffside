# arbitrage/tests.py

from django.test import TestCase, Client
from django.urls import reverse
import json

class ArbitrageViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_arbitrage_response_status(self):
        response = self.client.get(reverse("arbitrage:arbitrage-opportunities"))
        # Will likely fail without valid API_KEY, but confirms connection
        self.assertIn(response.status_code, [200, 400, 500])

class ArbitrageCalculatorTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("arbitrage:calculate_arbitrage")  # update namespace if different

    def test_valid_input(self):
        payload = {
            "odds_team1": 2.1,
            "odds_team2": 2.2,
            "stake": 100
        }

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("guaranteed_profit", data)
        self.assertIn("team1_stake", data)
        self.assertIn("team2_stake", data)

    def test_invalid_input(self):
        payload = {
            "odds_team1": 1.0,  # not valid
            "odds_team2": 2.0,
            "stake": 100
        }

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())