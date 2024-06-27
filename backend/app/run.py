# app.run.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, current_app
import requests
import geoip2.database
from app.models.user import User
from app.models.dbConnector import dbConnector
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
#db = dbConnector().get_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists. Please use a different email.')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))  # Redirect to login page after successful registration

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Example authentication logic
        if username == 'demo' and email == 'demo@example.com' and password == 'password':
            # Successful login
            return redirect(url_for('index'))  # Redirect to index route
        else:
            # Failed login
            flash('Invalid username or password')  # Optional: Use Flask flash for error messages
            return redirect(url_for('login'))  # Redirect back to login route on failed login

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
    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,windspeed_10m'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            temperature_2m = data['hourly'].get('temperature_2m', [])
            windspeed_10m = data['hourly'].get('windspeed_10m', [])
            weather_condition = "Clear"  # This is a placeholder. Replace with actual data if available.
            weather_icon = "01d"  # Default icon. Replace with actual data if available.

            if temperature_2m and windspeed_10m:
                current_temp_c = temperature_2m[0]
                current_wind_speed_kmh = windspeed_10m[0]

                current_temp_f = (current_temp_c * 9/5) + 32
                current_wind_speed_mph = current_wind_speed_kmh * 0.621371

                return {
                    'temperature': current_temp_f,
                    'wind_speed': current_wind_speed_mph,
                    'condition': weather_condition,
                    'icon': weather_icon  # Add weather icon here
                }
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
    lat, lon = 40.7128, -74.0060  # Example coordinates. Replace with actual logic to get user location.
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

    # Fetch weather data (replace lat and lon with actual coordinates)
    lat, lon = 40.7128, -74.0060  # Example coordinates, replace with actual values
    weather_data = fetch_weather(lat, lon)
    
    print("Weather data:", weather_data)  # Debugging output

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
    user = User(user_id=None)
    user.insert_user(username="local_user")
    
    ip_address = fetch_public_ip()
    if ip_address:
        location = fetch_location(ip_address, mmdb_path)
        if location:
            user.update_location_db(location['latitude'], location['longitude'], ip_address)
            
            weather = fetch_weather(location['latitude'], location['longitude'])
            if weather:
                user.store_weather_data(weather)
                print("Location and weather data stored successfully.")

def init_db():
    db_connector = dbConnector()
    db_connector.create_schema()

if __name__ == '__main__':
    mmdb_path = os.path.join(os.path.dirname(__file__), 'data', 'GeoLite2-City.mmdb')
    with app.app_context():
        init_db() # Initialize the database
        run_as_local_user(mmdb_path) # Basic functionality for MVP
    app.run(debug=True)