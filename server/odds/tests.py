# Create your tests here.
import json
import unittest

import requests
from django.core.cache import cache
from django.http import JsonResponse

from odds.utils.view_helpers import parse_event_odds
from django.test import TestCase, RequestFactory
from unittest.mock import MagicMock, patch
from odds.views import fetch_event_odds
from odds.utils.sample_responses import sample_input, expected_parsed_output
import logging

logger = logging.getLogger(__name__)


class TestParseEventOdds(unittest.TestCase):
    def setUp(self):

        # Expected output structure
        self.expected_output = expected_parsed_output
        self.sample_input = sample_input

    def test_parse_event_odds_basic_structure(self):
        """Test that the function returns the expected basic structure"""
        result = parse_event_odds(self.sample_input)

        self.assertEqual(result["id"], self.expected_output["id"])
        self.assertEqual(result["sport_key"], self.expected_output["sport_key"])
        self.assertEqual(result["sport_title"], self.expected_output["sport_title"])
        self.assertEqual(result["commence_time"], self.expected_output["commence_time"])
        self.assertEqual(result["home_team"], self.expected_output["home_team"])
        self.assertEqual(result["away_team"], self.expected_output["away_team"])
        self.assertEqual(result["market"], self.expected_output["market"])

    def test_parse_event_odds_bookmaker_data(self):
        """Test that bookmaker data is correctly parsed"""
        result = parse_event_odds(self.sample_input)

        self.assertIn("draftkings", result["bookmaker"])
        self.assertEqual(result["bookmaker"]["draftkings"]["title"], "DraftKings")

        self.assertIn("fanduel", result["bookmaker"])
        self.assertEqual(result["bookmaker"]["fanduel"]["title"], "FanDuel")

    def test_parse_event_odds_player_data(self):
        """Test that player data is correctly organized"""
        result = parse_event_odds(self.sample_input)

        self.assertIn("Shai Gilgeous-Alexander", result["player"])

        player_data = result["player"]["Shai Gilgeous-Alexander"]
        self.assertIn("DraftKings", player_data)
        self.assertIn("FanDuel", player_data)

        dk_data = player_data["DraftKings"]
        self.assertEqual(dk_data["Over"]["price"], 1.8)
        self.assertEqual(dk_data["Over"]["point"], 30.5)
        self.assertIn("link", dk_data["Over"])
        self.assertEqual(dk_data["Under"]["price"], 1.95)
        self.assertEqual(dk_data["Under"]["point"], 30.5)
        self.assertIn("link", dk_data["Under"])

        fd_data = player_data["FanDuel"]
        self.assertEqual(fd_data["Over"]["price"], 1.88)
        self.assertEqual(fd_data["Over"]["point"], 31.5)
        self.assertIn("link", fd_data["Over"])
        self.assertEqual(fd_data["Under"]["price"], 1.88)
        self.assertEqual(fd_data["Under"]["point"], 31.5)
        self.assertIn("link", fd_data["Under"])

    def test_parse_event_odds_multiple_players(self):
        """Test that multiple players are handled correctly"""
        modified_input = json.loads(json.dumps(self.sample_input))

        modified_input["bookmakers"][0]["markets"][0]["outcomes"].extend(
            [
                {
                    "name": "Over",
                    "description": "Jaren Jackson Jr",
                    "price": 1.95,
                    "point": 23.5,
                    "link": "https://example.com/jjj_over",
                },
                {
                    "name": "Under",
                    "description": "Jaren Jackson Jr",
                    "price": 1.8,
                    "point": 23.5,
                    "link": "https://example.com/jjj_under",
                },
            ]
        )

        result = parse_event_odds(modified_input)

        self.assertIn("Shai Gilgeous-Alexander", result["player"])
        self.assertIn("Jaren Jackson Jr", result["player"])

        jjj_data = result["player"]["Jaren Jackson Jr"]["DraftKings"]
        self.assertEqual(jjj_data["Over"]["price"], 1.95)
        self.assertEqual(jjj_data["Over"]["point"], 23.5)
        self.assertEqual(jjj_data["Over"]["link"], "https://example.com/jjj_over")
        self.assertEqual(jjj_data["Under"]["price"], 1.8)
        self.assertEqual(jjj_data["Under"]["point"], 23.5)
        self.assertEqual(jjj_data["Under"]["link"], "https://example.com/jjj_under")


if __name__ == "__main__":
    unittest.main()


class OddsViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.sport = "basketball_nba"
        self.event_id = "c1f70941e477df98e94d9c55421d7b71"
        self.markets = "player_points"
        self.date = "2023-01-01"

        # Mock API response
        self.sample_odds_response = expected_parsed_output

    @patch("requests.get")
    def test_fetch_event_odds_success(self, mock_get):
        """Test successful fetch_event_odds response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Return the raw sample input that needs to be parsed
        mock_response.json.return_value = sample_input
        mock_get.return_value = mock_response

        request = self.factory.get("/fetch_event_odds/")
        response = fetch_event_odds(request, self.sport, self.event_id, self.markets)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["metadata"]["cached"], False)
        self.assertIn("data", data)

    @patch("requests.get")
    def test_fetch_event_odds_cached(self, mock_get):
        """Test fetch_event_odds with cached data"""
        cache_key = f"event_odds_{self.sport}_{self.event_id}_{self.markets}"
        cache.set(cache_key, {"test": "data"}, 60)

        request = self.factory.get("/fetch_event_odds/")
        response = fetch_event_odds(request, self.sport, self.event_id, self.markets)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["metadata"]["cached"], True)
        self.assertEqual(data["data"], {"test": "data"})
        mock_get.assert_not_called()

    @patch("requests.get")
    def test_fetch_event_odds_api_error(self, mock_get):
        """Test fetch_event_odds with API error"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_get.return_value = mock_response

        request = self.factory.get("/fetch_event_odds/")
        response = fetch_event_odds(request, self.sport, self.event_id, self.markets)

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertEqual(data["error"], "Failed to fetch odds")

    @patch("requests.get")
    def test_fetch_event_odds_network_error(self, mock_get):
        """Test that network errors are caught."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to connect")

        request = self.factory.get("/fetch_event_odds/")
        response = fetch_event_odds(request, self.sport, self.event_id, self.markets)

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertEqual(data["error"], "An unexpected error occurred")

    def tearDown(self):
        cache.clear()
