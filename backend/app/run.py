# app.run.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
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

def fetch_location(ip_address, db_path):
    try:
        reader = geoip2.database.Reader(db_path)
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
            current_temp = data['hourly']['temperature_2m']['0']['value']
            current_wind_speed = data['hourly']['windspeed_10m']['0']['value']
            return {'temperature': current_temp, 'windspeed': current_wind_speed}
        else:
            return None
    except requests.exceptions.RequestException as e:
        print("Request error while fetching weather data:", e)
        return None
    except Exception as e:
        print("An error occurred while fetching weather data:", e)
        return None

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
        'siteSearch': 'in-fisherman.com',
        'siteSearch': 'nps.gov',  # Restrict search to .gov sites
        #'siteSearch': 'takemefishing.org',
        #'siteSearch': 'saltstrong.com',
        'siteSearchFilter': 'i'   # i: Include results from the specified site(s)
    }

    if categories:
        category_filter = ' OR '.join(categories)
        search_parameters['q'] += f' ({category_filter})'

    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}'

    # @ carson, I think we can remove the "?q={query}&key={api_key}&cx={cx}"
    # from url since they are already getting passed into the below request as params
    # -tanner

    response = requests.get(url, params=search_parameters)
    data = response.json()

    if 'items' not in data:
        return jsonify({"error": "No results found"}), 404

    return render_template('results.html', results=data['items'])

@app.route('/weather.html')
def weather():
    return render_template('weather.html')

@app.route('/profile.html')
def profile():
    return render_template('profile.html')

@app.route('/fish.html')
def fish():
    return render_template('fish.html')

def store_local_user(db_path):
    user = User(user_id=None)
    user.insert_user(username="local_user")
    
    ip_address = fetch_public_ip()
    if ip_address:
        location = fetch_location(ip_address, db_path)
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
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'GeoLite2-City.mmdb')
    with app.app_context():
        init_db() # Initialize the database
        store_local_user(db_path) # Basic functionality for MVP
    app.run(debug=True)