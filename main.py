import typer
from agents.geocoder import geocode_location
from agents.poi_fetcher import fetch_pois

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

@app.command()
def veiw_trip():
    print("\n📅 Viewing trip details...")
    # Placeholder for viewing trip details logic
    print("Trip details are currently not implemented.")

if __name__ == "__main__":
    app()
