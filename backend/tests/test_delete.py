# tests.test_run_then_delete.py

# This runs the basic local user functionality:
# 1) Creates MySQL database schema.
# 2) Get user IP, location, and weather data.
# 3) Stores it in the database as local_user.
# 4) Deletes all database tables.

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

import unittest
from flask import Flask
from app.models.user import User
from app.models.dbConnector import dbConnector
from app.run import init_db, run_as_local_user

class TestApp(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Set up the Flask app similar to run.py
        cls.app = Flask(__name__)
        cls.app.config.from_object('config.Config')
        cls.app.testing = True
        cls.client = cls.app.test_client()

        # Initialize the database and run as local user
        with cls.app.app_context():
            init_db()

        cls.db_connector = dbConnector()
        
        cls.user_id = None
        cls.query_id = None

    def test_01_deletion(cls):
        cls.db_connector.delete_database()

    @classmethod
    def tearDownClass(cls):
        cls.db_connector.close_connection(cls.db_connector.get_connection())

if __name__ == '__main__':
    unittest.main()