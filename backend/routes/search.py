from flask import Blueprint, request, jsonify
from services.google_search import perform_search

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    results = perform_search(query)
    return jsonify(results)
