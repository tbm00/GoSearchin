# app.routes.user.py
# Handles HTTP requests for users

from flask import Blueprint, request, jsonify
from ..models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    user_instance = User(user_id=user_id)
    user_data = user_instance.get_user()
    if user_data:
        return jsonify(user_data), 200
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user_instance = User(user_id=None)
    new_user_instance.insert_user(data.get('username'))
    user_data = new_user_instance.get_user()
    if user_data:
        return jsonify({"id": user_data['user_id']}), 201
    else:
        return jsonify({"error": "User creation failed"}), 400

@user_bp.route('/user/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    data = request.get_json()
    user_instance = User(user_id=user_id)
    success = user_instance.update_user(data)
    if success:
        return jsonify({"message": "User updated"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route('/user/<int:user_id>', methods=['DELETE'], endpoint='remove_user')
def remove_user(user_id):
    user_instance = User(user_id=user_id)
    success = user_instance.delete_user()
    if success:
        return jsonify({"message": "User deleted"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route('/user/<int:user_id>/location', methods=['GET'])
def get_user_location(user_id):
    user_instance = User(user_id=user_id)
    location = user_instance.get_location()
    if location:
        return jsonify(location), 200
    else:
        return jsonify({"error": "Location not found"}), 404

@user_bp.route('/user/<int:user_id>/location', methods=['PUT'])
def update_user_location(user_id):
    user_instance = User(user_id=user_id)
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    ip = data.get('ip')
    if latitude is not None and longitude is not None and ip is not None:
        user_instance.update_location_db(latitude, longitude, ip)
        return jsonify({"message": "Location updated"}), 200
    else:
        return jsonify({"error": "Invalid data"}), 400

@user_bp.route('/user/<int:user_id>/weather/store', methods=['POST'])
def store_user_weather(user_id):
    user_instance = User(user_id=user_id)
    weather_data = request.get_json()
    user_instance.store_weather_data(weather_data)
    return jsonify({"message": "Weather data stored"}), 200

@user_bp.route('/user/<int:user_id>/weather', methods=['GET'])
def get_user_weather(user_id):
    user_instance = User(user_id=user_id)
    weather_data = user_instance.get_weather_data()
    if weather_data:
        return jsonify(weather_data), 200
    else:
        return jsonify({"error": "No weather data found"}), 404