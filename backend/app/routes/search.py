# Handles HTTP requests for searches

from flask import Blueprint, request, jsonify, current_app
from ..services.google_search import perform_search
from ..models.user import User

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    user_id = request.args.get('user_id')

    # Ensure user_id and query are provided
    if not user_id or not query:
        return jsonify({"error": "user_id and query are required"}), 400

    # Initialize User instance
    user_instance = User(user_id=user_id)
    
    # Perform the search using Google Search API
    api_key = current_app.config['GOOGLE_API_KEY']
    cx = current_app.config['GOOGLE_CX']
    results = perform_search(query, api_key, cx)

    # Record the search query and results in the database
    user_instance.insert_query(query)
    for result in results.get('items', []):
        user_instance.insert_search_result(query, result['title'])

    return jsonify(results)

@search_bp.route('/api/search/results', methods=['GET'])
def get_search_results():
    user_id = request.args.get('user_id')
    query = request.args.get('query')

    # Ensure user_id and query are provided
    if not user_id or not query:
        return jsonify({"error": "user_id and query are required"}), 400

    # Initialize User instance
    user_instance = User(user_id=user_id)
    
    # Retrieve search results from the database
    results = user_instance.get_search_results(query)
    
    if results:
        return jsonify([result['result_text'] for result in results]), 200
    else:
        return jsonify({"error": "No results found"}), 404