# app.models.dbConnector.py

import mysql.connector
from mysql.connector import pooling, Error
from config import Config

class dbConnector:
    def __init__(self):
        self.dbconfig = {
            "host": Config.USER_DB_HOST,
            "port": Config.USER_DB_PORT,
            "user": Config.USER_DB_USER,
            "password": Config.USER_DB_PASS,
            "database": Config.USER_DB_NAME
        }
        self.connection_pool = pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            **self.dbconfig
        )

    def get_connection(self):
        return self.connection_pool.get_connection()
    
    def close_connection(self, connection):
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")

    def create_schema(self):
        schema_queries = [
            """
            CREATE TABLE IF NOT EXISTS Location (
                location_id INT AUTO_INCREMENT PRIMARY KEY,
                latitude DECIMAL(9,6),
                longitude DECIMAL(9,6),
                ip VARCHAR(45),
                weather_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (ip)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Accounts (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100),
                location_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES Location(location_id) ON DELETE SET NULL,
                UNIQUE KEY (username),
                INDEX (location_id),
                INDEX (username)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Queries (
                query_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                query_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Accounts(user_id) ON DELETE CASCADE,
                INDEX (user_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Results (
                result_id INT AUTO_INCREMENT PRIMARY KEY,
                query_id INT,
                result_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (query_id) REFERENCES Queries(query_id) ON DELETE CASCADE,
                INDEX (query_id)
            );
            """
        ]
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    for query in schema_queries:
                        cursor.execute(query)
                    conn.commit()
                print("Database schema created successfully")
        except Error as e:
            print(f"Error creating schema: {e}")

    def delete_database(self):
        tables = ['Location', 'Accounts', 'Queries', 'Results']
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                    for table in tables:
                        cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                    conn.commit()
                    print("All specified tables deleted successfully")
        except Exception as e:
            print(f"Error deleting tables: {e}")