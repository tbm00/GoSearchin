import mysql.connector
import requests
from geopy.geocoders import Nominatim

class User:
    def __init__(self, username):
        self.username = username
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="Insert mysql server username",
            password="Insert mysql server password",
            database="usersDB"
        )
        self.cursor = self.db_connection.cursor()
        self.geocoder = Nominatim(user_agent='user_location')
        self.google_api_key = "Insert google api key"

    def insert_query(self, query_text):
        insert_query = "INSERT INTO search_queries (user_id, query_text) VALUES ((SELECT user_id FROM Accounts WHERE username = %s), %s)"
        user_query = (self.username, query_text)
        self.cursor.execute(insert_query, user_query)
        self.db_connection.commit()

    def retrieve_queries(self):
        retrieve_query = "SELECT query_text FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s)"
        user_query = (self.username,)
        self.cursor.execute(retrieve_query, user_query)
        return self.cursor.fetchall()

    def delete_query(self, query_text):
        delete_query = "DELETE FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s) AND query_text = %s"
        user_query = (self.username, query_text)
        self.cursor.execute(delete_query, user_query)
        self.db_connection.commit()

    def get_ip(self):
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={self.google_api_key}"
        response = requests.post(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('location', {}).get('lat'), data.get('location', {}).get('lng')
        else:
            return None

    def get_user_location(self):
        user_ip = self.get_ip()
        if user_ip:
            location = self.geocoder.geocode(user_ip)
            if location:
                return {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "city": location.address.split(',')[-3].strip(),
                    "state": location.address.split(',')[-2].strip(),
                    "country": location.address.split(',')[-1].strip()
                }
        return None

    def update_location(self):
        location = self.get_user_location()
        if location:
            latitude = location['latitude']
            longitude = location['longitude']
            city = location['city']
            state = location['state']
            country = location['country']
            self.update_location_db(latitude, longitude, city, state, country)
            return True
        return False

    def update_location_db(self, latitude, longitude, city, state, country):
        update_location_query = "UPDATE Location SET latitude = %s, longitude = %s, city = %s, state = %s, country = %s WHERE location_id = (SELECT location_id FROM Accounts WHERE username = %s)"
        location_data = (latitude, longitude, city, state, country, self.username)
        self.cursor.execute(update_location_query, location_data)
        self.db_connection.commit()

    def retrieve_location(self):
        retrieve_location_query = "SELECT latitude, longitude, city, state, country FROM Location WHERE location_id = (SELECT location_id FROM Accounts WHERE username = %s)"
        user_query = (self.username,)
        self.cursor.execute(retrieve_location_query, user_query)
        return self.cursor.fetchone()

    def insert_search_result(self, query, result_text):
        insert_result_query = "INSERT INTO results (query_id, result_text) VALUES ((SELECT query_id FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s) AND query_text = %s), %s)"
        user_query = (self.username, query, result_text)
        self.cursor.execute(insert_result_query, user_query)
        self.db_connection.commit()

    def delete_search_result(self, query, result_text):
        delete_result_query = "DELETE FROM results WHERE query_id = (SELECT query_id FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s) AND query_text = %s) AND result_text = %s"
        user_query = (self.username, query, result_text)
        self.cursor.execute(delete_result_query, user_query)
        self.db_connection.commit()

    def retrieve_search_results(self, query):
        retrieve_results_query = "SELECT result_text FROM results WHERE query_id = (SELECT query_id FROM search_queries WHERE user_id = (SELECT user_id FROM Accounts WHERE username = %s) AND query_text = %s)"
        user_query = (self.username, query)
        self.cursor.execute(retrieve_results_query, user_query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.cursor.close()
        self.db_connection.close()
