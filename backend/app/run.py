# app.py or run.py

from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    api_key = 'AIzaSyDa83ukRR4dlqykb_5NmxRm3o-BKj6_zkY'
    cx = '674dd5606f7914a34'
    search_parameters = {
        'q': query,
        'key': api_key,
        'cx': cx,
        'siteSearch': 'tpwd.texas.gov',
        'siteSearch': 'fisheries.noa',
        'siteSearch': 'nps.gov',  # Restrict search to .gov sites
        'siteSearch': 'takemefishing.org',
        'siteSearch': 'saltstrong.com',
        'siteSearchFilter': 'i'   # i: Include results from the specified site(s)
    }

    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}'

    response = requests.get(url, params=search_parameters)
    data = response.json()

    if 'items' not in data:
        return jsonify({"error": "No results found"}), 404

    return render_template('results.html', results=data['items'])

if __name__ == '__main__':
    app.run(debug=True)
