# app.config.py

import os

class Config:
    # Google Search API
    GOOGLE_API_KEY = 'AIzaSyDjs_U4wn959j-JSzTjRA6K3S98V73Z1t8'
    GOOGLE_CX = '928929e517dbc4982'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'key'

    # MySQL: User Database
    USER_DB_HOST = '194.104.156.210'
    USER_DB_PORT = '3306'
    USER_DB_USER = 'u30529_i8EvvPQCAB'
    USER_DB_PASS = '1BrMMkcomapI9zdW=aeuBMMl'
    USER_DB_NAME = 's30529_userDB'