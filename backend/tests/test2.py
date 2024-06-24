import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure the app directory is in the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from app.models.user import User
from app.models.dbConnector import dbConnector
from app.services.google_search import perform_search
from app.services.weather import get_weather_data
from app.config import Config

class TestGoFish(unittest.TestCase):
    @classmethod
    @patch('app.models.dbConnector.dbConnector.get_connection', return_value=MagicMock())
    def setUpClass(cls, mock_db):
        cls.db = dbConnector()
        cls.test_user = User("test_user")

    def test_insert_user(self):
        #Test inserting a user into the Accounts table
        self.test_user.insert_user()
        user = self.test_user.get_user()
        self.assertIsNotNone(user, "User should be inserted")

    def test_update_user(self):
        #Test updating a user's email
        data = {"email": "test_user@example.com"}
        result = self.test_user.update_user(data)
        self.assertTrue(result, "User email should be updated")
        user = self.test_user.get_user()
        self.assertEqual(user["email"], data["email"], "User email should be updated in database")

    def test_delete_user(self):
        #Test deleting a user from the Accounts table
        self.test_user.insert_user()  # Ensure user exists
        result = self.test_user.delete_user()
        self.assertTrue(result, "User should be deleted")
        user = self.test_user.get_user()
        self.assertIsNone(user, "User should not exist after deletion")

    def test_get_weather_data(self):
        #Test fetching weather data using coordinates
        latitude, longitude = 37.7749, -122.4194  # San Francisco coordinates
        weather_data = get_weather_data(latitude, longitude)
        self.assertIn("hourly", weather_data, "Weather data should contain 'hourly' key")

    def test_perform_search(self):
        #Test performing a search using Google Custom Search API
        query = "fishing tips"
        api_key = Config.GOOGLE_API_KEY
        cx = Config.GOOGLE_CX
        search_results = perform_search(query, api_key, cx)
        self.assertIn("items", search_results, "Search results should contain 'items' key")

    def test_user_location_operations(self):
        #Test storing and retrieving user location
        location = "San Francisco, CA"
        self.test_user.store_weather_data(location)
        stored_location = self.test_user.get_location()
        self.assertEqual(stored_location, location, "Stored location should match the input location")

    def test_weather_data_storage(self):
        #Test storing and retrieving weather data
        weather_data = {"temp": 75, "conditions": "Sunny"}
        self.test_user.store_weather_data(weather_data)
        stored_weather = self.test_user.get_weather_data()
        self.assertEqual(stored_weather, weather_data, "Stored weather data should match the input weather data")

    @classmethod
    def tearDownClass(cls):
        cls.test_user.delete_user()  # Clean up the test user

if __name__ == '__main__':
    unittest.main()