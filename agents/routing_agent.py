import requests
import os
from dotenv import load_dotenv
import openrouteservice
from openrouteservice import convert

load_dotenv()

ORS_API_KEY = os.getenv("ORS_API_KEY")
BASE_URL = "https://api.openrouteservice.org/v2/directions/foot-walking"  # or 'foot-walking'

def get_route(coords: list, mode: str = "foot-walking"):
    """
    Calculates route through all coordinates in the given order.
    """
    # Validate input
    if len(coords) < 2:
        raise ValueError("Need at least 2 coordinates for routing")
        
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }

    body = {
        "coordinates": coords,  # List of [lon, lat]
        "format": "json",       # Changed from geojson to json
        "instructions": True
    }

    url = f"https://api.openrouteservice.org/v2/directions/{mode}"
    
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        
        data = response.json()
        
        # The API returns routes instead of features
        if 'routes' not in data or not data['routes']:
            print(f"Unexpected API response: {data}")
            raise ValueError(f"API response missing 'routes' field")
            
        route = data['routes'][0]
        if 'summary' not in route:
            raise ValueError(f"API response missing 'summary' field")
            
        # Collect steps from all segments
        all_steps = []
        if 'segments' in route:
            for segment in route['segments']:
                if 'steps' in segment:
                    all_steps.extend(segment['steps'])
                
        return {
            "distance_km": route['summary']['distance'] / 1000,
            "duration_min": route['summary']['duration'] / 60,
            "steps": all_steps,
            "geometry": convert.decode_polyline(route.get('geometry', ''))['coordinates']  # list of [lat, lon]
        }
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")
    except (KeyError, IndexError, ValueError) as e:
        raise Exception(f"Error processing routing data: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")