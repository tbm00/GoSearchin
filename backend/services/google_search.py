import requests

def perform_search(query):
    # Google Search API Key and URL
    api_key = 'AIzaSyDa83ukRR4dlqykb_5NmxRm3o-BKj6_zkY'
    search_url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}'
    response = requests.get(search_url)
    return response.json()
