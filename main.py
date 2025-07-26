import typer
from agents.geocoder import geocode_location

app = typer.Typer()

@app.command()
def plan_trip(destination: str):
    print(f"\n🔍 Geocoding destination: {destination}")
    try:
        geo_info = geocode_location(destination)
        print(f"📍 Found coordinates: {geo_info['lat']}, {geo_info['lon']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Placeholder for next steps (POI agent, etc.)
    print("\n✅ Geocoding complete. Ready to call POI agent next!")

@app.command()
def veiw_trip():
    print("\n📅 Viewing trip details...")
    # Placeholder for viewing trip details logic
    print("Trip details are currently not implemented.")

if __name__ == "__main__":
    app()
