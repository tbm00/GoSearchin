import requests

def get_weather_data(latitude, longitude):
    try:
        weather_url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'hourly': 'temperature_2m'
        }
        response = requests.get(weather_url, params=params)
        response.raise_for_status()  # raises exception for http errors
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return {"error": "Weather data fetch failed"}