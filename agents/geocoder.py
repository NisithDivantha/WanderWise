import requests
import time
import re

import requests
import time
import re
import os

def geocode_location(location: str):
    """Try Google Maps Geocoding first, fallback to Nominatim if needed."""
    location_clean = clean_location_string(location)
    search_strategies = [
        location_clean,
        f"{location_clean}, city",
        location_clean.replace(",", ""),
        location_clean.split(",")[0].strip() if "," in location_clean else location_clean
    ]

    # Try Google Maps Geocoding first
    for i, search_term in enumerate(search_strategies):
        try:
            print(f"🌍 Google Geocoding attempt {i+1}: '{search_term}'")
            result = google_maps_geocode(search_term)
            if result:
                print(f"✅ Google Success: {result['name']}")
                return result
        except Exception as e:
            print(f"❌ Google error with '{search_term}': {e}")
            continue

    # Fallback to Nominatim
    for i, search_term in enumerate(search_strategies):
        try:
            print(f"🔍 Nominatim Geocoding attempt {i+1}: '{search_term}'")
            result = nominatim_search(search_term)
            if result:
                print(f"✅ Nominatim Success: {result['name']}")
                return result
        except Exception as e:
            print(f"❌ Nominatim error with '{search_term}': {e}")
            continue

    raise ValueError(f"Could not geocode: {location}")

