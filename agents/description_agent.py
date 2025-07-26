import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENTRIPMAP_API_KEY")
BASE_URL = "https://api.opentripmap.com/0.1/en/places"

def fetch_poi_description(xid: str):
    url = f"{BASE_URL}/xid/{xid}"
    params = {'apikey': API_KEY}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            'name': data.get('name'),
            'description': data.get('wikipedia_extracts', {}).get('text', 'No description available.'),
            'url': data.get('otm', ''),
            'image': data.get('preview', {}).get('source', '')
        }
    else:
        raise Exception(f"Error fetching description for xid={xid}: {response.status_code}")
