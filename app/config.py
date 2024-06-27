# app.config.py

import os

class Config:
    # Google Search API
    GOOGLE_API_KEY = 'AIzaSyDa83ukRR4dlqykb_5NmxRm3o-BKj6_zkY'
    GOOGLE_CX = '674dd5606f7914a34'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'key'

    # MySQL: User Database
    USER_DB_HOST = '194.104.156.210'
    USER_DB_PORT = '3306'
    USER_DB_USER = 'u30529_i8EvvPQCAB'
    USER_DB_PASS = '1BrMMkcomapI9zdW=aeuBMMl'
    USER_DB_NAME = 's30529_userDB'

    # MySQL: Knowledgebase Database
    #KNOW_DB_HOST = 'localhost'
    #KNOW_DB_PORT = '3306'
    #KNOW_DB_USER = 'bassholes'
    #KNOW_DB_PASS = 'password'
    #KNOW_DB_NAME = 'knowledgeDB'