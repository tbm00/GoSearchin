# Responsible for interacting with database

import requests
from dbConnector import dbConnector
from geopy.geocoders import Nominatim

class User:
    def __init__(self, username):
        self.username = username
        self.db = dbConnector()
        self.geocoder = Nominatim(user_agent='user_location')
        self.google_api_key = 'INSERT GOOGLE API KEY'

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

    def retrieve_queries(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    retrieve_query = "SELECT query_text FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s)"
                    user_query = (self.username,)
                    cursor.execute(retrieve_query, user_query)
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

    def retrieve_location(self):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    retrieve_location_query = "SELECT latitude, longitude FROM Location WHERE location_id = (SELECT location_id FROM Accounts WHERE username = %s)"
                    user_query = (self.username,)
                    cursor.execute(retrieve_location_query, user_query)
                    return cursor.fetchone()
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

    def retrieve_search_results(self, query):
        try:
            with self.db.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    retrieve_results_query = """
                        SELECT result_text 
                        FROM results 
                        WHERE query_id = 
                        (SELECT query_id FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s) AND query_text = %s)
                    """
                    user_query = (self.username, query)
                    cursor.execute(retrieve_results_query, user_query)
                    return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving search results: {e}")
            return None
