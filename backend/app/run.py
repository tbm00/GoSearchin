# app.py or run.py

from flask import Flask, render_template, request, current_app, jsonify
import requests
import geoip2.database
from app.models.user import User
from app.models.dbConnector import dbConnector
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

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

def fetch_location(ip_address):
    try:
        # Specify the path to the MaxMind GeoIP2 database
        reader = geoip2.database.Reader('/data/GeoLite2-City.mmdb')

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

@app.route('/')
def index():
    return render_template('index.html')

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

def store_local_user():
    user = User(user_id=None)
    user.insert_user(username="local_user")
    
    ip_address = fetch_public_ip()
    if ip_address:
        location = fetch_location(ip_address)
        if location:
            user.update_location_db(location['latitude'], location['longitude'])
            
            weather = fetch_weather(location['latitude'], location['longitude'])
            if weather:
                user.store_weather_data(weather)
                print("Location and weather data stored successfully.")

if __name__ == '__main__':
    with app.app_context():
        store_local_user() # basic functionality for MVP
    app.run(debug=True)