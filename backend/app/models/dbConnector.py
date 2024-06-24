import mysql.connector
from mysql.connector import pooling, Error
from config import Config

class dbConnector:
    def __init__(self):
        self.dbconfig = {
            "host": Config.MYSQL_HOST,
            "user": Config.MYSQL_USER,
            "password": Config.MYSQL_PASSWORD,
            "database": Config.MYSQL_DB
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