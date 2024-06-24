# Responsible for interacting with database

import requests
import json
from dbConnector import dbConnector
from geopy.geocoders import Nominatim
from services.weather import get_weather_data
#from datetime import datetime

class User:
    def __init__(self, username):
        self.username = username
        self.db = dbConnector()
        self.geocoder = Nominatim(user_agent='user_location')
        self.google_api_key = 'INSERT GOOGLE API KEY' # I don't think this should be needed anymore?

    def get_user(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    query = "SELECT * FROM Accounts WHERE username = %s"
                    cursor.execute(query, (self.username,))
                    return cursor.fetchone()
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
                    print("User inserted successfully")
        except Exception as e:
            print(f"Error inserting user: {e}")

    def update_user(self, data):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    update_query = "UPDATE Accounts SET email = %s WHERE username = %s"
                    cursor.execute(update_query, (data['email'], self.username))
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
                    delete_query = "DELETE FROM Accounts WHERE username = %s"
                    cursor.execute(delete_query, (self.username,))
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
                    insert_query = "INSERT INTO search_queries (user_id, query_text) VALUES ((SELECT user_id FROM Accounts WHERE username = %s), %s)"
                    user_query = (self.username, query_text)
                    cursor.execute(insert_query, user_query)
                    conn.commit()
        except Exception as e:
            print(f"Error inserting query: {e}")

    def get_queries(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    get_query = "SELECT query_text FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s)"
                    user_query = (self.username,)
                    cursor.execute(get_query, user_query)
                    return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving queries: {e}")
            return None

    def delete_query(self, query_text):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    delete_query = "DELETE FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s) AND query_text = %s"
                    user_query = (self.username, query_text)
                    cursor.execute(delete_query, user_query)
                    conn.commit()
        except Exception as e:
            print(f"Error deleting query: {e}")

    def get_user_location(self):
        try:
            response = requests.post(
            "https://www.googleapis.com/geolocation/v1/geolocate",
            json={},
            params={"key": self.google_api_key}
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
                        WHERE location_id = (SELECT location_id FROM Accounts WHERE username = %s)
                    """
                    location_data = (latitude, longitude, self.username)
                    cursor.execute(update_location_query, location_data)
                    conn.commit()
        except Exception as e:
            print(f"Error updating location in DB: {e}")

    def get_location(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    get_location_query = "SELECT latitude, longitude FROM Location WHERE location_id = (SELECT location_id FROM Accounts WHERE username = %s)"
                    user_query = (self.username,)
                    cursor.execute(get_location_query, user_query) # Not sure why user query is passed
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
                        INSERT INTO results (query_id, result_text) 
                        VALUES ((SELECT query_id FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s) AND query_text = %s), %s)
                    """
                    user_query = (self.username, query, result_text)
                    cursor.execute(insert_result_query, user_query)
                    conn.commit()
        except Exception as e:
            print(f"Error inserting search result: {e}")

    def delete_search_result(self, query, result_text):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    delete_result_query = """
                        DELETE FROM results 
                        WHERE query_id = (SELECT query_id FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s) AND query_text = %s) 
                        AND result_text = %s
                    """
                    user_query = (self.username, query, result_text)
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
                        FROM results 
                        WHERE query_id = 
                        (SELECT query_id FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s) AND query_text = %s)
                    """
                    user_query = (self.username, query)
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
                        WHERE location_id = (SELECT location_id FROM Accounts WHERE username = %s)
                    """
                    cursor.execute(insert_weather_data_query, (json.dumps(weather_data), self.username))
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
                        WHERE location_id = (SELECT location_id FROM Accounts WHERE username = %s)
                    """
                    cursor.execute(get_weather_data_query, (self.username,))
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