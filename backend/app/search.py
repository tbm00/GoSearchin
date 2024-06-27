# app.search.py

from flask import Blueprint, request, jsonify
from app.services.google_search import perform_search
from config import Config

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    API_KEY = Config.GOOGLE_API_KEY
    CX = Config.GOOGLE_CX

    search_results = perform_search(query, API_KEY, CX)
    return jsonify(search_results)