def google_maps_geocode(location: str) -> dict:
    """Geocode using Google Maps Geocoding API"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        raise ValueError("Google Maps API key not found in environment variables.")
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": location, "key": api_key}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"HTTP Status: {response.status_code}")
        
        data = response.json()
        print(f"Response status: {data.get('status')}")
        
        if data.get("status") == "REQUEST_DENIED":
            print(f"Request denied: {data.get('error_message', 'Unknown error')}")
            
        if data.get("status") == "OVER_QUERY_LIMIT":
            print(f"Quota exceeded")
            
        if data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            location_data = result["geometry"]["location"]
            return {
                "name": result.get("formatted_address", location),
                "lat": location_data["lat"],
                "lon": location_data["lng"],
                "source": "google"
            }
        
    except Exception as e:
        print(f"Request failed: {e}")
        
    return None

def clean_location_string(location: str) -> str:
    """Clean and standardize location string"""
    # Remove extra whitespace
    location = re.sub(r'\s+', ' ', location.strip())
    
    # Common replacements
    replacements = {
        'St.': 'Saint',
        'Mt.': 'Mount',
        'Ft.': 'Fort',
        'N.': 'North',
        'S.': 'South',
        'E.': 'East',
        'W.': 'West'
    }
    
    for old, new in replacements.items():
        location = location.replace(old, new)
    
    return location

def nominatim_search(location: str) -> dict:
    """Perform Nominatim search with enhanced parameters"""
    
    url = "https://nominatim.openstreetmap.org/search"
    
    # Enhanced search parameters
    params = {
        'q': location,
        'format': 'json',
        'limit': 5,  # Get more results to choose from
        'addressdetails': 1,  # Include address details
        'namedetails': 1,  # Include name details
        'extratags': 1,  # Include extra tags
        'dedupe': 1,  # Remove duplicates
        'bounded': 0,  # Don't restrict to viewbox
        'polygon_text': 0  # Don't need polygon data
    }
    
    headers = {
        'User-Agent': 'PersonalizedTravelPlanner/1.0 (nisithdiwantha@example.com)',
        'Accept': 'application/json',
        'Accept-Language': 'en'
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    
    if response.status_code == 200 and response.json():
        results = response.json()
        
        # Find the best result
        best_result = select_best_result(results, location)
        
        if best_result:
            # Extract additional information
            address = best_result.get('address', {})
            
            return {
                'name': format_location_name(best_result, location),
                'lat': float(best_result['lat']),
                'lon': float(best_result['lon']),
                'display_name': best_result.get('display_name', ''),
                'place_type': best_result.get('type', ''),
                'importance': float(best_result.get('importance', 0)),
                'country': address.get('country', ''),
                'state': address.get('state', ''),
                'city': address.get('city') or address.get('town') or address.get('village', ''),
                'osm_id': best_result.get('osm_id', ''),
                'osm_type': best_result.get('osm_type', ''),
                'bounding_box': best_result.get('boundingbox', [])
            }
    
    return None

def select_best_result(results: list, original_query: str) -> dict:
    """Select the best result from multiple Nominatim results"""
    
    if not results:
        return None
    
    if len(results) == 1:
        return results[0]
    
    # Scoring system for results
    scored_results = []
    
    for result in results:
        score = 0
        display_name = result.get('display_name', '').lower()
        result_type = result.get('type', '')
        importance = float(result.get('importance', 0))
        
        # Boost score based on result type preference
        type_scores = {
            'city': 100,
            'town': 90,
            'village': 80,
            'administrative': 70,
            'county': 60,
            'state': 50,
            'country': 40,
            'tourism': 85,
            'attraction': 85
        }
        
        score += type_scores.get(result_type, 20)
        
        # Boost score based on importance
        score += importance * 50
        
        # Boost if query terms appear in display name
        query_words = original_query.lower().split()
        for word in query_words:
            if len(word) > 2 and word in display_name:
                score += 30
        
        # Penalize if result is too generic
        if len(display_name) > 100:
            score -= 10
        
        scored_results.append((score, result))
    
    # Return the highest scoring result
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return scored_results[0][1]

def format_location_name(result: dict, original_query: str) -> str:
    """Format a nice location name from Nominatim result"""
    
    address = result.get('address', {})
    
    # Try to build a nice name
    name_parts = []
    
    # Add city/town/village
    city = address.get('city') or address.get('town') or address.get('village')
    if city:
        name_parts.append(city)
    
    # Add state/region if different from city
    state = address.get('state')
    if state and state != city:
        name_parts.append(state)
    
    # Add country
    country = address.get('country')
    if country:
        name_parts.append(country)
    
    if name_parts:
        return ', '.join(name_parts)
    else:
        # Fallback to original query
        return original_query

def geocode_multiple_locations(locations: list) -> list:
    """Geocode multiple locations with rate limiting"""
    
    results = []
    
    for i, location in enumerate(locations, 1):
        try:
            print(f"\n📍 Geocoding {i}/{len(locations)}: {location}")
            result = geocode_location(location)
            results.append(result)
            
        except Exception as e:
            print(f"❌ Failed to geocode {location}: {e}")
            results.append({
                'name': location,
                'lat': 0.0,
                'lon': 0.0,
                'error': str(e)
            })
        
        # Rate limiting - be nice to Nominatim
        if i < len(locations):
            time.sleep(1)
    
    return results

def reverse_geocode(lat: float, lon: float) -> dict:
    """Convert coordinates back to address using Nominatim"""
    
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1
    }
    
    headers = {
        'User-Agent': 'PersonalizedTravelPlanner/1.0 (nisithdiwantha@example.com)'
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        address = data.get('address', {})
        
        return {
            'address': data.get('display_name', f"{lat}, {lon}"),
            'lat': lat,
            'lon': lon,
            'country': address.get('country', ''),
            'state': address.get('state', ''),
            'city': address.get('city') or address.get('town') or address.get('village', ''),
            'road': address.get('road', ''),
            'postcode': address.get('postcode', '')
        }
    
    return {
        'address': f"{lat}, {lon}",
        'lat': lat,
        'lon': lon,
        'error': 'Reverse geocoding failed'
    }

def get_location_details(location: str) -> dict:
    """Get detailed information about a location"""
    
    try:
        result = geocode_location(location)
        
        # Add nearby places
        lat, lon = result['lat'], result['lon']
        
        # Search for nearby places of interest
        nearby_url = "https://nominatim.openstreetmap.org/search"
        nearby_params = {
            'format': 'json',
            'limit': 10,
            'bounded': 1,
            'viewbox': f"{lon-0.01},{lat+0.01},{lon+0.01},{lat-0.01}",  # Small bounding box
            'q': 'tourism OR historic OR amenity'
        }
        
        headers = {
            'User-Agent': 'PersonalizedTravelPlanner/1.0 (nisithdiwantha@example.com)'
        }
        
        nearby_response = requests.get(nearby_url, params=nearby_params, headers=headers, timeout=10)
        
        nearby_places = []
        if nearby_response.status_code == 200:
            nearby_data = nearby_response.json()
            for place in nearby_data[:5]:  # Limit to 5 nearby places
                nearby_places.append({
                    'name': place.get('display_name', ''),
                    'type': place.get('type', ''),
                    'lat': float(place['lat']),
                    'lon': float(place['lon'])
                })
        
        result['nearby_places'] = nearby_places
        return result
        
    except Exception as e:
        raise ValueError(f"Could not get location details for: {location}")

# Test function
def test_geocoder():
    """Test the enhanced geocoder with various locations"""
    
    test_locations = [
        "Kandy, Sri Lanka",
        "Paris, France", 
        "Tokyo, Japan",
        "New York City",
        "London",
        "Invalid Location 12345"
    ]
    
    print("🧪 Testing Enhanced Nominatim Geocoder")
    print("=" * 50)
    
    for location in test_locations:
        try:
            result = geocode_location(location)
            print(f"✅ {location} -> {result['name']} ({result['lat']:.4f}, {result['lon']:.4f})")
        except Exception as e:
            print(f"❌ {location} -> Failed: {e}")
        
        time.sleep(1)  # Rate limiting

if __name__ == "__main__":
    test_geocoder()