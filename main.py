import typer
from agents.geocoder import geocode_location
from agents.poi_fetcher import fetch_pois
from agents.description_agent import fetch_poi_description
from agents.routing_agent import get_route


app = typer.Typer()

@app.command()
def plan_trip(destination: str):
    print(f"\n🔍 Geocoding destination: {destination}")
    try:
        geo_info = geocode_location(destination)
        print(f"📍 Coordinates: {geo_info['lat']}, {geo_info['lon']}")
    except Exception as e:
        print(f"❌ Geocoding error: {e}")
        return

    print("\n📌 Fetching nearby points of interest...")
    try:
        pois = fetch_pois(geo_info['lat'], geo_info['lon'], kinds=["interesting_places","sport"])
        for i, poi in enumerate(pois, start=1):
            print(f"{i}. {poi['name']} ({poi['dist']:.0f}m away)")
    except Exception as e:
        print(f"❌ POI fetch error: {e}")

    print("\n📝 Fetching detailed descriptions...")
    for i, poi in enumerate(pois[:5], start=1):  # limit to top 5
        try:
            desc = fetch_poi_description(poi['id'])
            print(f"\n{i}. {desc['name']}")
            print(f"   📖 {desc['description']}")
            print(f"   🔗 {desc['url']}")
            if desc['image']:
                print(f"   🖼️ Image: {desc['image']}")
        except Exception as e:
            print(f"   ⚠️ Failed to get description: {e}")

    print("\n🗺️ Calculating route through top 3 POIs...")
    coords = [[poi['lon'], poi['lat']] for poi in pois[:3]]

    print("\n🛣️ Planning fixed route through selected POIs...")
    try:
        route = get_route(coords)
        print(f"📏 Total Distance: {route['distance_km']:.2f} km")
        print(f"⏱️ Estimated Time: {route['duration_min']:.1f} min")

        print("\n📍 Step-by-step directions:")
        for i, step in enumerate(route['steps']):
            print(f"{i+1}. {step['instruction']} ({step['distance']} m, {round(step['duration'] / 60, 1)} min)")
    except Exception as e:
        print(f"❌ Routing error: {e}")
@app.command()
def veiw_trip():
    print("\n📅 Viewing trip details...")
    # Placeholder for viewing trip details logic
    print("Trip details are currently not implemented.")

if __name__ == "__main__":
    app()
