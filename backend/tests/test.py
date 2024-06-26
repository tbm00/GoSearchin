# test_app.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

import unittest
from flask import Flask
from app.models.user import User
from app.models.dbConnector import dbConnector
from app.run import init_db, store_local_user

class TestApp(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Set up the Flask app similar to run.py
        cls.app = Flask(__name__)
        cls.app.config.from_object('config.Config')
        cls.app.testing = True
        cls.client = cls.app.test_client()

        # Initialize the database and store local user
        with cls.app.app_context():
            init_db()
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'GeoLite2-City.mmdb'))
            store_local_user(db_path)

        cls.db_connector = dbConnector()
        cls.user_id = None
        cls.query_id = None

    @classmethod
    def tearDownClass(cls):
        # Clean up the database after tests
        with cls.db_connector.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS Results;")
                cursor.execute("DROP TABLE IF EXISTS Queries;")
                cursor.execute("DROP TABLE IF EXISTS Accounts;")
                cursor.execute("DROP TABLE IF EXISTS Location;")
            conn.commit()

    def test_01_mysql_connection(self):
        print("Running test_01_mysql_connection...")
        try:
            conn = self.db_connector.get_connection()
            self.assertIsNotNone(conn)
            self.db_connector.close_connection(conn)
            print("MySQL connection test passed.")
        except Exception as e:
            self.fail(f"Failed to connect to MySQL: {e}")

    def test_02_schema_creation(self):
        print("Running test_02_schema_creation...")
        try:
            with self.db_connector.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW TABLES;")
                    tables = cursor.fetchall()
                    self.assertGreater(len(tables), 0, "No tables found in the database.")
            print("Schema creation test passed. Tables found:", tables)
        except Exception as e:
            self.fail(f"Failed to verify schema creation: {e}")

    def test_03_user_creation(self):
        print("Running test_03_user_creation...")
        user = User(username="test_user")
        user.insert_user(username="test_user")
        fetched_user = user.get_user()
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user['username'], "test_user")
        TestApp.user_id = fetched_user['user_id']
        print("User creation test passed. User details:", fetched_user)

    def test_04_user_update(self):
        print("Running test_04_user_update...")
        user = User(user_id=TestApp.user_id)
        success = user.update_user({"email": "test_user@example.com"})
        self.assertTrue(success)
        updated_user = user.get_user()
        self.assertEqual(updated_user['email'], "test_user@example.com")
        print("User update test passed. Updated user details:", updated_user)

    def test_05_user_deletion(self):
        print("Running test_05_user_deletion...")
        user = User(user_id=TestApp.user_id)
        success = user.delete_user()
        self.assertTrue(success)
        deleted_user = user.get_user()
        self.assertIsNone(deleted_user)
        print("User deletion test passed. User successfully deleted.")

    def test_06_query_creation(self):
        print("Running test_06_query_creation...")
        user = User(username="test_user")
        user.insert_user(username="test_user")
        TestApp.user_id = user.get_user()['user_id']
        user.insert_query("test_query")
        queries = user.get_queries()
        self.assertGreater(len(queries), 0)
        TestApp.query_id = queries[0]['query_text']
        print("Query creation test passed. Queries:", queries)

    def test_07_query_deletion(self):
        print("Running test_07_query_deletion...")
        user = User(user_id=TestApp.user_id)
        user.delete_query("test_query")
        queries = user.get_queries()
        self.assertEqual(len(queries), 0)
        print("Query deletion test passed. Remaining queries:", queries)

    def test_08_location_update(self):
        print("Running test_08_location_update...")
        user = User(user_id=TestApp.user_id)
        user.update_location_db(37.7749, -122.4194, "8.8.8.8")
        location = user.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location['latitude'], 37.7749)
        self.assertEqual(location['longitude'], -122.4194)
        self.assertEqual(location['ip'], "8.8.8.8")
        print("Location update test passed. Location details:", location)

    def test_09_weather_update(self):
        print("Running test_09_weather_update...")
        user = User(user_id=TestApp.user_id)
        weather_data = {
            "temperature": 20,
            "windspeed": 5
        }
        user.store_weather_data(weather_data)
        fetched_weather = user.get_weather_data()
        self.assertIsNotNone(fetched_weather)
        self.assertEqual(fetched_weather['temperature'], 20)
        self.assertEqual(fetched_weather['windspeed'], 5)
        print("Weather update test passed. Weather details:", fetched_weather)

if __name__ == '__main__':
    unittest.main()