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
    print(f"\n🗺️ ROUTING AGENT DEBUG:")
    print(f"   📍 Input coords: {coords}")
    print(f"   🚶 Mode: {mode}")
    
    # Validate input
    if len(coords) < 2:
        error_msg = "Need at least 2 coordinates for routing"
        print(f"   ❌ Validation error: {error_msg}")
        raise ValueError(error_msg)
        
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
    print(f"   🌐 API URL: {url}")
    print(f"   📤 Request body: {body}")
    
    try:
        response = requests.post(url, headers=headers, json=body)
        print(f"   📊 Response status: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        print(f"   📥 Raw API response keys: {data.keys()}")
        
        # The API returns routes instead of features
        if 'routes' not in data or not data['routes']:
            print(f"   ❌ Unexpected API response: {data}")
            raise ValueError(f"API response missing 'routes' field")
            
        route = data['routes'][0]
        print(f"   🛣️ Route data keys: {route.keys()}")
        
        if 'summary' not in route:
            print(f"   ❌ Route missing 'summary' field")
            raise ValueError(f"API response missing 'summary' field")
            
        # Collect steps from all segments
        all_steps = []
        if 'segments' in route:
            print(f"   🔢 Route has {len(route['segments'])} segments")
            for i, segment in enumerate(route['segments']):
                if 'steps' in segment:
                    segment_steps = len(segment['steps'])
                    print(f"      Segment {i}: {segment_steps} steps")
                    all_steps.extend(segment['steps'])
                
        result = {
            "distance_km": route['summary']['distance'] / 1000,
            "duration_min": route['summary']['duration'] / 60,
            "steps": all_steps,
            "geometry": convert.decode_polyline(route.get('geometry', ''))['coordinates']  # list of [lat, lon]
        }
        
        print(f"   ✅ FINAL RESULT:")
        print(f"      📏 Distance: {result['distance_km']:.2f} km")
        print(f"      ⏱️ Duration: {result['duration_min']:.1f} minutes")
        print(f"      🚶 Steps: {len(result['steps'])}")
        print(f"      🗺️ Geometry points: {len(result['geometry'])}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {e}"
        print(f"   ❌ {error_msg}")
        raise Exception(error_msg)
    except (KeyError, IndexError, ValueError) as e:
        error_msg = f"Error processing routing data: {e}"
        print(f"   ❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"   ❌ {error_msg}")
        raise Exception(error_msg)

def create_route_map(route_data: dict, pois: list = None, filename: str = "route_map.html") -> str:
    """
    Create an interactive HTML map from route data.
    
    Args:
        route_data: Route dictionary with geometry, distance_km, duration_min, steps
        pois: Optional list of POI dictionaries with lat/lon coordinates
        filename: Output HTML filename
    
    Returns:
        Path to created HTML file
    """
    try:
        import folium
    except ImportError:
        print("❌ folium not installed. Install with: pip install folium")
        return None
    
    geometry = route_data.get('geometry', [])
    if not geometry:
        print("❌ No geometry data in route")
        return None
    
    # Calculate center point
    center_lat = sum(point[0] for point in geometry) / len(geometry)
    center_lon = sum(point[1] for point in geometry) / len(geometry)
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    
    # Add route line
    route_coords = [[lat, lon] for lat, lon in geometry]
    folium.PolyLine(
        route_coords,
        weight=4,
        color='blue',
        opacity=0.8,
        popup=f"Route: {route_data.get('distance_km', 0):.2f}km, {route_data.get('duration_min', 0):.1f}min"
    ).add_to(m)
    
    # Add start/end markers
    if geometry:
        folium.Marker([geometry[0][0], geometry[0][1]], 
                     popup="Start", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker([geometry[-1][0], geometry[-1][1]], 
                     popup="End", icon=folium.Icon(color='red')).add_to(m)
    
    # Add POI markers
    if pois:
        for poi in pois:
            lat = poi.get('lat', 0)
            lon = poi.get('lon', 0) or poi.get('lng', 0)
            if lat and lon:
                folium.Marker(
                    [lat, lon],
                    popup=poi.get('name', 'POI'),
                    icon=folium.Icon(color='orange')
                ).add_to(m)
    
    # Save map
    file_path = os.path.abspath(filename)
    m.save(file_path)
    print(f"🗺️ Route map saved to: {file_path}")
    return file_path