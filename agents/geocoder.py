import requests

def geocode_location(location: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': location,
        'format': 'json',
        'limit': 1
    }

    headers = {
        'User-Agent': 'PersonalizedTravelPlanner/1.0 (nisithdiwantha@example.com)'  # Change this to avoid rate limit issues
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return {
            'name': location,
            'lat': float(data['lat']),
            'lon': float(data['lon'])
        }
    else:
        raise ValueError(f"Could not geocode: {location}")
