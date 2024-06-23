# Handles HTTP requests for searches

from flask import Blueprint, request, jsonify, current_app
from services.google_search import perform_search

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    api_key = current_app.config['GOOGLE_API_KEY']
    cx = current_app.config['GOOGLE_CX']
    results = perform_search(query, api_key, cx)
    return jsonify(results)