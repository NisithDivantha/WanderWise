import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENTRIPMAP_API_KEY")
BASE_URL = "https://api.opentripmap.com/0.1/en/places"

def fetch_pois(lat, lon, radius=15000, kinds="interesting_places", limit=20):
    url = f"{BASE_URL}/radius"
    params = {
        'apikey': API_KEY,
        'radius': radius,
        'lon': lon,
        'lat': lat,
        'kinds': kinds,
        'format': 'json',
        'limit': limit
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = []
        for poi in data:
            results.append({
                'name': poi.get('name'),
                'lat': poi['point']['lat'],
                'lon': poi['point']['lon'],
                'kind': poi.get('kinds'),
                'dist': poi.get('dist'),
                'id': poi.get('xid')
            })
        return results
    else:
        raise Exception(f"Error fetching POIs: {response.status_code}")
