# app.models.user.py
# Interacts with database

import requests
import json
from .dbConnector import dbConnector
from flask import current_app

class User:
    def __init__(self, user_id=None, username=None):
        self.user_id = user_id
        self.username = username
        self.db = dbConnector()

    def get_user(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    if self.user_id:
                        query = "SELECT * FROM Accounts WHERE user_id = %s"
                        cursor.execute(query, (self.user_id,))
                    elif self.username:
                        query = "SELECT * FROM Accounts WHERE username = %s"
                        cursor.execute(query, (self.username,))
                    else:
                        return None
                    user_data = cursor.fetchone()
                    if user_data:
                        self.user_id = user_data['user_id']
                    return user_data
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None

    def insert_user(self, username):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    insert_user_query = "INSERT INTO Accounts (username) VALUES (%s)"
                    cursor.execute(insert_user_query, (username,))
                    conn.commit()
                    self.user_id = cursor.lastrowid
                    print("User inserted successfully")
        except Exception as e:
            print(f"Error inserting user: {e}")

    def update_user(self, data):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    update_query = "UPDATE Accounts SET email = %s WHERE user_id = %s"
                    cursor.execute(update_query, (data['email'], self.user_id))
                    conn.commit()
                    print("User updated successfully")
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def delete_user(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    delete_query = "DELETE FROM Accounts WHERE user_id = %s"
                    cursor.execute(delete_query, (self.user_id,))
                    conn.commit()
                    print("User deleted successfully")
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def insert_query(self, query_text):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    insert_query = "INSERT INTO Queries (user_id, query_text) VALUES (%s, %s)"
                    cursor.execute(insert_query, (self.user_id, query_text))
                    conn.commit()
        except Exception as e:
            print(f"Error inserting query: {e}")

    def get_queries(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    get_query = "SELECT query_text FROM Queries WHERE user_id = %s"
                    cursor.execute(get_query, (self.user_id,))
                    return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving queries: {e}")
            return None

    def delete_query(self, query_text):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    delete_query = "DELETE FROM Queries WHERE user_id = %s AND query_text = %s"
                    cursor.execute(delete_query, (self.user_id, query_text))
                    conn.commit()
        except Exception as e:
            print(f"Error deleting query: {e}")

    def update_location_db(self, latitude, longitude, ip):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    update_location_query = """
                        UPDATE Location SET latitude = %s, longitude = %s, ip = %s
                        WHERE location_id = (SELECT location_id FROM Accounts WHERE user_id = %s)
                    """
                    location_data = (latitude, longitude, ip, self.user_id)
                    cursor.execute(update_location_query, location_data)
                    conn.commit()
        except Exception as e:
            print(f"Error updating location in DB: {e}")

    def get_location(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    get_location_query = "SELECT latitude, longitude, ip FROM Location WHERE location_id = (SELECT location_id FROM Accounts WHERE user_id = %s)"
                    cursor.execute(get_location_query, (self.user_id,))
                    result = cursor.fetchone()
                    if result:
                        return result
                    return None
        except Exception as e:
            print(f"Error retrieving location: {e}")
            return None

    def insert_search_result(self, query, result_text):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    insert_result_query = """
                        INSERT INTO Results (query_id, result_text) 
                        VALUES ((SELECT query_id FROM Queries WHERE user_id = %s AND query_text = %s), %s)
                    """
                    user_query = (self.user_id, query, result_text)
                    cursor.execute(insert_result_query, user_query)
                    conn.commit()
        except Exception as e:
            print(f"Error inserting search result: {e}")

    def delete_search_result(self, query, result_text):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    delete_result_query = """
                        DELETE FROM Results 
                        WHERE query_id = (SELECT query_id FROM Queries WHERE user_id = %s AND query_text = %s) 
                        AND result_text = %s
                    """
                    user_query = (self.user_id, query, result_text)
                    cursor.execute(delete_result_query, user_query)
                    conn.commit()
        except Exception as e:
            print(f"Error deleting search result: {e}")

    def get_search_results(self, query):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    get_results_query = """
                        SELECT result_text 
                        FROM Results 
                        WHERE query_id = 
                        (SELECT query_id FROM Queries WHERE user_id = %s AND query_text = %s)
                    """
                    user_query = (self.user_id, query)
                    cursor.execute(get_results_query, user_query)
                    return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving search results: {e}")
            return None

    def store_weather_data(self, weather_data):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    insert_weather_data_query = """
                        UPDATE Location 
                        SET weather_data = %s 
                        WHERE location_id = (SELECT location_id FROM Accounts WHERE user_id = %s)
                    """
                    cursor.execute(insert_weather_data_query, (json.dumps(weather_data), self.user_id))
                    conn.commit()
                    print("Weather data stored successfully")
        except Exception as e:
            print(f"Error storing weather data: {e}")

    def get_weather_data(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    get_weather_data_query = """
                        SELECT weather_data 
                        FROM Location 
                        WHERE location_id = (SELECT location_id FROM Accounts WHERE user_id = %s)
                    """
                    cursor.execute(get_weather_data_query, (self.user_id,))
                    result = cursor.fetchone()
                    return json.loads(result['weather_data']) if result and 'weather_data' in result else None
        except Exception as e:
            print(f"Error retrieving weather data: {e}")
            return None