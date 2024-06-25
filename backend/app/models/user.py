# Responsible for interacting with database

import requests
import json
from geopy.geocoders import Nominatim
from .dbConnector import dbConnector
from ..services.weather import get_weather_data
from flask import current_app

class User:
    def __init__(self, user_id=None, username=None):
        self.user_id = user_id
        self.username = username
        self.db = dbConnector()
        self.geocoder = Nominatim(user_agent='user_location')

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
                        self.user_id = user_data['user_id']  # Update the instance with the user_id
                    return user_data
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None

    def insert_user(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    insert_user_query = "INSERT INTO Accounts (username) VALUES (%s)"
                    cursor.execute(insert_user_query, (self.username,))
                    conn.commit()
                    self.user_id = cursor.lastrowid # store inserted user's ID to self
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


    def get_user_location(self):
        try:
            google_api_key = current_app.config['GOOGLE_API_KEY']
            response = requests.post(
                "https://www.googleapis.com/geolocation/v1/geolocate",
                json={},
                params={"key": google_api_key}
            )

            if response.status_code == 200:
                data = response.json()
                latitude = data["location"]["lat"]
                longitude = data["location"]["lng"]
                return {
                    "latitude": latitude,
                    "longitude": longitude
                }
            else:
                print("Failed to get user location:", response.text)
                return None
        except requests.RequestException as e:
            print("Request error:", e)
            return None
        except Exception as e:
            print(f"Error getting user location: {e}")
            return None

    def update_location(self):
        try:
            location = self.get_user_location()
            if location:
                latitude = location['latitude']
                longitude = location['longitude']
                self.update_location_db(latitude, longitude)
                return True
            return False
        except Exception as e:
            print(f"Error updating location: {e}")
            return False

    def update_location_db(self, latitude, longitude):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    update_location_query = """
                        UPDATE Location SET latitude = %s, longitude = %s 
                        WHERE location_id = (SELECT location_id FROM Accounts WHERE user_id = %s)
                    """
                    location_data = (latitude, longitude, self.user_id)
                    cursor.execute(update_location_query, location_data)
                    conn.commit()
        except Exception as e:
            print(f"Error updating location in DB: {e}")

    def get_location(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    get_location_query = "SELECT latitude, longitude FROM Location WHERE location_id = (SELECT location_id FROM Accounts WHERE user_id = %s)"
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

    def get_lat_lon(self, address):
        try:
            location = self.geocoder.geocode(address)
            if location:
                return location.latitude, location.longitude
            print(f"Geocoding failed for address: {address}")
            return None, None
        except Exception as e:
            print(f"Error during geocoding: {e}")
            return None, None
        
    def get_weather(self):
        location = self.get_location()
        if location:
            latitude, longitude = self.get_lat_lon(location)
            if latitude is not None and longitude is not None:
                return get_weather_data(latitude, longitude)
        return None