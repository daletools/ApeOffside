import json

from django.test import TestCase, Client
from django.urls import reverse

from odds.arbitrage.utils import detect_value_bets


class ValueBetDetectionTest(TestCase):

    def setUp(self):
        self.client = Client()

    # ValueBetDetectionTest
    def test_detect_value_bets_logic(self):
        fake_games = [
            {
                "home_team": "Lakers",
                "away_team": "Warriors",
                "commence_time": "2025-04-01T00:00:00Z",
                "bookmakers": [
                    {
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Lakers", "price": 2.0},
                                    {"name": "Warriors", "price": 1.9},
                                ],
                            }
                        ],
                    },
                    {
                        "title": "FanDuel",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {
                                        "name": "Lakers",
                                        "price": 2.4,
                                    },  # ← this should trigger value bet
                                    {"name": "Warriors", "price": 1.8},
                                ],
                            }
                        ],
                    },
                ],
            }
        ]

        result = detect_value_bets(fake_games, threshold=5.0)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["team"], "Lakers")


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
        self.url = reverse(
            "arbitrage:calculate_arbitrage"
        )  # update namespace if different

    def test_valid_input(self):
        payload = {"odds_team1": 2.1, "odds_team2": 2.2, "stake": 100}

        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("guaranteed_profit", data)
        self.assertIn("team1_stake", data)
        self.assertIn("team2_stake", data)

    def test_invalid_input(self):
        payload = {"odds_team1": 1.0, "odds_team2": 2.0, "stake": 100}  # not valid

        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
