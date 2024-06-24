# Handles HTTP requests for users

from flask import Blueprint, request, jsonify
from models.user import get_user, insert_user, update_user, delete_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    user = get_user(user_id)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user_id = insert_user(data)
    if new_user_id:
        return jsonify({"id": new_user_id}), 201
    else:
        return jsonify({"error": "User creation failed"}), 400

@user_bp.route('/user/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    data = request.get_json()
    success = update_user(user_id, data)
    if success:
        return jsonify({"message": "User updated"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route('/user/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
    success = delete_user(user_id)
    if success:
        return jsonify({"message": "User deleted"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route('/user/<int:user_id>/location', methods=['GET'])
def get_user_location(user_id):
    user = get_user(user_id)
    if user:
        location = user.get_user_location()
        if location:
            return jsonify(location), 200
        else:
            return jsonify({"error": "Location not found"}), 404
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route('/user/<int:user_id>/location', methods=['PUT'])
def update_user_location(user_id):
    user = get_user(user_id)
    if user:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if latitude is not None and longitude is not None:
            user.update_location()
            return jsonify({"message": "Location updated"}), 200
        else:
            return jsonify({"error": "Invalid data"}), 400
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route('/user/<int:user_id>/weather/store', methods=['POST'])
def store_user_weather(user_id):
    user = get_user(user_id)
    if user:
        weather_data = request.get_json()
        user.store_weather_data(weather_data)
        return jsonify({"message": "Weather data stored"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route('/user/<int:user_id>/weather', methods=['GET'])
def get_user_weather(user_id):
    user = get_user(user_id)
    if user:
        weather_data = user.get_weather_data()
        if weather_data:
            return jsonify(weather_data), 200
        else:
            return jsonify({"error": "No weather data found"}), 404
    else:
        return jsonify({"error": "User not found"}), 404

@user_bp.route('/user/<int:user_id>/weather/current', methods=['GET'])
def get_current_weather(user_id):
    user = get_user(user_id)
    if user:
        current_weather = user.get_weather()
        if current_weather:
            return jsonify(current_weather), 200
        else:
            return jsonify({"error": "Weather data fetch failed"}), 500
    else:
        return jsonify({"error": "User not found"}), 404