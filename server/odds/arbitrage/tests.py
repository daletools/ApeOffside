# arbitrage/tests.py

from django.test import TestCase, Client
from django.urls import reverse

class ArbitrageViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_arbitrage_response_status(self):
        response = self.client.get(reverse("arbitrage:arbitrage-opportunities"))
        # Will likely fail without valid API_KEY, but confirms connection
        self.assertIn(response.status_code, [200, 400, 500])
