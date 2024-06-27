# app.run.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, current_app
from datetime import datetime, timezone
import requests, pytz
import geoip2.database
from app.models.user import User
from app.models.dbConnector import dbConnector
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
local_user = User(user_id=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        temp_username = request.form['username']
        temp_email = request.form['email']
        temp_password = request.form['password']

        # Check if the user already exists
        existing_user = User.query.filter_by(email=temp_email).first()
        if existing_user:
            flash('Email address already exists. Please use a different one.')
            return redirect(url_for('register'))
        existing_user = User.query.filter_by(username=temp_username).first()
        if existing_user:
            flash('Username already exists. Please use a different one.')
            return redirect(url_for('register'))

        success = local_user.update_user(temp_username, temp_email)

        if success:
            # Redirect to login page after successful registration
            flash('Registration successful. Username and email saved.')
            return redirect(url_for('index'))
        else:
            flash('Registration failed. Please try again.')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        temp_id = local_user.find_username(username)
        if temp_id:
            # Successful login
            local_user.user_id = temp_id
            local_user.username = username
            local_user.email = email
            return redirect(url_for('index'))  # Redirect to index
        else:
            # Failed login
            flash('Invalid username or password') 
            return redirect(url_for('login'))  # Redirect back to login

    # GET request (initial visit to /login or after failed login)
    return render_template('login.html')


# Route for index page (default landing page)
@app.route('/')
def index():
    return render_template('index.html')  # Redirect to login page by default

def fetch_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            ip_data = response.json()
            return ip_data['ip']
        else:
            print("Failed to get public IP address:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print("Request error while fetching public IP address:", e)
        return None
    except Exception as e:
        print("An error occurred while fetching public IP address:", e)
        return None

def fetch_location(ip_address, mmdb_path):
    try:
        reader = geoip2.database.Reader(mmdb_path)
        response = reader.city(ip_address)
        location = {
            "latitude": response.location.latitude,
            "longitude": response.location.longitude,
            #"city": response.city.name,
            #"country": response.country.name
        }
        return location
    except geoip2.errors.AddressNotFoundError:
        print("Address not found in MaxMind database for IP:", ip_address)
        return None
    except Exception as e:
        print("An error occurred while fetching location:", e)
        return None

def fetch_weather(lat, lon):
    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,windspeed_10m&temperature_unit=celsius&timezone=auto'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            temperature_2m = data['hourly'].get('temperature_2m', [])
            windspeed_10m = data['hourly'].get('windspeed_10m', [])
            timestamps = data['hourly'].get('time', [])
            elevation_m = data.get('elevation')

            if temperature_2m and windspeed_10m and timestamps:
                # Convert timestamps to datetime objects
                timestamps = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
                # Find the index of the most recent timestamp
                latest_index = max(range(len(timestamps)), key=lambda i: timestamps[i])
                
                current_temp_c = temperature_2m[latest_index]
                current_wind_speed_kmh = windspeed_10m[latest_index]

                current_temp_f = (current_temp_c * 9/5) + 32
                current_wind_speed_mph = current_wind_speed_kmh * 0.621371
                elevation_f = elevation_m * 3.28084 if elevation_m is not None else None
                elevation_f_r = round(elevation_f * 2) / 2 if elevation_f is not None else None

                weather_data = {
                    'temperature': current_temp_f,
                    'wind_speed': current_wind_speed_mph,
                    'elevation': elevation_f_r,
                }
                return weather_data
            else:
                print("Weather data is empty or not available.")
                return None
        else:
            print(f"Failed to fetch weather data: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print("Request error while fetching weather data:", e)
        return None
    except Exception as e:
        print("An error occurred while fetching weather data:", e)
        return None

@app.route('/get_weather_data')
def get_weather_data():
    lat, lon = local_user.coords['latitude'] , local_user.coords['longitude']
    weather_data = fetch_weather(lat, lon)
    return jsonify(weather_data)


@app.route('/search')
def search():
    query = request.args.get('q')
    categories = request.args.getlist('categories')

    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    api_key = current_app.config['GOOGLE_API_KEY']
    cx = current_app.config['GOOGLE_CX']
    search_parameters = {
        'q': query,
        'key': api_key,
        'cx': cx,
        'siteSearch': '.gov',
        'siteSearch': 'tpwd.texas.gov',
        'siteSearch': 'fisheries.noaa.gov',
        'siteSearchFilter': 'i'
    }

    if categories:
        category_filter = ' OR '.join(categories)
        search_parameters['q'] += f' ({category_filter})'

    response = requests.get('https://www.googleapis.com/customsearch/v1', params=search_parameters)
    data = response.json()

    if 'items' not in data:
        return jsonify({"error": "No results found"}), 404

    search_results = data['items']

    lat, lon = local_user.coords['latitude'] , local_user.coords['longitude']
    weather_data = fetch_weather(lat, lon)
    
    print("Weather data while searching:", weather_data)

    return render_template('results.html', results=search_results, weather=weather_data)

@app.route('/weather')
def weather():
    return render_template('weather.html')

app.route('/location')
def location():
    return render_template('location.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/fish.html')
def fish():
    return render_template('fish.html')

def run_as_local_user(mmdb_path):
    local_user.insert_user(username="local_user")

    local_user.ip = fetch_public_ip()
    print("Checkpoint: local_user.ip = " + local_user.ip)

    if local_user.ip != "null":
        local_user.coords = fetch_location(local_user.ip, mmdb_path)
        print("Checkpoint: local_user.coords = " + str(local_user.coords))
        
        if local_user.coords != [0,0]:
            local_user.update_location_db(local_user.coords['latitude'], local_user.coords['longitude'], local_user.ip)
            local_user.weather = fetch_weather(local_user.coords['latitude'], local_user.coords['longitude'])
            print("Checkpoint: local_user.weather = " + str(local_user.weather))
            
            if local_user.weather != [0, 0, 0]:
                local_user.store_weather_data(local_user.weather)
                print("Local user location and weather data stored in database.")

def init_db():
    db_connector = dbConnector()
    db_connector.create_schema()

if __name__ == '__main__':
    mmdb_path = os.path.join(os.path.dirname(__file__), 'data', 'GeoLite2-City.mmdb')
    with app.app_context():
        init_db() # Initialize the database
        run_as_local_user(mmdb_path) # Basic functionality for MVP
    app.run(debug=True)