import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure the app directory is in the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from app.models.user import User

class TestUserOperations(unittest.TestCase):
    @classmethod
    @patch('app.models.dbConnector.dbConnector.get_connection', return_value=MagicMock())
    def setUpClass(cls, mock_db):
        # Create a User object with a test username
        cls.test_user = User(user_id=None)

    def test_insert_user(self):
        # Insert the user into the Accounts table
        self.test_user.insert_user(username="test_user")
        user_data = self.test_user.get_user()
        self.assertIsNotNone(user_data, "User should be inserted")
        self.test_user.user_id = user_data['user_id']

    def test_update_user(self):
        data = {"email": "test_user@example.com"}
        result = self.test_user.update_user(data)
        self.assertTrue(result, "User email should be updated")
        user_data = self.test_user.get_user()
        self.assertEqual(user_data["email"], data["email"], "User email should be updated in database")

    def test_delete_user(self):
        result = self.test_user.delete_user()
        self.assertTrue(result, "User should be deleted")
        user_data = self.test_user.get_user()
        self.assertIsNone(user_data, "User should not exist after deletion")

    def test_insert_query(self):
        # Insert a search query
        query = "test_query"
        self.test_user.insert_query(query)
        queries = self.test_user.get_queries()
        self.assertIn(query, [q['query_text'] for q in queries], "Query should be inserted")

    def test_delete_query(self):
        # Insert and then delete a search query
        query = "test_query"
        self.test_user.insert_query(query)
        self.test_user.delete_query(query)
        queries = self.test_user.get_queries()
        self.assertNotIn(query, [q['query_text'] for q in queries], "Query should be deleted")

    def test_update_location(self):
        # Update user location
        self.assertTrue(self.test_user.update_location(), "Location should be updated successfully")

    def test_retrieve_location(self):
        # Retrieve user location
        location = self.test_user.retrieve_location()
        self.assertIsNotNone(location, "Location should be retrieved")

    def test_insert_search_result(self):
        # Insert a search result
        query = "test_query"
        result = "test_result"
        self.test_user.insert_search_result(query, result)
        results = self.test_user.get_search_results(query)
        self.assertIn(result, [r['result_text'] for r in results], "Search result should be inserted")

    def test_delete_search_result(self):
        # Insert and then delete a search result
        query = "test_query"
        result = "test_result"
        self.test_user.insert_search_result(query, result)
        self.test_user.delete_search_result(query, result)
        results = self.test_user.get_search_results(query)
        self.assertNotIn(result, [r['result_text'] for r in results], "Search result should be deleted")

    @classmethod
    def tearDownClass(cls):
        # Clean up the test user
        cls.test_user.delete_user()

if __name__ == '__main__':
    unittest.main()