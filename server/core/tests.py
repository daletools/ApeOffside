import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from core.views import fetch_sports, fetch_current_games


class SportsViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.sport = "basketball_nba"
        self.sample_sports_data = [{"key": "basketball_nba", "title": "NBA"}]
        self.sample_games_data = [{"id": "game1", "sport_key": "basketball_nba"}]

    @patch("requests.get")
    def test_fetch_sports_success(self, mock_get):
        """Test successful sports fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_sports_data
        mock_get.return_value = mock_response

        request = self.factory.get("/fetch_sports/")
        response = fetch_sports(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), self.sample_sports_data)

    @patch("requests.get")
    def test_fetch_sports_api_failure(self, mock_get):
        """Test API failure (non-200 status)"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_get.return_value = mock_response

        request = self.factory.get("/fetch_sports/")
        response = fetch_sports(request)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            json.loads(response.content),
            {"error": "Failed to fetch sports", "details": "Server Error"},
        )

    @patch("requests.get")
    def test_fetch_current_games_success(self, mock_get):
        """Test successful games fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_games_data
        mock_get.return_value = mock_response

        request = self.factory.get(f"/games/{self.sport}/")
        response = fetch_current_games(request, self.sport)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), self.sample_games_data)

    @patch("requests.get")
    def test_fetch_current_games_api_failure(self, mock_get):
        """Test API failure (non-200 status)"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        request = self.factory.get(f"/games/{self.sport}/")
        response = fetch_current_games(request, self.sport)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            json.loads(response.content),
            {"error": "Failed to fetch games", "details": "Not Found"},
        )

    @patch("requests.get")
    def test_fetch_current_games_connection_error(self, mock_get):
        """Test network failure (e.g., connection error)"""
        mock_get.side_effect = Exception("Connection failed")

        request = self.factory.get(f"/games/{self.sport}/")
        response = fetch_current_games(request, self.sport)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            json.loads(response.content),
            {"error": "An unexpected error occurred"},
        )
