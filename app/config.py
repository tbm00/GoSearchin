# app.config.py

import os

class Config:
    # Google Search API
    GOOGLE_API_KEY = ''
    GOOGLE_CX = ''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'key'

    # MySQL: User Database
    USER_DB_HOST = ''
    USER_DB_PORT = ''
    USER_DB_USER = ''
    USER_DB_PASS = ''
    USER_DB_NAME = ''

    # MySQL: Knowledgebase Database
    #KNOW_DB_HOST = ''
    #KNOW_DB_PORT = ''
    #KNOW_DB_USER = ''
    #KNOW_DB_PASS = ''
    #KNOW_DB_NAME = ''