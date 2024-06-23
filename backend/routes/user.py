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