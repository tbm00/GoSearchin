import unittest
import os
import sys

# Ensure the app directory is in the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from app.models.user import User

class TestUserOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a User object with a test username
        cls.test_user = User("test_user")

    def test_insert_user(self):
        # Insert the user into the Accounts table
        self.test_user.insert_user()
        user = self.test_user.get_user()
        self.assertIsNotNone(user, "User should be inserted")

    def test_insert_query(self):
        # Insert a search query
        query = "test_query"
        self.test_user.insert_query(query)
        queries = self.test_user.retrieve_queries()
        self.assertIn(query, [q['query'] for q in queries], "Query should be inserted")

    def test_delete_query(self):
        # Insert and then delete a search query
        query = "test_query"
        self.test_user.insert_query(query)
        self.test_user.delete_query(query)
        queries = self.test_user.retrieve_queries()
        self.assertNotIn(query, [q['query'] for q in queries], "Query should be deleted")

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
        results = self.test_user.retrieve_search_results(query)
        self.assertIn(result, [r['result'] for r in results], "Search result should be inserted")

    def test_delete_search_result(self):
        # Insert and then delete a search result
        query = "test_query"
        result = "test_result"
        self.test_user.insert_search_result(query, result)
        self.test_user.delete_search_result(query, result)
        results = self.test_user.retrieve_search_results(query)
        self.assertNotIn(result, [r['result'] for r in results], "Search result should be deleted")

    @classmethod
    def tearDownClass(cls):
        # Clean up the test user
        cls.test_user.delete_user()

if __name__ == '__main__':
    unittest.main()