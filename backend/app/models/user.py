# app.models.user.py
# Interacts with database

import json
from .dbConnector import dbConnector

class User:
    def __init__(self, user_id=None, username=None, email=None, ip=None, coords=None, weather=None):
        self.db = dbConnector()
        self.user_id = user_id
        self.username = username if username is not None else "null"
        self.email = email if email is not None else "null"
        self.ip = ip if ip is not None else "null"
        self.coords = coords if coords is not None else [0, 0]
        self.weather = weather if weather is not None else [0, 0, 0]
        

    def get_user(self):
        try:
            with self.db.get_connection() as conn:
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

    def find_username(self, username):
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    query = "SELECT user_id FROM Accounts WHERE username = %s"
                    cursor.execute(query, (username,))
                    result = cursor.fetchone()
                    if result:
                        return result['user_id']
                    return None
        except Exception as e:
            print(f"Error finding user by username: {e}")
            return None

    def insert_user(self, username):
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    if self.user_id:
                        # Update existing user
                        update_user_query = "UPDATE Accounts SET username = %s WHERE user_id = %s"
                        cursor.execute(update_user_query, (username, self.user_id))
                    else:
                        # Insert new user
                        insert_user_query = "INSERT INTO Accounts (username) VALUES (%s)"
                        cursor.execute(insert_user_query, (username,))
                        self.user_id = cursor.lastrowid
                    
                    conn.commit()
                    self.username = username
                    print("User inserted or updated successfully")
                    return self.user_id
        except Exception as e:
            print(f"Error inserting or updating user: {e}")
            return None

    def update_user(self, username, email):
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    update_query = "UPDATE Accounts SET username = %s, email = %s WHERE user_id = %s"
                    cursor.execute(update_query, (username, email, self.user_id))
                    conn.commit()
                    self.username = username
                    self.email = email
                    print("User updated successfully")
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def delete_user(self):
        try:
            with self.db.get_connection() as conn:
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
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    insert_query = "INSERT INTO Queries (user_id, query_text) VALUES (%s, %s)"
                    cursor.execute(insert_query, (self.user_id, query_text))
                    conn.commit()
        except Exception as e:
            print(f"Error inserting query: {e}")

    def get_queries(self, db):
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    get_query = "SELECT query_text FROM Queries WHERE user_id = %s"
                    cursor.execute(get_query, (self.user_id,))
                    return cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving queries: {e}")
            return None

    def delete_query(self, query_text):
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    delete_query = "DELETE FROM Queries WHERE user_id = %s AND query_text = %s"
                    cursor.execute(delete_query, (self.user_id, query_text))
                    conn.commit()
        except Exception as e:
            print(f"Error deleting query: {e}")

    def update_location_db(self, latitude, longitude, ip):
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    # Check if location exists for the user
                    check_location_query = """
                        SELECT location_id FROM Accounts WHERE user_id = %s
                    """
                    cursor.execute(check_location_query, (self.user_id,))
                    location_id_result = cursor.fetchone()

                    if location_id_result:
                        location_id = location_id_result['location_id']
                        # Update existing location
                        update_location_query = """
                            UPDATE Location SET latitude = %s, longitude = %s, ip = %s
                            WHERE location_id = %s
                        """
                        cursor.execute(update_location_query, (latitude, longitude, ip, location_id))
                    else:
                        # Insert new location
                        insert_location_query = """
                            INSERT INTO Location (latitude, longitude, ip) VALUES (%s, %s, %s)
                        """
                        cursor.execute(insert_location_query, (latitude, longitude, ip))
                        new_location_id = cursor.lastrowid
                        # Update user's location_id
                        update_user_location_query = """
                            UPDATE Accounts SET location_id = %s WHERE user_id = %s
                        """
                        cursor.execute(update_user_location_query, (new_location_id, self.user_id))

                    conn.commit()
                    print("Location updated successfully")
        except Exception as e:
            print(f"Error updating location in DB: {e}")

    def get_location(self, db):
        try:
            with self.db.get_connection() as conn:
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
            with self.db.get_connection() as conn:
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
            with self.db.get_connection() as conn:
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
            with self.db.get_connection() as conn:
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
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if location exists for the user
                    check_location_query = """
                        SELECT location_id FROM Accounts WHERE user_id = %s
                    """
                    cursor.execute(check_location_query, (self.user_id,))
                    location_id = cursor.fetchone()

                    if location_id:
                        # Update existing location with weather data
                        update_weather_query = """
                            UPDATE Location 
                            SET weather_data = %s 
                            WHERE location_id = %s
                        """
                        cursor.execute(update_weather_query, (json.dumps(weather_data), location_id['location_id']))
                    else:
                        # Insert new location with weather data
                        insert_location_query = """
                            INSERT INTO Location (weather_data) VALUES (%s)
                        """
                        cursor.execute(insert_location_query, (json.dumps(weather_data),))
                        new_location_id = cursor.lastrowid

                    conn.commit()
                    print("Weather data stored successfully")
        except Exception as e:
            print(f"Error storing weather data: {e}")

    def store_weather_data(self, weather_data):
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    # Check if location exists for the user
                    check_location_query = """
                        SELECT location_id FROM Accounts WHERE user_id = %s
                    """
                    cursor.execute(check_location_query, (self.user_id,))
                    location_id_result = cursor.fetchone()

                    if location_id_result:
                        location_id = location_id_result['location_id']
                        # Update existing location with weather data
                        update_weather_query = """
                            UPDATE Location 
                            SET weather_data = %s 
                            WHERE location_id = %s
                        """
                        cursor.execute(update_weather_query, (json.dumps(weather_data), location_id))
                    else:
                        # Insert new location with weather data
                        insert_location_query = """
                            INSERT INTO Location (weather_data) VALUES (%s)
                        """
                        cursor.execute(insert_location_query, (json.dumps(weather_data),))
                        new_location_id = cursor.lastrowid
                        # Update user's location_id
                        update_user_location_query = """
                            UPDATE Accounts SET location_id = %s WHERE user_id = %s
                        """
                        cursor.execute(update_user_location_query, (new_location_id, self.user_id))

                    conn.commit()
                    print("Weather data stored successfully")
        except Exception as e:
            print(f"Error storing weather data: {e}")

    def get_weather_data(self):
        try:
            with self.db.get_connection() as conn:
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