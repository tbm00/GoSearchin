# app/search.py
from flask import Blueprint, request, jsonify
import requests

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    API_KEY = 'AIzaSyDa83ukRR4dlqykb_5NmxRm3o-BKj6_zkY'  # Replace with your actual API key
    CX = '674dd5606f7914a34'  # Replace with your actual Search Engine ID

    url = f'https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query}'

    response = requests.get(url)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Error fetching results from Google'}), response.status_code
